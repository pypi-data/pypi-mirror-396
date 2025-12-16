import unittest
from music_dataset_test import TestMusicDataset
from analysis_test import TestMusicAnalysis
from layer_test import TestLayer
from MLPMusicGen_test import TestMLPMusicGen
from MLPnetwork_test import TestMLPNetwork
from neuron_test import TestLayer
from pretrain_model_test import TrainedMusicGen
from value_test import TestValue
from trainer_test import TestTrainer
from play_song_test import TestPlaySong
from midi_to_dataset_test import TestMidiToDataset

## Implement a test suite
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMusicAnalysis))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMusicDataset))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestLayer))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMLPMusicGen))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMLPNetwork))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TrainedMusicGen))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestValue))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestTrainer))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPlaySong))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMidiToDataset))
    runner = unittest.TextTestRunner()
    print(runner.run(suite))

suite()