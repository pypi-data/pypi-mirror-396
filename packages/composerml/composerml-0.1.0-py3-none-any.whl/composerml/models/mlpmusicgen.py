from .mlpnetwork import MLPNetwork
import numpy as np
from mido import MidiFile, MidiTrack, Message

class SeedError(Exception):
    """Custom exception to indicate that the seed length is insufficient."""
    pass

class MLPMusicGen(MLPNetwork):
    def __init__(self, context_length =10, hidden_sizes = [64,64], activation_type="tanh"):
        super().__init__(
            input_dim= context_length*128,
            n_neurons= hidden_sizes + [128],
            activation_type = activation_type,
            classification = "softmax"
        )
        
        self.context_length = context_length
        
    def _make_onehot(self, indicies, total=128):
        """
        Convert indicies into one-hot vectors by
        first creating an identity matrix of shape [total, total],
        then indexing the appropriate columns of that identity matrix.

        Parameters:
            `indices` - a numpy array of some shape where
                        the value in these arrays should correspond to category
                        indices (e.g. note values between 0-127)
            `total` - the total number of categories (e.g. total number of notes)

        Returns: a numpy array of one-hot vectors
            If the `indices` array is shaped (N,)
            then the returned array will be shaped (N, total)
            If the `indices` array is shaped (N, D)
            then the returned array will be shaped (N, D, total)
            ... and so on.
        """
        I = np.eye(total)
        return I[indicies]

    
    
    def generate_piece(self, file_name = None, song_part = None, max_len=100,):
        """
        Generate a piece of music after asking the user for a inspiration piece 
        The user can specify how much portion of the generation piece they want to use

        Parameters:
            `file_name` - path to a midi file to use as inspiration.
            `song_part` - fraction of the song to use as seed (between 0 and 1)
            `max_len` - maximum number of total notes in the piece.

            Returns: a list of sequence of notes with length at most `max_len`
            """
        # Load notes    
        if file_name is not None:
            seed = self.get_midi_file_notes(file_name)
        else:
            try:
                file_name = input("Input a song in MIDI format as inspiration: ")
                seed = self.get_midi_file_notes(file_name)
            except Exception as e:
                print(f"Error loading MIDI file: {e}")
                return []

        # Ask user how much of the song to use as seed
        if song_part is None:
            try:
                song_part = input("How much of the song do you want to use (0–1)? ")
                song_part = float(song_part)
                assert 0 < song_part <= 1
            except:
                raise ValueError("Please enter a number between 0 and 1.")

        
        

        # Take the first fraction of the song
        cutoff = int(len(seed) * song_part)
        seed = seed[:cutoff]

        # Ensure context is long enough
        if len(seed) <= self.context_length:
            raise SeedError("Seed length is insufficient. Please provide a longer seed or use a larger song_part value.")
        
        if len(seed) > max_len:
            raise Warning("Seed length exceeds max_len, model will return original seed/song only.")
                

        generated = seed #tracking the number of notes
        while len(generated) < max_len:
            # Use the model to predict the next note given the previous CONTEXT_LENGTH notes
            last_n_notes = generated[-self.context_length:]
            x = self._make_onehot(last_n_notes).reshape((1, -1)) #concat all the notes
            x = x.flatten().tolist()

            y = self.predict(x) # return a list of probabilities for the best next notes

            probabilities = [val.data for val in y]
            next_note = probabilities.index(max(probabilities))

            if next_note == 0:  # Look for the marker for the end of the song
                break
            generated.append(next_note)


        return generated
    
    
    def predict(self, x):
        """
        Override predict so that:
        - x can be a nested list (list of lists, etc.), because it is aone hot encoded list of notes
        - flatten it automatically before calling parent.predict()
        """
        # Convert to numpy array so we can flatten cleanly
        x = np.array(x).flatten().tolist()

        # Call parent MLPNetwork.predict
        return super().predict(x)
    
    
    
    def get_midi_file_notes(self,filename):
        """Returns the sequence of notes played in the midi file
        There are 128 possible notes on a MIDI device, and they are numbered 0 to 127.
        The middle C is note number 60. Larger numbers indiciate higher pitch notes,
        and lower numbers indicate lower pitch notes.
        """
        notes = []
        for msg in  MidiFile(filename):
            if msg.type == 'note_on':
                notes.append(msg.note)
        return notes
    
    