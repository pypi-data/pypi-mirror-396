from composerml.models import MLPNetwork
from composerml.training.losses import *
from composerml.training.optimizer import *
import random


class Trainer:
    def __init__(self, model: MLPNetwork, optimizer = None, loss_fn = None):
        """
        Parameters:
        model: instance of any model (default is MLPNetwork)
        learning_rate: learning rate for optimizer
        epochs: number of training epochs
        optimizer: optimization algorithm to use ("SGD" supported)
        """
        
        self.model = model

        # Initialize optimizer 
        self.optimizer = optimizer if optimizer is not None else SGD(learning_rate=0.01)

        # Initialize loss 
        self.loss_fn = loss_fn if loss_fn is not None else LinearLoss()

        

        # Logging
        if model.classification != "none":
            print(
                f"Trainer initialized for classification task using {type(self.loss_fn).__name__} loss."
            )
        else:
            print(
                f"Trainer initialized for regression task using {type(self.loss_fn).__name__} loss."
            )


        
    def fit(self, X, y, batch_size=1, epochs=100):
        """
        Parameters:
        X: list of input samples, each sample is a list of Values or floats/ints
        y: list of target values (floats/ints)
        batch_size: number of samples per batch for training
        
        Trains the model using mini-batch gradient descent.
        """
        n = len(X)
        
        # Training loop
        for epoch in range(epochs):
            indices = list(range(n))
            random.shuffle(indices)

            epoch_loss = 0.0
            
            # Mini-batch training
            for start in range(0, n, batch_size):
                end = min(start + batch_size, n)
                batch_idx = indices[start:end]
                
                # Zero gradients before processing the batch
                self.model.zero_grad()

                batch_losses = []
                
                #Calculate loss for each sample in the batch
                for i in batch_idx:
                    inputs = X[i]
                    target = y[i]

                    outputs = self.model.predict(inputs) 

                    loss = self.loss_fn(outputs, target)
                    batch_losses.append(loss)
                    epoch_loss += loss.data

                # Compute average loss for the batch and backpropagate to get gradients
                batch_loss = sum(batch_losses) / len(batch_losses)
                batch_loss.backward()
                
                # Update model parameters
                self.optimizer.step(self.model.parameters())
                
            # Monitor average loss for the epoch
            epoch_loss /= n

            if (epoch + 1) % 20 == 0 or epoch == 0 or epoch == epochs-1:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss:.4f}")
    
    def test(self, X, y):
        from .evaluator import evaluate
        return evaluate(self.model, X, y, self.loss_fn)
    
    
        
        
    



