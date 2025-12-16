from .value import Value
from .layer import Layer

class MLPNetwork:
    def __init__(self, input_dim, n_neurons, label="", activation_type="tanh", classification="none"):
        """
        input_dim:      number of input features (int)
        n_neurons:      list containing number of neurons in each layer, e.g. [16, 8, 1]
        label:          string to label the network / layers
        activation_type:activation function to use in hidden layers (e.g. "tanh", "relu")
        classification: "none", "softmax" (multi-class), "sigmoid" (single-output binary)    
        """
        self.classification = classification
        self.input_dim = input_dim
        sizes = [input_dim] + n_neurons
        

        # Build layers: all hidden layers get activation; last layer is linear
        self.layers = [
            Layer(
                sizes[i],
                sizes[i + 1],
                label=f"{label}_L{i}",
                activation_type=activation_type if i < len(n_neurons) - 1 else None
            )
            for i in range(len(n_neurons))
        ]

    def predict(self, x):
        """
        Parameters:
        x: list of input features (floats/ints/Values) with length equal to input_dim
        
        Returns:
        predicted outputs as list of Values
        """
        # If the input dimension does not match, raise error
        if len(x) != self.input_dim:
            raise ValueError(f"Input dimension {len(x)} does not match network input dimension {self.input_dim}.")
        

        # Pass through all layers
        for layer in self.layers:
            x = layer(x)

        # x is now list[Value] representing final layer outputs (logits)
        if self.classification == "softmax":
            x = self.softmax(x)

        elif self.classification == "sigmoid":
            x = self.sigmoid(x)

        return x

    def parameters(self):
        """Aggregate all parameters from all layers."""
        params = []
        for layer in self.layers:
            params.extend(layer.parameters())
        return params
    
    def gradients(self):
        """Return all gradients from all parameters."""
        grads = []
        for p in self.parameters():
            grads.append(p.grad)
        return grads

    @staticmethod
    def softmax(vals):
        # vals: list[Value]
        exps = [v.exp() for v in vals]
        total = exps[0]
        for e in exps[1:]:
            total = total + e
        return [e / total for e in exps]

    @staticmethod
    def sigmoid(vals):
        # vals: list of values
        res = [1 / (1 + (-x).exp()) for x in vals]
        return res

    def zero_grad(self):
        """Set all gradients to zero; call before/after each learning step."""
        for p in self.parameters():
            p.grad = 0.0