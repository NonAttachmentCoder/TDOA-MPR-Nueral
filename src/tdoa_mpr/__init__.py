"""TDOA-MPR research foundations; see CONTRACT.md for units and assumptions."""
from .physics import range_differences, mpr_jacobians, local_information, tangent_basis
from .covariance import differencing_matrix, range_difference_covariance, effective_covariance

__all__ = ["range_differences", "mpr_jacobians", "local_information",
           "tangent_basis", "differencing_matrix", "range_difference_covariance",
           "effective_covariance"]
