''' This module implements the Variable class for uncertainty quantification.'''

import numpy as np
from .distributions import UniformDistribution
from .polysys import syschar_to_polysys
import pint

class Variable():
    ''' Variable class for uncertanty quantification.
            
        Attributes
        ----------
        name: str
            Variable name.

        dist : Distribution object
            Variable distribution.

        fixed_val: float
            Fixed value of the variable, if applicable.

        is_fixed: bool
            Flag showing whether the variable is fixed.

        unit: str, optional
            Variable unit.
            
        Methods
        -------
        __init__(self, name, dist_or_num, unit=None, *args, **kwargs)
            Variable constructor.

        __repr__(self)
            Returns the string representation of the Variable object.

        mean(self)
            Return mean value of the distribution.

        var(self)
            Return variance of the distribution.

        moments(self)
            Return the moments of the distribution.

        pdf(self, x)
            Return the probability density function of the distribution, evaluated at x.

        cdf(self, p)
            Return the cumulative density function of the distribution, evaluated at p.
        
        ppf(self, q)
            Return the percentage point function (inverse of cdf) of the distribution, evaluated at q.

        sample(self, n)
            Return n samples from the distribution.

        get_gpc_dist(self)
            Return the GPC base distribution.

        get_gpc_polysys(self, normalized)
            Return the GPC polynomial system.

        get_gpc_syschar(self, normalized)
            Return the GPC polynomial system characteristic string.

        param2germ(self, q)
            Convert from parameter to germ space.

        germ2param(self,x)
            Convert from germ to parameter space.

        convert_to(self, to_unit: str)
            Convert the variable and its distribution parameters to a different unit.'''
        
    def __init__(self, name :str, dist_or_num, unit=None, *args, **kwargs):
        ''' Variable constructor.
            
            Parameters
            ----------
            name: str
                Variable name.

            dist_or_num : Distribution object or float
                Variable distribution or fixed value.

            unit: str, optional
                Variable unit.
                
            args, kwargs
                Additional arguments.'''
        
        self.name = name
        self.dist = dist_or_num if hasattr(dist_or_num, 'pdf') else None
        self.fixed_val = dist_or_num if not hasattr(dist_or_num, 'pdf') else None
        self.is_fixed = self.fixed_val is not None
        self.unit = unit

    def __repr__(self):
        ''' Returns the string representation of the Variable object.
        
            Returns
            -------
            repr_string : str
                String representation of the Variable object.'''
        
        repr_string = 'Param({}, {})'.format(self.name, self.dist.__repr__())
        return repr_string

    def mean(self):
        ''' Return mean value of the distribution.

            Returns
            -------
            mean : float
                Mean value of the distribution.'''
        
        mean = self.dist.mean()
        return mean

    def var(self):
        ''' Return variance of the distribution.

            Returns
            -------
            var : float
                Variance of the distribution.'''
        
        var = self.dist.var()
        return var

    def moments(self):
        ''' Return the moments of the distribution.

            Returns
            -------
            moments : list
                Moments of the distribution ([mean, var, skew, kurt]).'''
        
        moments = self.dist.moments()
        return moments

    def pdf(self, x):
        ''' Return the probability density function of the variable, evaluated at x.

            Parameters
            ----------
            x : array_like
                Points at which to evaluate the pdf.

            Returns
            -------
            pdf_values : array_like
                Probability density function values at x.'''
        
        pdf_values = self.dist.pdf(x)
        return pdf_values

    def cdf(self, p):
        ''' Return the cumulative distribution function of the variable, evaluated at p.

            Parameters
            ----------
            p : array_like
                Points at which to evaluate the cdf.

            Returns
            -------
            cdf_values : array_like
                Cumulative distribution function values at p.'''
        
        cdf_values = self.dist.cdf(p)
        return cdf_values
    
    def ppf(self, q):
        ''' Return the percentage point function (inverse of cdf) of the variable, evaluated at q.

            Parameters
            ----------
            q : array_like
                Points at which to evaluate the ppf.

            Returns
            -------
            ppf_values : array_like
                Percentage point function values at q.'''
        
        ppf_values = self.dist.invcdf(q)
        return ppf_values

    def sample(self, n):
        return self.dist.sample(n)

    def get_gpc_dist(self):
        ''' Return the GPC base distribution.

            Returns
            -------
            dist : Distribution object
                GPC base distribution.'''
        
        dist = self.dist.get_base_dist()
        return dist

    def get_gpc_polysys(self, normalized):
        syschar = self.get_gpc_syschar(normalized)
        return syschar_to_polysys(syschar)

    def get_gpc_syschar(self, normalized):
        ''' Return the GPC polynomial system characteristic string.

            Parameters
            ----------
            normalized : bool
                Flag indicating whether to return the normalized polynomial system characteristic string.

            Returns
            -------
            syschar : str
                GPC polynomial system characteristic string.'''
        
        syschar = self.dist.get_base_dist().orth_polysys_syschar(normalized)
        return syschar

    def germ2param(self,x):
        ''' Convert from germ to parameter space.

            Parameters
            ----------
            x : array_like
                Points in germ space.

            Returns
            -------
            q : array_like
                Points in parameter space.'''
        
        q = self.dist.base2dist(x)
        return q

    def param2germ(self, q):
        ''' Convert from parameter to germ space.

            Parameters
            ----------
            q : array_like
                Points in parameter space.
            
            Returns
            -------
            x : array_like
                Points in germ space.'''
        
        x = self.dist.dist2base(q)
        return x
    
    def convert_to(self, to_unit: str):
        ''' Convert the variable and its distribution parameters to a different unit.
            
            Parameters
            ----------
            to_unit : str
                Target unit for conversion.'''
        ureg = pint.UnitRegistry()

        if self.unit is None:
            raise ValueError("Current unit is not defined.")
        
        if self.is_fixed:
            q = self.fixed_val * ureg(self.unit)
            self.fixed_val = q.to(to_unit).magnitude
            self.unit = to_unit
        
        else:
            for attr, value in vars(self.dist).items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    q = value * ureg(self.unit)
                    setattr(self.dist, attr, q.to(to_unit).magnitude)

        self.unit = to_unit

if __name__ == "__main__":
    from distributions import UniformDistribution
    P = Variable('p', UniformDistribution(-2,2))
    print(P.moments())
    print(P.pdf(np.array([-3, -2, -1, 0, 1, 2, 3])))
    print(P.cdf(np.array([-3, -2, -1, 0, 1, 2, 3])))
    print(P.get_gpc_polysys(True))
    print(P.param2germ(np.array([-3, -2, -1, 0, 1, 2, 3])))
    print(P.germ2param(np.array([-2, -1, -0.5, 0, 0.5, 1, 2])))
    print(P.get_gpc_syschar(False))
