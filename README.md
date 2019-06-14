# Rojak

## Requirement(s)

- python3 (and pip3)

## Install + Setup

`./setup.sh -s` (use `-h` for more info on available options)

## Build a new model

`python3 process_datasets.py -a` (only use -a when you need to update the models)

## Share files online (using https://0x0.st/)

`curl -F 'file=@kaggle_epi_dataset.csv' https:/0x0.st`

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
