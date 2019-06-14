# Rojak

## Requirement(s)

- python3 (and pip3)

## Install + Setup

`./setup.sh -s` (use `-h` for more info on available options)

## Run the API endpoint

`python3 foodRequest.py`

## Test in Postman

`curl http://localhost:5000/todo/api/v1.0/recipes/`

Add Body sample:

```json
{
    "content": "fried noodles"
}
```

## To test Rojak Search manually

```python
from RojakCore import KnowledgeGraph
rojak = KnowledgeGraph()
rojak.search("spicy curry chicken with vegetable")
```

Returns array of 10 recipes `[...]`

