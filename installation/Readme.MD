# Installation

The game engine is built in Python, using the Pygame and NumPy packages.

Pygame is a 32-bit package. You will need a 32-bit version of Python. We use Python 2.7.

## Macintosh OSX 10.7 and above 

(For Mojave see the Anaconda instructions below)

1. brew install python
2. pip install numpy
3. pip install --upgrade pip setuptools
4. pip install pygame

## Linux Fedora

1. sudo yum install numpy
2. sudo yum install pygame pygame-devel

## Linux Mint

1. Get Python 2.7.6
2. sudo apt-get install python-pygame
3. sudo apt-get install python numpy

## Windows

1. Install Python (version 2.7.x recommended) [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. pip install numpy
3. pip install pygame

# Run the basic game engine

```python runbasic.py```

# Anaconda

We provide an Anacoda YAML file to provide a clean python environment in which to run the game engine. This Anacoda environment also helps with issues with MacOSX Mojave.

1. Download miniconda or anaconda for Mac  
2. Save environment_gameai_yml.yaml to a directory of your choice
3. Run the following in the directory you saved the YAML file
```conda env create -f environment_gameai_yml.yaml```
4. Start the environment:
```source activate gameai```
