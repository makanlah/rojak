#!/bin/bash

RED='\033[0;31m'
NC='\033[0m'
python_command="python"
pip_command="pip"

function checkPythonVersion () {
    case "$($1 --version 2>&1)" in
    *" 3."*)
        return 1
        ;;
    *)
        return 0
        ;;
    esac
}

function checkPIPVersion () {
    case "$($1 --version 6>&1)" in
    *" 3."*)
        return 1
        ;;
    *)
        return 0
        ;;
    esac
}

function main () {
    if checkPythonVersion $python_command; then
        python_command="python3"
        if checkPythonVersion $python_command; then
            echo "Python3 not found."
            exit 1
        fi
        echo "Using python3 instead of python"
    fi

    if checkPIPVersion $pip_command; then
        pip_command="pip3"
        if checkPIPVersion $pip_command; then
            echo "pip for Python3 not found."
            exit 1
        fi
        echo "Using pip3 instead of pip"
    fi

    $pip_command install -r requirements.txt
}

function full () {
    echo -e "Running the ${RED}full${NC} setup (including building the model)"
    main
    mkdir data
    curl https://transfer.sh/V7mkg/recipe_raw.tsv -o data/recipe_raw.tsv
    $python_command process_datasets.py -a
}

function short () {
    echo -e "Running the ${RED}short${NC} setup (reuse existing model)"
    main
    curl https://transfer.sh/SkuTv/uuid_dish.npy -o models/uuid_dish.npy
    # missing url for names_counter.npy
    $python_command process_datasets.py
}

function help () {
    cat << EOF
usage:
-f  All (including model rebuild)
-h  Show help (this menu)
-s  Short (reuse prebuilt model)
EOF
}

function error () {
    echo $@
    echo "use \"-h\" for more description"
    exit 1
}

while getopts :fhsx: opt; do
    case $opt in
        f)
            full
            ;;
        h)
            help
            ;;
        s)
            short
            ;;
        * )
            error "Invalid option: -$OPTARG" >&2
            ;;
    esac
    exit 0
done

error "Missing option"