''' This module implements various probability distributions for uncertainty quantification.

    Classes
    -------
    Distribution(ABC)
        Abstract base class for probability distributions.
        
    TranslatedDistribution(Distribution)
        Class for translated and scaled distributions.
        
    NormalDistribution(Distribution)
        Class for normal (Gaussian) distribution.
        
    UniformDistribution(Distribution)
        Class for uniform distribution.
        
    LogNormalDistribution(Distribution)
        Class for log-normal distribution.
        
    BetaDistribution(Distribution)
        Class for beta distribution.

    ExponentialDistribution(Distribution)
        Class for exponential distribution.

    WignerSemicircleDistribution(Distribution)
        Class for Wigner semicircle distribution.
        
    Functions
    ---------
    unwrap_if_scalar(arr)
        Utility function to unwrap single-element arrays.'''

import numpy as np
from scipy.stats.qmc import Halton
from scipy.stats.qmc import LatinHypercube as LHS
from scipy.stats.qmc import Sobol
# from SALib.sample import saltelli
import scipy.special as sc
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

# Set random seed
np.random.seed(seed=1234)

def unwrap_if_scalar(arr):
    """ Return the item if the array has only one element, else return the array.

        Parameters
        ----------
        arr : array_like
            Input array.

        Returns
        -------
        output : scalar or array_like
            Unwrapped item if arr has one element, else arr itself."""
    
    output = arr.item() if arr.size == 1 else arr
    return output

class Distribution(ABC):
    ''' Abstract class for probability distributions.

        Methods
        -------
        moments()
            Return the moments of the distribution.
            
        logpdf(x)
            Return the log of the probability density function of the distribution, evaluated at x.
            
        sample(n, method='MC', **params)
            Return n samples from the distribution.
            
        translate(shift, scale)
            Return a translated and scaled version of the distribution.

        fix_moments(mean, var)
            Fix the distribution to have specified mean and variance.

        fix_bounds(min, max, q0=0, q1=1)
            Fix the distribution to have specified bounds.

        stdnor2base(x)
            Convert from standard normal space to distribution space.

        base2stdnor(y)
            Convert from distribution space to standard normal space.
            
        get_base_dist()
            Return the GPC base distribution.
            
        base2dist(y)
            Convert from base (germ) space to distribution space.
            
        dist2base(x)
            Convert from distribution space to base (germ) space.
            
        orth_polysys()
            Return the GPC polynomial system.

        get_bounds(delta=0.02)
            Return the bounds of the distribution.'''
            
    @abstractmethod
    def pdf(self, x):
        ''' Abstract method to return the probability density function of the distribution, evaluated at x.
            Subclasses must implement this method.'''
        
        pass

    @abstractmethod
    def cdf(self, x):
        ''' Abstract method to return the cumulative distribution function of the distribution, evaluated at x.
            Subclasses must implement this method.'''
        
        pass

    @abstractmethod
    def invcdf(self, y):
        ''' Abstract method to return the inverse cumulative distribution function of the distribution, evaluated at y.
            Subclasses must implement this method.'''
        
        pass

    @abstractmethod
    def mean(self):
        ''' Abstract method to return the mean of the distribution.
            Subclasses must implement this method.'''
        
        pass

    @abstractmethod
    def var(self):
        ''' Abstract method to return the variance of the distribution.
            Subclasses must implement this method.'''
        
        pass

    @abstractmethod
    def skew(self):
        ''' Abstract method to return the skewness of the distribution.
            Subclasses must implement this method.'''
        
        pass

    @abstractmethod
    def kurt(self):
        ''' Abstract method to return the kurtosis of the distribution.
            Subclasses must implement this method.'''
        
        pass

    def moments(self):
        ''' Return the moments of the distribution.
        
            Returns
            -------
            moments : list
                List containing the mean, variance, skewness, and kurtosis of the distribution.'''
        
        moments = [self.mean(), self.var(), self.skew(), self.kurt()]
        return moments

    def logpdf(self, x):
        ''' Return the log of the probability density function of the distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the logpdf.
                
            Returns
            -------
            y : array_like
                Log probability density function values at x.'''
        
        pdf = self.pdf(x)
        y = np.log(pdf)
        return y

    def sample(self, n, method="MC", **params):
        if method == "MC":
            yi = np.random.rand(n)
        elif method == "QMC_Halton":
            sampler = Halton(d=1)
            yi = sampler.random(n)
        elif method == "QMC_LHS":
            sampler = LHS(d=1)
            yi = sampler.random(n)
        elif method == "QMC_Sobol":
            sampler = Sobol(d=1)
            yi = sampler.random(n)
        # elif method == 'Sobol_saltelli': # It's not


    def translate(self, shift, scale):
        ''' Return a translated and scaled version of the distribution.
            
            Parameters
            ----------
            shift : float
                Shift to apply to the distribution.

            scale : float
                Scale to apply to the distribution.
                
            Returns
            -------
            tdist : TranslatedDistribution
                Translated and scaled distribution.'''
        
        tdist = TranslatedDistribution(self, shift, scale)
        return tdist

    def get_shift(self):
        """ Return the shift of the distribution.

            Returns
            -------
            shift : float
                Shift of the distribution."""
        
        shift = self-shift
        return self.shift

    def get_scale(self):
        """ Return the scale of the distribution.

            Returns
            -------
            scale : float
                Scale of the distribution."""
        
        scale = self.scale
        return scale

    def fix_moments(self, mean, var):
        ''' Fix the distribution to have specified mean and variance.
        
            Parameters
            ----------
            mean : float
                Desired mean of the distribution.
                
            var : float
                Desired variance of the distribution.
                
            Returns
            -------
            new_dist : TranslatedDistribution
                Translated and scaled distribution with specified moments.'''
        
        old_mean, old_var = self.mean(), self.var()
        self.shift = mean - old_mean
        self.scale = np.sqrt(var / old_var)
        new_dist = self.translate(self.shift, self.scale)
        return new_dist

    def fix_bounds(self, min, max, q0=0, q1=1):
        ''' Fix the distribution to have specified bounds.
        
            Parameters
            ----------
            min : float
                Desired minimum of the distribution.
                
            max : float
                Desired maximum of the distribution.
                
            q0 : float, optional
                Quantile corresponding to the minimum (default is 0).
                
            q1 : float, optional
                Quantile corresponding to the maximum (default is 1).
                
            Returns
            -------
            new_dist : TranslatedDistribution
                Translated and scaled distribution with specified bounds.'''
        
        if not (0 <= q0 <= 1):
            raise ValueError(f"q0 must be between 0 and 1, got {q0}")
        if not (q0 <= q1 <= 1):
            raise ValueError(f"q1 must be between q0 and 1, got {q1}")

        old_min = self.invcdf(q0)
        old_max = self.invcdf(q1)

        if not np.isfinite(old_min):
            # raise ValueError(f"Lower quantile (q0) gives infinity (unbounded distribution?)")
            print(
                f"Lower quantile (q0) gives infinity (unbounded distribution?). Using new q0=0.02"
            )
            old_min, _ = self.get_bounds()
        if not np.isfinite(old_max):
            # raise ValueError(f"Upper quantile (q1) gives infinity (unbounded distribution?)")
            print(
                f"Upper quantile (q1) gives infinity (unbounded distribution?). Using new q1=0.98"
            )
            _, old_max = self.get_bounds()

        center = self.mean()
        self.scale = (max - min) / (old_max - old_min)
        self.shift = min - ((old_min - center) * self.scale + center)
        new_dist = self.translate(self.shift, self.scale)
        return new_dist

    def stdnor2base(self, x):
        ''' Convert from standard normal space to distribution space.
        
            Parameters
            ----------
            x : array_like
                Points in standard normal space.
                
            Returns
            -------
            y : array_like
                Points in distribution space.'''
        
        y = self.invcdf(NormalDistribution().cdf(x))
        return y

    def base2stdnor(self, y):
        ''' Convert from distribution space to standard normal space.
        
            Parameters
            ----------
            y : array_like
                Points in distribution space.
                
            Returns
            -------
            x : array_like
                Points in standard normal space.'''
        
        x = NormalDistribution().invcdf(self.cdf(y))
        return x

    def get_base_dist(self):
        ''' Return the GPC base distribution.
            
            Returns
            -------
            dist_germ : Distribution object
                GPC base distribution.'''
        
        dist_germ = NormalDistribution(0, 1)
        return dist_germ

    def base2dist(self, y):
        ''' Convert from base (germ) space to distribution space.
            
            Parameters
            ----------
            y : array_like
                Points in base (germ) space.
                
            Returns
            -------
            x : array_like
                Points in distribution space.'''
        
        x = self.invcdf(self.get_base_dist().cdf(y))
        return x

    def dist2base(self, x):
        ''' Convert from distribution space to base (germ) space.
            
            Parameters
            ----------
            x : array_like
                Points in distribution space.
                
            Returns
            -------
            y : array_like
                Points in base (germ) space.'''
        
        y = self.get_base_dist().invcdf(self.cdf(x))
        return y

    def orth_polysys(self):
        """ Return the GPC polynomial system.

            Raises
            ------
            Exception
                If no polynomial system is defined for this distribution."""
        
        raise Exception(f"No polynomial system for this distribution ({self})")

    def get_bounds(self, delta=0.02):
        ''' Return the bounds of the distribution.
            
            Parameters
            ----------
            delta : float, optional
                Small probability to define the bounds (default is 0.02).
            
            Returns
            -------
            bounds : array_like
                Bounds of the distribution as [lower_bound, upper_bound].'''
        
        bounds = self.invcdf(np.array([delta, 1 - delta]))
        return bounds

class TranslatedDistribution(Distribution):
    ''' Distribution obtained by applying an affine 
        transformation to another base distribution.
        
        Attributes
        ----------
        dist: Distribution
            Underlying base distribution.

        shift: float
            Additive translation applied after scaling.

        scale: float
            Scaling factor applied to centered values.

        center: float
            Center point for scaling transformation.
            
        Methods
        -------
        __init__(dist, shift, scale, center=None)
            Initialize the translated distribution.
            
        __repr__()
            Return a string representation of the translated distribution.
            
        get_dist_type()
            Return the type identifier of this distribution.
            
        get_dist_params()
            Return the parameter tuple of the translated distribution.
            
        translate_points(x, forward)
            Apply the forward or backward affine transformation to points.
            
        pdf(x)
            Evaluate the probability density function.

        cdf(x)
            Evaluate the cumulative distribution function.

        invcdf(y)
            Evaluate the inverse cumulative distribution function.

        mean()
            Return the mean of the translated distribution.

        var()
            Return the variance of the translated distribution.

        skew()
            Return the skewness of the translated distribution.

        kurt()
            Return the kurtosis of the translated distribution.

        sample(n)
            Draw random samples from the translated distribution.

        moments()
            Return the first four moments of the translated distribution.

        get_base_dist()
            Return the underlying base distribution.

        translate_points_forward(x, shift, scale, center)
            Apply the forward affine transformation.

        translate_points_backwards(x, shift, scale, center)
            Apply the inverse affine transformation.

        translate_moments(m, shift, scale, center)
            Transform the moments of a distribution under an affine transformation.'''
    
    def __init__(self, dist, shift, scale, center=None):
        ''' Initialize the translated distribution.
        
            Parameters
            ----------
            dist: Distribution
                Underlying base distribution
                
            shift: float
                Additive translation applied after scaling.
            
            scale: float
                Scaling factor applied to centered values.
            
            center: float
                Center point for scaling transformation.'''
        
        self.dist = dist
        self.shift = shift
        self.scale = scale
        if center is None:
            self.center = self.dist.moments()[0]
        else:
            self.center = center

    def __repr__(self):
        ''' Returns the string representation of the TranslatedDistribution object.
        
            Returns
            -------
            repr_string : str
                String representation of the TranslatedDistribution object.'''

        repr_string = "Translated({}, {}, {}, {})".format(
            self.dist, self.shift, self.scale, self.center
        )
        return repr_string
    
    def get_dist_type(self):
        """ Return the type identifier of this distribution.

        Returns
        -------
        str
            Always returns ``'translated'``."""
        return "translated"
    
    def get_dist_params(self):
        """ Return the parameter tuple of the translated distribution.

            Returns
            -------
            parameters: tuple
                Parameters of the base distribution followed by
                ``(shift, scale, center)``."""

        parameters = self.dist.get_dist_params() + (self.shift, self.scale, self.center)
        return parameters

    def translate_points(self, x, forward):
        """ Apply the forward or backward affine transformation to points.

            Parameters
            ----------
            x : array_like
                Input values to transform.

            forward : bool
                If True, apply the forward transformation (base → translated).
                If False, apply the backward transformation (translated → base).

            Returns
            -------
            y: array_like
                Transformed points."""

        if forward:
            y = TranslatedDistribution.translate_points_forward(
                x, self.shift, self.scale, self.center
            )
        else:
            y = TranslatedDistribution.translate_points_backwards(
                x, self.shift, self.scale, self.center
            )
        return y

    def pdf(self, x):
        """ Evaluate the probability density function.

            Parameters
            ----------
            x: array_like
                Points at which to evaluate the PDF of the translated distribution.

            Returns
            -------
            y: array_like
                PDF values."""

        x = self.translate_points(x, False)
        y = self.dist.pdf(x) / self.scale
        return y

    def cdf(self, x):
        """ Evaluate the cumulative distribution function.

            Parameters
            ----------
            x: array_like
                Points at which to evaluate the CDF of the translated distribution.

            Returns
            -------
            y: array_like
                CDF values."""

        x = self.translate_points(x, False)
        y = self.dist.cdf(x) / 1
        return y

    def invcdf(self, y):
        """ Evaluate the inverse cumulative distribution function.

            Parameters
            ----------
            y: array_like
                CDF values for which to compute the quantiles.

            Returns
            -------
            x: array_like
                Quantile values after affine transformation."""

        x = self.dist.invcdf(y)
        x = self.translate_points(x, True)
        return x / 1 # TODO ????

    def mean(self):
        """ Return the mean of the translated distribution.

            Returns
            -------
            mean: float
                The translated mean."""

        moments = self.dist.moments()
        moments = TranslatedDistribution.translate_moments(
            moments, self.shift, self.scale, self.center
        )
        mean = moments[0]
        return mean

    def var(self):
        """ Return the variance of the translated distribution.

            Returns
            -------
            var : float
                The translated variance."""

        moments = self.dist.moments()
        moments = TranslatedDistribution.translate_moments(
            moments, self.shift, self.scale, self.center
        )
        var = moments[1]
        return var

    def skew(self):
        """ Return the skewness of the translated distribution.

            Returns
            -------
            skew : float
                Skewness of the base distribution."""

        moments = self.dist.moments()
        moments = TranslatedDistribution.translate_moments(
            moments, self.shift, self.scale, self.center
        )
        skew = moments[2]
        return skew

    def kurt(self):
        """ Return the kurtosis of the translated distribution.

            Returns
            -------
            kurt : float
                Kurtosis of the base distribution."""

        moments = self.dist.moments()
        moments = TranslatedDistribution.translate_moments(
            moments, self.shift, self.scale, self.center
        )
        kurt = moments[3]
        return kurt

    def sample(self, n):
        """ Draw random samples from the translated distribution.

            Parameters
            ----------
            n : int
                Number of samples.

            Returns
            -------
            xi : ndarray
                Array of transformed samples."""

        xi = self.dist.sample(n)
        xi = self.translate_points(xi, True)
        return xi

    def moments(self):
        """ Return the first four moments of the translated distribution.

            Returns
            -------
            moments : list
                List of moments ``[mean, variance, skewness, kurtosis]``."""

        moments = self.dist.moments()
        moments = TranslatedDistribution.translate_moments(
            moments, self.shift, self.scale, self.center
        )
        return moments

    def get_base_dist(self):
        """ Return the underlying base distribution.

            Returns
            -------
            dist_germ : Distribution
                The untransformed base distribution."""

        dist_germ = self.dist.get_base_dist()
        return dist_germ

    @staticmethod
    def translate_points_forward(x, shift, scale, center):
        """ Apply the forward affine transformation:

            y = (x - center) * scale + center + shift

            Parameters
            ----------
            x : array_like
                Values from the base distribution.

            shift : float
                Translation offset.

            scale : float
                Scaling factor.

            center : float
                Center of scaling.

            Returns
            -------
            y : array_like
                Transformed points."""

        y = (x - center) * scale + center + shift
        return y

    @staticmethod
    def translate_points_backwards(x, shift, scale, center):
        """ Apply the inverse affine transformation:

            x = (y - shift - center) / scale + center

            Parameters
            ----------
            x : array_like
                Values from the translated distribution.

            shift : float
                Translation offset.

            scale : float
                Scaling factor.

            center : float
                Center of scaling.

            Returns
            -------
            y: array_like
                Points mapped back to the base distribution domain."""

        y = (x - shift - center) / scale + center
        return y

    @staticmethod
    def translate_moments(m, shift, scale, center):
        """ Transform the moments of a distribution under an affine transformation.

            Parameters
            ----------
            m : list
                Moments of the base distribution in the form
                ``[mean, variance, skewness, kurtosis]``.

            shift : float
                Translation offset.

            scale : float
                Scaling factor.

            center : float
                Center of scaling.

            Returns
            -------
            m: list
                Transformed moments."""
        
        if len(m) >= 1:
            m[0] = TranslatedDistribution.translate_points_forward(
                m[0], shift, scale, center
            )
        if len(m) >= 2:
            m[1] = m[1] * scale**2
        # Higher (standardized) moments like skewness or kurtosis are
        # not affected by neither shift nor scale
        return m

class NormalDistribution(Distribution):
    ''' Class for normal (Gaussian) distribution.
    
        Attributes
        ----------
        mu : float
            Mean of the normal distribution.
            
        sigma : float
            Standard deviation of the normal distribution.
            
        Methods
        -------
        __init__(mu=0, sigma=1)
            Initialize the normal distribution with mean mu and standard deviation sigma.
            
        __repr__()
            Returns the string representation of the NormalDistribution object.
            
        pdf(x)
            Return the probability density function of the normal distribution, evaluated at x.
            
        logpdf(x)
            Return the log of the probability density function of the normal distribution, evaluated at x.
            
        cdf(x)
            Return the cumulative distribution function of the normal distribution, evaluated at x.
            
        invcdf(y)
            Return the inverse cumulative distribution function of the normal distribution, evaluated at y.
            
        sample(n, method='MC', **params)
            Return n samples from the normal distribution.
            
        mean()
            Return the mean of the normal distribution.
            
        var()
            Return the variance of the normal distribution.
            
        skew()
            Return the skewness of the normal distribution.
            
        kurt()
            Return the kurtosis of the normal distribution.
            
        get_base_dist()
            Return the GPC base distribution.
            
        translate(shift, scale)
            Return a translated and scaled version of the normal distribution.
            
        base2dist(y)
            Convert from base (germ) space to normal distribution space.
            
        dist2base(x)
            Convert from normal distribution space to base (germ) space.
            
        orth_polysys()
            Return the GPC polynomial system for the normal distribution.
            
        orth_polysys_syschar(normalized)
            Return the GPC polynomial system characteristic string for the normal distribution.'''
    
    def __init__(self, mu=0, sigma=1):
        ''' Initialize the normal distribution with mean mu and standard deviation sigma.
        
            Parameters
            ----------
            mu : float, default = 0
                Mean of the normal distribution.

            sigma : float, default = 1
                Standard deviation of the normal distribution.'''
        
        assert sigma > 0
        self.mu = mu
        self.sigma = sigma

    def __repr__(self):
        ''' Returns the string representation of the NormalDistribution object.
        
            Returns
            -------
            repr_string : str
                String representation of the NormalDistribution object.'''
        
        repr_string = "N({}, {:.2f})".format(self.mu, self.sigma**2)
        return repr_string

    def get_dist_type(self):
        """ Return the type identifier of this distribution.

            Returns
            -------
            str
                Always returns ``'translated'``."""

        return "norm"
    
    def get_dist_params(self):
        return self.mu, self.sigma

    def pdf(self, x):
        ''' Return the probability density function of the normal distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the pdf.
                
            Returns
            -------
            y : array_like
                Probability density function values at x.'''
        
        mu = self.mu
        sigma = self.sigma
        root = (x - mu) / sigma
        y_exp = root**2
        y_exp = -1 / 2 * y_exp
        y = np.exp(y_exp) / (sigma * np.sqrt(2 * np.pi))
        return y

    def logpdf(self, x):
        ''' Return the log of the probability density function of the normal distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the logpdf.
                
            Returns
            -------
            y : array_like
                Log probability density function values at x.'''
        
        mu = self.mu
        sigma = self.sigma
        root = (x - mu) / sigma
        y = -1 / 2 * (root**2) - np.log(sigma * np.sqrt(2 * np.pi))
        return y

    def cdf(self, x):
        ''' Return the cumulative distribution function of the normal distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the cdf.
                
            Returns
            -------
            y : array_like
                Cumulative distribution function values at x.'''
        
        mu = self.mu
        sigma = self.sigma
        y = 1 / 2 * (1 + sc.erf((x - mu) / (sigma * np.sqrt(2))))
        return y

    def invcdf(self, y):
        ''' Return the inverse cumulative distribution function of the normal distribution, evaluated at y.
        
            Parameters
            ----------
            y : array_like
                Points at which to evaluate the invcdf.
                
            Returns
            -------
            x : array_like
                Inverse cumulative distribution function values at y.'''
        
        mu = self.mu
        sigma = self.sigma
        y = np.array(y)
        x = np.full(y.shape, np.nan)  # original
        ind = (y >= 0) & (y <= 1)
        x[ind] = mu + sigma * np.sqrt(2) * sc.erfinv(2 * y[ind] - 1)
        x = x / 1
        return x

    def sample(self, n, method="MC", **params): # ??? TODO
        ''' Return n samples from the normal distribution.

            Parameters
            ----------
            n : int
                Number of samples to generate.
                
            method : str, optional
                Sampling method to use (default is 'MC' for Monte Carlo).
            
            **params : dict
                Additional parameters for the sampling method.
                
            Returns
            -------
            samples : array_like
                Generated samples from the normal distribution.'''
        
        if method == "MC":
            xi = np.random.randn(n)
        else:
            xi = UniformDistribution().sample(n, method, **params)
        samples = (xi * self.sigma) + self.mu
        return samples

    def mean(self):
        """ Return the mean of the normal distribution.

            Returns
            -------
            mean : float
                Mean of the normal distribution."""
        
        mean = self.mu
        return mean

    def var(self):
        """ Return the variance of the normal distribution.

            Returns
            -------
            var : float
                Variance of the normal distribution."""

        var = self.sigma * self.sigma
        return var

    def skew(self):
        """ Return the skewness of the normal distribution.

            Returns
            -------
            skew : float
                Skewness of the normal distribution."""
        
        skew = 0
        return skew

    def kurt(self):
        """ Return the kurtosis of the normal distribution.

            Returns
            -------
            kurt : float
                Kurtosis of the normal distribution."""

        kurt = 0
        return kurt

    def get_base_dist(self):
        ''' Return the GPC base distribution.

            Returns
            -------
            dist_germ : Distribution object
                GPC base distribution.'''
        
        dist_germ = NormalDistribution(0, 1)
        return dist_germ

    def translate(self, shift, scale):
        ''' Return a translated and scaled version of the normal distribution.
        
            Parameters
            ----------
            shift : float
                Shift to apply to the distribution.

            scale : float
                Scale to apply to the distribution.
            
            Returns
            -------
            new_dist : NormalDistribution
                Translated and scaled normal distribution.'''
        
        new_dist = NormalDistribution(self.mu + shift, self.sigma * scale)
        return new_dist

    def base2dist(self, y):
        """ Convert from base (germ) space to normal distribution space.

            Parameters
            ----------
            y : array_like
                Points in base (germ) space.

            Returns
            -------
            x : array_like
                Points in normal distribution space."""

        x = self.mu + y * self.sigma
        return x
    
    def dist2base(self, x):
        """ Return from normal distribution space to base (germ) space.

            Parameters
            ----------
            x : array_like
                Points in normal distribution space.

            Returns
            -------
            y : array_like
                Points in base (germ) space."""

        y = (x - self.mu) / self.sigma
        return y

    def orth_polysys(self):
        ''' Return the GPC polynomial system for the normal distribution.
        
            Returns
            -------
            polysys : PolynomialSystem object
                GPC polynomial system for the normal distribution.'''
        
        from polysys import HermitePolynomials

        if self.mu == 0 and self.sigma == 1:
            polysys = HermitePolynomials()
        else:
            polysys = Distribution.orth_polysys(self)
        return polysys

    def orth_polysys_syschar(self, normalized):
        ''' Return the GPC polynomial system characteristic string for the normal distribution.
        
            Parameters
            ----------
            normalized : bool
                Flag indicating whether to return the normalized polynomial system characteristic string.
                
            Returns
            -------
            polysys_char : str
                GPC polynomial system characteristic string for the normal distribution.'''
        
        if self.mu == 0 and self.sigma == 1:
            if normalized:
                polysys_char = "h"
            else:
                polysys_char = "H"
        else:
            polysys_char = []
        return polysys_char

class UniformDistribution(Distribution):
    ''' Class for uniform distribution.
    
        Attributes
        ----------
        a : float
            Lower bound of the uniform distribution.
            
        b : float
            Upper bound of the uniform distribution.
            
        Methods
        -------
        __init__(a=0, b=1)
            Initialize the uniform distribution with bounds a and b.
            
        __repr__()
            Returns the string representation of the UniformDistribution object.

        get_dist_type()
            Return the type of the distribution.

        get_dist_params()
            Return the parameters of the distribution.
            
        pdf(x)
            Return the probability density function of the uniform distribution, evaluated at x.
            
        logpdf(x)
            Return the log of the probability density function of the uniform distribution, evaluated at x.
            
        cdf(x)
            Return the cumulative distribution function of the uniform distribution, evaluated at x.
            
        invcdf(y)
            Return the inverse cumulative distribution function of the uniform distribution, evaluated at y.
            
        mean()
            Return the mean of the uniform distribution.
        
        var()
            Return the variance of the uniform distribution.
            
        skew()
            Return the skewness of the uniform distribution.
            
        kurt()
            Return the kurtosis of the uniform distribution.
            
        translate(shift, scale)
            Return a translated and scaled version of the uniform distribution.
            
        get_base_dist()
            Return the GPC base distribution.
            
        base2dist(y)
            Convert from base (germ) space to uniform distribution space.
            
        dist2base(x)
            Convert from uniform distribution space to base (germ) space.
            
        orth_polysys()
            Return the GPC polynomial system for the uniform distribution.
            
        orth_polysys_syschar(normalized)
            Return the GPC polynomial system characteristic string for the uniform distribution.
            
        get_bounds(delta=0)
            Return the bounds of the uniform distribution.'''
    
    def __init__(self, a=0, b=1):
        ''' Initialize the uniform distribution with bounds a and b.
        
            Parameters
            ----------
            a : float, default = 0
                Lower bound of the uniform distribution.
                
            b : float, default = 1
                Upper bound of the uniform distribution.'''
        assert b > a
        self.a = a
        self.b = b

    def __repr__(self):
        ''' Returns the string representation of the UniformDistribution object.
        
            Returns
            -------
            repr_string : str
                String representation of the UniformDistribution object.'''
        
        repr_string = "U({}, {})".format(self.a, self.b)
        return repr_string

    def get_dist_type(self):
        ''' Return the type of the distribution.
        
            Returns
            -------
            dist_type : str
                Type of the distribution.'''
        
        dist_type = "unif"
        return dist_type
    
    def get_dist_params(self):
        ''' Return the parameters of the distribution.
        
            Returns
            -------
            params : tuple
                Parameters of the distribution (a, b).'''
        
        params = [self.a, self.b]
        return params

    def pdf(self, x):
        ''' Return the probability density function of the uniform distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the pdf.
                
            Returns
            -------
            y : array_like
                Probability density function values at x.'''
        
        a = self.a
        b = self.b
        y = 1 / (b - a) * np.ones(np.size(x))
        y[x < a] = 0
        y[x > b] = 0
        y = unwrap_if_scalar(y)
        return y

    def logpdf(self, x):
        ''' Return the log of the probability density function of the uniform distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the logpdf.
                
            Returns
            -------
            y : array_like
                Log probability density function values at x.'''
        
        a = self.a
        b = self.b
        pdf = self.pdf(x)
        pdf = np.array(pdf)  # OR
        pdf = pdf.reshape(x.shape)
        y = np.zeros(x.shape)
        for i in range(len(x)):
            if pdf[i] == 0:
                y[i] = -np.Inf
            else:
                y[i] = np.log(pdf[i])
        return y

    def cdf(self, x):
        ''' Return the cumulative distribution function of the uniform distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the cdf.
                
            Returns
            -------
            y : array_like
                Cumulative distribution function values at x.'''
        
        a = self.a
        b = self.b
        y = (x - a) / (b - a)
        y = np.clip(y, 0, 1)
        return y

    def invcdf(self, y):
        ''' Return the inverse cumulative distribution function of the uniform distribution, evaluated at y.
            
            Parameters
            ----------
            y : array_like
                Points at which to evaluate the invcdf.
                
            Returns
            -------
            x : array_like
                Inverse cumulative distribution function values at y.'''
        
        a = self.a
        b = self.b
        y = np.array(y)
        x = np.full(np.size(y), np.nan)
        ind = (y >= 0) & (y <= 1)
        x[ind] = a + (b - a) * y[ind]
        x = unwrap_if_scalar(x)
        return x

    def mean(self):
        ''' Return the mean of the uniform distribution.
        
            Returns
            -------
            mean : float
                Mean of the uniform distribution.'''
        
        mean = 0.5 * (self.a + self.b)
        return mean

    def var(self):
        ''' Return the variance of the uniform distribution.
            
            Returns
            -------
            var : float
                Variance of the uniform distribution.'''
        
        var = (self.b - self.a) ** 2 / 12
        return var

    def skew(self):
        ''' Return the skewness of the uniform distribution.

            Returns
            -------
            skew : float
                Skewness of the uniform distribution.'''
        skew = 0
        return skew

    def kurt(self):
        ''' Return the kurtosis of the uniform distribution.

            Returns
            -------
            kurt : float
                Kurtosis of the uniform distribution.'''
        
        kurt = -6 / 5
        return kurt

    def translate(self, shift, scale):
        """ Return a translated and scaled version of the uniform distribution.

            Parameters
            ----------
            shift : float
                Shift to apply to the distribution.
            scale : float
                Scale to apply to the distribution.

            Returns
            -------
            new_dist : UniformDistribution
                Translated and scaled uniform distribution."""
        
        m = (self.a + self.b) / 2
        v = scale * (self.b - self.a) / 2

        a = m + shift - v
        b = m + shift + v
        new_dist = UniformDistribution(a, b)
        return new_dist

    def get_base_dist(self):
        """ Return the GPC base distribution.

            Returns
            -------
            dist_germ : Distribution object
                GPC base distribution."""
        
        dist_germ = UniformDistribution(-1, 1)
        return dist_germ

    def base2dist(self, y):
        """ Convert from base (germ) space to uniform distribution space.

            Parameters
            ----------
            y : array_like
                Points in base (germ) space.

            Returns
            -------
            x : array_like
                Points in distribution space."""
        
        x = self.mean() + y * (self.b - self.a) / 2
        return x

    def dist2base(self, x):
        """ Convert from uniform distribution space to base (germ) space.

            Parameters
            ----------
            x : array_like
                Points in distribution space.

            Returns
            -------
            y : array_like
                Points in base (germ) space."""
        
        y = (x - self.mean()) * 2 / (self.b - self.a)
        return y

    def orth_polysys(self):
        """ Return the GPC polynomial system for the uniform distribution.

            Returns
            -------
            polysys : PolynomialSystem object
                GPC polynomial system for the uniform distribution."""
        
        from polysys import LegendrePolynomials

        if self.a == -1 and self.b == 1:
            polysys = LegendrePolynomials()
        else:
            polysys = Distribution.orth_polysys(self)
        return polysys

    def orth_polysys_syschar(self, normalized):
        """ Return the GPC polynomial system characteristic string for the uniform distribution.

            Parameters
            ----------
            normalized : bool
                Flag indicating whether to return the normalized polynomial system characteristic string.

            Returns
            -------
            polysys_char : str
                GPC polynomial system characteristic string for the uniform distribution."""
        
        if self.a == -1 and self.b == 1:
            if normalized:
                polysys_char = "p"
            else:
                polysys_char = "P"
        else:
            polysys_char = []
        return polysys_char

    def get_bounds(self, delta=0):
        """ Return the bounds of the uniform distribution.

            Parameters
            ----------
            delta : int, optional
                Expansion factor for the bounds (default is 0).

            Returns
            -------
            bounds : numpy.ndarray
                Array containing the lower and upper bounds of the uniform distribution."""
        
        a = self.a
        b = self.b

        ab = b - a
        bounds = np.array([a - ab * delta, b + ab * delta])
        return bounds

class LogNormalDistribution(Distribution):
    ''' Class for log-normal distribution.
    
        Attributes
        ----------
        mu : float
            Mean of the underlying normal distribution.
            
        sigma : float
            Standard deviation of the underlying normal distribution.
            
        Methods
        -------
        __init__(mu=0, sigma=1)
            Initialize the log-normal distribution with parameters mu and sigma.
            
        __repr__()
            Returns the string representation of the LogNormalDistribution object.
            
        get_dist_type()
            Return the type of the distribution.
            
        get_dist_params()
            Return the parameters of the distribution.
            
        pdf(x)
            Return the probability density function of the log-normal distribution, evaluated at x.
            
        logpdf(x)
            Return the log of the probability density function of the log-normal distribution, evaluated at x.
            
        cdf(x)
            Return the cumulative distribution function of the log-normal distribution, evaluated at x.
            
        invcdf(y)
            Return the inverse cumulative distribution function of the log-normal distribution, evaluated at y.
            
        sample(n, method='MC', **params)
            Return n samples from the log-normal distribution.
            
        mean()
            Return the mean of the log-normal distribution.
            
        var()
            Return the variance of the log-normal distribution.
            
        skew()
            Return the skewness of the log-normal distribution.
            
        kurt()
            Return the kurtosis of the log-normal distribution.
            
        get_base_dist()
            Return the GPC base distribution.
            
        base2dist(y)
            Convert from base (germ) space to log-normal distribution space.
            
        dist2base(x)
            Convert from log-normal distribution space to base (germ) space.
            
        stdnor2base(y)
            Convert from standard normal space to log-normal distribution space.
            
        base2stdnor(x)
            Convert from log-normal distribution space to standard normal space.
            
        orth_polysys()
            Return the GPC polynomial system for the log-normal distribution.
            
        orth_polysys_syschar(normalized)
            Return the GPC polynomial system characteristic string for the log-normal distribution.'''
    
    def __init__(self, mu=0, sigma=1):
        ''' Initialize the log-normal distribution with parameters mu and sigma.
        
            Parameters
            ----------
            mu : float, default = 0
                Mean of the underlying normal distribution.
                
            sigma : float, default = 1
                Standard deviation of the underlying normal distribution.'''
        
        assert sigma > 0
        self.mu = mu
        self.sigma = sigma

    def __repr__(self):
        ''' Returns the string representation of the LogNormalDistribution object.
        
            Returns
            -------
            repr_string : str
                String representation of the LogNormalDistribution object.'''
        
        repr_string = "lnN({}, {})".format(self.mu, self.sigma**2)
        return repr_string
    
    def get_dist_type(self):
        """ Return the type of the distribution.

            Returns
            -------
            type_string : str
                Type of the distribution."""

        type_string = "lognorm"
        return type_string
    
    def get_dist_params(self):
        """ Return the parameters of the distribution.

            Returns
            -------
            params : tuple
                Parameters of the distribution (mu, sigma)."""
        
        params = (self.mu, self.sigma)
        return params

    def pdf(self, x):
        ''' Return the probability density function of the log-normal distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the pdf.
                
            Returns
            -------
            y : array_like
                Probability density function values at x.'''
        
        x = np.array(x)
        y = np.zeros(x.shape)
        ind = x > 0
        mu = self.mu
        sigma = self.sigma
        root = (np.log(x[ind]) - mu) / sigma
        y_exp = root**2
        y_exp = -1 / 2 * y_exp
        y[ind] = np.exp(y_exp) / (x[ind] * sigma * np.sqrt(2 * np.pi))
        y = unwrap_if_scalar(y)
        return y

    def logpdf(self, x):
        ''' Return the log of the probability density function of the log-normal distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the logpdf.
                
            Returns
            -------
            y : array_like
                Log probability density function values at x.'''
        
        y = np.zeros(x.shape)
        ind = x > 0
        mu = self.mu
        sigma = self.sigma
        root = (np.log(x[ind]) - mu) / sigma
        y = -1 / 2 * (root**2) - x[ind] * sigma * np.sqrt(2 * np.pi)
        return y

    def cdf(self, x):
        ''' Return the cumulative distribution function of the log-normal distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the cdf.
                
            Returns
            -------
            y : array_like
                Cumulative distribution function values at x.'''
        
        x = np.array(x)
        y = np.zeros(x.shape)
        ind = x > 0
        mu = self.mu
        sigma = self.sigma
        y[ind] = 1 / 2 * (1 + sc.erf((np.log(x[ind]) - mu) / (sigma * np.sqrt(2))))
        y = unwrap_if_scalar(y)
        return y

    def invcdf(self, y):
        ''' Return the inverse cumulative distribution function of the log-normal distribution, evaluated at y.
        
            Parameters
            ----------
            y : array_like
                Points at which to evaluate the invcdf.
                
            Returns
            -------
            x : array_like
                Inverse cumulative distribution function values at y.'''
        
        y = np.array(y)
        x = np.full(y.shape, np.nan)
        ind = (y >= 0) & (y <= 1)
        mu = self.mu
        sigma = self.sigma
        x[ind] = np.exp(mu + sigma * np.sqrt(2) * sc.erfinv(2 * y[ind] - 1))
        return x

    def sample(self, n, method="MC", **params):
        ''' Return n samples from the log-normal distribution.
        
            Parameters
            ----------
            n : int
                Number of samples to generate.
                
            method : str, optional
                Sampling method to use (default is 'MC' for Monte Carlo).
                
            **params : dict
                Additional parameters for the sampling method.
                
            Returns
            -------
            samples : array_like
                Generated samples from the log-normal distribution.'''
        
        if method == "MC":
            xi = np.random.randn(n)
        else:
            xi = UniformDistribution().sample(n, method, **params)
        samples = np.exp((xi * self.sigma) + self.mu)
        return samples

    def mean(self):
        ''' Return the mean of the log-normal distribution.
        
            Returns
            -------
            mean : float
                Mean of the log-normal distribution.'''
        
        mean = np.exp(self.mu + (self.sigma**2) / 2)
        return mean

    def var(self):
        ''' Return the variance of the log-normal distribution.
        
            Returns
            -------
            var : float
                Variance of the log-normal distribution.'''
        
        var = (np.exp(self.sigma**2) - 1) * (np.exp(2 * self.mu + self.sigma**2))
        return var

    def skew(self):
        ''' Return the skewness of the log-normal distribution.
        
            Returns
            -------
            skew : float
                Skewness of the log-normal distribution.'''
        
        skew = (np.exp(self.sigma**2) + 2) * (np.sqrt(np.exp(self.sigma**2) - 1))
        return skew

    def kurt(self):
        ''' Return the kurtosis of the log-normal distribution.
        
            Returns
            -------
            kurt : float
                Kurtosis of the log-normal distribution.'''
        
        kurt = (
            np.exp(4 * self.sigma**2)
            + 2 * np.exp(3 * self.sigma**2)
            + 3 * np.exp(2 * self.sigma**2)
            - 6
        )
        return kurt

    def get_base_dist(self):
        ''' Return the GPC base distribution.
            
            Returns
            -------
            dist_germ : Distribution object
                GPC base distribution.'''
        
        base = NormalDistribution(0, 1)
        return base

    def base2dist(self, y):
        ''' Convert from base (germ) space to log-normal distribution space.
        
            Parameters
            ----------
            y : array_like
                Points in base (germ) space.
                
            Returns
            -------
            x : array_like
                Points in log-normal distribution space.'''
        
        x = np.exp(y * self.sigma + self.mu)
        return x

    def dist2base(self, x):
        ''' Convert from log-normal distribution space to base (germ) space.
        
            Parameters
            ----------
            x : array_like
                Points in log-normal distribution space.
                
            Returns
            -------
            y : array_like
                Points in base (germ) space.'''
        
        # ignore RuntimeWarning in case x == 0
        with np.errstate(divide="ignore", invalid="ignore"): #TODO ???
            y = (np.log(x) - self.mu) / self.sigma
            return y

    def stdnor2base(self, y):  # same as base2dist??
        ''' Convert from standard normal space to log-normal distribution space.
        
            Parameters
            ----------
            y : array_like
                Points in standard normal space.
                
            Returns
            -------
            x : array_like
                Points in log-normal distribution space.'''
        
        x = np.exp(y * self.sigma + self.mu)
        return x

    def base2stdnor(self, x):  # same as dist2base??
        ''' Convert from log-normal distribution space to standard normal space.
        
            Parameters
            ----------
            x : array_like
                Points in log-normal distribution space.
                
            Returns
            -------
            y : array_like
                Points in standard normal space.'''
        
        y = (np.log(x) - self.mu) / self.sigma
        return y

    def orth_polysys(self):
        ''' Return the GPC polynomial system for the log-normal distribution.
        
            Returns
            -------
            polysys : PolynomialSystem object
                GPC polynomial system for the log-normal distribution.'''
        
        from polysys import HermitePolynomials

        if self.mu == 0 and self.sigma == 1:
            polysys = HermitePolynomials()
        else:
            polysys = Distribution.orth_polysys(self)
        return polysys

    def orth_polysys_syschar(self, normalized):
        ''' Return the GPC polynomial system characteristic string for the log-normal distribution.
            
            Parameters
            ----------
            normalized : bool
                Flag indicating whether to return the normalized polynomial system characteristic string.
                
            Returns
            -------
            polysys_char : str
                GPC polynomial system characteristic string for the log-normal distribution.'''
        
        if self.mu == 0 and self.sigma == 1:
            if normalized:
                polysys_char = "h"
            else:
                polysys_char = "H"
        else:
            polysys_char = []
        return polysys_char

class BetaDistribution(Distribution):
    ''' Class for beta distribution.
    
        Attributes
        ----------
        a : float
            First shape parameter of the beta distribution.
            
        b : float
            Second shape parameter of the beta distribution.
            
        Methods
        -------
        __init__(a, b)
            Initialize the beta distribution with shape parameters a and b.
            
        __repr__()
            Returns the string representation of the BetaDistribution object.
            
        get_dist_type()
            Return the type of the distribution.
            
        get_dist_params()
            Return the parameters of the distribution.
            
        pdf(x)
            Return the probability density function of the beta distribution, evaluated at x.
            
        cdf(x)
            Return the cumulative distribution function of the beta distribution, evaluated at x.
        
        invcdf(y)
            Return the inverse cumulative distribution function of the beta distribution, evaluated at y.
            
        moments()
            Return the first four moments of the beta distribution.
            
        mean()
            Return the mean of the beta distribution.
            
        var()
            Return the variance of the beta distribution.
            
        skew()
            Return the skewness of the beta distribution.
            
        kurt()
            Return the kurtosis of the beta distribution.
            
        get_base_dist()
            Return the GPC base distribution.
            
        base2dist(y)
            Convert from base (germ) space to beta distribution space.
            
        dist2base(x)
            Convert from beta distribution space to base (germ) space.
            
        orth_polysys()
            Return the GPC polynomial system for the beta distribution.'''
    
    def __init__(self, a, b):
        ''' Initialize the beta distribution with shape parameters a and b.
        
            Parameters
            ----------
            a : float
                First shape parameter of the beta distribution.
                
            b : float
                Second shape parameter of the beta distribution.'''
        
        self.a = a
        self.b = b

    def __repr__(self):
        ''' Returns the string representation of the BetaDistribution object.
        
            Returns
            -------
            repr_string : str
                String representation of the BetaDistribution object.'''
        
        repr_string = "Beta({}, {})".format(self.a, self.b)
        return repr_string
    
    def get_dist_type(self):
        ''' Return the type of the distribution.
        
            Returns
            -------
            dist_type : str
                Type of the distribution.'''
        
        dist_type = "beta"
        return dist_type
    
    def get_dist_params(self):
        ''' Return the parameters of the distribution.
        
            Returns
            -------
            params : tuple
                Parameters of the distribution (a, b).'''
        
        params = (self.a, self.b)
        return params

    def pdf(self, x):
        ''' Return the probability density function of the beta distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the pdf.
                
            Returns
            -------
            y : array_like
                Probability density function values at x.'''
        
        x = TranslatedDistribution.translate_points_backwards(x, -1, 2, 0)
        x = np.array(x)
        y = np.zeros(x.shape)
        ind = (x >= 0) & (x <= 1)
        y[ind] = (
            x[ind] ** (self.a - 1)
            * (1 - x[ind]) ** (self.b - 1)
            / sc.beta(self.a, self.b)
        )
        y = unwrap_if_scalar(y)
        return y

    def cdf(self, x):
        ''' Return the cumulative distribution function of the beta distribution, evaluated at x.
        
            Parameters
            ----------
            x : array_like
                Points at which to evaluate the cdf.
                
            Returns
            -------
            y : array_like
                Cumulative distribution function values at x.'''
        
        x = TranslatedDistribution.translate_points_backwards(x, -1, 2, 0)
        x = np.array(x)
        y = np.zeros(x.shape)
        ind = (x >= 0) & (x <= 1)
        y[ind] = sc.betainc(self.a, self.b, x[ind])
        y[x > 1] = 1
        y = unwrap_if_scalar(y)
        return y

    def invcdf(self, y):
        ''' Return the inverse cumulative distribution function of the beta distribution, evaluated at y.
            
            Parameters
            ----------
            y : array_like
                Points at which to evaluate the invcdf.
                
            Returns
            -------
            x : array_like
                Inverse cumulative distribution function values at y.'''
        
        # TODO implementing the Matlab code
        y = np.array(y)
        x = np.full(y.shape, np.nan)
        ind = (y >= 0) & (y <= 1)
        x[ind] = sc.betaincinv(self.a, self.b, y[ind])
        x = TranslatedDistribution.translate_points_forward(x, -1, 2, 0)
        x = unwrap_if_scalar(x)
        return x

    def moments(self):
        ''' Return the first four moments of the beta distribution.
        
            Returns
            -------
            moments : list
                List containing the first four moments [mean, variance, skewness, kurtosis] of the beta distribution.'''
        
        mean = self.mean()
        var = self.var()
        skew = self.skew()
        kurt = self.kurt()

        moments = [mean, var, skew, kurt]
        moments = TranslatedDistribution.translate_moments(moments, -1, 2, 0)
        return moments

    def mean(self):
        """ Return the mean of the beta distribution.

            Returns
            -------
            mean : float
                Mean of the beta distribution."""
        
        mean = self.a / (self.a + self.b)
        return mean

    def var(self):
        """ Return the variance of the beta distribution.

            Returns
            -------
            var : float
                Variance of the beta distribution."""
        
        var = self.a * self.b / (((self.a + self.b) ** 2) * (self.a + self.b + 1))
        return var

    def skew(self):
        """ Return the skewness of the beta distribution.

            Returns
            -------
            skew : float
                Skewness of the beta distribution."""
        
        skew = (
            2
            * (self.b - self.a)
            * np.sqrt(self.a + self.b + 1)
            / ((self.a + self.b + 2) * np.sqrt(self.a * self.b))
        )
        return skew

    def kurt(self):
        """ Return the kurtosis of the beta distribution.

            Returns
            -------
            kurt : float
                Kurtosis of the beta distribution."""
        
        kurt = (
            6
            * (
                self.a**3
                - (self.a**2) * (2 * self.b - 1)
                + (self.b**2) * (self.b + 1)
                - 2 * self.a * self.b * (self.b + 2)
            )
            / (self.a * self.b * (self.a + self.b + 2) * (self.a + self.b + 3))
        )
        return kurt

    def get_base_dist(self):
        """ Return the GPC base distribution.

            Returns
            -------
            dist_germ : Distribution object
                GPC base distribution."""
        
        dist_germ = self
        return dist_germ

    def base2dist(self, y):
        """ Convert from base (germ) space to beta distribution space.

            Parameters
            ----------
            y : array_like
                Points in base (germ) space.

            Returns
            -------
            x : array_like
                Points in distribution space."""
        
        x = y
        return x

    def dist2base(self, x):
        """ Convert from beta distribution space to base (germ) space.

            Parameters
            ----------
            x : array_like
                Points in distribution space.

            Returns
            -------
            y : array_like
                Points in base (germ) space."""
        
        y = x
        return y

    def orth_polysys(self):
        """ Return the GPC polynomial system for the beta distribution.

            Returns
            -------
            polysys : PolynomialSystem object
                GPC polynomial system for the beta distribution."""
        
        from polysys import JacobiPolynomials

        polysys = JacobiPolynomials(self.b - 1, self.a - 1)
        return polysys

    # def orth_polysys_syschar(self, normalized):
    #     #TODO
    #     if self.mu == 0 and self.sigma == 1:
    #         if normalized:
    #             polysys_char = 'h'
    #         else:
    #             polysys_char = 'H'
    #     else:
    #         polysys_char = []
    #     return polysys_char
    #     polysys=JacobiPolynomials(dist.b-1, dist.a-1);

class ExponentialDistribution(Distribution):
    """ Class for exponential distribution.

        Attributes
        ----------
        lambda_ : float
            Rate parameter of the exponential distribution.

        Methods
        -------
        __init__(lambda_)
            Initialize the exponential distribution with rate parameter lambda_.

        __repr__()
            Returns the string representation of the ExponentialDistribution object.

        get_dist_type()
            Return the type of the distribution.
        
        get_dist_params()
            Return the parameters of the distribution.

        pdf(x)
            Return the probability density function of the exponential distribution, evaluated at x.

        cdf(x)
            Return the cumulative distribution function of the exponential distribution, evaluated at x.

        invcdf(y)
            Return the inverse cumulative distribution function of the exponential distribution, evaluated at y.

        mean()
            Return the mean of the exponential distribution.

        var()
            Return the variance of the exponential distribution.

        skew()
            Return the skewness of the exponential distribution.

        kurt()
            Return the kurtosis of the exponential distribution.

        sample(n, method='MC', **params)
            Return n samples from the exponential distribution.

        orth_polysys()
            Return the GPC polynomial system for the exponential distribution.

        get_base_dist()
            Return the GPC base distribution.

        base2dist(y)
            Convert from base (germ) space to exponential distribution space.

        dist2base(x)
            Convert from exponential distribution space to base (germ) space."""
    
    def __init__(self, lambda_):
        """ Initialize the exponential distribution with rate parameter lambda_.

            Parameters
            ----------
            lambda_ : float
                Rate parameter of the exponential distribution."""

        self.lambda_ = lambda_

    def __repr__(self):
        """ Returns the string representation of the ExponentialDistribution object.

            Returns
            -------
            repr_string : str
                String representation of the ExponentialDistribution object."""
        
        repr_string = "Exp({})".format(self.lambda_)
        return repr_string
    
    def get_dist_type(self):
        """ Return the type of the distribution.

            Returns
            -------
            type_string : str
                Type of the distribution."""
        
        type_string = "exp"
        return type_string
    
    def get_dist_params(self):
        """ Return the parameters of the distribution.

            Returns
            -------
            params : float
                Parameters of the distribution (lambda_)."""
        
        params = self.lambda_
        return params

    def pdf(self, x):
        """ Return the probability density function of the exponential distribution, evaluated at x.

            Parameters
            ----------
            x : array_like
                Points at which to evaluate the pdf.

            Returns
            -------
            y : array_like
                Probability density function values at x."""

        x = np.array(x)
        y = np.zeros(x.shape)
        ind = x >= 0
        y[ind] = self.lambda_ * np.exp(-self.lambda_ * x[ind])
        y = unwrap_if_scalar(y)
        return y

    def cdf(self, x):
        """ Return the cumulative distribution function of the exponential distribution, evaluated at x.

            Parameters
            ----------
            x : array_like
                Points at which to evaluate the cdf.

            Returns
            -------
            y : array_like
                Cumulative distribution function values at x."""
        
        x = np.array(x)
        y = np.zeros(x.shape)
        # y = np.zeros(np.size(x))
        ind = x >= 0
        y[ind] = 1 - np.exp(-self.lambda_ * x[ind])
        y = unwrap_if_scalar(y)
        return y

    def invcdf(self, y):
        """ Return the inverse cumulative distribution function of the exponential distribution, evaluated at y.

            Parameters
            ----------
            y : array_like
                Points at which to evaluate the invcdf.

            Returns
            -------
            x : array_like
                Inverse cumulative distribution function values at y."""
        
        y = np.array(y)
        x = np.full(np.size(y), np.nan)
        ind = (y >= 0) & (y <= 1)
        # ignore RuntimeWarning in case x == 0
        with np.errstate(divide="ignore", invalid="ignore"):
            x[ind] = -np.log(1 - y[ind]) / self.lambda_
        x = unwrap_if_scalar(x)
        return x

    def mean(self):
        """ Return the mean of the exponential distribution.

            Returns
            -------
            mean : float
                Mean of the exponential distribution."""
        
        mean = 1 / self.lambda_
        return mean

    def var(self):
        """ Return the variance of the exponential distribution.

            Returns
            -------
            var : float
                Variance of the exponential distribution."""
            
        var = 1 / self.lambda_**2
        return var

    def skew(self):
        """ Return the skewness of the exponential distribution.

            Returns
            -------
            skew : float
                Skewness of the exponential distribution."""
        
        return 2

    def kurt(self):
        """ Return the kurtosis of the exponential distribution.

            Returns
            -------
            kurt : float
                Kurtosis of the exponential distribution."""
        
        return 6

    def sample(self, n, method="MC", **params):
        """ Return n samples from the exponential distribution.

            Parameters
            ----------
            n : int
                Number of samples to generate.

            method : str, optional
                Sampling method to use (default is 'MC' for Monte Carlo).
            
            **params : dict
                Additional parameters for the sampling method.

            Returns
            -------
            samples : array_like
                Generated samples from the exponential distribution."""
        
        # uni = UniformDistribution()
        yi = UniformDistribution().sample(n, method, **params)
        xi = self.invcdf(yi)
        return xi

    def orth_polysys(self):
        """ Return the GPC polynomial system for the exponential distribution.

            Returns
            -------
            polysys : PolynomialSystem object
                GPC polynomial system for the exponential distribution."""
            
        if self.lambda_:
            from polysys import LaguerrePolynomials

            polysys = LaguerrePolynomials()
        else:
            Distribution.orth_polysys()
        return polysys

    def get_base_dist(self):
        """ Return the GPC base distribution.

            Returns
            -------
            dist_germ : Distribution object
                GPC base distribution."""
            
        base = ExponentialDistribution(1)
        return base

    def base2dist(self, y):
        """ Convert from base (germ) space to exponential distribution space.

            Parameters
            ----------
            y : array_like
                Points in base (germ) space.

            Returns
            -------
            x : array_like
                Points in exponential distribution space."""
            
        x = y / self.lambda_
        return x

    def dist2base(self, x):
        """ Convert from exponential distribution space to base (germ) space.

            Parameters
            ----------
            x : array_like
                Points in exponential distribution space.
            
            Returns
            -------
            y : array_like
                Points in base (germ) space."""
        
        y = x * self.lambda_
        return y

class WignerSemicircleDistribution(Distribution):
    """ Class for Wigner semicircle distribution.

        Attributes
        ----------
        radius : float
            Radius of the semicircle.

        Methods
        -------
        __init__(radius)
            Initialize the Wigner semicircle distribution with radius.

        __repr__()
            Returns the string representation of the WignerSemicircleDistribution object.

        get_dist_type()
            Return the type of the distribution.

        get_dist_params()
            Return the parameters of the distribution.

        pdf(x)
            Return the probability density function of the Wigner semicircle distribution, evaluated at x.

        cdf(x)
            Return the cumulative distribution function of the Wigner semicircle distribution, evaluated at x.

        invcdf(y)
            Return the inverse cumulative distribution function of the Wigner semicircle distribution, evaluated at y.

        mean()
            Return the mean of the Wigner semicircle distribution.

        var()
            Return the variance of the Wigner semicircle distribution.

        skew()
            Return the skewness of the Wigner semicircle distribution.

        kurt()
            Return the kurtosis of the Wigner semicircle distribution."""

    def __init__(self, radius):
        """ Initialize the Wigner semicircle distribution with radius.

            Parameters
            ----------
            radius : float
                Radius of the semicircle."""
        
        assert radius > 0
        self.radius = radius

    def __repr__(self):
        """ Returns the string representation of the WignerSemicirlceDistribution object.

            Returns
            -------
            repr_string : str
                String representation of the WignerSemicircleDistribution object."""
        
        repr_string = "W({})".format(self.radius)
        return repr_string

    def get_dist_type(self):
        """ Return the type of the distribution.

            Returns
            -------
            type_string : str
                Type of the distribution."""
        
        type_string = "wigner"
        return type_string
    
    def get_dist_params(self):
        """ Return the parameters of the distribution.

            Returns
            -------
            params : float
                Parameters of the distribution (radius)."""
        
        params = self.radius
        return params
    
    def pdf(self, x):
        """ Return the probability density function of the Wigner semicircle distribution, evaluated at x.

            Parameters
            ----------
            x : array_like
                Points at which to evaluate the pdf.

            Returns
            -------
            y : array_like
                Probability density function values at x. """
        
        x = np.array(x)
        y = np.zeros(x.shape)
        ind = (x >= -self.radius) & (x <= self.radius)
        y[ind] = (2 / (np.pi * self.radius**2)) * np.sqrt(self.radius**2 - x[ind] ** 2)
        y = unwrap_if_scalar(y)
        return y
    
    def cdf(self, x):
        """ Return the cumulative distribution function of the Wigner semicircle distribution, evaluated at x.

            Parameters
            ----------
            x : array_like
                Points at which to evaluate the cdf.

            Returns
            -------
            y : array_like
                Cumulative distribution function values at x."""
        
        x = np.array(x)
        y = np.zeros(x.shape)
        ind1 = x < -self.radius
        ind2 = (x >= -self.radius) & (x <= self.radius)
        ind3 = x > self.radius
        y[ind1] = 0
        y[ind2] = 1 / 2 + (x[ind2] * np.sqrt(self.radius**2 - x[ind2]**2)) / (np.pi * self.radius**2) + (
            np.arcsin(x[ind2] / self.radius)
        ) / np.pi
        y[ind3] = 1
        y = unwrap_if_scalar(y)
        return y

    def invcdf(self, y):
        """ Return the inverse cumulative distribution function of the Wigner semicircle distribution, evaluated at y.

            Parameters
            ----------
            y : array_like
                Points at which to evaluate the invcdf.

            Returns
            -------
            x : array_like
                Inverse cumulative distribution function values at y. """
        
        y = np.array(y)
        x = np.full(y.shape, np.nan)
        ind = (y >= 0) & (y <= 1)
        x[ind] = self.radius * np.sin(np.pi * (y[ind] - 1 / 2))
        return x
    
    def mean(self):
        """ Return the mean of the Wigner semicircle distribution.

            Returns
            -------
            mean : float
                Mean of the Wigner semicircle distribution. """
        
        mean = 0
        return mean
    
    def var(self):
        """ Return the variance of the Wigner semicircle distribution.

            Returns
            -------
            var : float
                Variance of the Wigner semicircle distribution. """
        
        var = self.radius**2 / 4
        return var
    
    def skew(self):
        """ Return the skewness of the Wigner semicircle distribution.

            Returns
            -------
            skew : float
                Skewness of the Wigner semicircle distribution. """
        
        skew = 0
        return skew
    
    def kurt(self):
        """ Return the kurtosis of the Wigner semicircle distribution.

            Returns
            -------
            kurt : float
                Kurtosis of the Wigner semicircle distribution. """
        
        kurt = -1
        return kurt

if __name__ == "__main__":
    arr = np.arange(-10, 10, 1)
    print(arr)

    dist = NormalDistribution(0, 3)
    print(dist.moments())
    problem = {
        "num_vars": 1,
        "names": ["x1"],
        "bounds": [[-3.14159265359, 3.14159265359]],
    }

    dist.sample(16, method="MC", problem=problem)
    # plt.plot(arr, dist.pdf(arr))
    print(dist.pdf(arr))
    print(dist.logpdf(arr))
    # plt.plot(arr, dist.logpdf(arr))
    print(dist.cdf(arr))
    # plt.plot(arr, dist.cdf(arr))
    print(dist.get_base_dist().mu, dist.get_base_dist().sigma)
    print(dist.dist2base(np.array([-3, -2, -1, 0, 1, 2, 3])))
    print(dist.base2dist(np.array([-2, -1, -0.5, 0, 0.5, 1, 2])))
    print(dist.get_bounds())

    fig1, ax1 = plt.subplots(3)
    ax1[0].plot(arr, dist.pdf(arr))
    ax1[1].plot(arr, dist.logpdf(arr))
    ax1[2].plot(arr, dist.cdf(arr))

    print("------")

    dist = UniformDistribution(0, 3)
    print(dist.moments())
    print(dist.pdf(arr))
    # plt.plot(arr, dist.logpdf(arr))
    print(dist.logpdf(arr))
    print(dist.cdf(np.array([-3, -2, -1, 0, 1, 2, 3])))
    print(dist.get_base_dist().a, dist.get_base_dist().b)
    print(dist.dist2base(np.array([-3, -2, -1, 0, 1, 2, 3])))
    print(dist.base2dist(np.array([-2, -1, -0.5, 0, 0.5, 1, 2])))
    print(dist.get_bounds())

    fig2, ax2 = plt.subplots(3)
    ax2[0].plot(arr, dist.pdf(arr))
    ax2[1].plot(arr, dist.logpdf(arr))
    ax2[2].plot(arr, dist.cdf(arr))

    print("------")

    dist = LogNormalDistribution(-3, 3)
    print(dist.moments())
    print(dist.pdf(arr))
    # plt.plot(arr, dist.logpdf(arr))
    print(dist.logpdf(arr))
    print(dist.cdf(np.array([-3, -2, -1, 0, 1, 2, 3])))
    print(dist.get_base_dist().mu, dist.get_base_dist().sigma)
    # print(dist.dist2base(np.array([-3, -2, -1, 0, 1, 2, 3])))
    # print(dist.base2dist(np.array([-2, -1, -0.5, 0, 0.5, 1, 2])))
    ##print(dist.get_bounds())

    # fig2, ax2 = plt.subplots(3)
    # ax2[0].plot(arr, dist.pdf(arr))
    # ax2[1].plot(arr, dist.logpdf(arr))
    # ax2[2].plot(arr, dist.cdf(arr))

    plt.show()
