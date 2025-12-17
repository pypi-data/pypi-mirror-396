"""Aggregation utilities for computing average success rates."""

from proportions.aggregation.average_posterior import (
    compute_posterior_t_from_group_posteriors,
    compute_posterior_t_hierarchical_bayes,
    compute_prior_t_hierarchical_bayes,
)
from proportions.aggregation.moment_matching import (
    beta_mean,
    beta_variance,
    fit_beta_from_moments,
    validate_beta_fit,
)
from proportions.aggregation.mc_intervals import (
    weighted_quantiles,
    mc_confidence_interval,
)

__all__ = [
    "compute_posterior_t_from_group_posteriors",
    "compute_posterior_t_hierarchical_bayes",
    "compute_prior_t_hierarchical_bayes",
    "beta_mean",
    "beta_variance",
    "fit_beta_from_moments",
    "validate_beta_fit",
    "weighted_quantiles",
    "mc_confidence_interval",
]
