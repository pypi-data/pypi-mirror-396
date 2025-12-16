import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt


class MusicAnalysisError(Exception):
    """Base exception for MusicAnalysis errors."""


class InvalidDataError(MusicAnalysisError):
    """Raised when input data is invalid or empty."""


class InvalidNoteError(MusicAnalysisError):
    """Raised when a note value is out of valid MIDI range (0-127)."""


class MusicAnalysis:
    """
    A class for analyzing musical note data.
    """
    char_dict = char_notes = {
        "C_1": 0,  "CS_1": 1,  "D_1": 2,  "DS_1": 3,  "E_1": 4,  "ES_1": 5,
        "FS_1": 6, "G_1": 7,  "GS_1": 8,  "A_1": 9,  "AS_1": 10, "B_1": 11,
        "BS_1": 12, "CS0": 13, "D0": 14, "DS0": 15, "E0": 16, "ES0": 17,
        "FS0": 18, "G0": 19, "GS0": 20, "A0": 21, "AS0": 22, "B0": 23,
        "BS0": 24, "CS1": 25, "D1": 26, "DS1": 27, "E1": 28, "ES1": 29,
        "FS1": 30, "G1": 31, "GS1": 32, "A1": 33, "AS1": 34, "B1": 35,
        "BS1": 36, "CS2": 37, "D2": 38, "DS2": 39, "E2": 40, "ES2": 41,
        "FS2": 42, "G2": 43, "GS2": 44, "A2": 45, "AS2": 46, "B2": 47,
        "BS2": 48, "CS3": 49, "D3": 50, "DS3": 51, "E3": 52, "ES3": 53,
        "FS3": 54, "G3": 55, "GS3": 56, "A3": 57, "AS3": 58, "B3": 59,
        "BS3": 60, "CS4": 61, "D4": 62, "DS4": 63, "E4": 64, "ES4": 65,
        "FS4": 66, "G4": 67, "GS4": 68, "A4": 69, "AS4": 70, "B4": 71,
        "BS4": 72, "CS5": 73, "D5": 74, "DS5": 75, "E5": 76, "ES5": 77,
        "FS5": 78, "G5": 79, "GS5": 80, "A5": 81, "AS5": 82, "B5": 83,
        "BS5": 84, "CS6": 85, "D6": 86, "DS6": 87, "E6": 88, "ES6": 89,
        "FS6": 90, "G6": 91, "GS6": 92, "A6": 93, "AS6": 94, "B6": 95,
        "BS6": 96, "CS7": 97, "D7": 98, "DS7": 99, "E7": 100, "ES7": 101,
        "FS7": 102, "G7": 103, "GS7": 104, "A7": 105, "AS7": 106, "B7": 107,
        "BS7": 108, "CS8": 109, "D8": 110, "DS8": 111, "E8": 112, "ES8": 113,
        "FS8": 114, "G8": 115, "GS8": 116, "A8": 117, "AS8": 118, "B8": 119,
        "BS8": 120, "CS9": 121, "D9": 122, "DS9": 123, "E9": 124, "ES9": 125,
        "FS9": 126, "G9": 127
    }

    char_notes = (pd.DataFrame([{"note": n, "int": i} for n, i in char_dict.items(
    )]).sort_values("int").reset_index(drop=True))

    def __init__(self, data):
        """
        Initialize the MusicAnalysis with a DataFrame containing music data and ensures
        data is in list format.
        """
        if data is None:
            raise InvalidDataError("Data cannot be None")

        try:
            if isinstance(data, (pd.Series, pd.DataFrame)):
                self.data = data.values.flatten().tolist()
            elif isinstance(data, np.ndarray):
                self.data = data.flatten().tolist()
            elif isinstance(data, (list, tuple)):
                self.data = list(data)
            else:
                raise InvalidDataError(
                    f"Data must be a list, array, or Series, got {type(data).__name__}")
        except Exception as e:
            raise InvalidDataError(
                f"Error converting data to list: {str(e)}") from e

        if len(self.data) == 0:
            raise InvalidDataError("Data cannot be empty")

        try:
            invalid_notes = [note for note in self.data if not isinstance(
                note, (int, float, np.integer, np.floating)) or note < 0 or note > 127]
            if invalid_notes:
                raise InvalidNoteError(
                    f"Found {len(invalid_notes)} invalid note(s). MIDI notes must be between 0-127. First invalid: {invalid_notes[0]}")
        except TypeError as exc:
            raise InvalidNoteError("Data contains non-numeric values") from exc

    def count_notes(self):
        """
        Count the occurrences of each note in the dataset and pair them 
        with the corresponding note names in the Note file.
        """
        if len(self.data) == 0:
            raise InvalidDataError("Cannot count notes on empty data")

        try:
            note_counts = pd.Series(self.data).value_counts().sort_index()
            note_counts.index.name = 'int'
            note_counts = note_counts.reset_index(name='count')
            merged = pd.merge(self.char_notes, note_counts,
                              on='int', how='left').fillna(0)
            merged_counts = merged[['note', 'count']].query('count > 0')

            if merged_counts.empty:
                raise InvalidDataError("No valid notes found in data")

            print(merged_counts)
            return merged_counts
        except Exception as e:
            if isinstance(e, InvalidDataError):
                raise
            raise InvalidDataError(f"Error counting notes: {str(e)}") from e

    def riffs(self):
        """
        Identify and count repeated sequences of notes (riffs) in the dataset.
        """
        if len(self.data) < 3:
            raise InvalidDataError("Need at least 3 notes to identify riffs")

        try:
            patterns = [tuple(self.data[i:i+3])
                        for i in range(len(self.data)-2)]

            if not patterns:
                raise InvalidDataError("No patterns found in data")

            pattern_counts = Counter(patterns)
            max_pattern = max(pattern_counts, key=pattern_counts.get)

            named_pattern = []
            for note in max_pattern:
                matching_notes = self.char_notes.loc[self.char_notes['int']
                                                     == note, 'note']
                if matching_notes.empty:
                    raise InvalidNoteError(
                        f"Note value {note} not found in note mapping")
                named_pattern.append(matching_notes.values[0])

            print(
                f"Most common riff: {'-'.join(named_pattern)} with count {pattern_counts[max_pattern]}")
            return pattern_counts
        except (KeyError, IndexError) as e:
            raise InvalidDataError(f"Error analyzing riffs: {str(e)}") from e

    def pitch(self):
        """
        Calculate the average note value in the dataset, and print the 2 note
        characters on either side of the average value.
        """
        if len(self.data) == 0:
            raise InvalidDataError("Cannot calculate pitch on empty data")

        try:
            avg = round(np.mean(self.data), 3)

            if not (0 <= avg <= 127):
                raise InvalidNoteError(
                    f"Average note {avg} is outside valid MIDI range (0-127)")

            lo = int(np.floor(avg))
            hi = int(np.ceil(avg))
            lo_notes = self.char_notes.loc[self.char_notes['int']
                                           == lo, 'note']
            hi_notes = self.char_notes.loc[self.char_notes['int']
                                           == hi, 'note']

            if lo_notes.empty:
                raise InvalidNoteError(
                    f"Note value {lo} not found in note mapping")
            if hi_notes.empty:
                raise InvalidNoteError(
                    f"Note value {hi} not found in note mapping")

            lo_note = lo_notes.iat[0]
            hi_note = hi_notes.iat[0]

            print(
                f"Average note value is {avg} which is between {lo_note} and {hi_note}")
        except (ValueError, TypeError) as e:
            raise InvalidDataError(f"Error calculating pitch: {str(e)}") from e

    def plot_music(self):
        """
        Plot a bar chart of reversed note values (127 - note) 
        in the order they appear in the sequence.
        """
        if len(self.data) == 0:
            raise InvalidDataError("Cannot plot empty data")

        try:
            data = self.data
            note_positions = range(len(data))
            plt.figure(figsize=(12, 4))
            plt.bar(note_positions, data)
            plt.xticks([0, len(data) - 1], ["Beginning", "End"])
            plt.yticks([0, 127], ["Low Pitch", "High Pitch"])
            plt.xlabel("Note Position")
            plt.ylabel("Pitch")
            plt.title("Pitch Plot of Song")
            plt.tight_layout()
            plt.show()
        except Exception as e:
            raise InvalidDataError(f"Error creating plot: {str(e)}") from e

    def counts_plot(self):
        """
        Plot a bar chart of note counts from the merged DataFrame.
        """
        if len(self.data) == 0:
            raise InvalidDataError("Cannot plot empty data")

        try:
            merged_counts = self.count_notes()

            if merged_counts.empty:
                raise InvalidDataError("No note counts to plot")

            plt.figure(figsize=(12, 6))
            plt.bar(merged_counts['note'], merged_counts['count'])
            plt.xticks(rotation=90)
            plt.xlabel("Note")
            plt.ylabel("Count")
            plt.title("Note Counts")
            plt.tight_layout()
            plt.show()

        except Exception as e:
            if isinstance(e, (InvalidDataError, InvalidNoteError)):
                raise
            raise InvalidDataError(
                f"Error creating counts plot: {str(e)}") from e


music_analysis = MusicAnalysis([60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60,
                                67, 67, 65, 65, 64, 64, 62, 67, 67, 65, 65, 64, 64, 62, 60, 60, 67, 67, 69, 69, 67,
                                65, 65, 64, 64, 62, 62, 60, 67, 67, 74, 74, 76, 76, 74, 72, 72, 71, 71, 69, 69, 67,
                                74, 74, 72, 72, 71, 71, 69, 74, 74, 72, 72, 71, 71, 69, 67, 67, 74, 74, 76, 76, 74,
                                72, 72, 71, 71, 69, 69, 67, 74, 74, 72, 72, 71, 71, 69, 74, 74, 72, 72, 71, 71, 69,
                                67, 67, 74, 74, 76, 76, 74, 72, 72, 71, 71, 69, 69, 67])

music_analysis.count_notes()
music_analysis.riffs()
music_analysis.pitch()
music_analysis.plot_music()
music_analysis.counts_plot()
