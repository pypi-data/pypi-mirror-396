# composerml

## Overview

Datamint is a lightweight Python library for music generation built on a fully custom neural-network engine, inspired by the micrograd repo by Andrej Karpathy  
It contains modular MLP components, training utilities, and a complete pipeline for preparing MIDI data to train a model to generate new music.

### Sub-Package 1 - Models

- Value.py - Just regulars numbers but supports differentiation/gradient calculation

- Neuron.py - A neuron that receives a list of inputs (list of value objects) and produces one output (a value object).

- Layer.py  - A group of neurons working together to produce an output

- MLPnetwork.py  - Builds a multilayer perceptron by stacking layers. Handles forward passes and supports classification or regression depending on configuration.

- MLPMusicGen.py - Inherits MLPnetwork.py. Creates an MLP specific to music generation. Has an additional function call generate_piece that ask the user for a seed/context of music and generate a piece of music of fix length
  
### Sub-Package 2 - Training

- musictrainer.py - this will train our model on music data
- evaluator.py - this module contains helper function to evaluate the model
- Trainer.py - will fit the model using training data, uses helper functions/classes contained in the following sub-folders.
    - Folder 1: Losses Module
        - loss.py - parent class
        - bce_loss.py - binary cross entropy loss
        - ce_loss.py - cross entropy loss function
        - Linear_loss.py  - linear loss function
    - Folder 2: Optimizer Module
        - optimizer.py - parent class
        - SGD.py - stochastic gradient descent
        - musictrainer.py - uses trainer to train the music daya

### Sub-Package 3 - Music Generation

This package provides the complete pipeline for preparing MIDI data, building datasets, and generating or playing music.

- midi_to_dataset.py - Utilities for loading MIDI files and extracting note sequences.  

- music_dataset.py  - Main class that allow the user to input a folder containing midi files and generate a dataset including (features: context-notes) and targets (next note)


- play_song.py  - Once the model generate notes, the user then can initialize this class with the notes, and music will play.

- Analysis.py - analyzes the distribution of the notes output by our network (in the music generation branch)

## Additional Files

Example.ipynb provides an example on how to use this package and the oputput file untrained_Test.mid is the output midifile of our network after training.

You can see the coverage report for our test suite listed in the repository in the coverage_percent.png file 

We implemented github workflow to allow continuous integration. The link to the workflow is provided below.
https://github.com/AequaIis/composerml/tree/main/.github/workflows

To instal and run the package you can run the below code

