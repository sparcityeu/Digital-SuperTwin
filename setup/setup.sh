#!/usr/bin/env bash

export PYTHON_VERSION="3.10"
export LOGGING_LEVEL="INFO"


echo "Installing python"$PYTHON_VERSION" and pip"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        . /etc/os-release
        if [[ "$ID" == "ubuntu" ]]; then
            sudo apt update &&
            sudo apt install software-properties-common &&
            sudo add-apt-repository ppa:deadsnakes/ppa &&
            sudo apt install "python"$PYTHON_VERSION && 
            sudo apt-get -y install python3-pip

        elif [[ "$ID" == "manjaro" ]]; then
            pacman -U $PYTHON_VERSION
        fi

elif [[ "$OSTYPE" == "darwin"* ]]; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" &&
        brew install "python@"$PYTHON_VERSION
        curl -O https://bootstrap.pypa.io/get-pip.py && sudo python3 get-pip.py
else
    echo "your operating system is not supported"
    exit 1
fi


echo "Installing the necessary pip packages"

pip3 install -r ../requirements.txt
pip3 install distro

echo "Calling python setup script"

python$PYTHON_VERSION main.py

