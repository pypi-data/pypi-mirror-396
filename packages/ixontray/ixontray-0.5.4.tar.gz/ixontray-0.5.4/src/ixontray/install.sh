#!/bin/bash
# Install dependecies for qt6
sudo apt-get -qq install libegl1 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxkbcommon-x11-0
pipx install --force -e .
