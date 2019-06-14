# Rojak

## Requirement(s)

- python3 (and pip3)

## Install + Setup

`./setup.sh -s` (use `-h` for more info on available options)

## Share files online (using https://0x0.st/)

`curl -F 'file=@kaggle_epi_dataset.csv' https:/0x0.st`
Returns a url to download it: `https://0x0.st/zQIn.csv`
To download: simply do `curl https://0x0.st/zQIn.csv -o [output file name]`

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

## To test Rojak Search manually
`from Rojak import Rojak`
`rojak = Rojak()`
`rojak.search("spicy curry chicken with vegetable")`
Returns array with at max 10 dishes `[...]`
