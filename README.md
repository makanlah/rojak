# Cari Makan-ni

## Requirement(s)

- python3 (and pip)

## Install + Setup

`./setup.sh`

## Build a new model

`python3 process_datasets.py -a` (only use -a when you need to update the models)

## Share files online (using transfer.sh)

`curl --upload-file raw_data.tsv https://transfer.sh/recipe_raw_data`

## Run the API endpoint

`python3 foodRequest.py`

## Test in Postman

`curl http://localhost:5000/todo/api/v1.0/recipes/`

Add Body sample:

```json
{
    "content":"fried noodles"
}
```