# cm-flakes

This repository contains a code for the paper "Fully automated search for 2D material samples"

Folder 'NeuralNetwork' contains machine learning part of the algorithm created using Tensorflow.
For the minimal use of the algorithm input images of the wafer into the folder 'raw_data' and run the script 'run_me.py'.
Models trained for recognition of hexagonal Boron Nitride flakes are saved in the folder 'models'.
For users who wish to re-train the model (either fully or partially) for another material, the training and evaluation code is 'nn_v0_algo.py'. The detailed readme is provided inside the folder: readme_NN.

To perform a scan of a chip run the file GlovBox.py (in the folder GloveBox).

The imported modules / classes can be found in the following files:
Camera.py (in the folder Camera) contains the class which handles the captrue of images via screenshots.
Ivecon.py (in the folder Microscope) contains the class which controls the microscope e.g. the height and magnification of the objective.
maerzhaeuser.py (in the folder Stage) controls the stage e.g. the x- and y-position.
UserInterface.py (in the folder UserInterface) handles the userinterface.

To run neural net classification in parallel to the scan run NeuralNetwork/run_me.py and GloveBox/GlovBox.py at the same time.

NOTE: currently the file Microscope/lvecon.py is missing driver 'Nikon.LvMic.NikonLv'. The driver can be requested via Nikon developer program (https://sdk.nikonimaging.com/apply/) or should be replaced by the specific driver for the microscope your lab is using.
