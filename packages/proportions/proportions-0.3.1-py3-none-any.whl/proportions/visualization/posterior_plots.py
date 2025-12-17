"""Visualization utilities for posterior distributions.

This module provides plotting functions for visualizing prior and posterior
distributions from Hierarchical Bayes and Flat Bayes (Single-Theta) inference.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta as beta_dist

from proportions.core.models import HierarchicalBayesResult, SingleThetaResult, BinomialData
from proportions.aggregation import compute_prior_t_hierarchical_bayes


def plot_posterior_mu(
    result: HierarchicalBayesResult,
    figsize: tuple[float, float] = (10, 6),
    title: str | None = None,
    show_ci: bool = True,
    ci_level: float = 0.95,
    color: str = 'blue',
    xlim: tuple[float, float] | None = None,
    ax: plt.Axes | None = None,
) -> plt.Figure:
    """Plot posterior distribution of μ (average success rate).

    Creates a visualization showing the posterior distribution of μ (the average
    success rate across all groups) from Hierarchical Bayes inference, using the
    fitted Beta distribution.

    Args:
        result: HierarchicalBayesResult from hierarchical_bayes().
        figsize: Figure size as (width, height) tuple (default: (10, 6)).
                 Ignored if ax is provided.
        title: Optional custom title. If None, generates descriptive title.
        show_ci: If True, shows credible interval bounds as vertical lines (default: True).
        ci_level: Credible interval level to display (default: 0.95).
        color: Color for the posterior curve (default: 'blue').
        xlim: Optional (xmin, xmax) tuple for x-axis limits. If None, auto-determines
              from credible interval.
        ax: Optional matplotlib Axes to plot into. If None, creates new figure.

    Returns:
        Matplotlib Figure object.

    Raises:
        ValueError: If result doesn't have fitted posterior parameters.

    Example:
        >>> from proportions.core.models import BinomialData
        >>> from proportions.inference.hierarchical_bayes import hierarchical_bayes
        >>> from proportions.visualization.posterior_plots import plot_posterior_mu
        >>>
        >>> data = BinomialData(x=np.array([8, 7, 9]), n=np.array([10, 10, 10]))
        >>> result = hierarchical_bayes(data, random_seed=42)
        >>> fig = plot_posterior_mu(result)
        >>> fig.savefig('posterior_mu.png', dpi=150, bbox_inches='tight')
        >>> plt.show()
    """
    if result.posterior.alpha_fitted is None or result.posterior.beta_fitted is None:
        raise ValueError("Result must have fitted posterior parameters (alpha_fitted, beta_fitted)")

    # Determine x-axis range
    if xlim is None:
        # Use credible interval with some padding
        ci_width = result.posterior.ci_upper - result.posterior.ci_lower
        xmin = max(0.0, result.posterior.ci_lower - 0.2 * ci_width)
        xmax = min(1.0, result.posterior.ci_upper + 0.2 * ci_width)
    else:
        xmin, xmax = xlim

    # Generate x values and compute PDF
    x = np.linspace(xmin, xmax, 1000)
    y = beta_dist.pdf(x, result.posterior.alpha_fitted, result.posterior.beta_fitted)

    # Create figure or use provided axes
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        created_figure = True
    else:
        fig = ax.get_figure()
        created_figure = False

    # Plot weighted histogram if samples and weights are available
    if (result.posterior.samples is not None and
        result.importance_weights is not None):
        ax.hist(result.posterior.samples, bins=60, weights=result.importance_weights,
                density=True, alpha=0.6, color=color, edgecolor='black',
                linewidth=0.5, label='Posterior samples (weighted)')

    # Plot posterior curve
    ax.plot(x, y, color=color, linewidth=2.5, label='Fitted Beta', alpha=0.9)

    # Mark mean
    ax.axvline(result.posterior.mu, color=color, linestyle='--', linewidth=2,
               alpha=0.7, label=f'Mean: {result.posterior.mu:.4f}')

    # Show credible interval if requested
    if show_ci:
        ci_lower = result.posterior.ci_lower
        ci_upper = result.posterior.ci_upper

        pdf_lower = beta_dist.pdf(ci_lower, result.posterior.alpha_fitted, result.posterior.beta_fitted)
        pdf_upper = beta_dist.pdf(ci_upper, result.posterior.alpha_fitted, result.posterior.beta_fitted)

        ax.plot([ci_lower, ci_lower], [0, pdf_lower], color=color, linestyle=':',
                linewidth=2, alpha=0.6)
        ax.plot([ci_upper, ci_upper], [0, pdf_upper], color=color, linestyle=':',
                linewidth=2, alpha=0.6)

        # Shade CI region
        x_ci = x[(x >= ci_lower) & (x <= ci_upper)]
        y_ci = beta_dist.pdf(x_ci, result.posterior.alpha_fitted, result.posterior.beta_fitted)
        ax.fill_between(x_ci, y_ci, color=color, alpha=0.3)

    # Labels and title
    ax.set_xlabel('μ (Average Success Rate)', fontsize=12)
    ax.set_ylabel('Posterior Density', fontsize=12)

    if title is None:
        title = (f'Posterior Distribution of μ\n'
                f'Mean: {result.posterior.mu:.4f}, '
                f'{int(ci_level*100)}% CI: [{result.posterior.ci_lower:.4f}, {result.posterior.ci_upper:.4f}]')
    ax.set_title(title, fontsize=13, fontweight='bold')

    # Set y-axis to start at 0
    ylim = ax.get_ylim()
    ax.set_ylim(0, ylim[1] * 1.05)

    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    if created_figure:
        plt.tight_layout()
    return fig


def plot_prior_mu(
    alpha_samples: np.ndarray,
    beta_samples: np.ndarray,
    data: BinomialData,
    figsize: tuple[float, float] = (10, 6),
    title: str | None = None,
    show_ci: bool = True,
    ci_level: float = 0.95,
    color: str = 'gray',
    xlim: tuple[float, float] | None = None,
    ax: plt.Axes | None = None,
) -> plt.Figure:
    """Plot prior distribution of μ (average success rate).

    Creates a visualization showing the prior distribution of μ (the average
    success rate across all groups) from hyperparameter samples, using uniform
    weights across samples (not importance weights).

    Args:
        alpha_samples: Array of α samples from hyperprior.
        beta_samples: Array of β samples from hyperprior.
        data: BinomialData (used only to determine number of groups).
        figsize: Figure size as (width, height) tuple (default: (10, 6)).
                 Ignored if ax is provided.
        title: Optional custom title. If None, generates descriptive title.
        show_ci: If True, shows credible interval bounds as vertical lines (default: True).
        ci_level: Credible interval level to display (default: 0.95).
        color: Color for the prior curve (default: 'gray').
        xlim: Optional (xmin, xmax) tuple for x-axis limits. If None, auto-determines
              from credible interval.
        ax: Optional matplotlib Axes to plot into. If None, creates new figure.

    Returns:
        Matplotlib Figure object.

    Raises:
        ValueError: If alpha_samples and beta_samples have different lengths.

    Example:
        >>> from proportions.core.models import BinomialData
        >>> from proportions.inference.hierarchical_bayes import hierarchical_bayes
        >>> from proportions.visualization.posterior_plots import plot_prior_mu
        >>>
        >>> data = BinomialData(x=np.array([8, 7, 9]), n=np.array([10, 10, 10]))
        >>> result = hierarchical_bayes(data, random_seed=42, return_samples=True)
        >>> fig = plot_prior_mu(result.alpha_samples, result.beta_samples, data)
        >>> fig.savefig('prior_mu.png', dpi=150, bbox_inches='tight')
        >>> plt.show()
    """
    # Compute prior distribution
    prior = compute_prior_t_hierarchical_bayes(
        alpha_samples, beta_samples, data, ci_level=ci_level
    )

    if prior.alpha_fitted is None or prior.beta_fitted is None:
        raise ValueError("Prior fitting failed - could not compute fitted parameters")

    # Determine x-axis range
    if xlim is None:
        # Use credible interval with some padding
        ci_width = prior.ci_upper - prior.ci_lower
        xmin = max(0.0, prior.ci_lower - 0.2 * ci_width)
        xmax = min(1.0, prior.ci_upper + 0.2 * ci_width)
    else:
        xmin, xmax = xlim

    # Generate x values and compute PDF
    x = np.linspace(xmin, xmax, 1000)
    y = beta_dist.pdf(x, prior.alpha_fitted, prior.beta_fitted)

    # Create figure or use provided axes
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        created_figure = True
    else:
        fig = ax.get_figure()
        created_figure = False

    # Plot histogram if samples are available
    if prior.samples is not None:
        ax.hist(prior.samples, bins=60, density=True, alpha=0.6,
                color=color, edgecolor='black', linewidth=0.5, label='Prior samples')

    # Plot prior curve
    ax.plot(x, y, color=color, linewidth=2.5, label='Fitted Beta', alpha=0.9)

    # Mark mean
    ax.axvline(prior.mu, color=color, linestyle='--', linewidth=2,
               alpha=0.7, label=f'Mean: {prior.mu:.4f}')

    # Show credible interval if requested
    if show_ci:
        ci_lower = prior.ci_lower
        ci_upper = prior.ci_upper

        pdf_lower = beta_dist.pdf(ci_lower, prior.alpha_fitted, prior.beta_fitted)
        pdf_upper = beta_dist.pdf(ci_upper, prior.alpha_fitted, prior.beta_fitted)

        ax.plot([ci_lower, ci_lower], [0, pdf_lower], color=color, linestyle=':',
                linewidth=2, alpha=0.6)
        ax.plot([ci_upper, ci_upper], [0, pdf_upper], color=color, linestyle=':',
                linewidth=2, alpha=0.6)

        # Shade CI region
        x_ci = x[(x >= ci_lower) & (x <= ci_upper)]
        y_ci = beta_dist.pdf(x_ci, prior.alpha_fitted, prior.beta_fitted)
        ax.fill_between(x_ci, y_ci, color=color, alpha=0.3)

    # Labels and title
    ax.set_xlabel('μ (Average Success Rate)', fontsize=12)
    ax.set_ylabel('Prior Density', fontsize=12)

    if title is None:
        title = (f'Prior Distribution of μ\n'
                f'Mean: {prior.mu:.4f}, '
                f'{int(ci_level*100)}% CI: [{prior.ci_lower:.4f}, {prior.ci_upper:.4f}]')
    ax.set_title(title, fontsize=13, fontweight='bold')

    # Set y-axis to start at 0
    ylim = ax.get_ylim()
    ax.set_ylim(0, ylim[1] * 1.05)

    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    if created_figure:
        plt.tight_layout()
    return fig


def plot_prior_posterior_mu(
    result: HierarchicalBayesResult,
    data: BinomialData,
    figsize: tuple[float, float] = (10, 6),
    title: str | None = None,
    show_ci: bool = True,
    ci_level: float = 0.95,
    prior_color: str = 'gray',
    posterior_color: str = 'blue',
    xlim: tuple[float, float] | None = None,
    ax: plt.Axes | None = None,
) -> plt.Figure:
    """Plot prior and posterior distributions of μ on the same axes.

    Creates a comparison visualization showing both the prior and posterior
    distributions of μ (average success rate) from Hierarchical Bayes inference.
    The prior uses uniform weights across hyperparameter samples, while the
    posterior uses importance weights based on the data likelihood.

    Args:
        result: HierarchicalBayesResult from hierarchical_bayes() with return_samples=True.
        data: BinomialData used in the analysis.
        figsize: Figure size as (width, height) tuple (default: (10, 6)).
                 Ignored if ax is provided.
        title: Optional custom title. If None, generates descriptive title.
        show_ci: If True, shows credible interval bounds for both distributions (default: True).
        ci_level: Credible interval level to display (default: 0.95).
        prior_color: Color for the prior curve (default: 'gray').
        posterior_color: Color for the posterior curve (default: 'blue').
        xlim: Optional (xmin, xmax) tuple for x-axis limits. If None, auto-determines
              to show both distributions.
        ax: Optional matplotlib Axes to plot into. If None, creates new figure.

    Returns:
        Matplotlib Figure object.

    Raises:
        ValueError: If result doesn't have hyperparameter samples (need return_samples=True)
                    or fitted posterior parameters.

    Example:
        >>> from proportions.core.models import BinomialData
        >>> from proportions.inference.hierarchical_bayes import hierarchical_bayes
        >>> from proportions.visualization.posterior_plots import plot_prior_posterior_mu
        >>>
        >>> data = BinomialData(x=np.array([8, 7, 9]), n=np.array([10, 10, 10]))
        >>> result = hierarchical_bayes(data, random_seed=42, return_samples=True)
        >>> fig = plot_prior_posterior_mu(result, data)
        >>> fig.savefig('prior_posterior_mu.png', dpi=150, bbox_inches='tight')
        >>> plt.show()
    """
    # Validate inputs
    if result.alpha_samples is None or result.beta_samples is None:
        raise ValueError(
            "Result must have hyperparameter samples. "
            "Call hierarchical_bayes() with return_samples=True"
        )

    if result.posterior.alpha_fitted is None or result.posterior.beta_fitted is None:
        raise ValueError("Result must have fitted posterior parameters")

    # Compute prior distribution
    prior = compute_prior_t_hierarchical_bayes(
        result.alpha_samples, result.beta_samples, data, ci_level=ci_level,
        generate_samples=True  # Generate samples for histogram
    )

    if prior.alpha_fitted is None or prior.beta_fitted is None:
        raise ValueError("Prior fitting failed - could not compute fitted parameters")

    # Determine x-axis range to show both distributions
    if xlim is None:
        # Find range that covers both distributions
        all_bounds = [
            prior.ci_lower, prior.ci_upper,
            result.posterior.ci_lower, result.posterior.ci_upper
        ]
        xmin = max(0.0, min(all_bounds) - 0.05)
        xmax = min(1.0, max(all_bounds) + 0.05)
    else:
        xmin, xmax = xlim

    # Generate x values
    x = np.linspace(xmin, xmax, 1000)

    # Compute PDFs
    y_prior = beta_dist.pdf(x, prior.alpha_fitted, prior.beta_fitted)
    y_posterior = beta_dist.pdf(x, result.posterior.alpha_fitted, result.posterior.beta_fitted)

    # Create figure or use provided axes
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        created_figure = True
    else:
        fig = ax.get_figure()
        created_figure = False

    # Plot prior histogram if samples available
    if prior.samples is not None:
        ax.hist(prior.samples, bins=50, density=True, alpha=0.3,
                color=prior_color, edgecolor='black', linewidth=0.3)

    # Plot prior curve
    ax.plot(x, y_prior, color=prior_color, linewidth=2.5, label='Prior', alpha=0.8)
    ax.fill_between(x, y_prior, color=prior_color, alpha=0.15)

    # Plot posterior histogram if samples and weights available
    if (result.posterior.samples is not None and
        result.importance_weights is not None):
        ax.hist(result.posterior.samples, bins=50, weights=result.importance_weights,
                density=True, alpha=0.4, color=posterior_color, edgecolor='black',
                linewidth=0.3)

    # Plot posterior curve
    ax.plot(x, y_posterior, color=posterior_color, linewidth=2.5, label='Posterior', alpha=0.8)
    ax.fill_between(x, y_posterior, color=posterior_color, alpha=0.15)

    # Mark means
    ax.axvline(prior.mu, color=prior_color, linestyle='--', linewidth=2,
               alpha=0.6, label=f'Prior mean: {prior.mu:.4f}')
    ax.axvline(result.posterior.mu, color=posterior_color, linestyle='--', linewidth=2,
               alpha=0.6, label=f'Posterior mean: {result.posterior.mu:.4f}')

    # Show credible intervals if requested
    if show_ci:
        # Prior CI
        prior_ci_lower = prior.ci_lower
        prior_ci_upper = prior.ci_upper
        pdf_prior_lower = beta_dist.pdf(prior_ci_lower, prior.alpha_fitted, prior.beta_fitted)
        pdf_prior_upper = beta_dist.pdf(prior_ci_upper, prior.alpha_fitted, prior.beta_fitted)

        ax.plot([prior_ci_lower, prior_ci_lower], [0, pdf_prior_lower],
                color=prior_color, linestyle=':', linewidth=1.5, alpha=0.5)
        ax.plot([prior_ci_upper, prior_ci_upper], [0, pdf_prior_upper],
                color=prior_color, linestyle=':', linewidth=1.5, alpha=0.5)

        # Posterior CI
        post_ci_lower = result.posterior.ci_lower
        post_ci_upper = result.posterior.ci_upper
        pdf_post_lower = beta_dist.pdf(post_ci_lower, result.posterior.alpha_fitted,
                                        result.posterior.beta_fitted)
        pdf_post_upper = beta_dist.pdf(post_ci_upper, result.posterior.alpha_fitted,
                                        result.posterior.beta_fitted)

        ax.plot([post_ci_lower, post_ci_lower], [0, pdf_post_lower],
                color=posterior_color, linestyle=':', linewidth=1.5, alpha=0.5)
        ax.plot([post_ci_upper, post_ci_upper], [0, pdf_post_upper],
                color=posterior_color, linestyle=':', linewidth=1.5, alpha=0.5)

    # Labels and title
    ax.set_xlabel('μ (Average Success Rate)', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)

    if title is None:
        title = (f'Prior vs Posterior Distribution of μ\n'
                f'Prior: {prior.mu:.4f} [{prior.ci_lower:.4f}, {prior.ci_upper:.4f}] | '
                f'Posterior: {result.posterior.mu:.4f} '
                f'[{result.posterior.ci_lower:.4f}, {result.posterior.ci_upper:.4f}]')
    ax.set_title(title, fontsize=13, fontweight='bold')

    # Set y-axis to start at 0
    ylim = ax.get_ylim()
    ax.set_ylim(0, ylim[1] * 1.05)

    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc='best')

    if created_figure:
        plt.tight_layout()
    return fig


# ==============================================================================
# Flat Bayes (Single-Theta) Visualization Functions
# ==============================================================================


def plot_flat_bayes_prior(
    alpha_prior: float,
    beta_prior: float,
    figsize: tuple[float, float] = (10, 6),
    title: str | None = None,
    show_ci: bool = True,
    ci_level: float = 0.95,
    color: str = 'gray',
    xlim: tuple[float, float] | None = None,
    ax: plt.Axes | None = None,
) -> plt.Figure:
    """Plot prior distribution for Flat Bayes (Single-Theta) model.

    Creates a visualization showing the Beta prior distribution on θ used in
    the Flat Bayes model, which assumes all groups share a common success rate.

    Args:
        alpha_prior: Prior alpha parameter for Beta(α, β).
        beta_prior: Prior beta parameter for Beta(α, β).
        figsize: Figure size as (width, height) tuple (default: (10, 6)).
                 Ignored if ax is provided.
        title: Optional custom title. If None, generates descriptive title.
        show_ci: If True, shows credible interval bounds as vertical lines (default: True).
        ci_level: Credible interval level to display (default: 0.95).
        color: Color for the prior curve (default: 'gray').
        xlim: Optional (xmin, xmax) tuple for x-axis limits. If None, uses (0, 1).
        ax: Optional matplotlib Axes to plot into. If None, creates new figure.

    Returns:
        Matplotlib Figure object.

    Example:
        >>> from proportions.visualization.posterior_plots import plot_flat_bayes_prior
        >>> import matplotlib.pyplot as plt
        >>>
        >>> # Uniform prior
        >>> fig = plot_flat_bayes_prior(1.0, 1.0, title='Flat Bayes Prior: Uniform(0,1)')
        >>> fig.savefig('flat_bayes_prior.png', dpi=150, bbox_inches='tight')
        >>> plt.show()
    """
    # Determine x-axis range
    if xlim is None:
        xmin, xmax = 0.0, 1.0
    else:
        xmin, xmax = xlim

    # Generate x values and compute PDF
    x = np.linspace(xmin, xmax, 1000)
    y = beta_dist.pdf(x, alpha_prior, beta_prior)

    # Create figure or use provided axes
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        created_figure = True
    else:
        fig = ax.get_figure()
        created_figure = False

    # Plot prior curve
    ax.plot(x, y, color=color, linewidth=2.5, label='Prior', alpha=0.9)
    ax.fill_between(x, y, color=color, alpha=0.15)

    # Mark mean
    mean_prior = alpha_prior / (alpha_prior + beta_prior)
    ax.axvline(mean_prior, color=color, linestyle='--', linewidth=2,
               alpha=0.7, label=f'Mean: {mean_prior:.4f}')

    # Show credible interval if requested
    if show_ci:
        alpha_lower = (1 - ci_level) / 2
        alpha_upper = 1 - alpha_lower
        from proportions.distributions.beta import beta_quantiles
        quantiles = beta_quantiles([alpha_lower, alpha_upper], alpha_prior, beta_prior)
        ci_lower = float(quantiles[0])
        ci_upper = float(quantiles[1])

        pdf_lower = beta_dist.pdf(ci_lower, alpha_prior, beta_prior)
        pdf_upper = beta_dist.pdf(ci_upper, alpha_prior, beta_prior)

        ax.plot([ci_lower, ci_lower], [0, pdf_lower], color=color, linestyle=':',
                linewidth=2, alpha=0.6)
        ax.plot([ci_upper, ci_upper], [0, pdf_upper], color=color, linestyle=':',
                linewidth=2, alpha=0.6)

        # Shade CI region
        x_ci = x[(x >= ci_lower) & (x <= ci_upper)]
        y_ci = beta_dist.pdf(x_ci, alpha_prior, beta_prior)
        ax.fill_between(x_ci, y_ci, color=color, alpha=0.3)

    # Labels and title
    ax.set_xlabel('θ (Success Rate)', fontsize=12)
    ax.set_ylabel('Prior Density', fontsize=12)

    if title is None:
        title = (f'Flat Bayes Prior: Beta({alpha_prior:.1f}, {beta_prior:.1f})\n'
                f'Mean: {mean_prior:.4f}')
    ax.set_title(title, fontsize=13, fontweight='bold')

    # Set y-axis to start at 0
    ylim = ax.get_ylim()
    ax.set_ylim(0, ylim[1] * 1.05)

    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    if created_figure:
        plt.tight_layout()
    return fig


def plot_flat_bayes_posterior(
    result: SingleThetaResult,
    figsize: tuple[float, float] = (10, 6),
    title: str | None = None,
    show_ci: bool = True,
    ci_level: float = 0.95,
    color: str = 'blue',
    xlim: tuple[float, float] | None = None,
    ax: plt.Axes | None = None,
) -> plt.Figure:
    """Plot posterior distribution for Flat Bayes (Single-Theta) model.

    Creates a visualization showing the posterior distribution of θ (the pooled
    success rate) from Flat Bayes inference, using the fitted Beta distribution.

    Args:
        result: SingleThetaResult from single_theta_bayesian().
        figsize: Figure size as (width, height) tuple (default: (10, 6)).
                 Ignored if ax is provided.
        title: Optional custom title. If None, generates descriptive title.
        show_ci: If True, shows credible interval bounds as vertical lines (default: True).
        ci_level: Credible interval level to display (default: 0.95).
        color: Color for the posterior curve (default: 'blue').
        xlim: Optional (xmin, xmax) tuple for x-axis limits. If None, auto-determines
              from credible interval.
        ax: Optional matplotlib Axes to plot into. If None, creates new figure.

    Returns:
        Matplotlib Figure object.

    Raises:
        ValueError: If result doesn't have fitted posterior parameters.

    Example:
        >>> import numpy as np
        >>> from proportions.core.models import BinomialData
        >>> from proportions.inference.single_theta import single_theta_bayesian
        >>> from proportions.visualization.posterior_plots import plot_flat_bayes_posterior
        >>>
        >>> data = BinomialData(x=np.array([8, 7, 9]), n=np.array([10, 10, 10]))
        >>> result = single_theta_bayesian(data, alpha_prior=1.0, beta_prior=1.0)
        >>> fig = plot_flat_bayes_posterior(result)
        >>> fig.savefig('flat_bayes_posterior.png', dpi=150, bbox_inches='tight')
        >>> plt.show()
    """
    if result.posterior.alpha_fitted is None or result.posterior.beta_fitted is None:
        raise ValueError("Result must have fitted posterior parameters (alpha_fitted, beta_fitted)")

    # Determine x-axis range
    if xlim is None:
        # Use credible interval with some padding
        ci_width = result.posterior.ci_upper - result.posterior.ci_lower
        xmin = max(0.0, result.posterior.ci_lower - 0.2 * ci_width)
        xmax = min(1.0, result.posterior.ci_upper + 0.2 * ci_width)
    else:
        xmin, xmax = xlim

    # Generate x values and compute PDF
    x = np.linspace(xmin, xmax, 1000)
    y = beta_dist.pdf(x, result.posterior.alpha_fitted, result.posterior.beta_fitted)

    # Create figure or use provided axes
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        created_figure = True
    else:
        fig = ax.get_figure()
        created_figure = False

    # Plot posterior curve
    ax.plot(x, y, color=color, linewidth=2.5, label='Posterior', alpha=0.9)
    ax.fill_between(x, y, color=color, alpha=0.15)

    # Mark mean
    ax.axvline(result.posterior.mu, color=color, linestyle='--', linewidth=2,
               alpha=0.7, label=f'Mean: {result.posterior.mu:.4f}')

    # Show credible interval if requested
    if show_ci:
        ci_lower = result.posterior.ci_lower
        ci_upper = result.posterior.ci_upper

        pdf_lower = beta_dist.pdf(ci_lower, result.posterior.alpha_fitted, result.posterior.beta_fitted)
        pdf_upper = beta_dist.pdf(ci_upper, result.posterior.alpha_fitted, result.posterior.beta_fitted)

        ax.plot([ci_lower, ci_lower], [0, pdf_lower], color=color, linestyle=':',
                linewidth=2, alpha=0.6)
        ax.plot([ci_upper, ci_upper], [0, pdf_upper], color=color, linestyle=':',
                linewidth=2, alpha=0.6)

        # Shade CI region
        x_ci = x[(x >= ci_lower) & (x <= ci_upper)]
        y_ci = beta_dist.pdf(x_ci, result.posterior.alpha_fitted, result.posterior.beta_fitted)
        ax.fill_between(x_ci, y_ci, color=color, alpha=0.3)

    # Labels and title
    ax.set_xlabel('θ (Success Rate)', fontsize=12)
    ax.set_ylabel('Posterior Density', fontsize=12)

    if title is None:
        title = (f'Flat Bayes Posterior: Beta({result.posterior.alpha_fitted:.1f}, {result.posterior.beta_fitted:.1f})\n'
                f'Mean: {result.posterior.mu:.4f}, '
                f'{int(ci_level*100)}% CI: [{result.posterior.ci_lower:.4f}, {result.posterior.ci_upper:.4f}]')
    ax.set_title(title, fontsize=13, fontweight='bold')

    # Set y-axis to start at 0
    ylim = ax.get_ylim()
    ax.set_ylim(0, ylim[1] * 1.05)

    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    if created_figure:
        plt.tight_layout()
    return fig


def plot_flat_bayes_prior_posterior(
    result: SingleThetaResult,
    figsize: tuple[float, float] = (10, 6),
    title: str | None = None,
    show_ci: bool = True,
    ci_level: float = 0.95,
    prior_color: str = 'gray',
    posterior_color: str = 'blue',
    xlim: tuple[float, float] | None = None,
    ax: plt.Axes | None = None,
) -> plt.Figure:
    """Plot prior and posterior distributions for Flat Bayes model on same axes.

    Creates a comparison visualization showing both the prior and posterior
    distributions of θ (pooled success rate) from Flat Bayes inference.

    Args:
        result: SingleThetaResult from single_theta_bayesian().
        figsize: Figure size as (width, height) tuple (default: (10, 6)).
                 Ignored if ax is provided.
        title: Optional custom title. If None, generates descriptive title.
        show_ci: If True, shows credible interval bounds for both distributions (default: True).
        ci_level: Credible interval level to display (default: 0.95).
        prior_color: Color for the prior curve (default: 'gray').
        posterior_color: Color for the posterior curve (default: 'blue').
        xlim: Optional (xmin, xmax) tuple for x-axis limits. If None, auto-determines
              to show both distributions.
        ax: Optional matplotlib Axes to plot into. If None, creates new figure.

    Returns:
        Matplotlib Figure object.

    Raises:
        ValueError: If result doesn't have fitted posterior parameters.

    Example:
        >>> import numpy as np
        >>> from proportions.core.models import BinomialData
        >>> from proportions.inference.single_theta import single_theta_bayesian
        >>> from proportions.visualization.posterior_plots import plot_flat_bayes_prior_posterior
        >>>
        >>> data = BinomialData(x=np.array([8, 7, 9]), n=np.array([10, 10, 10]))
        >>> result = single_theta_bayesian(data, alpha_prior=1.0, beta_prior=1.0)
        >>> fig = plot_flat_bayes_prior_posterior(result)
        >>> fig.savefig('flat_bayes_prior_posterior.png', dpi=150, bbox_inches='tight')
        >>> plt.show()
    """
    if result.posterior.alpha_fitted is None or result.posterior.beta_fitted is None:
        raise ValueError("Result must have fitted posterior parameters")

    # Determine x-axis range to show both distributions
    if xlim is None:
        # Use posterior credible interval with some padding
        ci_width = result.posterior.ci_upper - result.posterior.ci_lower
        xmin = max(0.0, result.posterior.ci_lower - 0.2 * ci_width)
        xmax = min(1.0, result.posterior.ci_upper + 0.2 * ci_width)
    else:
        xmin, xmax = xlim

    # Generate x values
    x = np.linspace(xmin, xmax, 1000)

    # Compute PDFs
    y_prior = beta_dist.pdf(x, result.prior_alpha, result.prior_beta)
    y_posterior = beta_dist.pdf(x, result.posterior.alpha_fitted, result.posterior.beta_fitted)

    # Create figure or use provided axes
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        created_figure = True
    else:
        fig = ax.get_figure()
        created_figure = False

    # Plot prior curve
    ax.plot(x, y_prior, color=prior_color, linewidth=2.5, label='Prior', alpha=0.8)
    ax.fill_between(x, y_prior, color=prior_color, alpha=0.15)

    # Plot posterior curve
    ax.plot(x, y_posterior, color=posterior_color, linewidth=2.5, label='Posterior', alpha=0.8)
    ax.fill_between(x, y_posterior, color=posterior_color, alpha=0.15)

    # Mark means
    mean_prior = result.prior_alpha / (result.prior_alpha + result.prior_beta)
    ax.axvline(mean_prior, color=prior_color, linestyle='--', linewidth=2,
               alpha=0.6, label=f'Prior mean: {mean_prior:.4f}')
    ax.axvline(result.posterior.mu, color=posterior_color, linestyle='--', linewidth=2,
               alpha=0.6, label=f'Posterior mean: {result.posterior.mu:.4f}')

    # Show credible intervals if requested
    if show_ci:
        # Prior CI
        alpha_lower = (1 - ci_level) / 2
        alpha_upper = 1 - alpha_lower
        from proportions.distributions.beta import beta_quantiles
        quantiles_prior = beta_quantiles([alpha_lower, alpha_upper], result.prior_alpha, result.prior_beta)
        prior_ci_lower = float(quantiles_prior[0])
        prior_ci_upper = float(quantiles_prior[1])

        pdf_prior_lower = beta_dist.pdf(prior_ci_lower, result.prior_alpha, result.prior_beta)
        pdf_prior_upper = beta_dist.pdf(prior_ci_upper, result.prior_alpha, result.prior_beta)

        ax.plot([prior_ci_lower, prior_ci_lower], [0, pdf_prior_lower],
                color=prior_color, linestyle=':', linewidth=1.5, alpha=0.5)
        ax.plot([prior_ci_upper, prior_ci_upper], [0, pdf_prior_upper],
                color=prior_color, linestyle=':', linewidth=1.5, alpha=0.5)

        # Posterior CI
        post_ci_lower = result.posterior.ci_lower
        post_ci_upper = result.posterior.ci_upper
        pdf_post_lower = beta_dist.pdf(post_ci_lower, result.posterior.alpha_fitted,
                                        result.posterior.beta_fitted)
        pdf_post_upper = beta_dist.pdf(post_ci_upper, result.posterior.alpha_fitted,
                                        result.posterior.beta_fitted)

        ax.plot([post_ci_lower, post_ci_lower], [0, pdf_post_lower],
                color=posterior_color, linestyle=':', linewidth=1.5, alpha=0.5)
        ax.plot([post_ci_upper, post_ci_upper], [0, pdf_post_upper],
                color=posterior_color, linestyle=':', linewidth=1.5, alpha=0.5)

    # Labels and title
    ax.set_xlabel('θ (Success Rate)', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)

    if title is None:
        title = (f'Flat Bayes: Prior vs Posterior\n'
                f'Prior: Beta({result.prior_alpha:.1f}, {result.prior_beta:.1f}) | '
                f'Posterior: Beta({result.posterior.alpha_fitted:.1f}, {result.posterior.beta_fitted:.1f})')
    ax.set_title(title, fontsize=13, fontweight='bold')

    # Set y-axis to start at 0
    ylim = ax.get_ylim()
    ax.set_ylim(0, ylim[1] * 1.05)

    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc='best')

    if created_figure:
        plt.tight_layout()
    return fig
