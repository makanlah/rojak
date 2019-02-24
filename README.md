# First thing to do:

download the raw dataset using this:

`curl https://transfer.sh/YnprZ/recipe_raw_data -o recipe_raw.txt`

go back to cari-makan-ni and run the following to generate the models:

`mkdir data models`

`python process_datasets.py -a` (only use -a when you need to update the models)

# How to share files online (using transfer.sh)
`curl --upload-file raw_data.tsv https://transfer.sh/recipe_raw_data`
