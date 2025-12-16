import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

def split_test_train(df, seed=42, split=None, cv=None, time_range=None, sample=False, flag="Site",
 verbose=1, quality=None, gradient_direction='random_gradient', grid_size=10, thumbnail=False, project_path=None, add_flag=False, test_region=None):
    """
    Split dataframe into training and test sets with various strategies.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with at least 'longitude' and 'latitude' columns
    seed : int, default=42
        Random seed for reproducibility
    split : float, optional
        Proportion of data for test set (e.g., 0.1 means 10% test). 
        Cannot be used together with cv.
    cv : int, optional
        Number of folds for cross-validation (e.g., cv=5 for 5-fold CV).
        Cannot be used together with split.
    time_range : tuple, optional
        (start_date, end_date) to filter data by time
    sample : int, list of int, or False, default=False
        If int, randomly sample this many data points before splitting.
        If list of int, perform splitting for each sample size and return dict.
    flag : str or list of str, default="Site"
        Splitting strategy (or list of strategies):
        - "Site": Split by unique sites (longitude, latitude pairs)
        - "Site_gradient": Split by sites with gradient-based sampling
        - "Grid": Split by spatial grid cells
        - "Sample": Split by random samples
        - "Time": Split by time points
        - "OrderTime": Split by ordered time (first N time points for test)
        - "Hours": Split by hours of day
        - "Spatiotemporal": Combined spatial and temporal split (no data leakage)
            * Step 1: Split grids spatially using Grid method (e.g., 90% train, 10% test)
            * Step 2: Split ALL time points globally (50% train, 50% test, non-overlapping)
            * Train = train grids × train times
            * Test = test grids × test times
            * Guarantees test samples are new in BOTH space and time
            * Returns standard train/test format (same as other flags)
        - "train": Special mode for memorization testing
            * With split: all data as training, subset as test (test ⊂ train)
            * With cv: each fold uses (cv-1)/cv of data for both train and test (excludes 1 fold each time)
        If list (e.g., ['Site', 'Grid']), performs splitting for each strategy
        and returns dict with strategy names as keys
    verbose : int, default=1
        Verbosity level (0=silent, 1=detailed output)
    quality : list, optional
        Quality values to filter data
    gradient_direction : str, default='random_gradient'
        Direction for gradient sampling: 'longitude', 'latitude', 
        'distance_from_center', or 'random_gradient'
    grid_size : int, default=10
        Grid size for Grid-based splitting (creates grid_size x grid_size grids)
    thumbnail : bool, default=False
        If True, display spatial distribution plots (plt.show()) for 'Site', 'Grid', 'Site_gradient', or 'train' flags
        - Split mode: Green for train, Red for test
        - CV mode: Different color for each fold
        Note: Thumbnails are ALWAYS saved to project_path (as metadata) when project_path is provided
    project_path : str, optional
        If provided, automatically save split results to this directory.
        When sample is a list, creates subdirectories for each sample size.
    add_flag : bool, default=False
        Incremental mode for adding new flags to existing splits.
        - If False: Strict validation mode. Any configuration mismatch raises ValueError.
        - If True: Allows adding new flags to existing data without regenerating old ones.
          * Validates all existing flags strictly (sample, seed, cv must match)
          * Only generates data for new flags not in existing metadata
          * Updates metadata files while preserving existing entries
          * Raises ValueError if any existing flag configuration mismatches
    
    Returns
    -------
    If flag is a list:
        dict
            Dictionary with strategy names as keys, each containing the split results
            for that strategy. If sample is also a list, values are dicts with sample
            sizes as keys.
    
    If sample is a list (but flag is single):
        dict
            Dictionary with sample sizes as keys, each containing:
            (train_site_numbers, test_site_numbers, train_indices, test_indices, df_copy)
    
    If split mode (single split):
        train_site_numbers : list
            List of site numbers in training set
        test_site_numbers : list
            List of site numbers in test set
        train_indices : list
            List of dataframe indices for training set
        test_indices : list
            List of dataframe indices for test set
        df_copy : pd.DataFrame
            Processed dataframe copy
    
    If cv mode (cross-validation):
        train_site_numbers_list : list of lists
            List containing train site numbers for each fold
        test_site_numbers_list : list of lists
            List containing test site numbers for each fold
        train_indices_list : list of lists
            List containing train indices for each fold
        test_indices_list : list of lists
            List containing test indices for each fold
        df_copy : pd.DataFrame
            Processed dataframe copy
    
    Raises
    ------
    ValueError
        If both split and cv are provided, or if cv mode is used with unsupported flag
    
    Examples
    --------
    >>> # Single split mode
    >>> train_sites, test_sites, train_ind, test_ind, df_split = split_test_train(
    ...     df, split=0.2, flag='Site', seed=42
    ... )
    
    >>> # Cross-validation mode
    >>> train_site_list, test_site_list, train_ind_list, test_ind_list, df_split = split_test_train(
    ...     df, cv=5, flag='Site', seed=42
    ... )
    
    >>> # Memorization test mode (split)
    >>> train_sites, test_sites, train_ind, test_ind, df_split = split_test_train(
    ...     df, split=0.2, flag='train', seed=42
    ... )
    
    >>> # Memorization test mode (cv) - each fold uses 4/5 of data for both train and test
    >>> train_list, test_list, train_ind_list, test_ind_list, df_split = split_test_train(
    ...     df, cv=5, flag='train', seed=42
    ... )
    >>> # Fold 1 uses folds 2-5, Fold 2 uses folds 1,3-5, etc.
    
    >>> # Multiple strategies (flags)
    >>> results_dict = split_test_train(
    ...     df, cv=5, flag=['Site', 'Grid', 'Time'], seed=42,
    ...     project_path='data/splits/multi_strategy'
    ... )
    >>> # returns: {'Site': (train_list, test_list, ...), 'Grid': (...), 'Time': (...)}
    
    >>> # Multiple strategies + multiple samples (most complex case)
    >>> results_dict = split_test_train(
    ...     df, cv=5, flag=['Site', 'Grid'], sample=[10000, 50000], seed=42,
    ...     project_path='data/splits/multi_all'
    ... )
    >>> # returns: {'Site': {10000: (...), 50000: (...)}, 'Grid': {10000: (...), 50000: (...)}}
    
    >>> # Spatiotemporal split mode (Grid-based spatial + time split, no data leakage)
    >>> train_sites, test_sites, train_ind, test_ind, df_split = split_test_train(
    ...     df, split=0.2, flag='Spatiotemporal', seed=42, grid_size=10
    ... )
    >>> # Train: 80% grids × 50% global times (e.g., ~40% of total data)
    >>> # Test: 20% grids × other 50% global times (e.g., ~10% of total data)
    >>> # Test points are guaranteed new in BOTH location (grids) and time
    
    >>> # Spatiotemporal CV mode
    >>> train_list, test_list, train_ind_list, test_ind_list, df_split = split_test_train(
    ...     df, cv=5, flag='Spatiotemporal', seed=42, grid_size=10
    ... )
    >>> # Same spatiotemporal guarantee for each fold
    """

    
    # ============================================================================
    # STEP 0: Check existing metadata and validate consistency if project_path provided
    # ============================================================================
    if project_path:
        should_skip, existing_results, new_flags = validate_and_check_existing_splits(
            project_path, flag, sample, split, cv, seed, df, verbose, add_flag
        )
        
        # If validation passed and data exists
        if should_skip:
            # Full skip: all data already exists
            print("loaded splitting")
            return existing_results
        elif add_flag and new_flags is not None:
            # Incremental mode: only generate new flags
            if verbose == 1:
                print(f"\n✓ Incremental mode: generating only new flags: {new_flags}")
                print(f"  Existing flags will be loaded: {list(set([f if isinstance(flag, str) else f for f in flag]) - set(new_flags))}")
            # Update flag to only process new ones
            flag = new_flags if len(new_flags) > 1 else new_flags[0]
    
    # ============================================================================
    # STEP 1: Handle multiple flags (outermost layer)
    # ============================================================================
    if isinstance(flag, list) and len(flag) > 1:
        if verbose == 1:
            print(f"Processing multiple strategies (flags): {flag}")
        
        results_dict = {}
        for single_flag in flag:
            if verbose == 1:
                print(f"\n{'='*60}")
                print(f"Processing strategy: {single_flag}")
                print(f"{'='*60}")
            
            # Recursive call with single flag
            result = split_test_train(
                df=df, seed=seed, split=split, cv=cv, time_range=time_range,
                sample=sample,  # Pass through (will be handled in next recursion layer)
                flag=single_flag,  # Single flag string
                verbose=verbose, quality=quality,
                gradient_direction=gradient_direction, grid_size=grid_size,
                thumbnail=thumbnail, project_path=None, test_region=test_region  # Don't auto-save yet
            )
            results_dict[single_flag] = result
        
        # Save all results if project_path is provided
        if project_path:
            save_all_results(results_dict, flag, sample if sample else False, 
                           split, cv, seed, project_path, verbose, thumbnail=thumbnail)
        
        return results_dict
    
    # If flag is a list with single element, extract it
    if isinstance(flag, list) and len(flag) == 1:
        flag = flag[0]
    
    # ============================================================================
    # STEP 2: Handle multiple samples (second layer)
    # ============================================================================
    # Normalize sample to list for unified processing
    # Single sample is just a special case of multiple samples
    if sample and sample is not False:
        # Convert single sample to list
        if not isinstance(sample, list):
            sample_list = [sample]
            return_dict = False  # Return single result, not dict
        else:
            sample_list = sample
            return_dict = True  # Return dict of results
        
        if verbose == 1:
            if len(sample_list) > 1:
                print(f"Processing multiple sample sizes: {sample_list}")
            else:
                print(f"Processing sample size: {sample_list[0]}")
        
        results_dict = {}
        for sample_size in sample_list:
            if verbose == 1 and len(sample_list) > 1:
                print(f"\n{'='*60}")
                print(f"Processing sample size: {sample_size}")
                print(f"{'='*60}")
            
            # Apply time_range and quality filters BEFORE sampling
            df_sampled = df.copy()
            if time_range:
                time_range_converted = [pd.to_datetime(time_range[0]), pd.to_datetime(time_range[1])]
                df_sampled = df_sampled[(df_sampled['time'] >= time_range_converted[0]) & (df_sampled['time'] <= time_range_converted[1])]
            if quality:
                quality_list = quality + [10]
                df_sampled = df_sampled[df_sampled["Quality"].isin(quality_list)]
            
            # Perform sampling on filtered dataframe
            np.random.seed(seed)  # Set seed before sampling for reproducibility
            if len(df_sampled) > sample_size:
                sampled_indices = np.random.choice(df_sampled.index, size=sample_size, replace=False)
                df_sampled = df_sampled.loc[sampled_indices].copy()
            
            # Recursive call WITHOUT sample parameter (to avoid infinite recursion)
            # time_range and quality already applied, so set to None
            result = split_test_train(
                df=df_sampled, seed=seed, split=split, cv=cv, time_range=None,
                sample=False,  # Important: set to False to avoid recursion!
                flag=flag, verbose=verbose, quality=None,
                gradient_direction=gradient_direction, grid_size=grid_size,
                thumbnail=thumbnail, project_path=None, test_region=test_region  # Don't auto-save in recursive calls
            )
            results_dict[sample_size] = result
        
        # Save all results if project_path is provided (unified for single and multiple)
        if project_path:
            # Wrap results in flag dict for unified handling
            unified_results = {flag: results_dict}
            save_all_results(unified_results, [flag], sample, split, cv, seed, project_path, verbose, thumbnail=thumbnail, add_flag=add_flag)
        
        # Return single result or dict based on input
        if return_dict:
            return results_dict
        else:
            # Return single result (unwrap from dict)
            return results_dict[sample_list[0]]
    
    # Normalize flag to title case for consistency (Site, Grid, Sample, etc.)
    # Keep exact case for special flags
    flag_lower = flag.lower()
    if flag_lower in ['site', 'grid', 'sample', 'time', 'ordertime', 'hours', 'train', 'site_gradient', 'spatiotemporal', 'spatiotemporal_block']:
        if flag_lower == 'ordertime':
            flag = 'OrderTime'
        elif flag_lower == 'site_gradient':
            flag = 'Site_gradient'
        elif flag_lower == 'spatiotemporal':
            flag = 'Spatiotemporal'
        elif flag_lower == 'spatiotemporal_block':
            flag = 'Spatiotemporal_block'
        else:
            flag = flag_lower.capitalize()
    
    if verbose == 1:
        print(f"Using flag: {flag}")
    
    # Validate that only split or cv is provided, not both
    if split is not None and cv is not None:
        raise ValueError("Only one of 'split' or 'cv' can be provided, not both.")
    
    # Set default split value if neither is provided (for backward compatibility)
    if split is None and cv is None:
        split = 0.1
    
    # Determine if we're in CV mode
    cv_mode = cv is not None and cv > 1
    
    np.random.seed(seed)  # Set the seed for reproducibility
    df_copy = df.copy()

    # Create site identifier from longitude and latitude
    df_copy['Site_number'] = df_copy.groupby(['longitude', 'latitude']).ngroup()
    
    if time_range:
        time_range=[pd.to_datetime(time_range[0]),pd.to_datetime(time_range[1])]

    if time_range and flag != "Site_fixed_time_test":
        df_copy = df_copy[(df_copy['time'] >= time_range[0]) & (df_copy['time'] <= time_range[1])]

    if quality:
        quality=quality+[10]
        df_copy = df_copy[df_copy["Quality"].isin(quality)]
 
    # Special mode: test_region - split by specified geographic regions (by sites)
    if test_region is not None:
        if verbose == 1:
            print(f"Using test_region mode: {len(test_region)} region(s) specified")
        
        # Initialize all as Train
        df_copy['Set'] = 'Train'
        
        # Get unique sites with their coordinates
        site_coords = df_copy.groupby('Site_number').agg({
            'latitude': 'first',
            'longitude': 'first'
        }).reset_index()
        
        # Find test sites based on regions
        test_sites = []
        for i, region in enumerate(test_region):
            lat_min, lon_min, lat_max, lon_max = region  # [lat_min, lon_min, lat_max, lon_max]
            region_sites_mask = (
                (site_coords['latitude'] >= lat_min) & 
                (site_coords['latitude'] <= lat_max) &
                (site_coords['longitude'] >= lon_min) & 
                (site_coords['longitude'] <= lon_max)
            )
            region_sites = site_coords[region_sites_mask]['Site_number'].tolist()
            test_sites.extend(region_sites)
            
            if verbose == 1:
                # Count samples for these sites
                region_samples = df_copy[df_copy['Site_number'].isin(region_sites)].shape[0]
                print(f"  Region {i+1}: lat=[{lat_min}, {lat_max}], lon=[{lon_min}, {lon_max}] - {len(region_sites)} sites, {region_samples} samples")
        
        # Mark all data from test sites as Test
        test_sites = list(set(test_sites))  # Remove duplicates
        df_copy.loc[df_copy['Site_number'].isin(test_sites), 'Set'] = 'Test'
        
        # Get indices and site numbers
        train_indices = df_copy[df_copy['Set'] == 'Train'].index.tolist()
        test_indices = df_copy[df_copy['Set'] == 'Test'].index.tolist()
        train_site_numbers = df_copy.loc[train_indices, 'Site_number'].unique().tolist()
        test_site_numbers = test_sites
        
        if verbose == 1:
            print(f"\nTotal: Train={len(train_indices)} samples ({len(train_site_numbers)} sites), Test={len(test_indices)} samples ({len(test_site_numbers)} sites)")
        
        # Display thumbnail if requested
        if thumbnail:
            plot_region_thumbnail(df_copy, train_indices, test_indices, test_region)
        
        return train_site_numbers, test_site_numbers, train_indices, test_indices, df_copy
 
    if flag == "Site_gradient" and sample:
        # 加速版本的Site_gradient mode
        
        # 一次性获取所有站点信息
        site_info = df_copy.groupby('Site_number').agg({
            'longitude': 'first',
            'latitude': 'first'
        }).reset_index()
        
        # 计算梯度值
        if gradient_direction == 'longitude':
            gradient_values = site_info['longitude'].values
        elif gradient_direction == 'latitude':
            gradient_values = site_info['latitude'].values
        elif gradient_direction == 'distance_from_center':
            center_lon = site_info['longitude'].mean()
            center_lat = site_info['latitude'].mean()
            gradient_values = np.sqrt(
                (site_info['longitude'] - center_lon)**2 + 
                (site_info['latitude'] - center_lat)**2
            ).values
        elif gradient_direction == 'random_gradient':
            np.random.seed(seed)
            angle = np.random.uniform(0, 2*np.pi)
            gradient_values = (
                site_info['longitude'] * np.cos(angle) + 
                site_info['latitude'] * np.sin(angle)
            ).values
        else:
            raise ValueError("gradient_direction must be 'longitude', 'latitude', 'distance_from_center', or 'random_gradient'")
        
        # 快速排序和权重计算
        sort_idx = np.argsort(gradient_values)
        site_info_sorted = site_info.iloc[sort_idx].reset_index(drop=True)
        
        # 向量化权重计算
        weights = np.linspace(1.0, 0.1, len(site_info_sorted))
        target_samples_per_site = (weights / weights.sum() * sample).astype(int)
        
        # 快速调整总数
        diff = sample - target_samples_per_site.sum()
        if diff > 0:
            # 给前diff个站点各加1个样本
            target_samples_per_site[:diff] += 1
        elif diff < 0:
            # 从后-diff个站点各减1个样本
            target_samples_per_site[diff:] -= 1
        
        # 向量化采样 - 关键优化
        sampled_indices = []
        
        # 预先创建站点到索引的映射
        site_to_indices = df_copy.groupby('Site_number').groups
        
        # 向量化处理每个站点
        for i, site_number in enumerate(site_info_sorted['Site_number']):
            target_samples = target_samples_per_site[i]
            if target_samples > 0:
                site_indices = site_to_indices[site_number]
                actual_samples = min(target_samples, len(site_indices))
                if actual_samples == len(site_indices):
                    # 如果要全部样本，直接添加
                    sampled_indices.extend(site_indices)
                else:
                    # 否则随机采样
                    selected = np.random.choice(site_indices, size=actual_samples, replace=False)
                    sampled_indices.extend(selected)
        
        # 一次性过滤数据
        df_copy = df_copy.loc[sampled_indices].copy()
        
        if verbose == 1:
            print(f"Gradient direction: {gradient_direction}")
            print(f"Total samples after gradient sampling: {len(df_copy)}")
            print(f"Sites with samples: {df_copy['Site_number'].nunique()}")
    
    elif sample and flag != "Site_fixed_time_test":
        # 原始采样逻辑的向量化版本
        if len(df_copy) > sample:
            sampled_indices = np.random.choice(df_copy.index, size=sample, replace=False)
            df_copy = df_copy.loc[sampled_indices].copy()
    
    # Skip single split logic if in CV mode
    if not cv_mode:
        df_copy['Set'] = 'Train'  # Initialize 'Set' column for single split mode
            
    if not cv_mode and (flag == "Site" or flag == "Site_gradient"):
        unique_sites = df_copy['Site_number'].unique()
        num_sites_for_test = round(len(unique_sites) * split)
        test_sites = np.random.choice(unique_sites, size=num_sites_for_test, replace=False)
        
        # 向量化设置测试集
        df_copy.loc[df_copy['Site_number'].isin(test_sites), 'Set'] = 'Test'
        
    elif not cv_mode and flag == "Sample":
        test_indices = np.random.choice(df_copy.index, size=int(len(df_copy) * split), replace=False)
        df_copy.loc[test_indices, 'Set'] = 'Test'

    elif not cv_mode and flag == "Time":
        time_list = df_copy['time'].unique()
        num_test_samples = int(len(time_list) * split)
        test_times = np.random.choice(time_list, size=num_test_samples, replace=False)
        df_copy.loc[df_copy['time'].isin(test_times), 'Set'] = 'Test'
 
    elif not cv_mode and flag == "OrderTime":
        time_list = sorted(df_copy['time'].unique())
        num_test_samples = int(len(time_list) * split)
        test_times = time_list[:num_test_samples]
        df_copy.loc[df_copy['time'].isin(test_times), 'Set'] = 'Test'

    elif not cv_mode and flag == "Hours":
        df_copy['hour'] = df_copy['time'].dt.hour
        unique_hours = np.sort(df_copy['hour'].unique())
        num_test_samples = int(len(unique_hours) * split)
        test_hours = unique_hours[:num_test_samples] 
        df_copy.loc[df_copy['hour'].isin(test_hours), 'Set'] = 'Test'
        df_copy.drop('hour', axis=1, inplace=True)
    
    elif not cv_mode and flag == "Grid":
        # Grid-based split with stratified sampling
        
        # Step 1: Create grid system
        lon_min, lon_max = df_copy['longitude'].min(), df_copy['longitude'].max()
        lat_min, lat_max = df_copy['latitude'].min(), df_copy['latitude'].max()
        
        # Create grid boundaries
        lon_edges = np.linspace(lon_min, lon_max, grid_size + 1)
        lat_edges = np.linspace(lat_min, lat_max, grid_size + 1)
        
        # Assign grid IDs to each data point
        df_copy['grid_lon'] = np.digitize(df_copy['longitude'], lon_edges) - 1
        df_copy['grid_lat'] = np.digitize(df_copy['latitude'], lat_edges) - 1
        df_copy['grid_id'] = df_copy['grid_lon'] * grid_size + df_copy['grid_lat']
        
        # Step 2: Create grid statistics
        grid_stats = df_copy.groupby('grid_id').agg({
            'longitude': ['min', 'max'],
            'latitude': ['min', 'max'],
            'Site_number': 'nunique'
        }).reset_index()
        grid_stats.columns = ['grid_id', 'lon_min', 'lon_max', 'lat_min', 'lat_max', 'site_count']
        
        # Add sample count
        sample_counts = df_copy['grid_id'].value_counts().reset_index()
        sample_counts.columns = ['grid_id', 'sample_count']
        grid_stats = grid_stats.merge(sample_counts, on='grid_id', how='left')
        grid_stats['sample_count'] = grid_stats['sample_count'].fillna(0)
        
        # Step 3: Filter valid grids (with data)
        valid_grids = grid_stats[grid_stats['sample_count'] > 0].copy()
        valid_grids = valid_grids.sort_values('sample_count').reset_index(drop=True)
        
        # Step 4: Stratified sampling
        # Reset seed before grid selection to ensure reproducibility regardless of prior random operations
        np.random.seed(seed)
        num_valid_grids = len(valid_grids)
        num_test_grids = max(1, round(num_valid_grids * split))
        
        if num_test_grids >= num_valid_grids:
            # If we need to select almost all grids, just random select
            test_grids = np.random.choice(valid_grids['grid_id'], 
                                        size=min(num_test_grids, num_valid_grids), 
                                        replace=False)
        else:
            # Stratified sampling: divide into bins and select one from each bin
            bin_size = num_valid_grids // num_test_grids
            test_grids = []
            
            for i in range(num_test_grids):
                start_idx = i * bin_size
                if i == num_test_grids - 1:  # Last bin takes remaining grids
                    end_idx = num_valid_grids
                else:
                    end_idx = (i + 1) * bin_size
                
                bin_grids = valid_grids.iloc[start_idx:end_idx]['grid_id'].values
                selected_grid = np.random.choice(bin_grids)
                test_grids.append(selected_grid)
        
        # Step 5: Mark test data
        df_copy.loc[df_copy['grid_id'].isin(test_grids), 'Set'] = 'Test'
        
        # Clean up temporary columns
        df_copy.drop(['grid_lon', 'grid_lat', 'grid_id'], axis=1, inplace=True)
        
        if verbose == 1:
            print(f"Selected {len(test_grids)}  grids from {num_valid_grids} of {grid_size**2}")
            #test_samples = len(df_copy[df_copy['Set'] == 'Test'])
            #print(f"Test samples from selected grids: {test_samples}")
    
    elif not cv_mode and flag == "train":
        # Special "train" mode for memorization testing
        # Training set = all data, Test set = subset of all data
        if verbose == 1:
            print("Special 'train' mode: Using all data for training, subset for testing (memorization test)")
        
        # All data is training
        # Select subset for test (test is subset of train)
        num_test_samples = int(len(df_copy) * split)
        test_indices = np.random.choice(df_copy.index, size=num_test_samples, replace=False)
        df_copy.loc[test_indices, 'Set'] = 'Test'
        # Note: 'Set' column is 'Train' for all, but we mark test separately
    
    elif not cv_mode:
        print("Flag not right")

    # If in CV mode, generate multiple train/test splits
    if cv_mode:
        train_indices_list = []
        test_indices_list = []
        train_site_numbers_list = []
        test_site_numbers_list = []
        
        if flag in ["Site", "Site_gradient"]:
            # For Site-based CV, split sites into cv folds
            unique_sites = df_copy['Site_number'].unique()
            kf = KFold(n_splits=cv, shuffle=True, random_state=seed)
            
            for fold_idx, (train_site_idx, test_site_idx) in enumerate(kf.split(unique_sites)):
                train_sites = unique_sites[train_site_idx]
                test_sites = unique_sites[test_site_idx]
                
                train_mask = df_copy['Site_number'].isin(train_sites)
                test_mask = df_copy['Site_number'].isin(test_sites)
                
                train_indices = df_copy[train_mask].index.tolist()
                test_indices = df_copy[test_mask].index.tolist()
                
                train_indices_list.append(train_indices)
                test_indices_list.append(test_indices)
                train_site_numbers_list.append(train_sites.tolist())
                test_site_numbers_list.append(test_sites.tolist())
                
                if verbose == 1:
                    print(f"\n--- Fold {fold_idx + 1}/{cv} ---")
                    print(f"Train sites: {len(train_sites)}, Test sites: {len(test_sites)}")
                    print(f"Train samples: {len(train_indices)}, Test samples: {len(test_indices)}")
        
        elif flag == "Grid":
            # For Grid-based CV, split grids into cv folds
            # First need to create grid IDs
            lon_min, lon_max = df_copy['longitude'].min(), df_copy['longitude'].max()
            lat_min, lat_max = df_copy['latitude'].min(), df_copy['latitude'].max()
            
            lon_edges = np.linspace(lon_min, lon_max, grid_size + 1)
            lat_edges = np.linspace(lat_min, lat_max, grid_size + 1)
            
            df_copy['grid_lon'] = np.digitize(df_copy['longitude'], lon_edges) - 1
            df_copy['grid_lat'] = np.digitize(df_copy['latitude'], lat_edges) - 1
            df_copy['grid_id'] = df_copy['grid_lon'] * grid_size + df_copy['grid_lat']
            
            unique_grids = df_copy['grid_id'].unique()
            kf = KFold(n_splits=cv, shuffle=True, random_state=seed)
            
            for fold_idx, (train_grid_idx, test_grid_idx) in enumerate(kf.split(unique_grids)):
                train_grids = unique_grids[train_grid_idx]
                test_grids = unique_grids[test_grid_idx]
                
                train_mask = df_copy['grid_id'].isin(train_grids)
                test_mask = df_copy['grid_id'].isin(test_grids)
                
                train_indices = df_copy[train_mask].index.tolist()
                test_indices = df_copy[test_mask].index.tolist()
                train_sites = df_copy.loc[train_mask, 'Site_number'].unique().tolist()
                test_sites = df_copy.loc[test_mask, 'Site_number'].unique().tolist()
                
                train_indices_list.append(train_indices)
                test_indices_list.append(test_indices)
                train_site_numbers_list.append(train_sites)
                test_site_numbers_list.append(test_sites)
                
                if verbose == 1:
                    print(f"\n--- Fold {fold_idx + 1}/{cv} ---")
                    print(f"Train grids: {len(train_grids)}, Test grids: {len(test_grids)}")
                    print(f"Train samples: {len(train_indices)}, Test samples: {len(test_indices)}")
            
            # Clean up temporary columns
            df_copy.drop(['grid_lon', 'grid_lat', 'grid_id'], axis=1, inplace=True)
        
        elif flag == "Sample":
            # For Sample-based CV, split samples into cv folds
            kf = KFold(n_splits=cv, shuffle=True, random_state=seed)
            indices_array = df_copy.index.to_numpy()
            
            for fold_idx, (train_idx, test_idx) in enumerate(kf.split(indices_array)):
                train_indices = indices_array[train_idx].tolist()
                test_indices = indices_array[test_idx].tolist()
                train_sites = df_copy.loc[train_indices, 'Site_number'].unique().tolist()
                test_sites = df_copy.loc[test_indices, 'Site_number'].unique().tolist()
                
                train_indices_list.append(train_indices)
                test_indices_list.append(test_indices)
                train_site_numbers_list.append(train_sites)
                test_site_numbers_list.append(test_sites)
                
                if verbose == 1:
                    print(f"\n--- Fold {fold_idx + 1}/{cv} ---")
                    print(f"Train samples: {len(train_indices)}, Test samples: {len(test_indices)}")
        
        elif flag == "Time":
            # For Time-based CV, split time points into cv folds
            time_list = df_copy['time'].unique()
            kf = KFold(n_splits=cv, shuffle=True, random_state=seed)
            
            for fold_idx, (train_time_idx, test_time_idx) in enumerate(kf.split(time_list)):
                train_times = time_list[train_time_idx]
                test_times = time_list[test_time_idx]
                
                train_mask = df_copy['time'].isin(train_times)
                test_mask = df_copy['time'].isin(test_times)
                
                train_indices = df_copy[train_mask].index.tolist()
                test_indices = df_copy[test_mask].index.tolist()
                train_sites = df_copy.loc[train_mask, 'Site_number'].unique().tolist()
                test_sites = df_copy.loc[test_mask, 'Site_number'].unique().tolist()
                
                train_indices_list.append(train_indices)
                test_indices_list.append(test_indices)
                train_site_numbers_list.append(train_sites)
                test_site_numbers_list.append(test_sites)
                
                if verbose == 1:
                    print(f"\n--- Fold {fold_idx + 1}/{cv} ---")
                    print(f"Train time points: {len(train_times)}, Test time points: {len(test_times)}")
                    print(f"Train samples: {len(train_indices)}, Test samples: {len(test_indices)}")
        
        elif flag.lower() == "train":
            # Special "train" mode for CV: each fold uses other cv-1 parts for both train and test
            # Split data into cv parts, each fold uses (cv-1)/cv of data for both train and test
            # Fold 1: parts 2-5 for train and test, Fold 2: parts 1,3-5 for train and test, etc.
            if verbose == 1:
                print("Special 'train' mode in CV: Each fold uses other parts (cv-1 folds) of data for both training and testing (memorization test)")
            
            # Split all data into cv folds
            kf = KFold(n_splits=cv, shuffle=True, random_state=seed)
            indices_array = df_copy.index.to_numpy()
            
            # In KFold, for each split we get (train_idx, test_idx)
            # train_idx contains (cv-1)/cv of the data, which is what we want for each fold
            for fold_idx, (train_idx_arr, _) in enumerate(kf.split(indices_array)):
                # Use the train split ((cv-1)/cv of data) for both training and testing
                fold_indices = indices_array[train_idx_arr].tolist()
                fold_sites = df_copy.loc[fold_indices, 'Site_number'].unique().tolist()
                
                # Both train and test use the same data (cv-1 folds combined)
                train_indices_list.append(fold_indices)
                test_indices_list.append(fold_indices)
                train_site_numbers_list.append(fold_sites)
                test_site_numbers_list.append(fold_sites)
                
                if verbose == 1:
                    print(f"\n--- Fold {fold_idx + 1}/{cv} ---")
                    print(f"Using other {cv-1} parts (excluding part {fold_idx + 1})")
                    print(f"Train samples: {len(fold_indices)}, Test samples: {len(fold_indices)} (identical)")
                    print(f"Sites: {len(fold_sites)}")
        
        elif flag == "Spatiotemporal":
            # Spatiotemporal uses special handler (Grid-based spatial + random time split)
            return handle_spatiotemporal_split(df_copy, split, cv, seed, verbose, project_path, thumbnail, grid_size, use_time_blocks=False)
        
        elif flag == "Spatiotemporal_block":
            # Spatiotemporal_block uses special handler (Grid-based spatial + time block split)
            return handle_spatiotemporal_split(df_copy, split, cv, seed, verbose, project_path, thumbnail, grid_size, use_time_blocks=True)
        
        else:
            raise ValueError(f"CV mode not implemented for flag='{flag}'")
        
        # Display thumbnail for CV mode if requested (showing, not saving)
        if thumbnail and flag in ["Site", "Site_gradient", "Grid", "train", "Spatiotemporal", "Spatiotemporal_block"]:
            plot_cv_thumbnail(df_copy, train_indices_list, test_indices_list, cv, flag)
        
        # Note: Auto-save is handled by save_all_results when sample is provided
        # For no-sample case with project_path, still save directly
        if project_path and not sample:
            # Wrap result for unified handling
            result = (train_site_numbers_list, test_site_numbers_list, 
                     train_indices_list, test_indices_list, df_copy)
            unified_results = {flag: result}
            save_all_results(unified_results, [flag], False, None, cv, seed, project_path, verbose, thumbnail=thumbnail, add_flag=add_flag)
        
        return train_site_numbers_list, test_site_numbers_list, train_indices_list, test_indices_list, df_copy
    
    # Original single split mode
    # Special handling for Spatiotemporal in split mode (Grid-based)
    if flag == "Spatiotemporal":
        return handle_spatiotemporal_split(df_copy, split, cv, seed, verbose, project_path, thumbnail, grid_size, use_time_blocks=False)
    
    if flag == "Spatiotemporal_block":
        return handle_spatiotemporal_split(df_copy, split, cv, seed, verbose, project_path, thumbnail, grid_size, use_time_blocks=True)
    
    # 向量化统计计算
    if flag == "train":
        # Special handling for "train" mode: all data for training, subset for testing
        train_indices = df_copy.index.tolist()  # All data
        test_mask = df_copy['Set'] == 'Test'
        test_indices = df_copy[test_mask].index.tolist()  # Subset
        train_site_numbers = df_copy['Site_number'].unique().tolist()
        test_site_numbers = df_copy.loc[test_mask, 'Site_number'].unique().tolist()
    else:
        # Normal mode: separate training and test sets
        train_mask = df_copy['Set'] == 'Train'
        test_mask = df_copy['Set'] == 'Test'
        
        train_indices = df_copy[train_mask].index.tolist()
        test_indices = df_copy[test_mask].index.tolist()
        train_site_numbers = df_copy.loc[train_mask, 'Site_number'].unique().tolist()
        test_site_numbers = df_copy.loc[test_mask, 'Site_number'].unique().tolist()
      
    # 统计计算
    selected_site_count = len(test_site_numbers)
    unique_sites = df_copy['Site_number'].nunique()
    selected_site_percentage = (selected_site_count / unique_sites) * 100
    
    selected_row_count = len(test_indices)
    total_rows = len(df_copy)
    selected_row_percentage = (selected_row_count / total_rows) * 100

    if verbose==1:
        print(f"Selected Site Count: {selected_site_count}, ({selected_site_percentage:.2f}%)")
        print(f"Selected DataRow Count: {selected_row_count}, ({selected_row_percentage:.2f}%)")
    
    training_site_count = len(train_site_numbers)
    training_row_count = len(train_indices)
    training_site_percentage = (training_site_count / unique_sites) * 100
    training_row_percentage = (training_row_count / total_rows) * 100
    if verbose==1: 
        print(f"Training Site Count: {training_site_count}, ({training_site_percentage:.2f}%)")
        print(f"Training DataRow Count: {training_row_count}, ({training_row_percentage:.2f}%)")

    # Display thumbnail for single split mode if requested (showing, not saving)
    if thumbnail and flag in ["Site", "Site_gradient", "Grid", "train", "Spatiotemporal", "Spatiotemporal_block"]:
        plot_split_thumbnail(df_copy, train_indices, test_indices, flag)

    # Note: Auto-save is handled by save_all_results when sample is provided
    # For no-sample case with project_path, still save directly
    if project_path and not sample:
        # Wrap result for unified handling
        result = (train_site_numbers, test_site_numbers, train_indices, test_indices, df_copy)
        unified_results = {flag: result}
        save_all_results(unified_results, [flag], False, split, None, seed, project_path, verbose, thumbnail=thumbnail, add_flag=add_flag)

    return train_site_numbers, test_site_numbers, train_indices, test_indices, df_copy


def plot_split_thumbnail(df, train_indices, test_indices, flag):
    """
    Plot spatial distribution for single split mode.
    Train points in green, test points in red.
    """
    plt.figure(figsize=(10, 8))
    
    # Plot training points
    train_df = df.loc[train_indices]
    train_sites = train_df.groupby(['longitude', 'latitude']).size().reset_index()
    plt.scatter(train_sites['longitude'], train_sites['latitude'], 
                c='green', alpha=0.6, s=50, label='Train', edgecolors='darkgreen', linewidth=0.5)
    
    # Plot test points
    test_df = df.loc[test_indices]
    test_sites = test_df.groupby(['longitude', 'latitude']).size().reset_index()
    plt.scatter(test_sites['longitude'], test_sites['latitude'], 
                c='red', alpha=0.8, s=80, label='Test', edgecolors='darkred', linewidth=0.5, marker='^')
    
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)
    plt.title(f'Train/Test Split - {flag} mode\n(Green=Train, Red=Test)', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    print(f"✓ Thumbnail plot generated for {flag} mode")


def plot_region_thumbnail(df, train_indices, test_indices, test_regions):
    """
    Plot spatial distribution for region-based split mode.
    Train points in green, test points in red, with rectangles showing test regions.
    """
    plt.figure(figsize=(12, 8))
    
    # Plot training points
    train_df = df.loc[train_indices]
    train_sites = train_df.groupby(['longitude', 'latitude']).size().reset_index()
    plt.scatter(train_sites['longitude'], train_sites['latitude'], 
                c='green', alpha=0.6, s=50, label='Train Sites', edgecolors='darkgreen', linewidth=0.5)
    
    # Plot test points
    test_df = df.loc[test_indices]
    test_sites = test_df.groupby(['longitude', 'latitude']).size().reset_index()
    plt.scatter(test_sites['longitude'], test_sites['latitude'], 
                c='red', alpha=0.8, s=80, label='Test Sites', edgecolors='darkred', linewidth=0.5, marker='^')
    
    # Draw test region rectangles
    from matplotlib.patches import Rectangle
    for i, region in enumerate(test_regions):
        lat_min, lon_min, lat_max, lon_max = region
        width = lon_max - lon_min
        height = lat_max - lat_min
        rect = Rectangle((lon_min, lat_min), width, height, 
                        linewidth=2, edgecolor='blue', facecolor='none', 
                        linestyle='--', label=f'Test Region {i+1}' if i < 3 else '')
        plt.gca().add_patch(rect)
    
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)
    plt.title(f'Train/Test Split - Region mode\n(Green=Train, Red=Test, Blue boxes=Test regions)', 
              fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    print(f"✓ Thumbnail plot generated for Region mode with {len(test_regions)} test region(s)")


def save_split_thumbnail(df, train_indices, test_indices, flag, save_dir):
    """
    Save spatial distribution plot for split mode to file.
    Green dots for training, red dots for test.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with longitude and latitude
    train_indices : list
        Training indices
    test_indices : list
        Test indices
    flag : str
        Split strategy name
    save_dir : str
        Directory to save the thumbnail
    """
    plt.figure(figsize=(10, 8))
    
    # Plot training points
    train_df = df.loc[train_indices]
    train_sites = train_df.groupby(['longitude', 'latitude']).size().reset_index()
    plt.scatter(train_sites['longitude'], train_sites['latitude'], 
                c='green', alpha=0.6, s=50, label='Train', edgecolors='darkgreen', linewidth=0.5)
    
    # Plot test points
    test_df = df.loc[test_indices]
    test_sites = test_df.groupby(['longitude', 'latitude']).size().reset_index()
    plt.scatter(test_sites['longitude'], test_sites['latitude'], 
                c='red', alpha=0.8, s=80, label='Test', edgecolors='darkred', linewidth=0.5, marker='^')
    
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)
    plt.title(f'Train/Test Split - {flag} mode\n(Green=Train, Red=Test)', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # ✅ Save to file
    thumbnail_path = os.path.join(save_dir, 'split_thumbnail.png')
    plt.savefig(thumbnail_path, dpi=150, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    print(f"  ✓ Thumbnail saved to: {thumbnail_path}")


def plot_cv_thumbnail(df, train_indices_list, test_indices_list, cv, flag):
    """
    Plot spatial distribution for CV mode (display only, no save).
    Different colors for each fold.
    """
    # Define colors for up to 10 folds (extendable if needed)
    colors = ['red', 'blue', 'green', 'orange', 'purple', 
              'brown', 'pink', 'gray', 'olive', 'cyan']
    
    plt.figure(figsize=(8, 6))
    
    # Plot each fold with a different color
    for fold_idx in range(cv):
        fold_indices = test_indices_list[fold_idx]
        fold_df = df.loc[fold_indices]
        fold_sites = fold_df.groupby(['longitude', 'latitude']).size().reset_index()
        
        color = colors[fold_idx % len(colors)]
        plt.scatter(fold_sites['longitude'], fold_sites['latitude'], 
                    c=color, alpha=0.7, s=60, label=f'Fold {fold_idx + 1}', 
                    edgecolors='black', linewidth=0.5)
    
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)
    plt.title(f'{cv}-Fold Cross-Validation - {flag} mode\n(Each color represents one fold)', 
              fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10, ncol=2)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    print(f"✓ Thumbnail plot generated for {cv}-fold CV in {flag} mode")


def save_cv_thumbnail(df, train_indices_list, test_indices_list, cv, flag, save_dir):
    """
    Save spatial distribution plot for CV mode to file.
    Different colors for each fold.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with longitude and latitude
    train_indices_list : list of lists
        Train indices for each fold
    test_indices_list : list of lists
        Test indices for each fold
    cv : int
        Number of folds
    flag : str
        Split strategy name
    save_dir : str
        Directory to save the thumbnail
    """
    # Define colors for up to 10 folds
    colors = ['red', 'blue', 'green', 'orange', 'purple', 
              'brown', 'pink', 'gray', 'olive', 'cyan']
    
    plt.figure(figsize=(8, 6))
    
    # Plot each fold with a different color
    for fold_idx in range(cv):
        fold_indices = test_indices_list[fold_idx]
        fold_df = df.loc[fold_indices]
        fold_sites = fold_df.groupby(['longitude', 'latitude']).size().reset_index()
        
        color = colors[fold_idx % len(colors)]
        plt.scatter(fold_sites['longitude'], fold_sites['latitude'], 
                    c=color, alpha=0.7, s=60, label=f'Fold {fold_idx + 1}', 
                    edgecolors='black', linewidth=0.5)
    
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)
    plt.title(f'{cv}-Fold Cross-Validation - {flag} mode\n(Each color represents one fold)', 
              fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10, ncol=2)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # ✅ Save to file
    thumbnail_path = os.path.join(save_dir, 'cv_thumbnail.png')
    plt.savefig(thumbnail_path, dpi=150, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    print(f"  ✓ Thumbnail saved to: {thumbnail_path}")


def save_split_results(train_indices, test_indices, df, project_path, split_strategy='split', 
                       flag='Site', seed=42, split_ratio=None, cv=None, save_thumbnail=True):
    """
    Save split results including metadata, indices, and thumbnail visualization.
    
    Parameters
    ----------
    train_indices : list or list of lists
        Training indices. Single list for split mode, list of lists for CV mode.
    test_indices : list or list of lists
        Test indices. Single list for split mode, list of lists for CV mode.
    df : pd.DataFrame
        Original dataframe with 'longitude' and 'latitude' columns
    project_path : str
        Directory path to save all output files
    split_strategy : str, default='split'
        Either 'split' or 'cv'
    flag : str, default='Site'
        Split flag used (Site, Grid, Sample, etc.)
    seed : int, default=42
        Random seed used for splitting
    split_ratio : float, optional
        Split ratio if using split mode
    cv : int, optional
        Number of folds if using CV mode
    save_thumbnail : bool, default=True
        Whether to save thumbnail visualization
    
    Returns
    -------
    dict
        Dictionary containing paths to saved files
    
    Examples
    --------
    >>> # For split mode
    >>> save_split_results(train_ind, test_ind, df, 'data/splits', 
    ...                    split_strategy='split', split_ratio=0.2)
    
    >>> # For CV mode
    >>> save_split_results(train_ind_list, test_ind_list, df, 'data/splits',
    ...                    split_strategy='cv', cv=5)
    """
    # Create project directory if it doesn't exist
    os.makedirs(project_path, exist_ok=True)
    
    # Determine if CV mode or single split
    is_cv = split_strategy.lower() == 'cv' or isinstance(train_indices, list) and isinstance(train_indices[0], list)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Prepare metadata
    metadata = {
        'split_strategy': split_strategy,
        'flag': flag,
        'seed': seed,
        'timestamp': timestamp,
        'total_samples': len(df)
    }
    
    if is_cv:
        n_folds = cv if cv else len(train_indices)
        metadata['cv_folds'] = n_folds
        metadata['fold_info'] = []
        
        # Prepare CSV data
        csv_data = []
        
        for fold_idx in range(n_folds):
            train_ind = train_indices[fold_idx]
            test_ind = test_indices[fold_idx]
            
            fold_meta = {
                'fold': fold_idx + 1,
                'train_samples': len(train_ind),
                'test_samples': len(test_ind),
                'train_indices_file': f'fold_{fold_idx+1}_train_indices.npy',
                'test_indices_file': f'fold_{fold_idx+1}_test_indices.npy'
            }
            metadata['fold_info'].append(fold_meta)
            
            # Save indices as numpy arrays
            np.save(os.path.join(project_path, fold_meta['train_indices_file']), train_ind)
            np.save(os.path.join(project_path, fold_meta['test_indices_file']), test_ind)
            
            # Add to CSV data
            csv_data.append({
                'split_strategy': split_strategy,
                'fold': fold_idx + 1,
                'sample_number': len(train_ind),
                'train_file_path': fold_meta['train_indices_file'],
                'test_file_path': fold_meta['test_indices_file']
            })
        
        # Save CSV
        csv_df = pd.DataFrame(csv_data)
        csv_path = os.path.join(project_path, 'meta_info.csv')
        csv_df.to_csv(csv_path, index=False)
        
        # Save thumbnail if requested
        thumbnail_path = None
        if save_thumbnail:
            thumbnail_path = os.path.join(project_path, 'thumbnail_split_cv.png')
            save_thumbnail_plot(df, train_indices, test_indices, n_folds, flag, 
                              thumbnail_path, mode='cv')
        
    else:
        # Single split mode
        metadata['split_ratio'] = split_ratio
        metadata['train_samples'] = len(train_indices)
        metadata['test_samples'] = len(test_indices)
        metadata['train_indices_file'] = 'train_indices.npy'
        metadata['test_indices_file'] = 'test_indices.npy'
        
        # Save indices
        np.save(os.path.join(project_path, 'train_indices.npy'), train_indices)
        np.save(os.path.join(project_path, 'test_indices.npy'), test_indices)
        
        # Save CSV
        csv_data = [{
            'split_strategy': split_strategy,
            'fold': 1,
            'sample_number': len(train_indices),
            'train_file_path': 'train_indices.npy',
            'test_file_path': 'test_indices.npy'
        }]
        csv_df = pd.DataFrame(csv_data)
        csv_path = os.path.join(project_path, 'meta_info.csv')
        csv_df.to_csv(csv_path, index=False)
        
        # Save thumbnail if requested
        thumbnail_path = None
        if save_thumbnail:
            thumbnail_path = os.path.join(project_path, 'thumbnail_split.png')
            save_thumbnail_plot(df, train_indices, test_indices, None, flag, 
                              thumbnail_path, mode='split')
    
    # Save metadata JSON
    json_path = os.path.join(project_path, 'meta_split.json')
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Prepare return dictionary
    result = {
        'project_path': project_path,
        'metadata_json': json_path,
        'metadata_csv': csv_path,
        'thumbnail': thumbnail_path
    }
    
    print(f"\n✓ Split results saved to: {project_path}")
    print(f"  - Metadata JSON: meta_split.json")
    print(f"  - Metadata CSV: meta_info.csv")
    if is_cv:
        print(f"  - Indices files: fold_*_train/test_indices.npy ({n_folds} folds)")
    else:
        print(f"  - Indices files: train_indices.npy, test_indices.npy")
    if thumbnail_path:
        print(f"  - Thumbnail: {os.path.basename(thumbnail_path)}")
    
    return result


def save_thumbnail_plot(df, train_indices, test_indices, cv, flag, save_path, mode='split'):
    """
    Save thumbnail plot to file instead of displaying it.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with longitude and latitude
    train_indices : list or list of lists
        Training indices
    test_indices : list or list of lists
        Test indices
    cv : int or None
        Number of folds (for CV mode)
    flag : str
        Split flag
    save_path : str
        Full path to save the image
    mode : str
        Either 'split' or 'cv'
    """
    if mode == 'cv':
        # CV mode visualization
        colors = ['red', 'blue', 'green', 'orange', 'purple', 
                  'brown', 'pink', 'gray', 'olive', 'cyan']
        
        plt.figure(figsize=(8, 6))
        
        for fold_idx in range(cv):
            fold_indices = test_indices[fold_idx]
            fold_df = df.loc[fold_indices]
            fold_sites = fold_df.groupby(['longitude', 'latitude']).size().reset_index()
            
            color = colors[fold_idx % len(colors)]
            plt.scatter(fold_sites['longitude'], fold_sites['latitude'], 
                        c=color, alpha=0.7, s=60, label=f'Fold {fold_idx + 1}', 
                        edgecolors='black', linewidth=0.5)
        
        plt.xlabel('Longitude', fontsize=12)
        plt.ylabel('Latitude', fontsize=12)
        plt.title(f'{cv}-Fold Cross-Validation - {flag} mode\n(Each color represents one fold)', 
                  fontsize=14, fontweight='bold')
        plt.legend(loc='best', fontsize=10, ncol=2)
        plt.grid(True, alpha=0.3)
        
    else:
        # Split mode visualization
        plt.figure(figsize=(8, 6))
        
        train_df = df.loc[train_indices]
        train_sites = train_df.groupby(['longitude', 'latitude']).size().reset_index()
        plt.scatter(train_sites['longitude'], train_sites['latitude'], 
                    c='green', alpha=0.6, s=50, label='Train', 
                    edgecolors='darkgreen', linewidth=0.5)
        
        test_df = df.loc[test_indices]
        test_sites = test_df.groupby(['longitude', 'latitude']).size().reset_index()
        plt.scatter(test_sites['longitude'], test_sites['latitude'], 
                    c='red', alpha=0.8, s=80, label='Test', 
                    edgecolors='darkred', linewidth=0.5, marker='^')
        
        plt.xlabel('Longitude', fontsize=12)
        plt.ylabel('Latitude', fontsize=12)
        plt.title(f'Train/Test Split - {flag} mode\n(Green=Train, Red=Test)', 
                  fontsize=14, fontweight='bold')
        plt.legend(loc='best', fontsize=11)
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Thumbnail saved: {os.path.basename(save_path)}")


def save_all_results(results_dict, flags, sample, split_ratio, cv, seed, project_path, verbose, thumbnail=False, add_flag=False):
    """
    Unified save function for ALL cases (single/multiple flags, single/multiple samples).
    ALWAYS uses consistent directory format: sample_{size}_{strategy}/
    
    Supports incremental mode (add_flag=True): merges new results with existing metadata.
    
    Parameters
    ----------
    results_dict : dict
        Dictionary with flags as keys, values can be:
        - If sample is False/single: split results tuple
        - If sample is list: dict of {sample_size: split results}
    flags : list
        List of flag names used (always a list, even if single)
    sample : int, list, or False
        Sample size(s) used
    split_ratio : float or None
        Split ratio if using split mode
    cv : int or None
        Number of folds if using CV mode
    seed : int
        Random seed used
    project_path : str
        Base directory to save all results
    verbose : int
        Verbosity level
    thumbnail : bool, optional
        Not used - thumbnails are always saved as project metadata (kept for API compatibility)
    """
    os.makedirs(project_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    is_cv = cv is not None
    
    # Normalize inputs
    if not isinstance(flags, list):
        flags = [flags]
    
    if sample and sample is not False:
        sample_list = sample if isinstance(sample, list) else [sample]
    else:
        # No sampling - use "full" as identifier
        sample_list = ["full"]
    
    # Prepare configurations list (all combinations of flag x sample)
    configurations = []
    csv_rows = []  # For meta_info.csv
    
    for flag_name in flags:
        flag_results = results_dict[flag_name]
        
        # Check if flag_results is a dict (multiple samples) or tuple (single result)
        if isinstance(flag_results, dict):
            # Multiple samples
            for sample_size, result in flag_results.items():
                config, rows = process_and_save_config(
                    flag_name, sample_size, result, is_cv, cv, split_ratio, 
                    project_path, verbose, save_thumbnail=thumbnail  # ✅ Pass thumbnail
                )
                configurations.append(config)
                csv_rows.extend(rows)
        else:
            # Single result
            sample_size = sample_list[0]
            config, rows = process_and_save_config(
                flag_name, sample_size, flag_results, is_cv, cv, split_ratio,
                project_path, verbose, save_thumbnail=thumbnail  # ✅ Pass thumbnail
            )
            configurations.append(config)
            csv_rows.extend(rows)
    
    # Create overall metadata
    meta_json_path = os.path.join(project_path, 'meta_split.json')
    meta_csv_path = os.path.join(project_path, 'meta_info.csv')
    
    if add_flag and os.path.exists(meta_json_path):
        # Incremental mode: merge with existing metadata
        with open(meta_json_path, 'r') as f:
            overall_metadata = json.load(f)
        
        # Merge configurations
        existing_configs = overall_metadata.get('configurations', [])
        overall_metadata['configurations'] = existing_configs + configurations
        
        # Update flags list
        existing_flags = overall_metadata.get('flags', [])
        overall_metadata['flags'] = sorted(list(set(existing_flags + flags)))
        
        # Update timestamp
        overall_metadata['timestamp'] = timestamp
        
        if verbose == 1:
            print(f"  Merging with existing metadata ({len(existing_configs)} → {len(overall_metadata['configurations'])} configurations)")
    else:
        # Normal mode: create new metadata
        overall_metadata = {
            'split_strategy': 'cv' if is_cv else 'split',
            'flags': flags,
            'seed': seed,
            'timestamp': timestamp,
            'sample_sizes': [s for s in sample_list if s != "full"],
            'configurations': configurations
        }
        
        if is_cv:
            overall_metadata['cv_folds'] = cv
        else:
            overall_metadata['split_ratio'] = split_ratio
    
    # Save meta_split.json
    with open(meta_json_path, 'w') as f:
        json.dump(overall_metadata, f, indent=2)
    
    # Save meta_info.csv
    if csv_rows:
        import pandas as pd
        meta_df = pd.DataFrame(csv_rows)
        
        if add_flag and os.path.exists(meta_csv_path):
            # Append to existing CSV
            existing_csv = pd.read_csv(meta_csv_path)
            meta_df = pd.concat([existing_csv, meta_df], ignore_index=True)
        
        meta_df.to_csv(meta_csv_path, index=False)
    
    if verbose == 1:
        print(f"\n{'='*70}")
        print(f"✓ All results saved to: {project_path}")
        print(f"  Strategies: {', '.join(flags)}")
        print(f"  Configurations: {len(configurations)}")
        print(f"  Files: meta_split.json, meta_info.csv")
        print(f"{'='*70}")


def process_and_save_config(flag_name, sample_size, result, is_cv, cv, split_ratio, project_path, verbose, save_thumbnail=False):
    """
    Process and save a single configuration (one flag + one sample size).
    ALWAYS uses format: sample_{size}_{strategy}/
    
    Parameters
    ----------
    flag_name : str
        Split strategy name
    sample_size : int or str
        Sample size or "full"
    result : tuple
        Split results
    is_cv : bool
        Whether CV mode
    cv : int or None
        Number of folds
    split_ratio : float or None
        Split ratio
    project_path : str
        Base save path
    verbose : int
        Verbosity level
    save_thumbnail : bool, optional
        Not used - thumbnails are always saved as project metadata (kept for API compatibility)
    
    Returns:
        config_meta (dict): Configuration metadata
        csv_rows (list): Rows for meta_info.csv
    """
    # Create subdirectory name - ALWAYS use sample_{size}_{strategy} format
    subdir_name = f'sample_{sample_size}_{flag_name}'
    subdir_path = os.path.join(project_path, subdir_name)
    os.makedirs(subdir_path, exist_ok=True)
    
    if verbose == 1:
        print(f"  Saving: {subdir_name}")
    
    # Unpack result
    if is_cv:
        train_site_list, test_site_list, train_ind_list, test_ind_list, df_split = result
    else:
        train_sites, test_sites, train_ind, test_ind, df_split = result
    
    # Prepare configuration metadata
    config_meta = {
        'flag': flag_name,
        'sample_size': sample_size if sample_size != "full" else None,
        'subdirectory': subdir_name
    }
    
    csv_rows = []  # For meta_info.csv
    
    if is_cv:
        # CV mode
        config_meta['cv_folds'] = cv
        config_meta['folds'] = []
        
        for fold_idx in range(cv):
            train_ind = train_ind_list[fold_idx]
            test_ind = test_ind_list[fold_idx]
            
            fold_meta = {
                'fold': fold_idx + 1,
                'train_samples': len(train_ind),
                'test_samples': len(test_ind),
                'train_file': f'fold_{fold_idx+1}_train_indices.npy',
                'test_file': f'fold_{fold_idx+1}_test_indices.npy'
            }
            config_meta['folds'].append(fold_meta)
            
            # Save indices
            np.save(os.path.join(subdir_path, f'fold_{fold_idx+1}_train_indices.npy'), train_ind)
            np.save(os.path.join(subdir_path, f'fold_{fold_idx+1}_test_indices.npy'), test_ind)
            
            # CSV row for this fold
            csv_rows.append({
                'sample_number': sample_size if sample_size != "full" else len(df_split),
                'strategy': flag_name,  # ✅ Added strategy column
                'split_strategy': 'cv',
                'fold': fold_idx + 1,
                'train_sample_count': len(train_ind),
                'test_sample_count': len(test_ind),
                'train_file_path': os.path.join(subdir_name, f'fold_{fold_idx+1}_train_indices.npy'),
                'test_file_path': os.path.join(subdir_name, f'fold_{fold_idx+1}_test_indices.npy')
            })
        
        # ✅ Always save thumbnail as project metadata
        if flag_name.lower() in ["site", "site_gradient", "grid", "train", "spatiotemporal", "spatiotemporal_block"]:
            save_cv_thumbnail(df_split, train_ind_list, test_ind_list, cv, flag_name, subdir_path)
    
    else:
        # Split mode (treat as fold=1 for consistency)
        config_meta['split_ratio'] = split_ratio
        config_meta['cv_folds'] = 1  # Treat split as 1-fold for consistency
        config_meta['folds'] = []
        
        # Use fold_1 naming for consistency with CV mode
        fold_meta = {
            'fold': 1,
            'train_samples': len(train_ind),
            'test_samples': len(test_ind),
            'train_file': 'fold_1_train_indices.npy',
            'test_file': 'fold_1_test_indices.npy'
        }
        config_meta['folds'].append(fold_meta)
        
        # Save indices with fold_1 naming
        np.save(os.path.join(subdir_path, 'fold_1_train_indices.npy'), train_ind)
        np.save(os.path.join(subdir_path, 'fold_1_test_indices.npy'), test_ind)
        
        # CSV row (fold=1 for consistency)
        csv_rows.append({
            'sample_number': sample_size if sample_size != "full" else len(df_split),
            'strategy': flag_name,  # ✅ Added strategy column
            'split_strategy': 'split',
            'fold': 1,  # Changed from None to 1
            'train_sample_count': len(train_ind),
            'test_sample_count': len(test_ind),
            'train_file_path': os.path.join(subdir_name, 'fold_1_train_indices.npy'),
            'test_file_path': os.path.join(subdir_name, 'fold_1_test_indices.npy')
        })
        
        # ✅ Always save thumbnail as project metadata
        if flag_name.lower() in ["site", "site_gradient", "grid", "spatiotemporal", "spatiotemporal_block"]:
            save_split_thumbnail(df_split, train_ind, test_ind, flag_name, subdir_path)
    
    return config_meta, csv_rows


def save_multi_sample_results(results_dict, df, project_path, split_ratio, cv, flag, seed, save_thumbnail=True):
    """
    Save results for multiple sample sizes.
    
    Parameters
    ----------
    results_dict : dict
        Dictionary with sample sizes as keys and split results as values
    df : pd.DataFrame
        Original dataframe
    project_path : str
        Base directory to save all results
    split_ratio : float or None
        Split ratio if using split mode
    cv : int or None
        Number of folds if using CV mode
    flag : str
        Split flag used
    seed : int
        Random seed used
    save_thumbnail : bool
        Whether to save thumbnails
    """
    # Create base project directory
    os.makedirs(project_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    is_cv = cv is not None
    
    # Prepare overall metadata
    overall_metadata = {
        'split_strategy': 'cv' if is_cv else 'split',
        'flag': flag,
        'seed': seed,
        'timestamp': timestamp,
        'total_samples': len(df),
        'sample_sizes': list(results_dict.keys()),
        'samples_info': []
    }
    
    if is_cv:
        overall_metadata['cv_folds'] = cv
    else:
        overall_metadata['split_ratio'] = split_ratio
    
    # Prepare CSV data for all samples
    all_csv_data = []
    
    # Process each sample size
    for sample_size, result in results_dict.items():
        print(f"\nSaving results for sample size: {sample_size}")
        
        # Create subdirectory for this sample size
        sample_dir = os.path.join(project_path, f'sample_{sample_size}')
        os.makedirs(sample_dir, exist_ok=True)
        
        # Unpack result based on structure
        if is_cv:
            train_site_list, test_site_list, train_ind_list, test_ind_list, df_split = result
        else:
            train_sites, test_sites, train_ind, test_ind, df_split = result
        
        # Metadata for this sample size
        sample_metadata = {
            'sample_size': sample_size,
            'subdirectory': f'sample_{sample_size}'
        }
        
        if is_cv:
            # CV mode
            sample_metadata['folds'] = []
            
            for fold_idx in range(cv):
                train_ind = train_ind_list[fold_idx]
                test_ind = test_ind_list[fold_idx]
                
                fold_meta = {
                    'fold': fold_idx + 1,
                    'train_samples': len(train_ind),
                    'test_samples': len(test_ind),
                    'train_file': f'fold_{fold_idx+1}_train_indices.npy',
                    'test_file': f'fold_{fold_idx+1}_test_indices.npy'
                }
                sample_metadata['folds'].append(fold_meta)
                
                # Save indices
                np.save(os.path.join(sample_dir, fold_meta['train_file']), train_ind)
                np.save(os.path.join(sample_dir, fold_meta['test_file']), test_ind)
                
                # Add to CSV data
                all_csv_data.append({
                    'sample_number': sample_size,  # The sample parameter value
                    'split_strategy': 'cv',
                    'fold': fold_idx + 1,
                    'train_sample_count': len(train_ind),
                    'test_sample_count': len(test_ind),
                    'train_file_path': os.path.join(f'sample_{sample_size}', fold_meta['train_file']),
                    'test_file_path': os.path.join(f'sample_{sample_size}', fold_meta['test_file'])
                })
            
            # Save thumbnail for this sample size
            if save_thumbnail:
                thumbnail_path = os.path.join(sample_dir, 'thumbnail_cv.png')
                save_thumbnail_plot(df_split, train_ind_list, test_ind_list, cv, flag, 
                                  thumbnail_path, mode='cv')
                sample_metadata['thumbnail'] = 'thumbnail_cv.png'
        
        else:
            # Single split mode
            sample_metadata['train_samples'] = len(train_ind)
            sample_metadata['test_samples'] = len(test_ind)
            sample_metadata['train_file'] = 'train_indices.npy'
            sample_metadata['test_file'] = 'test_indices.npy'
            
            # Save indices
            np.save(os.path.join(sample_dir, 'train_indices.npy'), train_ind)
            np.save(os.path.join(sample_dir, 'test_indices.npy'), test_ind)
            
            # Add to CSV data
            all_csv_data.append({
                'sample_number': sample_size,  # The sample parameter value
                'split_strategy': 'split',
                'fold': 1,
                'train_sample_count': len(train_ind),
                'test_sample_count': len(test_ind),
                'train_file_path': os.path.join(f'sample_{sample_size}', 'train_indices.npy'),
                'test_file_path': os.path.join(f'sample_{sample_size}', 'test_indices.npy')
            })
            
            # Save thumbnail for this sample size
            if save_thumbnail:
                thumbnail_path = os.path.join(sample_dir, 'thumbnail.png')
                save_thumbnail_plot(df_split, train_ind, test_ind, None, flag, 
                                  thumbnail_path, mode='split')
                sample_metadata['thumbnail'] = 'thumbnail.png'
        
        overall_metadata['samples_info'].append(sample_metadata)
    
    # Save overall metadata JSON
    json_path = os.path.join(project_path, 'meta_split.json')
    with open(json_path, 'w') as f:
        json.dump(overall_metadata, f, indent=2)
    
    # Save overall CSV
    csv_df = pd.DataFrame(all_csv_data)
    csv_path = os.path.join(project_path, 'meta_info.csv')
    csv_df.to_csv(csv_path, index=False)
    
    print(f"\n{'='*60}")
    print(f"✓ All results saved to: {project_path}")
    print(f"  - Overall metadata: meta_split.json")
    print(f"  - Overall CSV: meta_info.csv")
    print(f"  - Sample subdirectories: {len(results_dict)}")
    for sample_size in results_dict.keys():
        print(f"    * sample_{sample_size}/")
    print(f"{'='*60}")


def validate_and_check_existing_splits(project_path, flag, sample, split, cv, seed, df, verbose, add_flag=False):
    """
    Validate existing split metadata and check index consistency.
    
    Logic:
    1. Check if meta_split.json exists
    2. If not exists: return (False, None, None) - proceed with generation
    3. If exists:
       a. Compare configurations (flags, sample, split/cv, seed)
       b. If add_flag=False (strict mode):
          - If different: raise ValueError (no auto-regeneration)
          - If same: validate indices → return (True, loaded_data, None)
       c. If add_flag=True (incremental mode):
          - Validate existing flags strictly (must match sample, seed, cv)
          - Identify new flags not in existing metadata
          - Return (False, None, new_flags) to generate only new flags
    
    Parameters:
    -----------
    project_path : str
        Path to project directory
    flag : str or list
        Split strategy flag(s)
    sample : int, list, or False
        Sample size(s)
    split : float or None
        Split ratio
    cv : int or None
        CV folds
    seed : int
        Random seed
    df : pd.DataFrame
        Input dataframe
    verbose : int
        Verbosity level
    
    Returns:
    --------
    tuple : (should_skip, existing_results, new_flags)
        - should_skip: True if should use existing data (all flags exist), False otherwise
        - existing_results: Loaded data if should_skip=True, None otherwise
        - new_flags: List of new flags to generate (only in add_flag mode), None otherwise
    
    Raises:
    -------
    ValueError : If indices don't match OR if configurations mismatch in strict mode
    """
    meta_json_path = os.path.join(project_path, 'meta_split.json')
    
    # If no existing metadata, proceed normally
    if not os.path.exists(meta_json_path):
        if verbose == 1:
            print("✓ No existing metadata found. Proceeding with new split generation.")
        return False, None, None
    
    # Load existing metadata
    with open(meta_json_path, 'r') as f:
        existing_meta = json.load(f)
    
    if verbose == 1:
        print(f"✓ Found existing metadata: {meta_json_path}")
    
    # Normalize current parameters for comparison
    current_flags = flag if isinstance(flag, list) else [flag]
    current_samples = []
    if sample and sample is not False:
        if isinstance(sample, list):
            current_samples = sample
        else:
            current_samples = [sample]
    
    current_split_strategy = 'cv' if cv is not None else 'split'
    
    # Extract existing parameters
    existing_flags = existing_meta.get('flags', [existing_meta.get('flag', '')])
    existing_samples = existing_meta.get('sample_sizes', [])
    existing_split_strategy = existing_meta.get('split_strategy', '')
    existing_seed = existing_meta.get('seed', None)
    existing_cv = existing_meta.get('cv_folds', None)
    existing_split_ratio = existing_meta.get('split_ratio', None)
    
    # Compare configurations
    configs_match = (
        set(current_flags) == set(existing_flags) and
        set(current_samples) == set(existing_samples) and
        current_split_strategy == existing_split_strategy and
        seed == existing_seed
    )
    
    if current_split_strategy == 'cv':
        configs_match = configs_match and (cv == existing_cv)
    else:
        configs_match = configs_match and (split == existing_split_ratio)
    
    # If configurations don't match
    if not configs_match:
        if not add_flag:
            # Strict mode: raise error for any mismatch
            raise ValueError(
                f"\n{'='*70}\n"
                f"❌ CONFIGURATION MISMATCH DETECTED\n"
                f"{'='*70}\n"
                f"Existing metadata found, but configuration does not match.\n"
                f"\n"
                f"Existing configuration:\n"
                f"  - Flags:    {existing_flags}\n"
                f"  - Samples:  {existing_samples}\n"
                f"  - Strategy: {existing_split_strategy}\n"
                f"  - Seed:     {existing_seed}\n"
                f"  - CV/Split: {existing_cv if existing_split_strategy == 'cv' else existing_split_ratio}\n"
                f"\n"
                f"Current parameters:\n"
                f"  - Flags:    {current_flags}\n"
                f"  - Samples:  {current_samples}\n"
                f"  - Strategy: {current_split_strategy}\n"
                f"  - Seed:     {seed}\n"
                f"  - CV/Split: {cv if current_split_strategy == 'cv' else split}\n"
                f"\n"
                f"Solutions:\n"
                f"  1. Use the same parameters as existing metadata\n"
                f"  2. Delete {project_path} to regenerate with new config\n"
                f"  3. Use a different project_path for new configuration\n"
                f"  4. Use add_flag=True to incrementally add new flags\n"
                f"{'='*70}\n"
            )
        else:
            # Incremental mode: check if only flags changed
            # Other parameters (sample, seed, cv/split) must match
            other_params_match = (
                set(current_samples) == set(existing_samples) and
                current_split_strategy == existing_split_strategy and
                seed == existing_seed
            )
            if current_split_strategy == 'cv':
                other_params_match = other_params_match and (cv == existing_cv)
            else:
                other_params_match = other_params_match and (split == existing_split_ratio)
            
            if not other_params_match:
                raise ValueError(
                    f"\n{'='*70}\n"
                    f"❌ CONFIGURATION MISMATCH IN ADD_FLAG MODE\n"
                    f"{'='*70}\n"
                    f"In add_flag mode, only new flags can be added.\n"
                    f"Other parameters (sample, seed, cv/split) must remain the same.\n"
                    f"\n"
                    f"Existing: samples={existing_samples}, strategy={existing_split_strategy}, "
                    f"seed={existing_seed}, cv/split={existing_cv if existing_split_strategy == 'cv' else existing_split_ratio}\n"
                    f"Current:  samples={current_samples}, strategy={current_split_strategy}, "
                    f"seed={seed}, cv/split={cv if current_split_strategy == 'cv' else split}\n"
                    f"\n"
                    f"Solution: Use the same parameters or disable add_flag mode.\n"
                    f"{'='*70}\n"
                )
            
            # Find new flags
            new_flags = list(set(current_flags) - set(existing_flags))
            if not new_flags:
                if verbose == 1:
                    print("✓ All flags already exist. No new flags to generate.")
                # All flags exist, can skip
                existing_results = load_existing_split_data(
                    project_path, existing_meta, df, current_flags, current_samples, verbose
                )
                return True, existing_results, None
            
            # Validate existing flags
            existing_flags_to_check = list(set(current_flags) & set(existing_flags))
            if existing_flags_to_check and verbose == 1:
                print(f"✓ Validating existing flags: {existing_flags_to_check}")
            
            # Return new flags to generate
            if verbose == 1:
                print(f"✓ New flags to generate: {new_flags}")
            return False, None, new_flags
    
    # Configurations match - validate index consistency
    if verbose == 1:
        print("✓ Configuration matches existing metadata.")
        print("  Validating index consistency...")
    
    # Validate indices
    validate_index_consistency(
        project_path, existing_meta, df, seed, split, cv, 
        current_flags, current_samples, verbose
    )
    
    # If validation passed, load and return existing data
    if verbose == 1:
        print("  Loading existing split data...")
    
    existing_results = load_existing_split_data(
        project_path, existing_meta, df, current_flags, current_samples, verbose
    )
    
    return True, existing_results, None


def validate_index_consistency(project_path, existing_meta, df, seed, split, cv, 
                               flags, samples, verbose):
    """
    Validate that generated indices match stored indices.
    
    Generates indices for configurations and compares with stored files.
    Raises error if any mismatch is found.
    
    Parameters:
    -----------
    project_path : str
        Project directory path
    existing_meta : dict
        Existing metadata from meta_split.json
    df : pd.DataFrame
        Input dataframe
    seed : int
        Random seed
    split : float or None
        Split ratio
    cv : int or None
        CV folds
    flags : list
        List of flags
    samples : list
        List of sample sizes (empty list for "full")
    verbose : int
        Verbosity level
    
    Raises:
    -------
    ValueError : If indices don't match
    """
    configurations = existing_meta.get('configurations', [])
    
    if not configurations:
        if verbose == 1:
            print("  ⚠️  No configurations in metadata, skipping validation.")
        return
    
    # Check first few configurations as representative sample
    num_to_check = min(3, len(configurations))
    
    for i, config in enumerate(configurations[:num_to_check]):
        flag_name = config['flag']
        sample_size = config.get('sample_size', 'full')
        subdir = config['subdirectory']
        
        if verbose == 1:
            print(f"  Checking: {flag_name}, sample={sample_size}")
        
        # Prepare dataframe (apply sampling if needed)
        df_test = df.copy()
        if sample_size != 'full' and sample_size is not None:
            np.random.seed(seed)
            if len(df_test) > sample_size:
                sampled_indices = np.random.choice(df_test.index, size=sample_size, replace=False)
                df_test = df_test.loc[sampled_indices].copy()
        
        # Add site numbers
        df_test['Site_number'] = df_test.groupby(['longitude', 'latitude']).ngroup()
        
        # Check if CV or split mode (split mode now also uses fold structure)
        is_cv = 'cv_folds' in config or cv is not None
        cv_folds = config.get('cv_folds', cv) if is_cv else 1
        
        if is_cv or 'folds' in config:
            # CV mode or split mode with fold structure: check first fold
            fold_info = config.get('folds', [{}])[0]  # Get first fold info
            
            # Generate indices for first fold
            if flag_name in ["Site", "Site_gradient"]:
                unique_sites = df_test['Site_number'].unique()
                kf = KFold(n_splits=cv_folds, shuffle=True, random_state=seed)
                
                for fold_idx, (train_site_idx, test_site_idx) in enumerate(kf.split(unique_sites)):
                    if fold_idx == 0:  # Only check first fold
                        train_sites = unique_sites[train_site_idx]
                        test_sites = unique_sites[test_site_idx]
                        
                        train_mask = df_test['Site_number'].isin(train_sites)
                        test_mask = df_test['Site_number'].isin(test_sites)
                        
                        generated_train = df_test[train_mask].index.to_numpy()
                        generated_test = df_test[test_mask].index.to_numpy()
                        break
            else:
                # For other modes, skip validation for now
                if verbose == 1:
                    print(f"    Skipping validation for {flag_name} mode")
                continue
            
            # Load stored indices
            train_file = os.path.join(project_path, subdir, fold_info['train_file'])
            test_file = os.path.join(project_path, subdir, fold_info['test_file'])
            
            if not os.path.exists(train_file) or not os.path.exists(test_file):
                if verbose == 1:
                    print(f"    ⚠️  Index files not found, skipping")
                continue
            
            stored_train = np.load(train_file)
            stored_test = np.load(test_file)
            
            # Sort for comparison (order doesn't matter)
            generated_train_sorted = np.sort(generated_train)
            generated_test_sorted = np.sort(generated_test)
            stored_train_sorted = np.sort(stored_train)
            stored_test_sorted = np.sort(stored_test)
            
            # Compare
            train_match = np.array_equal(generated_train_sorted, stored_train_sorted)
            test_match = np.array_equal(generated_test_sorted, stored_test_sorted)
            
            if not train_match or not test_match:
                raise ValueError(
                    f"\n{'='*70}\n"
                    f"❌ INDEX INCONSISTENCY DETECTED\n"
                    f"{'='*70}\n"
                    f"Configuration: {flag_name}, sample={sample_size}, fold=1\n"
                    f"\n"
                    f"Generated train indices: {len(generated_train)}\n"
                    f"Stored train indices:    {len(stored_train)}\n"
                    f"Train match: {train_match}\n"
                    f"\n"
                    f"Generated test indices:  {len(generated_test)}\n"
                    f"Stored test indices:     {len(stored_test)}\n"
                    f"Test match: {test_match}\n"
                    f"\n"
                    f"This suggests:\n"
                    f"  1. Input dataframe changed (different data or order), or\n"
                    f"  2. Random seed not working correctly, or\n"
                    f"  3. Previous split data corrupted\n"
                    f"\n"
                    f"Solutions:\n"
                    f"  1. Verify input dataframe is identical to original\n"
                    f"  2. Delete {project_path} and regenerate\n"
                    f"  3. Use different project_path for new splits\n"
                    f"{'='*70}\n"
                )
            
            if verbose == 1:
                print(f"    ✓ Indices match (fold 1)")
    
    if verbose == 1:
        print("✓ Index consistency validated successfully!")


def load_existing_split_data(project_path, existing_meta, df, flags, samples, verbose):
    """
    Load existing split data from files.
    
    Returns data in the same format as split_test_train would generate.
    
    Parameters:
    -----------
    project_path : str
        Project directory path
    existing_meta : dict
        Metadata from meta_split.json
    df : pd.DataFrame
        Input dataframe
    flags : list
        List of flag names
    samples : list
        List of sample sizes (empty for "full")
    verbose : int
        Verbosity level
    
    Returns:
    --------
    Results in same format as split_test_train:
    - If multiple flags: dict with flags as keys
    - If multiple samples: dict with sample sizes as keys
    - Otherwise: tuple of split results
    """
    configurations = existing_meta.get('configurations', [])
    is_cv = existing_meta.get('split_strategy') == 'cv'
    
    # Prepare df with Site_number
    df_copy = df.copy()
    df_copy['Site_number'] = df_copy.groupby(['longitude', 'latitude']).ngroup()
    
    # Build results structure
    if len(flags) > 1:
        # Multiple flags case
        results = {}
        for flag_name in flags:
            flag_configs = [c for c in configurations if c['flag'] == flag_name]
            
            if len(samples) > 1:
                # Multiple flags + multiple samples
                sample_results = {}
                for sample_size in samples:
                    config = next((c for c in flag_configs if c.get('sample_size') == sample_size), None)
                    if config:
                        result = load_single_config(project_path, config, df_copy, is_cv, verbose)
                        sample_results[sample_size] = result
                results[flag_name] = sample_results
            else:
                # Multiple flags + single/no sample
                sample_size = samples[0] if samples else 'full'
                config = next((c for c in flag_configs if c.get('sample_size', 'full') == sample_size), None)
                if config:
                    result = load_single_config(project_path, config, df_copy, is_cv, verbose)
                    results[flag_name] = result
        
        return results
    
    elif len(samples) > 1:
        # Single flag + multiple samples
        flag_name = flags[0]
        flag_configs = [c for c in configurations if c['flag'] == flag_name]
        
        results = {}
        for sample_size in samples:
            config = next((c for c in flag_configs if c.get('sample_size') == sample_size), None)
            if config:
                result = load_single_config(project_path, config, df_copy, is_cv, verbose)
                results[sample_size] = result
        
        return results
    
    else:
        # Single flag + single/no sample
        flag_name = flags[0]
        sample_size = samples[0] if samples else 'full'
        
        config = next((c for c in configurations 
                      if c['flag'] == flag_name and c.get('sample_size', 'full') == sample_size), 
                      None)
        
        if config:
            return load_single_config(project_path, config, df_copy, is_cv, verbose)
        else:
            raise ValueError(f"Configuration not found: flag={flag_name}, sample={sample_size}")


def load_single_config(project_path, config, df, is_cv, verbose):
    """
    Load split data for a single configuration.
    
    Parameters:
    -----------
    project_path : str
        Project directory path
    config : dict
        Configuration metadata
    df : pd.DataFrame
        Dataframe with Site_number column
    is_cv : bool
        Whether CV mode
    verbose : int
        Verbosity level
    
    Returns:
    --------
    tuple : Split results in same format as split_test_train
    """
    subdir = config['subdirectory']
    
    if is_cv:
        # CV mode: load all folds
        folds_info = config['folds']
        train_site_numbers_list = []
        test_site_numbers_list = []
        train_indices_list = []
        test_indices_list = []
        
        for fold_info in folds_info:
            train_file = os.path.join(project_path, subdir, fold_info['train_file'])
            test_file = os.path.join(project_path, subdir, fold_info['test_file'])
            
            train_ind = np.load(train_file).tolist()
            test_ind = np.load(test_file).tolist()
            
            train_sites = df.loc[train_ind, 'Site_number'].unique().tolist()
            test_sites = df.loc[test_ind, 'Site_number'].unique().tolist()
            
            train_indices_list.append(train_ind)
            test_indices_list.append(test_ind)
            train_site_numbers_list.append(train_sites)
            test_site_numbers_list.append(test_sites)
        
        if verbose == 1:
            print(f"    Loaded {len(folds_info)} folds for {config['flag']}")
        
        return train_site_numbers_list, test_site_numbers_list, train_indices_list, test_indices_list, df
    
    else:
        # Split mode: load single split (treat as fold=1 for consistency)
        # Use folds structure if available (new format), otherwise fall back to old format
        if 'folds' in config and len(config['folds']) > 0:
            # New format: use folds[0]
            fold_info = config['folds'][0]
            train_file = os.path.join(project_path, subdir, fold_info['train_file'])
            test_file = os.path.join(project_path, subdir, fold_info['test_file'])
        else:
            # Old format: backward compatibility
            train_file = os.path.join(project_path, subdir, config['train_file'])
            test_file = os.path.join(project_path, subdir, config['test_file'])
        
        train_ind = np.load(train_file).tolist()
        test_ind = np.load(test_file).tolist()
        
        train_sites = df.loc[train_ind, 'Site_number'].unique().tolist()
        test_sites = df.loc[test_ind, 'Site_number'].unique().tolist()
        
        if verbose == 1:
            print(f"    Loaded split for {config['flag']}")
        
        return train_sites, test_sites, train_ind, test_ind, df


def handle_spatiotemporal_split(df_copy, split, cv, seed, verbose, project_path, thumbnail, grid_size, use_time_blocks=False):
    """
    Handle spatiotemporal split: first split by space (Grid), then split by time (global).
    
    Ensures NO data leakage - test points are completely new in both space and time:
    - Step 1: Split grids into spatial train/test (e.g., 90%/10%)
    - Step 2: Split ALL time points globally into temporal train/test (50%/50%, non-overlapping)
      * If use_time_blocks=False: Random selection of time points
      * If use_time_blocks=True: Split time into blocks (ordered), then randomly select blocks
    - Final train: spatial train grids × temporal train times
    - Final test: spatial test grids × temporal test times
    
    This guarantees every test sample's (location, time) combination is unseen in training.
    
    Parameters
    ----------
    df_copy : pd.DataFrame
        DataFrame with longitude, latitude, time columns
    split : float or None
        Split ratio for spatial split
    cv : int or None
        Number of CV folds
    seed : int
        Random seed
    verbose : int
        Verbosity level
    project_path : str or None
        Project path for saving
    thumbnail : bool
        Whether to display thumbnail
    grid_size : int
        Grid size for spatial split (e.g., 10 for 10x10 grid)
    use_time_blocks : bool, default=False
        If True, split time into blocks and randomly select blocks
        If False, randomly select individual time points
    
    Returns
    -------
    Standard split format (same as other flags):
    - Split mode: (train_sites, test_sites, train_indices, test_indices, df_copy)
    - CV mode: (train_sites_list, test_sites_list, train_indices_list, test_indices_list, df_copy)
    """
    is_cv = cv is not None and cv > 1
    
    if verbose == 1:
        print("\n" + "="*70)
        print("SPATIOTEMPORAL SPLIT")
        print("="*70)
        print("Step 1: Spatial split (Grid-based)")
    
    # Create grid IDs for all data
    lon_min, lon_max = df_copy['longitude'].min(), df_copy['longitude'].max()
    lat_min, lat_max = df_copy['latitude'].min(), df_copy['latitude'].max()
    
    lon_edges = np.linspace(lon_min, lon_max, grid_size + 1)
    lat_edges = np.linspace(lat_min, lat_max, grid_size + 1)
    
    df_copy['grid_lon'] = np.digitize(df_copy['longitude'], lon_edges) - 1
    df_copy['grid_lat'] = np.digitize(df_copy['latitude'], lat_edges) - 1
    df_copy['grid_id'] = df_copy['grid_lon'] * grid_size + df_copy['grid_lat']
    
    if is_cv:
        # CV mode: split grids into cv folds
        unique_grids = df_copy['grid_id'].unique()
        kf = KFold(n_splits=cv, shuffle=True, random_state=seed)
        
        train_site_numbers_list = []
        test_site_numbers_list = []
        train_indices_list = []
        test_indices_list = []
        
        for fold_idx, (train_grid_idx, test_grid_idx) in enumerate(kf.split(unique_grids)):
            if verbose == 1:
                print(f"\n--- Fold {fold_idx + 1}/{cv} ---")
            
            train_grids = unique_grids[train_grid_idx]
            test_grids = unique_grids[test_grid_idx]
            
            # Get spatial subsets
            spatial_train_mask = df_copy['grid_id'].isin(train_grids)
            spatial_test_mask = df_copy['grid_id'].isin(test_grids)
            
            spatial_train_df = df_copy[spatial_train_mask]
            spatial_test_df = df_copy[spatial_test_mask]
            
            if verbose == 1:
                print(f"  Spatial train: {len(train_grids)} grids, {len(spatial_train_df)} samples")
                print(f"  Spatial test:  {len(test_grids)} grids, {len(spatial_test_df)} samples")
                mode_str = "block-random" if use_time_blocks else "random"
                print(f"Step 2: Temporal split (global 50%-50% time split, {mode_str})")
            
            # Temporal split: based on use_time_blocks parameter
            all_times = df_copy['time'].unique()  # Global time points
            
            if use_time_blocks:
                # Block mode: split time into blocks, then randomly select blocks
                all_times_sorted = np.sort(all_times)  # Sort by time
                
                # Determine number of blocks (make it even for 50-50 split)
                num_blocks = cv + 1 if cv % 2 == 1 else cv
                num_train_blocks = num_blocks // 2
                num_test_blocks = num_blocks - num_train_blocks
                
                # Split times into blocks
                time_blocks = np.array_split(all_times_sorted, num_blocks)
                
                # Randomly select train blocks
                np.random.seed(seed + fold_idx)
                block_indices = np.arange(num_blocks)
                train_block_indices = np.random.choice(block_indices, size=num_train_blocks, replace=False)
                test_block_indices = np.setdiff1d(block_indices, train_block_indices)
                
                # Flatten selected blocks into time point arrays
                train_time_points = np.concatenate([time_blocks[i] for i in train_block_indices])
                test_time_points = np.concatenate([time_blocks[i] for i in test_block_indices])
                
                if verbose == 1:
                    print(f"  Time blocks: {num_blocks} blocks, randomly selected {num_train_blocks} for train, {num_test_blocks} for test")
                    print(f"  Train blocks: {sorted(train_block_indices+1)}, Test blocks: {sorted(test_block_indices+1)}")
            else:
                # Random mode: randomly select individual time points
                num_all_times = len(all_times)
                num_train_times = num_all_times // 2
                
                np.random.seed(seed + fold_idx)
                train_time_points = np.random.choice(all_times, size=num_train_times, replace=False)
                test_time_points = np.setdiff1d(all_times, train_time_points)
            
            if verbose == 1:
                print(f"  Global times split: {len(train_time_points)} train times, {len(test_time_points)} test times (NO overlap)")
            
            # Final train: spatial train grids × temporal train times
            final_train_mask = spatial_train_df['time'].isin(train_time_points)
            final_train_indices = spatial_train_df[final_train_mask].index.tolist()
            
            # Final test: spatial test grids × temporal test times
            final_test_mask = spatial_test_df['time'].isin(test_time_points)
            final_test_indices = spatial_test_df[final_test_mask].index.tolist()
            
            if verbose == 1:
                print(f"  Final train: {len(final_train_indices)} samples ({len(final_train_indices)/len(df_copy)*100:.1f}%)")
                print(f"  Final test:  {len(final_test_indices)} samples ({len(final_test_indices)/len(df_copy)*100:.1f}%)")
            
            # Get site numbers for compatibility (though grids are primary)
            train_sites = spatial_train_df['Site_number'].unique().tolist()
            test_sites = spatial_test_df['Site_number'].unique().tolist()
            
            train_indices_list.append(final_train_indices)
            test_indices_list.append(final_test_indices)
            train_site_numbers_list.append(train_sites)
            test_site_numbers_list.append(test_sites)
        
        # Clean up temporary grid columns
        df_copy.drop(['grid_lon', 'grid_lat', 'grid_id'], axis=1, inplace=True)
        
        # Display thumbnail if requested (show spatial split only)
        if thumbnail:
            plot_cv_thumbnail(df_copy, train_indices_list, test_indices_list, cv, "Spatiotemporal")
        
        # No need for special save - will use standard save path
        # The calling function will handle saving via save_all_results
        
        return train_site_numbers_list, test_site_numbers_list, train_indices_list, test_indices_list, df_copy
    
    else:
        # Split mode: Grid-based spatial split
        # Get grid statistics to select representative grids
        grid_stats = df_copy.groupby('grid_id').size().reset_index(name='sample_count')
        valid_grids = grid_stats[grid_stats['sample_count'] > 0]['grid_id'].values
        
        # Stratified grid selection
        num_valid_grids = len(valid_grids)
        num_test_grids = max(1, round(num_valid_grids * split))
        
        np.random.seed(seed)
        test_grids = np.random.choice(valid_grids, size=num_test_grids, replace=False)
        train_grids = np.setdiff1d(valid_grids, test_grids)
        
        # Get spatial subsets
        spatial_train_mask = df_copy['grid_id'].isin(train_grids)
        spatial_test_mask = df_copy['grid_id'].isin(test_grids)
        
        spatial_train_df = df_copy[spatial_train_mask]
        spatial_test_df = df_copy[spatial_test_mask]
        
        # Get site numbers for compatibility
        train_sites = spatial_train_df['Site_number'].unique().tolist()
        test_sites = spatial_test_df['Site_number'].unique().tolist()
        
        if verbose == 1:
            print(f"  Spatial train: {len(train_grids)} grids ({len(train_sites)} sites), {len(spatial_train_df)} samples")
            print(f"  Spatial test:  {len(test_grids)} grids ({len(test_sites)} sites), {len(spatial_test_df)} samples")
            mode_str = "block-random" if use_time_blocks else "random"
            print(f"Step 2: Temporal split (global 50%-50% time split, {mode_str})")
        
        # Temporal split: based on use_time_blocks parameter
        all_times = df_copy['time'].unique()  # Global time points
        
        if use_time_blocks:
            # Block mode: split time into blocks, then randomly select blocks
            all_times_sorted = np.sort(all_times)  # Sort by time
            
            # Use 10 blocks by default for split mode
            num_blocks = 10
            num_train_blocks = num_blocks // 2
            num_test_blocks = num_blocks - num_train_blocks
            
            # Split times into blocks
            time_blocks = np.array_split(all_times_sorted, num_blocks)
            
            # Randomly select train blocks
            np.random.seed(seed)
            block_indices = np.arange(num_blocks)
            train_block_indices = np.random.choice(block_indices, size=num_train_blocks, replace=False)
            test_block_indices = np.setdiff1d(block_indices, train_block_indices)
            
            # Flatten selected blocks into time point arrays
            train_time_points = np.concatenate([time_blocks[i] for i in train_block_indices])
            test_time_points = np.concatenate([time_blocks[i] for i in test_block_indices])
            
            if verbose == 1:
                print(f"  Time blocks: {num_blocks} blocks, randomly selected {num_train_blocks} for train, {num_test_blocks} for test")
                print(f"  Train blocks: {sorted(train_block_indices+1)}, Test blocks: {sorted(test_block_indices+1)}")
        else:
            # Random mode: randomly select individual time points
            num_all_times = len(all_times)
            num_train_times = num_all_times // 2
            
            np.random.seed(seed)
            train_time_points = np.random.choice(all_times, size=num_train_times, replace=False)
            test_time_points = np.setdiff1d(all_times, train_time_points)
        
        if verbose == 1:
            print(f"  Global times split: {len(train_time_points)} train times, {len(test_time_points)} test times (NO overlap)")
        
        # Final train: spatial train grids × temporal train times
        final_train_mask = spatial_train_df['time'].isin(train_time_points)
        final_train_indices = spatial_train_df[final_train_mask].index.tolist()
        
        # Final test: spatial test grids × temporal test times
        final_test_mask = spatial_test_df['time'].isin(test_time_points)
        final_test_indices = spatial_test_df[final_test_mask].index.tolist()
        
        if verbose == 1:
            print(f"  Final train: {len(final_train_indices)} samples ({len(final_train_indices)/len(df_copy)*100:.1f}%)")
            print(f"  Final test:  {len(final_test_indices)} samples ({len(final_test_indices)/len(df_copy)*100:.1f}%)")
            print(f"  ✓ NO DATA LEAKAGE: Test has new grids AND new times!")
            print("="*70)
        
        # Clean up temporary grid columns
        df_copy.drop(['grid_lon', 'grid_lat', 'grid_id'], axis=1, inplace=True)
        
        # Display thumbnail if requested (show spatial split only)
        if thumbnail:
            plot_split_thumbnail(df_copy, final_train_indices, final_test_indices, "Spatiotemporal")
        
        # No need for special save - will use standard save path
        # The calling function will handle saving via save_all_results
        
        return train_sites, test_sites, final_train_indices, final_test_indices, df_copy

