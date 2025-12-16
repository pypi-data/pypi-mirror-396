import numpy as np
from mido import MidiFile, MidiTrack, Message
import pygame



class PlaySong:
    def __init__(self):
        pass 
        
        
        
         
    def generate_midi(self,notes, name_of_file):
        """
        Take in a list of notes and generate a midi file
        
        Parameters:
            `notes` - list of notes to be converted into midi file
            `name_of_file` - name of the output midi file
        """ 
        try:


            new_mid = MidiFile()
            new_track = MidiTrack()
            new_mid.tracks.append(new_track)

            for note in notes:
                try:
                    new_track.append(Message('note_on', note=note, velocity=64, time=128))
                except Exception as e:
                        print(f"[WARNING] Failed to add note {note}: {e}")
            new_mid.save(name_of_file)
        
        except Exception as e:
            print(f"[ERROR] Failed to generate MIDI: {e}")
            



    def play_midi(self,name_of_file):
        """
        Play a midi file given its file name
        
        Parameters:
            `name_of_file` - file path to the midi file to be played
        """
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(name_of_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"[ERROR] Failed to play MIDI: {e}")
            
         
          
    
    
    
    
    