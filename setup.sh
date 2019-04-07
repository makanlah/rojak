#!/bin/bash

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

python_command="python"
pip_command="pip"
correct_version=`checkPythonVersion $python_command`
if checkPythonVersion $python_command; then
    python_command="python3"
    pip_command="pip3"
    if checkPythonVersion $python_command; then
        echo "Python3 not found."
        exit 1
    fi
    echo "Using python3 instead of python"
fi

$pip_command install -r requirements.txt

mkdir data
curl https://transfer.sh/YnprZ/recipe_raw_data -o data/recipe_raw.tsv

$python_command process_datasets.py -a
