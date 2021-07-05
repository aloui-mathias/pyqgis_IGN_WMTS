# IGN ORTHOIMAGERY acces with QGIS

A small script to download an image from the ORTHOIMAGERY database of the IGN (Institut national de l'information géographique et forestière).

# Installation

To use this script, you need the python version of QGIS available with anaconda.

```
# Creation of the conda environment
conda env create -f environment.yml
```

# How to use

You can print the script usage with the command :

```
python generate_tiff.py --help
```

For example if we want an image of the Eiffel tower with coordinates from a map in EPSG:4326 projection :

```
python generate_tiff.py 2.2931322 48.8572656 2.2966832 48.8590224 --epsg 4326
```

Result (from --display option):

![Figure_1](https://user-images.githubusercontent.com/43454650/124477719-a0f94d80-dda4-11eb-9c56-4392d85970c9.png)
