## This script defines the estimation process to be performed for each workload
## application 

import padasip as pa
import numpy as np

class AdaptationEngine():

    def __init__(self, mu=0.99, w="random", current_x = None, current_inputs = None):
        self.mu = mu
        self.w = w
        self.alpha_bc = w[1]
        self.beta_bc = w[0]
        self.alpha = w[1]
        self.beta = w[0]
        self.change = False
        self.RLS = pa.filters.FilterRLS(n=2, mu = self.mu, w=self.w) 
        if current_x and current_inputs:
            self.RLS.run(current_x, current_inputs)

    def update_parameters(self, cpus, ttf):
        self.u = 1.0/(cpus)
        self.d = ttf
        self.RLS.adapt(self.d, np.array([self.u, 1.0]))
        self.errors()
        if self.change == True:
            if abs(self.error) > abs(self.errors_bc):
                print 'TRUE: use of old parameters'
                self.define_param(False)
            else:
                print 'TRUE: use of current estimated parameters'
                self.define_param(True)
            self.evaluate_abs_error_param()
            if self.abs_error > 20:
                self.change = False
                print 'CHANGE : FROM TRUE SET TO FALSE'
        else:
            if self.abs_error > 15:
                self.change = True
                print 'CHANGE SET TO TRUE'
            else:
                self.alpha_bc = self.RLS.w[1]
                self.beta_bc = self.RLS.w[0]
                print 'new alpha and beta defined'
            self.define_param(True)          

    def errors(self):
        ## Errors considering as parameters the current values given by the estimator
        self.value = self.RLS.w[0]*self.u + self.RLS.w[1]
        self.error = self.d - self.value
        self.abs_error = abs(self.error/self.d)*100
        self.errors_bc = self.d - self.beta_bc*self.u - self.alpha_bc

    def evaluate_abs_error_param(self):
        self.value = self.beta*self.u + self.alpha
        self.error = self.d - self.value
        self.abs_error = abs(self.error/self.d)*100

    def get_beta_bc(self):
        return self.beta_bc
      
    def get_beta_hat(self):
        return self.RLS.w[0]

    def get_alpha_hat(self):
        return self.RLS.w[1]

    def get_beta(self):
        return self.beta

    def get_error(self):
        return self.error

    def define_param(self, value):
        if value == True:
            self.alpha = self.RLS.w[1]
            self.beta = self.RLS.w[0]
        else:
            self.beta = self.beta_bc
            self.alpha = self.alpha_bc

    def get_param(self):
        return self.alpha, self.beta

    def get_param_bc(self):
        return self.alpha_bc, self.beta_bc

    def get_param_hat(self):
        return self.RLS.w


