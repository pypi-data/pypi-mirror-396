from .op import Optimizer

class SGD(Optimizer):
    def __init__(self, learning_rate = 0.01):
        self.learning_rate = learning_rate
    
    def step(self, param):
        for p in param:
            p.data -= self.learning_rate * p.grad
    