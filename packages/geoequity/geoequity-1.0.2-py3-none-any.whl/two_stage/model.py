"""
TwoStageModel: Two-Stage Spatial Accuracy Prediction Model

Stage 1: Monotonic GAM on density features (density, sufficiency)
Stage 2: SVM on spatial features (longitude, latitude) for residual prediction
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


class TwoStageModel:
    """
    Two-Stage Model: GAM (Density) + SVM (Spatial Residual)
    
    Stage 1: Uses sampling aggregation + Monotonic GAM to predict base R² (based on density features)
            Auto-detects sufficiency count:
            - Single sufficiency -> Uses density-only univariate monotonic GAM
            - Multiple sufficiency -> Uses (sufficiency_log, density) bivariate GAM + interaction
    
    Stage 2: Uses spatial aggregation + SVM to predict residuals (based on spatial features)
    
    Final: Prediction = GAM prediction + SVM residual prediction
    """
    
    def __init__(self, spline=7, lam=0.5, resolution=None, diagnose=False, 
                 spline_order=2, clip=None, diagnose_path=None):
        """
        Args:
            spline: Number of GAM spline knots
            lam: GAM regularization parameter
            resolution: Spatial aggregation resolution [lon_bins, lat_bins]
            diagnose: Whether to plot diagnostic figures after training (default False)
            spline_order: Spline order (0=constant, 1=linear, 2=quadratic, 3=cubic)
            clip: R² clipping range [min, max], default [-0.5, 1.0]
            diagnose_path: Diagnostic figure save paths [stage1_path, stage2_path]
        """
        self.spline = spline
        self.lam = lam
        self.resolution = resolution if resolution else [10, 10]
        self.auto_diagnose = diagnose  # Renamed to avoid shadowing diagnose() method
        self.spline_order = spline_order
        self.clip = clip if clip is not None else [-0.5, 1.0]
        self.diagnose_path = diagnose_path
        
        # Stage 1: GAM model (Density features)
        self.gam_model = None
        self.gam_scaler = None
        
        # Stage 2: SVM model (Spatial features for residual)
        self.svm_model = None
        self.svm_scaler = None
        self.stage2_features = ['longitude', 'latitude']
        
        # Auto-detect flag: single sufficiency value
        self.single_sufficiency = False
        
        # Diagnostic data cache - Stage 1 (GAM)
        self._stage1_X_raw = None
        self._stage1_X_scaled = None
        self._stage1_y_true = None
        self._stage1_y_pred = None
        self._actual_spline = None
        self._n_stage1 = 0
        
        # Diagnostic data cache - Stage 2 (SVM)
        self._stage2_data = None
        self._n_stage2 = 0
        
        # Scores and metrics
        self._stage1_score = None
        self._stage2_score = None
        self._stage1_corr = None
        self._stage1_mae = None
        self._stage2_corr = None
        self._stage2_mae = None
        self._total_corr = None
        self._total_mae = None
    
    def fit(self, df_train_raw, model_name, bins_intervals, use_seeds=True, split_by='grid', metric='r2'):
        """
        Train the two-stage model.
        
        Args:
            df_train_raw: Raw training data (must contain 'longitude', 'latitude', 'sufficiency', 
                         'sparsity', 'observed', 'predicted_{model_name}')
            model_name: Name of the model to predict (e.g., 'Ours')
            bins_intervals: Sparsity bins intervals (sparsity_bins_edges, suff_to_bin)
            use_seeds: Whether to use seeds aggregation
            split_by: Spatial aggregation method ('grid' or 'station')
            metric: Evaluation metric ('r2' or 'correlation')
        
        Returns:
            stage1_score: Stage 1 GAM score
            stage2_score: Stage 2 (GAM + SVM) score
        """
        from sklearn.metrics import r2_score
        from scipy.stats import pearsonr
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVR
        from pygam import LinearGAM, s, te
        
        # ====== Stage 1: Train GAM using sampling aggregation ======
        stage1_data_dict = prepare_sampling_features_space(
            bins_intervals, df_train_raw, [model_name], 
            split_by=split_by,
            resolution=self.resolution,
            use_seeds=use_seeds,
            clip=self.clip
        )

        stage1_data = stage1_data_dict.get(model_name)
        
        if stage1_data is None or len(stage1_data) < 5:
            raise ValueError(f"Insufficient data for model {model_name} in stage 1")
        
        # Auto-detect: check if sufficiency has only one unique value
        suff_log_values = stage1_data['sufficiency_log'].values
        suff_log_std = np.std(suff_log_values)
        self.single_sufficiency = (suff_log_std < 1e-6)
        
        # Extract density features (based on sufficiency count)
        if self.single_sufficiency:
            X_stage1 = stage1_data[['density']].values
        else:
            X_stage1 = stage1_data[['sufficiency_log', 'density']].values
        
        y_stage1 = stage1_data['r2'].values
        self._n_stage1 = len(y_stage1)
        
        # Auto-adjust spline count
        min_splines = self.spline_order + 1
        adjusted_spline = self.spline
        self._actual_spline = adjusted_spline
        
        # Train GAM with monotonic constraints
        self.gam_scaler = StandardScaler()
        X_stage1_scaled = self.gam_scaler.fit_transform(X_stage1)
        
        if self.single_sufficiency:
            self.gam_model = LinearGAM(
                s(0, constraints='monotonic_inc', n_splines=adjusted_spline, 
                  spline_order=self.spline_order, lam=self.lam)
            )
        else:
            interaction_spline = max(min_splines, adjusted_spline // 4)
            self.gam_model = LinearGAM(
                s(0, constraints='monotonic_inc', n_splines=adjusted_spline, 
                  spline_order=self.spline_order, lam=self.lam) + 
                s(1, constraints='monotonic_inc', n_splines=adjusted_spline, 
                  spline_order=self.spline_order, lam=self.lam) +
                te(0, 1, n_splines=[interaction_spline, interaction_spline],
                   spline_order=self.spline_order, lam=self.lam*2)
            )
        
        self.gam_model.fit(X_stage1_scaled, y_stage1)
        
        # Evaluate Stage 1
        y_gam_pred_train = self.gam_model.predict(X_stage1_scaled)
        from sklearn.metrics import mean_absolute_error
        self._stage1_corr, _ = pearsonr(y_stage1, y_gam_pred_train)
        self._stage1_mae = mean_absolute_error(y_stage1, y_gam_pred_train)
        self._stage1_score = self._stage1_corr  # Keep for compatibility
        
        # Save diagnostic data
        self._stage1_X_raw = X_stage1
        self._stage1_X_scaled = X_stage1_scaled
        self._stage1_y_true = y_stage1
        self._stage1_y_pred = y_gam_pred_train
        
        if self.auto_diagnose:
            stage1_save_path = self.diagnose_path[0] if self.diagnose_path and len(self.diagnose_path) > 0 else None
            self.plot_stage1_diagnosis(save_path=stage1_save_path)
        
        # ====== Stage 2: Train SVM to predict residuals ======
        stage2_data_dict = prepare_spatial_features(
            df_train_raw, [model_name],
            split_by=split_by,
            include_sampling_features=True,
            bins_intervals=bins_intervals,
            resolution=self.resolution,
            clip=self.clip
        )
        stage2_data = stage2_data_dict.get(model_name)
        
        if stage2_data is None or len(stage2_data) < 5:
            raise ValueError(f"Insufficient spatial data for model {model_name} in stage 2")
        
        self._n_stage2 = len(stage2_data)
        
        # Calculate residuals
        y_true = stage2_data['r2'].values
        
        # Use GAM to predict stage2 data
        if self.single_sufficiency:
            X_stage2_density = stage2_data[['density']].values
        else:
            X_stage2_density = stage2_data[['sufficiency_log', 'density']].values
        
        X_stage2_density_scaled = self.gam_scaler.transform(X_stage2_density)
        y_gam_pred = self.gam_model.predict(X_stage2_density_scaled)
        residuals = y_true - y_gam_pred
        
        # Train SVM to predict residuals
        X_stage2_spatial = stage2_data[self.stage2_features].values
        
        self.svm_scaler = StandardScaler()
        X_stage2_spatial_scaled = self.svm_scaler.fit_transform(X_stage2_spatial)
        
        self.svm_model = SVR(kernel='rbf', C=1, gamma='scale')
        self.svm_model.fit(X_stage2_spatial_scaled, residuals)
        
        # Evaluate Stage 2 (SVM for spatial residuals)
        residual_pred = self.svm_model.predict(X_stage2_spatial_scaled)
        y_final_pred = y_gam_pred + residual_pred
        
        from sklearn.metrics import mean_absolute_error
        # Total correlation (final prediction vs true)
        self._total_corr, _ = pearsonr(y_true, y_final_pred)
        self._total_mae = mean_absolute_error(y_true, y_final_pred)
        
        # Stage 2 SVM residual correlation
        self._stage2_corr, _ = pearsonr(residuals, residual_pred)
        self._stage2_mae = mean_absolute_error(residuals, residual_pred)
        self._stage2_score = self._total_corr  # Keep for compatibility
        
        # Save Stage 2 diagnostic data
        stage2_data_diag = stage2_data.copy()
        stage2_data_diag['r2_gam_pred'] = y_gam_pred
        stage2_data_diag['residual_true'] = residuals
        stage2_data_diag['residual_pred'] = residual_pred
        self._stage2_data = stage2_data_diag
        
        if self.auto_diagnose:
            stage2_save_path = self.diagnose_path[1] if self.diagnose_path and len(self.diagnose_path) > 1 else None
            self.plot_stage2_diagnosis(save_path=stage2_save_path)
        
        return self._stage1_score, self._stage2_score
    
    @property
    def stage1_score(self):
        return self._stage1_score if self._stage1_score is not None else 0.0
    
    @property
    def stage2_score(self):
        return self._stage2_score if self._stage2_score is not None else 0.0
    
    def predict(self, longitude, latitude, density, sufficiency=None):
        """
        Predict R² (full two-stage).
        
        Args:
            longitude: Scalar or array of longitude values
            latitude: Scalar or array of latitude values
            density: Scalar or array of density values
            sufficiency: Scalar or array of sufficiency values (raw, not log). 
                        Required if model was trained with multiple sufficiency levels.
                        Will be broadcast to match other arrays if scalar.
                        
        Returns:
            y_pred: Prediction (GAM + SVM residual)
        """
        if self.gam_model is None or self.svm_model is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        # Convert inputs to numpy arrays
        longitude = np.asarray(longitude).flatten()
        latitude = np.asarray(latitude).flatten()
        density = np.asarray(density).flatten()
        
        n_samples = len(longitude)
        
        # Check sufficiency requirement for multi-sufficiency mode
        if not self.single_sufficiency:
            if sufficiency is None:
                raise ValueError(
                    "Model was trained with multiple sufficiency levels. "
                    "You must provide 'sufficiency' parameter for prediction."
                )
            sufficiency = np.asarray(sufficiency).flatten()
            # Broadcast scalar to array if needed
            if len(sufficiency) == 1 and n_samples > 1:
                sufficiency = np.full(n_samples, sufficiency[0])
            sufficiency_log = np.log10(sufficiency)
        else:
            sufficiency_log = None
        
        # Stage 2: SVM predicts residual (using longitude, latitude)
        X_spatial = np.column_stack([longitude, latitude])
        X_spatial_scaled = self.svm_scaler.transform(X_spatial)
        residual_pred = self.svm_model.predict(X_spatial_scaled)
        
        # Stage 1: GAM predicts base R²
        if self.single_sufficiency:
            X_density = density.reshape(-1, 1)
        else:
            X_density = np.column_stack([sufficiency_log, density])
        
        X_density_scaled = self.gam_scaler.transform(X_density)
        y_gam_pred = self.gam_model.predict(X_density_scaled)
        
        # Final = GAM + residual
        y_pred = y_gam_pred + residual_pred
        
        return y_pred
    
    def predict_stage1_only(self, density, sufficiency=None):
        """
        Predict using only Stage 1 GAM (Density).
        
        Args:
            density: Array of density (sparsity) values
            sufficiency: Array of sufficiency values (raw, not log).
                        Required if model was trained with multiple sufficiency levels.
            
        Returns:
            y_pred: GAM prediction only (no SVM residual)
        """
        if self.gam_model is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        density = np.asarray(density).flatten()
        
        if not self.single_sufficiency:
            if sufficiency is None:
                raise ValueError(
                    "Model was trained with multiple sufficiency levels. "
                    "You must provide 'sufficiency' parameter for prediction."
                )
            sufficiency = np.asarray(sufficiency).flatten()
            sufficiency_log = np.log10(sufficiency)
            X_density = np.column_stack([sufficiency_log, density])
        else:
            X_density = density.reshape(-1, 1)
        
        X_density_scaled = self.gam_scaler.transform(X_density)
        y_gam_pred = self.gam_model.predict(X_density_scaled)
        
        return y_gam_pred
    
    def predict_stage2_only(self, longitude, latitude):
        """
        Predict using only Stage 2 SVM (Spatial residual).
        
        Args:
            longitude: Array of longitude values
            latitude: Array of latitude values
            
        Returns:
            residual_pred: SVM residual prediction only
        """
        if self.svm_model is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        longitude = np.asarray(longitude).flatten()
        latitude = np.asarray(latitude).flatten()
        
        X_spatial = np.column_stack([longitude, latitude])
        X_spatial_scaled = self.svm_scaler.transform(X_spatial)
        residual_pred = self.svm_model.predict(X_spatial_scaled)
        
        return residual_pred
    
    def plot_stage1_diagnosis(self, figsize=None, save_path=None):
        """
        Diagnose Stage 1 GAM fit quality.
        
        Single sufficiency: 1×3 figure (3 views of density)
        Multi sufficiency: 2×3 figure
          - Row 1: 3 views of sufficiency_log
          - Row 2: 3 views of density
        """
        import matplotlib.pyplot as plt
        
        if self._stage1_X_raw is None or self._stage1_y_true is None:
            print("⚠️  No diagnosis data available. Run fit() first.")
            return
        
        X_raw = self._stage1_X_raw
        y_true = self._stage1_y_true
        y_pred = self._stage1_y_pred
        
        # Determine layout based on mode
        if self.single_sufficiency:
            nrows, ncols = 1, 3
            figsize = figsize or (14, 5)
        else:
            nrows, ncols = 2, 3
            figsize = figsize or (14, 10)
        
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
        
        if nrows == 1:
            axes = axes.reshape(1, -1)
        
        def plot_variable_row(ax_row, X_var, var_name, row_idx):
            """Plot one row (3 subplots): X vs y_true, X vs y_pred+curve, y_true vs y_pred"""
            
            # Subplot 1: X vs y_true
            ax_row[0].scatter(X_var, y_true, alpha=0.6, s=30, c='steelblue', edgecolors='k', linewidths=0.5)
            ax_row[0].set_xlabel(var_name, fontsize=12)
            ax_row[0].set_ylabel('R² (True)', fontsize=12)
            ax_row[0].set_title(f'{var_name}: Training Data', fontsize=12, fontweight='bold')
            ax_row[0].grid(True, alpha=0.3)
            
            # Subplot 2: X vs y_pred + GAM fit curve
            ax_row[1].scatter(X_var, y_pred, alpha=0.6, s=30, c='coral', edgecolors='k', linewidths=0.5, label='GAM predictions')
            
            # Generate fit curve
            X_range = np.linspace(X_var.min(), X_var.max(), 200)
            
            if self.single_sufficiency:
                X_range_input = X_range.reshape(-1, 1)
                X_range_scaled = self.gam_scaler.transform(X_range_input)
                y_curve = self.gam_model.predict(X_range_scaled)
            else:
                # Bivariate: compute marginal average effect
                if row_idx == 0:
                    other_var_values = X_raw[:, 1]
                    y_curve_list = []
                    for x_val in X_range:
                        X_grid = np.column_stack([
                            np.full(len(other_var_values), x_val),
                            other_var_values
                        ])
                        X_grid_scaled = self.gam_scaler.transform(X_grid)
                        y_grid = self.gam_model.predict(X_grid_scaled)
                        y_curve_list.append(y_grid.mean())
                    y_curve = np.array(y_curve_list)
                else:
                    other_var_values = X_raw[:, 0]
                    y_curve_list = []
                    for x_val in X_range:
                        X_grid = np.column_stack([
                            other_var_values,
                            np.full(len(other_var_values), x_val)
                        ])
                        X_grid_scaled = self.gam_scaler.transform(X_grid)
                        y_grid = self.gam_model.predict(X_grid_scaled)
                        y_curve_list.append(y_grid.mean())
                    y_curve = np.array(y_curve_list)
            
            ax_row[1].plot(X_range, y_curve, 'b-', linewidth=2.5, label='GAM curve', alpha=0.8)
            ax_row[1].set_xlabel(var_name, fontsize=12)
            ax_row[1].set_ylabel('R² (GAM Predicted)', fontsize=12)
            ax_row[1].set_title(f'{var_name}: GAM Predictions + Curve', fontsize=12, fontweight='bold')
            ax_row[1].legend(loc='best', fontsize=9)
            ax_row[1].grid(True, alpha=0.3)
            
            # Subplot 3: y_true vs y_pred
            ax_row[2].scatter(y_true, y_pred, alpha=0.6, s=30, c='green', edgecolors='k', linewidths=0.5)
            ax_row[2].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 
                         'r--', linewidth=2, label='Perfect fit')
            ax_row[2].set_xlabel('R² (True)', fontsize=12)
            ax_row[2].set_ylabel('R² (GAM Predicted)', fontsize=12)
            ax_row[2].set_title('GAM Fit Quality', fontsize=12, fontweight='bold')
            ax_row[2].legend(fontsize=9)
            ax_row[2].grid(True, alpha=0.3)
        
        # Plot based on mode
        if self.single_sufficiency:
            plot_variable_row(axes[0], X_raw[:, 0], 'Density', 0)
        else:
            plot_variable_row(axes[0], X_raw[:, 0], 'Sufficiency_log', 0)
            plot_variable_row(axes[1], X_raw[:, 1], 'Density', 1)
        
        from sklearn.metrics import mean_absolute_error
        from scipy.stats import pearsonr
        corr, _ = pearsonr(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        
        mode_text = "Single Sufficiency (Density-only GAM)" if self.single_sufficiency else "Multiple Sufficiency (Full GAM)"
        fig.suptitle(f'Stage 1 GAM Diagnosis | Mode: {mode_text} | r={corr:.4f}, MAE={mae:.4f}', 
                     fontsize=14, fontweight='bold', y=1.02)
        
        plt.tight_layout()
        
        if save_path:
            import os
            os.makedirs(os.path.dirname(save_path), exist_ok=True) if os.path.dirname(save_path) else None
            file_format = os.path.splitext(save_path)[1][1:]
            plt.savefig(save_path, format=file_format, dpi=300, bbox_inches='tight')
            print(f"✓ Stage 1 diagram saved to: {save_path}")
        
        plt.show()
    
    def plot_stage2_diagnosis(self, figsize=None, save_path=None):
        """
        Diagnose Stage 2 SVM spatial residual fit.
        
        Rows by sufficiency bins, each row has 4 columns:
        - Col 1: Original R² spatial distribution
        - Col 2: True residual spatial distribution
        - Col 3: SVM predicted residual spatial distribution
        - Col 4: True vs predicted residual scatter plot
        """
        import matplotlib.pyplot as plt
        from sklearn.metrics import r2_score, mean_absolute_error
        
        if self._stage2_data is None:
            print("⚠️  No Stage 2 diagnosis data available. Run fit() first.")
            return
        
        df = self._stage2_data
        
        # Get unique sufficiency_bin values
        if 'sufficiency_bin' in df.columns:
            unique_bins = sorted(df['sufficiency_bin'].unique())
            n_rows = len(unique_bins)
        else:
            unique_bins = [None]
            n_rows = 1
        
        if figsize is None:
            figsize = (16, 4 * n_rows)
        
        fig, axes = plt.subplots(n_rows, 4, figsize=figsize)
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        
        for row_idx, suff_bin in enumerate(unique_bins):
            if suff_bin is not None:
                df_subset = df[df['sufficiency_bin'] == suff_bin]
                suff_mean = 10 ** df_subset['sufficiency_log'].mean()
                title_suffix = f"Sufficiency ≈ {suff_mean:.0f}"
            else:
                df_subset = df
                title_suffix = "All Data"
            
            lon = df_subset['longitude'].values
            lat = df_subset['latitude'].values
            r2_true = df_subset['r2'].values
            residual_true = df_subset['residual_true'].values
            residual_pred = df_subset['residual_pred'].values
            
            residual_r2 = r2_score(residual_true, residual_pred)
            residual_mae = mean_absolute_error(residual_true, residual_pred)
            from scipy.stats import pearsonr
            residual_corr, _ = pearsonr(residual_true, residual_pred)
            
            # Symmetric residual range
            residual_abs_max = max(abs(residual_true.min()), abs(residual_true.max()),
                                  abs(residual_pred.min()), abs(residual_pred.max()))
            residual_vmin, residual_vmax = -residual_abs_max, residual_abs_max
            
            # Col 1: Original R²
            ax1 = axes[row_idx, 0]
            scatter1 = ax1.scatter(lon, lat, c=r2_true, cmap='viridis', s=40, alpha=0.7, edgecolors='k', linewidths=0.5)
            ax1.set_xlabel('Longitude', fontsize=10)
            ax1.set_ylabel('Latitude', fontsize=10)
            ax1.set_title(f'Original R²\n{title_suffix}', fontsize=11, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            plt.colorbar(scatter1, ax=ax1, label='R² (True)')
            
            # Col 2: True residuals
            ax2 = axes[row_idx, 1]
            scatter2 = ax2.scatter(lon, lat, c=residual_true, cmap='coolwarm', s=40, alpha=0.7, 
                                  edgecolors='k', linewidths=0.5, vmin=residual_vmin, vmax=residual_vmax)
            ax2.set_xlabel('Longitude', fontsize=10)
            ax2.set_ylabel('Latitude', fontsize=10)
            ax2.set_title('Residual (True)', fontsize=11, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            plt.colorbar(scatter2, ax=ax2, label='Residual')
            
            # Col 3: Predicted residuals
            ax3 = axes[row_idx, 2]
            scatter3 = ax3.scatter(lon, lat, c=residual_pred, cmap='coolwarm', s=40, alpha=0.7,
                                  edgecolors='k', linewidths=0.5, vmin=residual_vmin, vmax=residual_vmax)
            ax3.set_xlabel('Longitude', fontsize=10)
            ax3.set_ylabel('Latitude', fontsize=10)
            ax3.set_title('Residual (SVM pred)', fontsize=11, fontweight='bold')
            ax3.grid(True, alpha=0.3)
            plt.colorbar(scatter3, ax=ax3, label='Residual (pred)')
            
            # Col 4: True vs Predicted
            ax4 = axes[row_idx, 3]
            ax4.scatter(residual_true, residual_pred, s=30, alpha=0.6, c='steelblue', edgecolors='k', linewidths=0.5)
            lim_min = min(residual_true.min(), residual_pred.min())
            lim_max = max(residual_true.max(), residual_pred.max())
            ax4.plot([lim_min, lim_max], [lim_min, lim_max], 'r--', linewidth=2, label='Perfect fit')
            ax4.set_xlabel('Residual (True)', fontsize=10)
            ax4.set_ylabel('Residual (SVM pred)', fontsize=10)
            ax4.set_title(f'True vs Predicted\nr={residual_corr:.3f}', fontsize=11, fontweight='bold')
            ax4.grid(True, alpha=0.3)
            ax4.legend(loc='best', fontsize=8)
        
        mode_text = "Single Sufficiency" if self.single_sufficiency else "Multiple Sufficiency"
        fig.suptitle(f'Stage 2 SVM Diagnosis | Mode: {mode_text}', fontsize=14, fontweight='bold', y=0.995)
        
        plt.tight_layout()
        
        if save_path:
            import os
            os.makedirs(os.path.dirname(save_path), exist_ok=True) if os.path.dirname(save_path) else None
            file_format = os.path.splitext(save_path)[1][1:]
            plt.savefig(save_path, format=file_format, dpi=300, bbox_inches='tight')
            print(f"✓ Stage 2 diagram saved to: {save_path}")
        
        plt.show()
    
    def diagnose(self, save_dir=None, show=True):
        """
        Generate diagnostic plots and text report.
        
        Args:
            save_dir: Directory to save outputs
            show: Whether to display plots
        """
        import os
        
        if self.gam_model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            self.plot_stage1_diagnosis(save_path=os.path.join(save_dir, 'stage1_gam.png'))
            self.plot_stage2_diagnosis(save_path=os.path.join(save_dir, 'stage2_svm.png'))
        else:
            if show:
                self.plot_stage1_diagnosis()
                self.plot_stage2_diagnosis()
        
        # Generate text report - with fallback for models fit before new metrics were added
        mode_text = "Single Sufficiency" if self.single_sufficiency else "Multi Sufficiency"
        
        # Fallback: compute metrics if not stored (for backward compatibility)
        if not hasattr(self, '_stage1_corr') or self._stage1_corr is None:
            from scipy.stats import pearsonr
            from sklearn.metrics import mean_absolute_error
            self._stage1_corr, _ = pearsonr(self._stage1_y_true, self._stage1_y_pred)
            self._stage1_mae = mean_absolute_error(self._stage1_y_true, self._stage1_y_pred)
        
        if not hasattr(self, '_total_corr') or self._total_corr is None:
            from scipy.stats import pearsonr
            from sklearn.metrics import mean_absolute_error
            df = self._stage2_data
            y_true = df['r2'].values
            y_final_pred = df['r2_gam_pred'].values + df['residual_pred'].values
            self._total_corr, _ = pearsonr(y_true, y_final_pred)
            self._total_mae = mean_absolute_error(y_true, y_final_pred)
            self._stage2_corr, _ = pearsonr(df['residual_true'].values, df['residual_pred'].values)
            self._stage2_mae = mean_absolute_error(df['residual_true'].values, df['residual_pred'].values)
        
        report = f"""
========== TwoStageModel Diagnosis ==========

Mode: {mode_text}

Stage 1 (Monotonic GAM) - Density/Sampling Effect:
  - r = {self._stage1_corr:.4f}, MAE = {self._stage1_mae:.4f}
  - Training samples: {self._n_stage1}
  - Spline knots: {self.spline}, Lambda: {self.lam}

Stage 2 (SVM) - Spatial Residual:
  - r = {self._stage2_corr:.4f}, MAE = {self._stage2_mae:.4f}
  - Training samples: {self._n_stage2}
  - Spatial features: {self.stage2_features}
  - Resolution: {self.resolution}

Total (GAM + SVM):
  - r = {self._total_corr:.4f}, MAE = {self._total_mae:.4f}

Key Insights:
  1. Density effect captured in Stage 1 (r={self._stage1_corr:.3f})
     → Predicts accuracy variation from sampling density
  2. Spatial pattern captured in Stage 2 (r={self._stage2_corr:.3f})
     → Predicts location-specific residuals
  3. Prediction ability:
     → Unseen sampling density: r={self._stage1_corr:.3f} (Stage 1)
     → Unseen locations: r={self._total_corr:.3f} (Total)

=============================================
"""
        
        if save_dir:
            with open(os.path.join(save_dir, 'diagnosis.txt'), 'w') as f:
                f.write(report.strip())
            print(f"✓ Diagnosis saved to: {save_dir}/")
            print("\nDiagnostic files saved:")
            print(f"  - {save_dir}/stage1_gam.png")
            print(f"  - {save_dir}/stage2_svm.png")
            print(f"  - {save_dir}/diagnosis.txt")
        
        if show:
            print(report)
        
        return {
            'stage1_corr': self._stage1_corr,
            'stage1_mae': self._stage1_mae,
            'stage2_corr': self._stage2_corr,
            'stage2_mae': self._stage2_mae,
            'total_corr': self._total_corr,
            'total_mae': self._total_mae,
            'n_stage1': self._n_stage1,
            'n_stage2': self._n_stage2,
            'single_sufficiency': self.single_sufficiency,
        }


# ============================================================
# Data Preparation Functions
# ============================================================

def prepare_sampling_features_space(bins_intervals, df, model_names, split_by='grid', 
                                    resolution=None, use_seeds=False, clip=None):
    """
    Two-stage aggregation: spatial grid first, then sufficiency/density bins.
    
    This is an enhanced version of prepare_sampling_features:
    - prepare_sampling_features: directly aggregates raw data by sufficiency×density
    - prepare_sampling_features_space: spatial aggregation → then sufficiency×density aggregation
    
    Args:
        bins_intervals: (sparsity_bins_edges, suff_to_bin) - passed to prepare_spatial_features
        df: Training data
        model_names: List of model names
        split_by: 'grid' or 'station'
        resolution: [lon_bins, lat_bins], default [10, 10]
        use_seeds: Compatibility parameter (unused)
        clip: R² clipping range [min, max], passed to prepare_spatial_features
    
    Returns:
        {model_name: DataFrame with columns [sufficiency_log, sparsity, longitude, latitude, r2]}
    """
    # Step 1: Call prepare_spatial_features to get spatially aggregated data (including density features)
    spatial_results = prepare_spatial_features(
        df, model_names,
        split_by=split_by,
        include_sampling_features=True,
        bins_intervals=bins_intervals,
        resolution=resolution,
        clip=clip
    )
    
    # Step 2: Further aggregate by sufficiency×density
    results_dict = {}
    
    for model_name, df_spatial in spatial_results.items():
        if len(df_spatial) == 0:
            results_dict[model_name] = pd.DataFrame()
            continue
        
        # Check for bin columns
        if 'sufficiency_bin' not in df_spatial.columns or 'density_bin' not in df_spatial.columns:
            raise ValueError("spatial_results must contain 'sufficiency_bin' and 'density_bin' columns")
        
        df_copy = df_spatial.copy()
        df_copy = df_copy.dropna(subset=['density_bin', 'sufficiency_bin'])
        
        # Aggregate by sufficiency_bin × density_bin
        results = []
        for name, group in df_copy.groupby(['sufficiency_bin', 'density_bin']):
            if len(group) < 1:
                continue
            
            result = {
                'sufficiency_log': group['sufficiency_log'].mean(),
                'density': group['density'].mean(),
                'longitude': group['longitude'].mean(),
                'latitude': group['latitude'].mean(),
                'sufficiency_bin': name[0],
                'density_bin': name[1],
                'r2': group['r2'].mean()
            }
            results.append(result)
        
        results_dict[model_name] = pd.DataFrame(results)
    
    return results_dict


def prepare_spatial_features(df, model_names, split_by='grid', include_sampling_features=True, 
                            bins_intervals=None, resolution=None, outlier_threshold=None, clip=None):
    """
    Prepare test data: aggregate by spatial method, optionally include sampling features.
    
    Args:
        df: Test data (must contain 'longitude', 'latitude', 'observed', 'predicted_{model_name}', 
            and optionally 'sparsity', 'sufficiency')
        model_names: List of model names
        split_by: 'grid' or 'station'
        include_sampling_features: Whether to include sufficiency_log and sparsity features
        bins_intervals: If include_sampling_features=True, provide bin boundaries
        resolution: [lon_bins, lat_bins], default [10, 10]
        outlier_threshold: R² outlier handling (deprecated, use clip)
        clip: R² clipping range [min, max], clips R² immediately after calculation
              e.g., [-0.5, 1.0] means clip R² to [-0.5, 1.0] range
              None means no clipping
    
    Returns:
        {model_name: DataFrame with columns [longitude, latitude, (sparsity, sufficiency_log), r2]}
    """
    from sklearn.metrics import r2_score
    
    if resolution is None:
        resolution = [10, 10]
    
    df_copy = df.copy()
    
    if split_by == 'grid':
        df_copy['longitude_bin'] = pd.cut(df_copy['longitude'], bins=resolution[0], labels=False)
        df_copy['latitude_bin'] = pd.cut(df_copy['latitude'], bins=resolution[1], labels=False)
        group_cols = ['longitude_bin', 'latitude_bin']
    else:  # station
        if 'Site_number' in df_copy.columns:
            df_copy['station_id'] = df_copy['Site_number']
        else:
            df_copy['station_id'] = df_copy.groupby(['longitude', 'latitude']).ngroup()
        group_cols = ['station_id']
    
    df_copy = df_copy.dropna(subset=group_cols)
    
    # If sampling features needed, assign bins
    if include_sampling_features and bins_intervals is not None:
        density_bins_edges, suff_to_bin = bins_intervals
        df_copy['density_bin'] = pd.cut(df_copy['density'], bins=density_bins_edges, labels=False)
        df_copy['sufficiency_bin'] = df_copy['sufficiency'].map(suff_to_bin)
        group_cols = group_cols + ['sufficiency_bin']
    
    results_dict = {}
    
    for model_name in model_names:
        model_col = f'predicted_{model_name}'
        if model_col not in df_copy.columns:
            continue
        
        results = []
        
        for name, group in df_copy.groupby(group_cols):
            if len(group) < 3:
                continue
            
            observed = group['observed'].values
            predicted = group[model_col].values
            valid_mask = ~(np.isnan(observed) | np.isnan(predicted) | 
                          np.isinf(observed) | np.isinf(predicted))
            
            if valid_mask.sum() < 5:
                continue
            
            r2 = r2_score(observed[valid_mask], predicted[valid_mask])
            
            # Clip R² (at source data stage, takes priority over outlier_threshold)
            if clip is not None and len(clip) == 2:
                r2 = np.clip(r2, clip[0], clip[1])
            
            # Handle outlier threshold (legacy, recommend using clip)
            if outlier_threshold is not None:
                if isinstance(outlier_threshold, str) and outlier_threshold.endswith('_remove'):
                    threshold_str = outlier_threshold.replace('_remove', '')
                    try:
                        threshold_val = float(threshold_str)
                        if r2 <= threshold_val:
                            continue
                    except ValueError:
                        pass
                elif isinstance(outlier_threshold, (int, float)):
                    if r2 <= outlier_threshold:
                        r2 = outlier_threshold
            
            result = {
                'longitude': group['longitude'].mean(),
                'latitude': group['latitude'].mean(),
                'r2': r2
            }
            
            if include_sampling_features:
                result['density'] = group['density'].mean()
                result['sufficiency_log'] = np.log10(group['sufficiency'].mean())
                result['density_bin'] = group['density_bin'].iloc[0]
                result['sufficiency_bin'] = group['sufficiency_bin'].iloc[0]
            
            results.append(result)
        
        results_dict[model_name] = pd.DataFrame(results)
    
    return results_dict


def find_bins_intervals(df, density_bins=7, sufficiency_values=None):
    """
    Find bin intervals for density and sufficiency.
    
    Args:
        df: DataFrame containing 'density' and 'sufficiency' columns
        density_bins: Number of density bins (default 7)
        sufficiency_values: List of unique sufficiency values. If None, auto-detect.
        
    Returns:
        (density_bins_edges, suff_to_bin): Tuple of bin edges and sufficiency mapping
    """
    # Density bins using quantiles
    density_bins_edges = np.quantile(df['density'].dropna(), 
                                     np.linspace(0, 1, density_bins + 1))
    density_bins_edges[0] = -np.inf
    density_bins_edges[-1] = np.inf
    
    # Sufficiency mapping
    if sufficiency_values is None:
        sufficiency_values = sorted(df['sufficiency'].unique())
    
    suff_to_bin = {v: i for i, v in enumerate(sufficiency_values)}
    
    return (density_bins_edges, suff_to_bin)
