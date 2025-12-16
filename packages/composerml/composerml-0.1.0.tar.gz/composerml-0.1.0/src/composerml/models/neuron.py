import random
from .value import Value

class Neuron:
    def __init__(self, nin, label = "", activation_type = 'tanh'):
        #receive a sets of weights
        self.w = [Value(random.uniform(-1,1), label = f"{label}_w_{i}") for i in range(nin)]
        #bias
        self.b = Value(random.uniform(-1, 1), label=f"{label}_b")
        self.activation_type = activation_type
        self.nin = nin
        
    
    def __call__(self,x):
        
        x_val = [Value._as_value(x[i]) for i in range(self.nin)]
        
        out = self.b
        
        for wi,xi in zip(self.w, x_val):
            out = out + wi*xi
        
        if self.activation_type == "tanh":
            out = out.tanh()
        elif self.activation_type == "relu":
            out = out.relu()

        
        return out
    
    def parameters(self):
        """ aaggregate all parameters of the neuron"""
        return self.w + [self.b]