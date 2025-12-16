import random
from composerml.music_generation.midi_to_dataset import MidiDatasetLoader
import numpy as np

class MusicDataset(MidiDatasetLoader):
    def __init__(self, folder_path, context_length=10, shuffle=True, seed=42):
        self.context_length = context_length
        self.shuffle = shuffle
        self.seed = seed

        super().__init__(folder_path)   # must set self.songs as list[list[int]]

        # Build sequences from all songs
        self.x, self.y = self._build_sequences(self.songs, context_length)
        # self.x: list[list[int]]
        # self.y: list[int]

        # One-hot encode inputs + targets
        self.encoded_x = self._one_hot(self.x)       # shape (N, context_length, 128)
        self.encoded_y = np.array(self.y)            # shape (N,)

        if shuffle:
            random.seed(seed)
            indices = list(range(len(self.x)))
            random.shuffle(indices)

            self.x         = [self.x[i] for i in indices]
            self.y         = [self.y[i] for i in indices]
            self.encoded_x = self.encoded_x[indices]
            self.encoded_y = self.encoded_y[indices]

    def _build_sequences(self, songs, context_length):
        """
        songs: list of songs, each song is a list[int] of note ids
        returns:
            X: list[list[int]], where each inner list contains notes equal to the context_length
            Y: list[int]        
        """
        X, Y = [], []

        for song in songs:   # song is a list[int]
            try:
                # Validate song type
                idx = songs.index(song)
                if not isinstance(song, list):
                    raise ValueError(f"Song {idx} is not a list: {song}")
                if len(song) <= context_length:
                    continue

                # sliding windows inside this single song
                for i in range(len(song) - context_length):
                    seq       = song[i:i+context_length]     # a list[int]
                    next_note = song[i+context_length]       # an int
                    X.append(seq)
                    Y.append(next_note)

                # End-of-song token
                X.append(song[-context_length:])
                Y.append(0)
            except Exception as e:
                print(f"[ERROR] Failed processing song index {idx}: {e}")
                continue

        return X, Y

    def _one_hot(self, x):
        """
        x: list[list[int]] of note ids
        returns: np.array of shape (N, context_length, 128)
        """
        I = np.eye(128, dtype=np.float32)
        # For each sequence, map each note id to its one-hot row
        return np.array([I[np.array(seq)] for seq in x])
    
    
