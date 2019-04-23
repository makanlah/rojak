#!/bin/bash

RED='\033[0;31m'
NC='\033[0m'
python_command="python"
pip_command="pip"
version="3"

# This should be updated to some url in a domain
# where we host this ourselves in the future.
data_url="https://transfer.sh/V7mkg/recipe_raw.tsv"
uuid_url="https://transfer.sh/SkuTv/uuid_dish.npy"

function checkVersion () {
    case "$($1 --version)" in
    *"ython $version."*)
        return 1
        ;;
    *)
        return 0
        ;;
    esac
}

function main () {
    if checkVersion $python_command; then
        python_command="python3"
        if checkVersion $python_command; then
            echo "Python 3 not found."
            exit 1
        fi
        echo "Using python3 instead of python"
    fi

    if checkVersion $pip_command; then
        pip_command="pip3"
        if checkVersion $pip_command; then
            echo "pip for Python 3 not found."
            exit 1
        fi
        echo "Using pip3 instead of pip"
    fi

    # $pip_command install -r requirements.txt
}

function full () {
    echo -e "Running the ${RED}full${NC} setup (including building the model)"
    main
    mkdir data
    curl $data_url -o data/recipe_raw.tsv
    $python_command process_datasets.py -a
}

function short () {
    echo -e "Running the ${RED}short${NC} setup (reuse existing model)"
    main
    curl $uuid_url -o models/uuid_dish.npy
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

option="false"

while getopts :fhsx: opt; do
    option="true"
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
done

if [ $option == "true" ]; then
    exit 0
fi

error "Missing option"