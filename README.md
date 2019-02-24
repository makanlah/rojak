# First thing to do:

download the raw dataset using this:

`mkdir data && curl https://transfer.sh/YnprZ/recipe_raw_data -o data/recipe_raw.tsv`

go back to cari-makan-ni and run the following to generate the models:

`mkdir models`

`python process_datasets.py -a` (only use -a when you need to update the models)

# How to share files online (using transfer.sh)
`curl --upload-file raw_data.tsv https://transfer.sh/recipe_raw_data`

# To run the API endpoint:
`python3 foodRequest.py`

# In Postman:
Do curl http://localhost:5000/todo/api/v1.0/recipes/
Add Body sample:
{
"content":"fried noodles"
}
