''' This module implements various polynomial systems used in polynomial chaos expansions.

    Classes
    -------
    PolynomialSystem
        Abstract base class for polynomial systems.

    NormalizedPolynomials
        Wrapper class for normalized polynomial systems.
        
    LegendrePolynomials
        Implementation of Legendre polynomial system.
        
    HermitePolynomials
        Implementation of Hermite polynomial system.
        
    JacobiPolynomials
        Implementation of Jacobi polynomial system.
        
    ChebyshevTPolynomials
        Implementation of Chebyshev polynomials of the first kind.
        
    ChebyshevUPolynomials
        Implementation of Chebyshev polynomials of the second kind.
        
    LaguerrePolynomials
        Implementation of Laguerre polynomial system.
                
    Functions
    ---------
    syschar_to_polysys(syschar)
        Convert a system characteristic string to the corresponding polynomial system.'''

import numpy as np
import scipy.special as sp
from .distributions import *

from abc import ABC, abstractmethod

class PolynomialSystem(ABC):
    ''' Abstract base class for polynomial systems.
    
        Methods
        -------
        evaluate(deg, xi)
            Evaluate the polynomial system up to degree deg at points xi.

        sqnorm(n)
            Return the squared norm of the polynomials of degree n.

        sqnorm_by_rc(rc)
            Return the squared norm using recurrence coefficients rc.

        normalized()
            Return the normalized version of the polynomial system.'''
    
    def evaluate(self, deg, xi):
        '''Evaluate polynomial system up to degree `deg` at points `xi`.

            Parameters
            ----------
            deg: int
                Highest polynomial degree to evaluate.
            xi: array_like
                Points at which the polynomials are evaluated.

            Returns
            -------
            y_alpha_j: numpy.ndarray
                Matrix of shape (len(xi), deg+1) containing evaluated polynomials.'''

        k = np.size(xi)
        p = np.zeros([k, deg+2])
        p[:,0] = 0
        p[:,1] = 1
        r = self.recur_coeff(deg+1)
        for d in range(deg):
           p[:, d+2] = (r[d,0] + xi * r[d,1]) * p[:, d+1] - r[d,2] * p[:,d]
        y_alpha_j = p[:,1:]
        return y_alpha_j

    def sqnorm(self, n):
        """ Return the squared norm of the polynomials of degree `n`.

            Parameters
            ----------
            n : array_like
                Degrees for which the squared norms are computed.

            Returns
            -------
            nrm2 : numpy.ndarray
                Array of squared norms corresponding to degrees in `n`."""
        
        deg = max(n.flatten()) + 1
        r = self.recur_coeff(deg)
        nrm2 = self.sqnorm_by_rc(r)
        nrm2 = np.reshape([nrm2[n+1], len(n)])
        return nrm2

    def sqnorm_by_rc(self, rc):
        """ Return the squared norm using recurrence coefficients `rc`.

            Parameters
            ----------
            rc : array_like
                Recurrence coefficients of shape (deg, 3).

            Returns
            -------
            nrm2 : numpy.ndarray
                Array of squared norms for polynomials up to degree `deg`."""
        
        b = rc[:, 1]
        h = b[0] / b[1:]
        c = rc[1:, 2]
        nrm2 = np.concatenate(np.ones([1]),  h.flatten * np.cumprod(c.flatten()))
        return nrm2

    def normalized(self):
        '''Return normalized version of this polynomial system.

        Returns
        -------
        polysys: NormalizedPolynomials
            Wrapped normalized polynomial system.'''

        polysys = NormalizedPolynomials(self)
        return polysys

    @abstractmethod
    def weighting_dist(self):
        ''' Abstract method to return the weighting distribution of the polynomial system.
            Subclasses must implement this method.'''
        
        pass

    @abstractmethod
    def recur_coeff(self, deg):
        ''' Abstract method to return the recurrence coefficients of the polynomial system.
            Subclasses must implement this method.'''
        
        pass

class NormalizedPolynomials(PolynomialSystem):
    """ Wrapper class for normalized polynomial systems.

        Attributes
        ----------
        base_polysys : PolynomialSystem
            The base polynomial system to be normalized.

        Methods
        -------
        __init__(base_polysys)
            Initialize the normalized polynomial system with a base polynomial system.

        recur_coeff(deg)
            Return the recurrence coefficients for the normalized polynomial system.

        weighting_dist()
            Return the weighting distribution of the base polynomial system."""
    
    def __init__(self, base_polysys):
        """ Initialize the normalized polynomial system with a base polynomial system.

            Parameters
            ----------
            base_polysys : PolynomialSystem
                The base polynomial system to be normalized."""
        
        self.base_polysys = base_polysys

    def recur_coeff(self, deg):
        """_summary_

            Parameters
            ----------
            deg : int
                Degree up to which recurrence coefficients are computed.

            Returns
            -------
            r : numpy.ndarray
                Recurrence coefficients for the normalized polynomial system."""
        
        r = self.base_polysys.recur_coeff(deg)
        n = np.array(range(deg))
        z = np.concatenate((np.zeros([1]), np.sqrt(self.base_polysys.sqnorm(np.arange(0,deg+1)))), axis=0)
        r = np.array([r[:, 0]*z[n + 1] / z[n + 2],
            r[:, 1] * z[n + 1] / z[n + 2],
            r[:, 2] * z[n] / z[n + 2]])
        r = r.transpose()
        return r

    def weighting_dist(self):
        """ Return the weighting distribution of the base polynomial system.

            Returns
            -------
            dist : Distribution
                Weighting distribution of the base polynomial system."""
        
        dist = self.base_polysys.weighting_dist()
        return dist

class LegendrePolynomials(PolynomialSystem):
    """ Implementation of Legendre polynomial system.

        Methods
        -------
        normalized()
            Return normalized version of Legendre polynomial system.
            
        recur_coeff(deg)
            Return the recurrence coefficients for Legendre polynomials.
            
        sqnorm(n)
            Return the squared norm of Legendre polynomials of degree `n`.
            
        weighting_dist()
            Return the weighting distribution for Legendre polynomials."""

    @classmethod
    def normalized(self):
        """ Return normalized version of Legendre polynomial system.

            Returns
            -------
            polysys: NormalizedPolynomials
                Wrapped normalized Legendre polynomial system."""
        
        polysys = NormalizedPolynomials(self)
        return polysys

    @staticmethod
    def recur_coeff(deg):
        """ Return the recurrence coefficients for Legendre polynomials.

            Parameters
            ----------
            deg : int
                Degree up to which recurrence coefficients are computed.

            Returns
            -------
            r : numpy.ndarray
                Recurrence coefficients for Legendre polynomials."""
        
        n = np.array(range(deg)).reshape(-1,1)
        zer = np.zeros(n.shape).reshape(-1,1)
        r = np.concatenate((zer, (2*n+1)/(n+1), n/(n+1)), axis=1)
        return r

    @staticmethod
    def sqnorm(n):
        """ Return the squared norm of Legendre polynomials of degree `n`.

            Parameters
            ----------
            n : array_like
                Degrees for which the squared norms are computed.

            Returns
            -------
            nrm2 : numpy.ndarray
                Array of squared norms corresponding to degrees in `n`."""
            
        nrm2 = 1/(2*n + 1)
        return nrm2

    @staticmethod
    def weighting_dist():
        """ Return the weighting distribution for Legendre polynomials.

            Returns
            -------
            dist : UniformDistribution
                Weighting distribution for Legendre polynomials."""
        
        dist = UniformDistribution(-1,1)
        return dist

class HermitePolynomials(PolynomialSystem):
    """ Implementation of Hermite polynomial system.

        Methods
        -------
        normalized()
            Return normalized version of Hermite polynomial system.

        recur_coeff(deg)
            Return the recurrence coefficients for Hermite polynomials.

        sqnorm(n)
            Return the squared norm of Hermite polynomials of degree `n`.

        weighting_dist()
            Return the weighting distribution for Hermite polynomials."""
    
    @classmethod
    def normalized(self):
        """ Return normalized version of Hermite polynomial system.

            Returns
            -------
            polysys: NormalizedPolynomials
                Wrapped normalized Hermite polynomial system."""

        polysys = NormalizedPolynomials(self)
        return polysys

    @staticmethod
    def recur_coeff(deg):
        """ Return the recurrence coefficients for Hermite polynomials.

            Parameters
            ----------
            deg :  int
                Degree up to which recurrence coefficients are computed.

            Returns
            -------
            r : numpy.ndarray
                Recurrence coefficients for Hermite polynomials."""
        
        n = np.arange(deg)
        one = np.ones_like(n)
        zero = np.zeros_like(n)
        r = np.column_stack((zero, one, n))
        return r

    @staticmethod
    def sqnorm(n):
        """ Return the squared norm of Hermite polynomials of degree `n`.

            Parameters
            ----------
            n : array_like
                Degrees for which the squared norms are computed.

            Returns
            -------
            nrm2 : numpy.ndarray
                Array of squared norms corresponding to degrees in `n`."""
        
        nrm2 = sp.factorial(n)
        return nrm2

    @staticmethod
    def weighting_dist():
        """ Return the weighting distribution for Hermite polynomials.

            Returns
            -------
            dist : NormalDistribution
                Weighting distribution for Hermite polynomials."""
        
        dist = NormalDistribution(0,1)
        return dist
    
class JacobiPolynomials(PolynomialSystem):
    """ Implementation of Jacobi polynomial system.

        Attributes
        ----------
        alpha : float
            First parameter of Jacobi polynomials.

        beta : float
            Second parameter of Jacobi polynomials.

        Methods
        -------
        __init__(alpha, beta)
            Initialize Jacobi polynomial system with parameters alpha and beta.

        normalized()
            Return normalized version of Jacobi polynomial system.

        recur_coeff(deg)
            Return the recurrence coefficients for Jacobi polynomials.

        sqnorm(n)
            Return the squared norm of Jacobi polynomials of degree `n`.

        weighting_dist()
            Return the weighting distribution for Jacobi polynomials."""
    
    def __init__(self, alpha, beta):
        """ 

        Parameters
        ----------
        alpha : float
            First parameter of Jacobi polynomials.

        beta : float
            Second parameter of Jacobi polynomials."""
        
        self.alpha = alpha
        self.beta = beta
        
    def normalized(self):
        """ Return normalized version of Jacobi polynomial system.

            Returns
            -------
            polysys: NormalizedPolynomials
                Wrapped normalized Jacobi polynomial system."""

        polysys = NormalizedPolynomials(self)
        return polysys

    def recur_coeff(self, deg):
        """ Return the recurrence coefficients for Jacobi polynomials.

            Parameters
            ----------
            deg : int
                Degree up to which recurrence coefficients are computed.

            Returns
            -------
            r : numpy.ndarray
                Recurrence coefficients for Jacobi polynomials."""
        
        n = np.array(range(deg)).reshape(-1,1)
        a = self.alpha
        b = self.beta
        
        b_n = (2*n+a+b+1)*(2*n+a+b+2)/( 2*(n+1)*(n+a+b+1) )
        a_n = (a*a-b*b)*(2*n+a+b+1)/( 2*(n+1)*(n+a+b+1)*(2*n+a+b) )
        c_n = (n+a)*(n+b)*(2*n+a+b+2)/( (n+1)*(n+a+b+1)*(2*n+a+b) )
        
        if a+b==0 or a+b==-1:
            b_n[0]=0.5*(a+b)+1
            a_n[0]=0.5*(a-b)
            c_n[0]=0
            
        r = np.concatenate((a_n, b_n, c_n), axis=1)
            
        return r

    def sqnorm(self, n):
        """ Return the squared norm of Jacobi polynomials of degree `n`.

            Parameters
            ----------
            n : array_like
                Degrees for which the squared norms are computed.

            Returns
            -------
            nrm2 : numpy.ndarray
                Array of squared norms corresponding to degrees in `n`."""
        
        nrm2 = PolynomialSystem.sqnorm(self, n)
        return nrm2

    def weighting_dist(self):
        """ Return the weighting distribution for Jacobi polynomials.

            Returns
            -------
            dist : BetaDistribution
                Weighting distribution for Jacobi polynomials."""
        
        dist = BetaDistribution(self.beta+1, self.alpha+1)
        return dist

class ChebyshevTPolynomials(PolynomialSystem):
    """ Implementation of Chebyshev polynomials of the first kind.

        Methods
        -------
        normalized()
            Return normalized version of first kind Chebyshev polynomial system.

        recur_coeff(deg)
            Return the recurrence coefficients for first kind Chebyshev polynomials.

        sqnorm(n)
            Return the squared norm of first kind Chebyshev polynomials of degree `n`.
        
        weighting_dist()
            Return the weighting distribution for first kind Chebyshev polynomials."""
    
    @classmethod
    def normalized(self):
        """ Return normalized version of the first kind Chebyshev polynomial system.

            Returns
            -------
            polysys: NormalizedPolynomials
                Wrapped normalized first kind Chebyshev polynomial system."""

        polysys = NormalizedPolynomials(self)
        return polysys

    @staticmethod
    def recur_coeff(deg):
        if deg == 0:
            r = np.array([[]])
        else:
            first_row = np.array([0, 1, 0])
            if deg == 1:
                r = first_row
            else:
                n = np.arange(deg)
                one = np.ones_like(n)
                two = one*2
                zero = np.zeros_like(n)
                r = np.column_stack((zero, two, one))
                r[0] = first_row
        return r

    @staticmethod
    def sqnorm(self, n):
        nrm2 = PolynomialSystem.sqnorm(self, n)
        return nrm2

    @staticmethod
    def weighting_dist():

        dist = WignerSemicircleDistribution(1)
        return dist

class ChebyshevUPolynomials(PolynomialSystem):
    @classmethod
    def normalized(self):
        """ Return normalized version of second kind Chebyshev polynomial system.

            Returns
            -------
            polysys: NormalizedPolynomials
                Wrapped normalized second kind Chebyshev polynomial system."""
        
        polysys = NormalizedPolynomials(self)
        return polysys

    @staticmethod
    def recur_coeff(deg):
        if deg == 0:
            r = np.array([[]])
        else:
            first_row = np.array([0, 2, 0])
            if deg == 1:
                r = first_row
            else:
                n = np.arange(deg)
                one = np.ones_like(n)
                two = one*2
                zero = np.zeros_like(n)
                r = np.column_stack((zero, two, one))
                r[0] = first_row

        return r

    @staticmethod
    def sqnorm(self, n):

        nrm2 = PolynomialSystem.sqnorm(self, n)
        return nrm2

    @staticmethod
    def weighting_dist():

        dist = WignerSemicircleDistribution(1)
        return dist

class LaguerrePolynomials(PolynomialSystem):
    @classmethod
    def normalized(self):
        """ Return normalized version of Laguerre polynomial system.
        
            Returns
            -------
            polysys: NormalizedPolynomials
                Wrapped normalized Laguerre polynomial system."""

        polysys = NormalizedPolynomials(self)
        return polysys

    @staticmethod
    def recur_coeff(deg):
        if deg == 0:
            r = np.array([[]])
        else:
            first_row = np.array([0, -1, -1])
            if deg == 1:
                r = first_row
            else:
                n = np.arange(deg)
                zero = np.zeros_like(n)
                sec_column = -(2*n + 1)/(n + 1)
                third_column = n/(n + 1)

                r = np.column_stack((zero, sec_column, third_column))
                r[0] = first_row

        return r

    @staticmethod
    def sqnorm(self, n):

        nrm2 = PolynomialSystem.sqnorm(self, n)
        return nrm2

    @staticmethod
    def weighting_dist():

        dist = ExponentialDistribution(1)
        return dist

def syschar_to_polysys(syschar):
    """ Convert a system characteristic string to the corresponding polynomial system.

        Parameters
        ----------
        syschar : str
            Characteristic string representing the polynomial system.

        Returns
        -------
        polysys : PolynomialSystem
            Corresponding polynomial system."""
    
    poly_dict = {'H': HermitePolynomials,
                'h': HermitePolynomials.normalized(),
                'P': LegendrePolynomials,
                'p': LegendrePolynomials.normalized(),
                'T': ChebyshevTPolynomials,
                't': ChebyshevTPolynomials.normalized(),
                'U': ChebyshevUPolynomials,
                'u': ChebyshevUPolynomials.normalized(),
                'L': LaguerrePolynomials,
                'l': LaguerrePolynomials.normalized()
                }
    
    polysys = poly_dict[syschar]
    return polysys

if __name__ == "__main__":
    print(LegendrePolynomials.recur_coeff(4))
    print(LegendrePolynomials.recur_coeff(3))
    print(LegendrePolynomials.recur_coeff(2))
    print(LegendrePolynomials.recur_coeff(1))
    print(LegendrePolynomials.recur_coeff(0))
    LegendrePolynomials.normalized()
    LegendrePolynomials.sqnorm(4)
    LegendrePolynomials.sqnorm(3)
    LegendrePolynomials.normalized().recur_coeff(4)




