''' This module implements the VariableSet class for managing a set of simulation variables
    with associated probability distributions.'''

import numpy as np
from scipy.stats.qmc import Halton
from scipy.stats.qmc import LatinHypercube as LHS
from scipy.stats.qmc import Sobol
from SALib.sample import saltelli

class VariableSet():
    ''' VariableSet class for managing a set of simulation variables.
        
        Attributes
        ----------
        normalized: bool
            Flag indicating whether the variables are normalized.

        variables: dict
            Dictionary of variable names and their corresponding Distribution objects.
            
        Methods
        -------
        __init__(self, normalized=True)
            VariableSet constructor.
            
        add(self, variable)
            Add a new Variable to the VariableSet.
            
        get_dist_types(self)
            Get the types of distributions for all variables in the VariableSet.
            
        get_dist_params(self)
            Get the parameters of distributions for all variables in the VariableSet.
            
        filter(self, variable_names)
            Create a new VariableSet containing only the specified variables.
            
        num_params(self)
            Get the number of variables in the VariableSet.
            
        param_names(self)
            Get the names of all variables in the VariableSet.
            
        get_params(self)
            Get the dictionary of variables in the VariableSet.
            
        mean(self)
            Get the mean values of all variables in the VariableSet.
            
        var(self)
            Get the variances of all variables in the VariableSet.
            
        pdf(self, q)
            Get the probability density function values for all variables in the VariableSet at given points.
            
        logpdf(self, q)
            Get the log probability density function values for all variables in the VariableSet at given points.
            
        cdf(self, q)
            Get the cumulative distribution function values for all variables in the VariableSet at given points.
            
        get_gpc_syschars(self)
            Get the GPC polynomial system characteristic string for all variables in the VariableSet.
            
        germ2params(self, xi_k_i)
            Convert from germ space to parameter space.
            
        params2germ(self, q_k_i)
            Convert from parameter space to germ space.
            
        get_bounds(self)
            Get the bounds of all variables in the VariableSet.
            
        sample(self, n, method='MC', random_seed=None, **kwargs)
            Generate samples from the VariableSet using specified sampling method.
        
        diminished_paramset(self, indices)
            Create a new VariableSet by selecting a subset of variables based on provided indices.'''
        
    def __init__(self, normalized=True):
        ''' VariableSet constructor.

            Parameter
            ---------
            normalized: bool
                Flag indicating whether the variables are normalized. Default is True.'''
        
        self.normalized = normalized
        self.variables = {}

    def add(self, variable):
        ''' Add a new Variable to the VariableSet.

            Parameter
            ---------
            variable: Variable object
                The Variable object to be added to the VariableSet.'''
        
        if variable.name in self.variables.keys():
            raise("Variable name {} already exists in VariableSet".format(variable.name))
        self.variables[variable.name] = variable.dist

    def get_dist_types(self):
        ''' Get the types of distributions for all variables in the VariableSet.
        
            Returns
            -------
            dist_types: list
                List of distribution types for each variable in the VariableSet.'''
        
        dist_types = []
        for dist in self.variables.values():
            dist_types.append(dist.get_dist_type())
        return dist_types
    
    def get_dist_params(self):
        ''' Get the parameters of distributions for all variables in the VariableSet.
            
            Returns
            -------
            dist_params: list
                List of distribution parameters for each variable in the VariableSet.'''
        
        dist_params = []
        for dist in self.variables.values():
            dist_params.append(dist.get_dist_params())
        return dist_params

    def filter(self, variable_names):
        ''' Create a new VariableSet containing only the specified variables.
            
            Parameter
            ---------
            variable_names: list
                List of variable names to include in the new VariableSet.
                
            Returns
            -------
            new_paramset: VariableSet object
                New VariableSet containing only the specified variables.'''
        
        new_variable_set = VariableSet(normalized=self.normalized)
        new_params = {}
        # To avoid confusion, use a list of original names to map indices
        original_names = list(self.variables.keys())
        for name in variable_names:
            if name not in self.variables:
                raise KeyError(f"Variable {name} not found in VariableSet")
            idx = original_names.index(name)
            new_params[name] = self.variables[name]
        new_variable_set.variables = new_params
        return new_variable_set

    def num_params(self):
        ''' Get the number of variables in the VariableSet.
        
            Returns
            -------
            num_params: int
                Number of variables in the VariableSet.'''
        
        num_params = len(self.variables)
        return num_params

    def param_names(self):
        ''' Get the names of all variables in the VariableSet.
        
            Returns
            -------
            param_names: list
                List of variable names in the VariableSet.'''
        
        param_names = list(self.variables.keys())
        return param_names
    
    def get_params(self):
        ''' Get the dictionary of variables in the VariableSet.
        
            Returns
            -------
            variables: dict
                Dictionary of variable names and their corresponding Distribution objects.'''
        
        variables = self.variables
        return variables

    def mean(self):
        ''' Get the mean values of all variables in the VariableSet.
            
            Returns
            -------
            
            q_mean: numpy.ndarray
                Array of mean values for each variable in the VariableSet.'''
        
        m = self.num_params()
        params = self.variables
        q_mean = np.zeros([m,1])
        for i, dist in enumerate(params.values()):
            q_mean[i] = dist.mean()
        return q_mean

    def var(self):
        ''' Get the variances of all variables in the VariableSet.
            
            Returns
            -------
            var: numpy.ndarray
                Array of variances for each variable in the VariableSet.'''
        
        m = self.num_params()
        params = self.variables
        var = np.zeros([m, 1])
        for i, dist in enumerate(params.values()):
            var[i] = dist.var()
        return var

    def pdf(self, q):
        ''' Get the probability density function values for all variables in the VariableSet at given points.
            
            Parameters
            ----------
            q: numpy.ndarray
                Array of points at which to evaluate the pdf. Shape should be (m, n) where m is the number of variables
                and n is the number of points.
                
            Returns
            -------
            p_q: numpy.ndarray
                Array of pdf values at the given points. Shape is (1, n).'''
        
        m = self.num_params()
        assert(q.shape[0] == m)
        n = q.shape[1]

        variables = self.variables
        p_q = np.ones([1, n])
        for i, dist in enumerate(variables.values()):
            p_q = p_q * dist.pdf(q[i])
        return p_q
    
    def logpdf(self, q):
        ''' Get the log probability density function values for all variables in the VariableSet at given points.
            
            Parameters
            ----------
            q: numpy.ndarray
                Array of points at which to evaluate the logpdf. Shape should be (m, n) where m is the number of variables
                and n is the number of points.
                
            Returns
            -------
            p_q: numpy.ndarray
                Array of logpdf values at the given points. Shape is (1, n).'''
        
        m = self.num_params()
        assert(q.shape[0] == m)
        n = q.shape[1]

        variables = self.variables
        p_q = np.zeros([1, n])
        for i, dist in enumerate(variables.values()):
            p_q = p_q + dist.logpdf(q[i])
        return p_q

    def cdf(self, q):
        ''' Get the cumulative distribution function values for all variables in the VariableSet at given points.
            
            Parameters
            ----------
            q: numpy.ndarray
                Array of points at which to evaluate the cdf. Shape should be (m, n) where m is the number of variables
                and n is the number of points.
                
            Returns
            -------
            p_q: numpy.ndarray
                Array of cdf values at the given points. Shape is (m, n).'''
        
        m = self.num_params()
        assert (q.shape[0] == m)
        n = q.shape[1]

        variables = self.variables
        p_q = np.empty([m, n])
        for i, dist in enumerate(variables.values()):
            p_q[i,:] = dist.cdf(q[i,:])

    def get_gpc_syschars(self):
        ''' Get the GPC polynomial system characteristic string for all variables in the VariableSet.
            
            Returns
            -------
            syschar: str
                GPC polynomial system characteristic string for the VariableSet.'''
        
        variables = self.variables
        syschar = ''
        for i, dist in enumerate(variables.values()):
            syschar = syschar + dist.get_base_dist().orth_polysys_syschar(True)
        return syschar
    
    def germ2params(self, xi_k_i):
        ''' Convert from germ space to parameter space.
            Parameters
            ----------
            xi_k_i : array_like
                Points in germ space to be converted. Shape is (n, m) where n is the number of points and m is the number of variables.
                
            Returns
            -------
            q_k_i : numpy.ndarray
                Points in parameter space. Shape is (n, m).'''
        
        m = self.num_params()
        assert (xi_k_i.shape[1] == m)
        n = xi_k_i.shape[0]

        params = self.variables
        q_k_i = np.zeros([n, m])
        for i, dist in enumerate(params.values()):
            q_k_i[:, i] = dist.base2dist(xi_k_i[:,i])
        return q_k_i
    
    def params2germ(self, q_k_i):
        ''' Convert from parameter space to germ space.
            Parameters
            ----------
            q_k_i : array_like
                Points in parameter space to be converted. Shape is (n, m) where n is the number of points and m is the number of variables.
                
            Returns
            -------
            xi_k_i : numpy.ndarray
                Points in germ space. Shape is (n, m).'''
        
        m = self.num_params()
        assert (q_k_i.shape[1] == m)
        n = q_k_i.shape[0]

        params = self.variables
        xi_k_i = np.zeros([n, m])
        for i, dist in enumerate(params.values()):
            xi_k_i[:, i] = dist.dist2base(q_k_i[:,i])
        return xi_k_i
    
    def get_bounds(self):
        ''' Get the bounds of all variables in the VariableSet.
            
            Returns
            -------
            bounds: numpy.ndarray
                Array of shape (m, 2) containing the lower and upper bounds for each variable in the VariableSet.'''
        
        m = self.num_params()
        bounds = np.zeros((m, 2))
        for i, dist in enumerate(self.variables.values()):
            bounds[i, :] = dist.get_bounds()
        return bounds

    def sample(self, n, method='MC', random_seed=None, **kwargs):
        ''' Generate samples from the VariableSet using specified sampling method.
            
            Parameters
            ----------
            n: int
                Number of samples to generate.

            method: {'MC', 'QMC_Halton', 'QMC_LHS', 'QMC_Sobol', 'Sobol_saltelli'}, default='MC'
                Sampling method to use. Options: 'MC' (Monte Carlo), 'QMC_Halton' (Quasi-Monte Carlo Halton), 
                'QMC_LHS' (Quasi-Monte Carlo Latin Hypercube), 'QMC_Sobol' (Quasi-Monte Carlo Sobol), 
                'Sobol_saltelli' (Sobol sampling using SALib Saltelli method). Default is 'MC'.

            random_seed: int or None
                Random seed for reproducibility. Default is None.

            **kwargs:
                Additional keyword arguments for specific sampling methods.
                
            Returns
            -------
            q_i_k: numpy.ndarray
                Array of shape (n, m) containing the generated samples in parameter space.'''
        
        m = self.num_params()
        q_i_k = np.zeros([m, n])
        variables = self.variables
        if method == 'MC':
            np.random.seed(random_seed)
            xi = np.random.rand(m,n)
        # QMC methods
        elif method == 'QMC_Halton':
            gen = Halton(m, seed=random_seed)
            xi = gen.random(n).T
        elif method == 'QMC_LHS':
            sampler = LHS(d=m, seed=random_seed)
            xi = sampler.random(n).T
        elif method == 'QMC_Sobol':
            sampler = Sobol(d=m, seed=random_seed)
            xi = sampler.random(n).T
        elif method == 'Sobol_saltelli':
            problem = {'num_vars': m, 'names': self.param_names(), 'dists': self.get_dist_types(), 'bounds': self.get_dist_params()}
            xi = saltelli.sample(problem, n).T
            return xi.transpose()
            
        for i, dist in enumerate(variables.values()):
            q_i_k[i,:] = dist.invcdf(xi[i,:])
            
        return q_i_k.transpose()
    
    def diminished_paramset(self, indices):
        ''' Create a new VariableSet by selecting a subset of variables based on provided indices.
            
            Parameters
            ----------
            indices: list or array_like
                List of indices of variables to include in the new VariableSet.
                
            Returns
            -------
            new_variable_set: VariableSet object
                New VariableSet containing only the selected variables.'''
        
        assert self.num_params() >= len(indices)

        diminished_variable_names = np.array(self.param_names())[indices]
        new_variable_set = VariableSet(normalized=self.normalized)
        new_variables = {}
        for i in range(len(indices)):
            new_variables[diminished_variable_names[i]] = self.variables[diminished_variable_names[i]]
        new_variable_set.variables = new_variables
        return new_variable_set

if __name__ == "__main__":
    from distributions import UniformDistribution, NormalDistribution
    from variable import Variable
    P1 = Variable('p1', UniformDistribution(-2,2))
    P2 = Variable('p2', NormalDistribution(0,2))

    Q = VariableSet()
    Q.add(P1)
    Q.add(P2)

    print(Q.mean())
    print(Q.pdf(np.array([-3, -2, -1, 0, 1, 2, 3]*2).reshape(2, -1).T))
    print(Q.cdf(np.array([-3, -2, -1, 0, 1, 2, 3]*2).reshape(2, -1).T))
    print(Q.get_gpc_syschars())
    print(Q.params2germ(np.array([-3, -2, -1, 0, 1, 2, 3]*2).reshape(2, -1).T))
    print(Q.germ2params(np.array([-2, -1, -0.5, 0, 0.5, 1, 2]*2).reshape(2,-1).T))
    Q.sample(10)
    Q.sample(10, method='MC')

    print(Q.get_bounds())