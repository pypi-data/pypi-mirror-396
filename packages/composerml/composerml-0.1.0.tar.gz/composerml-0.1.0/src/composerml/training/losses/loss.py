import math

class Loss:
    def __call__(self, predicted, actual):
        """Compute loss based on model type"""
        raise NotImplementedError("This method should be overridden by subclasses")
