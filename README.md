A dictionary utility of self dev py library

## Build
```shell
rm -fr dist
python -m build
# automate by following `-u {user} -p {token / password}`
# api automate by following `-u __token__ -p {token / password}`
python -m twine upload dist/*
```
