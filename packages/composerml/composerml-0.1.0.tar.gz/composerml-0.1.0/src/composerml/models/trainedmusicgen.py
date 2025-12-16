import os
import sys


from composerml.models.mlpmusicgen import MLPMusicGen

class TrainedMusicGen(MLPMusicGen):
    """
    Creating a model with 100 hidden units and loading pre-trained parameters
    """
    def __init__(self, model_path = "param.txt"):
        
        # Getting the absolute path of folder where this script is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_file = os.path.join(base_dir, model_path)

        super().__init__(context_length=20, hidden_sizes= [100], activation_type="relu")
        self.load_model(model_file)
    
    def load_model(self, model_path ):
        curr_param = self.parameters()

        try:
            with open(model_path, "r") as f:
                pre_trained_params = [float(line.strip()) for line in f]
        except FileNotFoundError:
            print(f"Model file not found at {model_path}")
            sys.exit(1)


        try: 
            for i, p in enumerate(curr_param):
                p.data = pre_trained_params[i]
        except Exception as e:
            print(len(pre_trained_params), len(list(curr_param)))
        else: 
            print("Model parameters loaded successfully.")

if __name__ == "__main__":
    model = TrainedMusicGen("param.txt")
    
    