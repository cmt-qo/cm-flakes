# cm-flakes

This repository contains a code for the paper "Fully automated search for 2D material samples"

Folder 'NeuralNetwork' contains machine learning part of the algorithm created using Tensorflow.
For the minimal use of the algorithm input images of the wafer into the folder 'raw_data' and run the script 'run_me.py'.
Models trained for recognition of hexagonal Boron Nitride flakes are saved in the folder 'models'.
For users who wish to re-train the model (either fully or partially) for another material, the training and evaluation code is 'nn_v0_algo.py'. The detailed readme is provided inside the folder: readme_NN.
