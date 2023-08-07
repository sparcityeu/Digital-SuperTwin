#!/bin/bash

echo "[OK] Remote Configuration started!!" 
source custom_queries.sh ## to get remote ssh function


function command_exists() { 
    local result="$(execute_remote_command ${SSH_NAME} ${SSH_PASSWD} 'command -v '$1' 2>/dev/null')"
    echo $result
}

function load_benchsuite_to_remote(){
    
    local result=$(execute_remote_command ${SSH_NAME} ${SSH_PASSWD} 'if [ -d "$HOME/'$BENCHMARK_SUITE'" ]; then echo "1"; else echo "0"; fi')
    if [ "$result" == "1" ]; then
        echo "Folder exists on the remote server."
        # Do something when the folder existsicpc
    else 
        scp -r ./"$BENCHMARK_SUITE" ${SSH_NAME}:/\$HOME/ 
    fi

    if [[ "$(command_exists icpc)" == "" ]]; then
        echo "icpc not found loading binaries..!!"
        scp -r ./"$LIBS/" ${SSH_NAME}:/\$HOME/
    else 
        echo "icpc alread installed !\n"
    fi
    echo "[OK] files transferred!!"
}

function install_intel_cpp_compiler(){
    if [[ "$(command_exists icpc)" != "" ]]; then
        echo "skipping: install_intel_cpp_compiler"
        return 0
    fi
    execute_remote_command ${SSH_NAME} ${SSH_PASSWD} 'cd "$HOME/'$LIBS/'" && pwd && chmod +x ./l_dpcpp-cpp-compiler_p_2023.2.0.49256_offline.sh'
    echo "l_dpcpp-cpp-compiler_p_2023.2.0.49256_offline.sh is being executed!"
    local result=$(execute_remote_command ${SSH_NAME} ${SSH_PASSWD} ' cd "$HOME/'$LIBS/'" && ./l_dpcpp-cpp-compiler_p_2023.2.0.49256_offline.sh -a -s --eula accept')
    execute_remote_command ${SSH_NAME} ${SSH_PASSWD} "echo PATH='\$PATH:\$HOME/intel/oneapi/compiler/2023.2.0/linux/bin/intel64' >> ~/.profile" ## add local paths to $PATH env variable.
    echo "[OK] installation result if any $result"
}

function install_klp(){
    if [[ "$(command_exists icpc)" != "" ]]; then
        echo "skipping: install_klp"
        return 0
    fi
    execute_remote_command ${SSH_NAME} ${SSH_PASSWD} 'cd "$HOME/'$LIBS/'" && pwd && chmod +x ./l_onemkl_p_2023.2.0.49497_offline.sh'
    echo "l_onemkl_p_2023.2.0.49497_offline.sh is being executed!"
    local result=$(execute_remote_command ${SSH_NAME} ${SSH_PASSWD} ' cd "$HOME/'$LIBS/'" && ./l_onemkl_p_2023.2.0.49497_offline.sh -a -s --eula accept')
    echo "[OK] installation result if any $result"
}

function unzip_benchsuite() {
    # Function to check if a command exists
    # Main script
    if [[ "$command_exists unzip" == "" ]]; then
        if [[ "$command_exists apt" != "" ]]; then
            echo "Detected APT package manager."
            sudo apt update
            sudo apt install -y unzip
        elif [[ "$command_exists yum" != "" ]]; then
            echo "Detected YUM package manager."
            sudo yum install -y unzip
        elif [[ "$command_exists dnf" != "" ]]; then
            echo "Detected DNF package manager."
            sudo dnf install -y unzip
        else
            echo "Unsupported package manager. Please install unzip manually."
            exit 1
        fi
    else
        echo "Unzip is already installed."
    fi
    execute_remote_command ${SSH_NAME} ${SSH_PASSWD} "cd \$HOME/$BENCHMARK_SUITE ; unzip -n \$HOME/$BENCHMARK_SUITE/matrixes.zip"
    echo "[OK] Unzipping benchsuite is completed"
}

function compile_bench_suite(){
    execute_remote_command ${SSH_NAME} ${SSH_PASSWD} "cd \$HOME/$BENCHMARK_SUITE && make cpu_spmv"
    echo "[OK] compilation done"
}
 
function get_suit_matrix_names(){ 
    local result=$(execute_remote_command ${SSH_NAME} ${SSH_PASSWD} "cd \$HOME/$BENCHMARK_SUITE/ && find ./matrixes/ -name \*.mtx -exec ls {} \\;")
    echo -e "${result}"
}   
echo "Remote Configuration Begun!!"


load_benchsuite_to_remote
unzip_benchsuite
install_intel_cpp_compiler # 2gb
install_klp
compile_bench_suite

echo "[OK] Remote Configuration completed!!"