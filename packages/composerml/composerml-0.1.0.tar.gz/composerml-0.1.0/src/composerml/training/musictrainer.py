import numpy as np
from composerml.training.trainer import Trainer
from composerml.models import MLPMusicGen
from composerml.training.losses import *


class MusicTrainer(Trainer):
    """
    Trainer specialized for MLPMusicGen.
    Uses sequences of integer notes and trains on (context_length -> next_note) pairs.
    """

    def __init__(self, model: MLPMusicGen):
        # Use CrossEntropyLoss by default for classification
        super().__init__(model=model,
                         optimizer=None,              
                         loss_fn=CrossEntropyLoss())
        
        
        
            