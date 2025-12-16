"""
Spatial regression models for accuracy prediction.

Models:
- Linear Regression
- SVM (RBF kernel)
- LightGBM
- GAM (Monotonic / Without Interaction)
"""

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.metrics import r2_score
from scipy.stats import pearsonr


class SpatialRegressor:
    """
    Wrapper for various spatial regression models.
    
    Parameters
    ----------
    model_type : str, default='svm'
        Model type: 'linear', 'svm', 'lightgbm', 'gam_monotonic', 'gam_without_interaction'
    spline : int, default=7
        Number of spline knots for GAM
    lam : float, default=0.5
        Regularization parameter for GAM
    
    Example
    -------
    >>> model = SpatialRegressor(model_type='svm')
    >>> model.fit(X_train, y_train)
    >>> predictions = model.predict(X_test)
    >>> score = model.score(X_test, y_test, metric='correlation')
    """
    
    MODEL_NAMES = {
        'linear': 'Linear Regression',
        'svm': 'SVM (RBF)',
        'lightgbm': 'LightGBM',
        'gam_monotonic': 'Monotonic GAM',
        'gam_without_interaction': 'GAM (no interaction)',
    }
    
    def __init__(self, model_type='svm', spline=7, lam=0.5):
        self.model_type = model_type
        self.spline = spline
        self.lam = lam
        self.model = None
        self.scaler = StandardScaler()
    
    @property
    def display_name(self):
        """Human-readable model name."""
        return self.MODEL_NAMES.get(self.model_type, self.model_type)
    
    def fit(self, X, y):
        """
        Fit the spatial regression model.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training features (e.g., [longitude, latitude] or [longitude, latitude, density])
        y : array-like of shape (n_samples,)
            Target values (e.g., R² scores)
        
        Returns
        -------
        self
        """
        X = np.asarray(X)
        y = np.asarray(y)
        
        # Standardize features
        X_scaled = self.scaler.fit_transform(X)
        
        if self.model_type == 'linear':
            self.model = LinearRegression()
            self.model.fit(X_scaled, y)
        
        elif self.model_type == 'svm':
            self.model = SVR(kernel='rbf', C=1, gamma='scale')
            self.model.fit(X_scaled, y)
        
        elif self.model_type == 'lightgbm':
            from lightgbm import LGBMRegressor
            self.model = LGBMRegressor(n_estimators=100, max_depth=5, verbose=-1)
            self.model.fit(X_scaled, y)
        
        elif self.model_type in ['gam_monotonic', 'gam_without_interaction']:
            from pygam import LinearGAM, s, te
            n_features = X.shape[1]
            
            # Build terms with monotonic constraints
            # Note: sum() doesn't work for single term, use reduce instead
            from functools import reduce
            from operator import add
            term_list = [
                s(i, constraints='monotonic_inc', n_splines=self.spline, lam=self.lam) 
                for i in range(n_features)
            ]
            terms = reduce(add, term_list)
            
            # Add interaction term for gam_monotonic if 2+ features
            if self.model_type == 'gam_monotonic' and n_features >= 2:
                te_splines = max(4, self.spline // 4)  # Must be > spline_order (default 3)
                terms = terms + te(0, 1, n_splines=[te_splines, te_splines], lam=self.lam * 2)
            
            self.model = LinearGAM(terms)
            self.model.fit(X_scaled, y)
        
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        return self
    
    def predict(self, X):
        """
        Predict using the fitted model.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Features to predict
        
        Returns
        -------
        predictions : np.ndarray
            Predicted values
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X = np.asarray(X)
        X_scaled = self.scaler.transform(X)
        
        return self.model.predict(X_scaled)
    
    def score(self, X, y, metric='correlation'):
        """
        Score the model on test data.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test features
        y : array-like of shape (n_samples,)
            True values
        metric : str, default='correlation'
            'correlation' or 'r2'
        
        Returns
        -------
        score : float
        """
        y_pred = self.predict(X)
        
        if metric == 'correlation':
            return pearsonr(y, y_pred)[0]
        else:
            return r2_score(y, y_pred)
    
    def fit_score(self, X_train, y_train, X_test, y_test, metric='correlation'):
        """
        Fit and score in one call.
        
        Returns
        -------
        score : float
        """
        self.fit(X_train, y_train)
        return self.score(X_test, y_test, metric=metric)
