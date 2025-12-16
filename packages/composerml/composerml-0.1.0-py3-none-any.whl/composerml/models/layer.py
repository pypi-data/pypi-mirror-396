from .neuron import Neuron


class Layer:
    def __init__(self, nin, nout, label="", activation_type="tanh"):
        self.neurons = [
            Neuron(nin, label=f"{label}_n{i}", activation_type=activation_type)
            for i in range(nout)
        ]

    def __call__(self, x):
        outs = [n(x) for n in self.neurons]
        return outs

    def parameters(self):
        """aggregate all parameters from all neurons in this layer"""
        params = []
        for n in self.neurons:
            params.extend(n.parameters())
        return params