#!/bin/bash

#==== remove these later

BENCHMARK_SUITE="merge-spmv"

#====


source custom_queries.sh ## to get remote ssh function

function load_benchsuite_to_remote(){
    local result=$(execute_remote_command ${SSH_NAME} ${SSH_PASSWD} 'if [ -d "$HOME/'$BENCHMARK_SUITE'" ]; then echo "1"; else echo "0"; fi')
    #echo $result
    if [ "$result" == "1" ]; then
        echo "Folder exists on the remote server."
        # Do something when the folder exists
    else
        echo "Folder does not exist on the remote server."
        scp -r ./"$BENCHMARK_SUITE" ${SSH_NAME}:/\$HOME/
    fi
    echo "loading completed!!"
}

function install_intel_cpp_compiler(){
    echo ""
}

function install_klp(){
    echo ""
}

function unzip_benchsuite() {
    # Function to check if a command exists
    function command_exists() {
        command -v "$1" >/dev/null 2>&1
    }

    # Main script
    if ! command_exists unzip; then
        if command_exists apt; then
            echo "Detected APT package manager."
            sudo apt update
            sudo apt install -y unzip
        elif command_exists yum; then
            echo "Detected YUM package manager."
            sudo yum install -y unzip
        elif command_exists dnf; then
            echo "Detected DNF package manager."
            sudo dnf install -y unzip
        else
            echo "Unsupported package manager. Please install unzip manually."
            exit 1
        fi
    else
        echo "Unzip is already installed."
    fi
    execute_remote_command ${SSH_NAME} ${SSH_PASSWD} "cd \$HOME/$BENCHMARK_SUITE && unzip \$HOME/$BENCHMARK_SUITE/matrixes_rcm.zip"
}

function get_all_benchmarks(){
    echo ""
}

SSH_NAME="rt7@127.0.0.1"
SSH_PASSWD="87826c8f"
 
load_benchsuite_to_remote
unzip_benchsuite
echo "completed!!"