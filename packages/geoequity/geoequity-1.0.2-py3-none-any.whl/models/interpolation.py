"""
Spatial interpolation methods.

IDW (Inverse Distance Weighting) is a simple and effective interpolation method.
"""

import numpy as np
from scipy.spatial.distance import cdist


class InterpolationModel:
    """
    Spatial interpolation model using IDW.
    
    Parameters
    ----------
    method : str, default='idw'
        Interpolation method: 'idw' (Inverse Distance Weighting)
    power : float, default=2
        Power parameter for IDW (higher = more local influence)
    
    Example
    -------
    >>> model = InterpolationModel(method='idw', power=2)
    >>> model.fit(train_coords, train_r2)
    >>> predictions = model.predict(test_coords)
    """
    
    def __init__(self, method='idw', power=2):
        self.method = method
        self.power = power
        self.X_train = None
        self.y_train = None
    
    def fit(self, X, y):
        """
        Fit the interpolation model.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, 2)
            Training coordinates [longitude, latitude]
        y : array-like of shape (n_samples,)
            Target values (e.g., R² scores)
        
        Returns
        -------
        self
        """
        self.X_train = np.asarray(X)
        self.y_train = np.asarray(y)
        return self
    
    def predict(self, X):
        """
        Predict values at new locations using IDW.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, 2)
            Coordinates to predict [longitude, latitude]
        
        Returns
        -------
        predictions : np.ndarray
            Interpolated values
        """
        if self.X_train is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X = np.asarray(X)
        
        if self.method == 'idw':
            return self._idw_predict(X)
        else:
            raise NotImplementedError(f"Method '{self.method}' not implemented")
    
    def _idw_predict(self, X):
        """
        Vectorized IDW interpolation using cdist.
        
        Much faster than loop-based implementation.
        """
        # Calculate all pairwise distances
        distances = cdist(X, self.X_train)
        
        # Avoid division by zero
        distances = np.maximum(distances, 1e-10)
        
        # IDW weights: w = 1/d^p
        weights = 1.0 / (distances ** self.power)
        
        # Normalize weights
        weights = weights / weights.sum(axis=1, keepdims=True)
        
        # Weighted average
        predictions = weights @ self.y_train
        
        return predictions
    
    def score(self, X, y, metric='correlation'):
        """
        Score the model on test data.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, 2)
            Test coordinates
        y : array-like of shape (n_samples,)
            True values
        metric : str, default='correlation'
            'correlation' or 'r2'
        
        Returns
        -------
        score : float
        """
        from scipy.stats import pearsonr
        from sklearn.metrics import r2_score
        
        y_pred = self.predict(X)
        
        if metric == 'correlation':
            return pearsonr(y, y_pred)[0]
        else:
            return r2_score(y, y_pred)
