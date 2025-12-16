import os
from mido import MidiFile

class MidiDatasetLoader:
    """
    Loads MIDI files from a specified directory and extracts note sequences.

    This class scans a folder for `.mid` and `.midi` files, reads each file
    safely using the `mido` library, and extracts pitch values from all
    `note_on` events with nonzero velocity. Each song is represented as a list
    of integer MIDI pitches. Files that cannot be read or parsed are skipped.

    Attributes
    ----------
    folder_path : str
        Path to the directory containing MIDI files.
    songs : list[list[int]]
        A list of extracted note sequences, one per successfully processed file.
    """
    def __init__(self,folder_path):
        """
        Initialize the dataset loader.

        Parameters
        ----------
        folder_path : str
            Path to the folder containing MIDI files to be processed.
        """
        
        self.folder_path =folder_path
        
        self.songs = self._load_all_songs()
        
    def _load_all_songs(self):
        
        """
        Iterate through all MIDI files in the folder, extract note sequences,
        and aggregate them into `self.songs`.

        Returns
        -------
        list[list[int]]
            A list of note sequences. Each sequence corresponds to one MIDI file.
        """
        songs = []
        midi_files = self._get_midi_files()
        
        for path in midi_files:
            notes=self._extract_notes(path)
            if notes:
                songs.append(notes)
        return songs
    
    def _get_midi_files(self):
        """
        Retrieve all `.mid` or `.midi` files from the specified folder.

        Returns
        -------
        list[str]
            A list of absolute file paths to MIDI files.
        """
        files=[]
        for name in os.listdir(self.folder_path):
            if name.lower().endswith((".mid", ".midi")):
                files.append(os.path.join(self.folder_path, name))  
        
    
        try:
            for name in os.listdir(self.folder_path):
                if name.lower().endswith((".mid", ".midi")):
                    files.append(os.path.join(self.folder_path, name))
        except FileNotFoundError:
            print(f"[ERROR] Folder not found: {self.folder_path}")
        except PermissionError:
            print(f"[ERROR] Permission denied when accessing: {self.folder_path}")
        except Exception as e:
            print(f"[ERROR] Unexpected error accessing folder {self.folder_path}: {e}")
        
        
        return files
    
    def _extract_notes(self,midi_path):
        """
        Extract MIDI note values from a single MIDI file.

        Parameters
        ----------
        midi_path : str
            Full path to the MIDI file.

        Returns
        -------
        list[int]
            A list of MIDI pitch values extracted from all tracks. An empty list
            is returned if the file cannot be read or contains no note events.

        Args:
            midi_path (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            midi = MidiFile(midi_path)
        except Exception as e:
            print(f"[ERROR] Could not read MIDI file {midi_path}: {e}")
            return notes
        notes=[]
        for track in midi.tracks:
            for msg in track:
                if msg.type == "note_on" and msg.velocity >0:
                    pitch = msg.note
                    notes.append(pitch)
        return notes