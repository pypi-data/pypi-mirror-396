"""
Baseline spatial regression models.

Classes:
- SpatialRegressor: Wrapper for various spatial models (Linear, SVM, LightGBM, GAM)
- InterpolationModel: Spatial interpolation (IDW)
"""

try:
    from .spatial import SpatialRegressor
    from .interpolation import InterpolationModel
except ImportError:
    from spatial import SpatialRegressor
    from interpolation import InterpolationModel

__all__ = ['SpatialRegressor', 'InterpolationModel']

