#!/bin/bash

mkdir -p ~/.config/fdes
mkdir -p ~/.local/share/fdes
cp conf/fdesrc ~/.config/fdes/
sudo cp src/fdes.py /usr/bin/fdes
