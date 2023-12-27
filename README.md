# online-clipboard

[netcut.cn](https://netcut.cn) style, minimal editable online clipboard.

Developed using Flask, Vue 3, Vuetify 3.

## Run

```shell
# Debug
flask run --debug
# Production
FLASK_ENV=production python wsgi.py
```

## Note

### Frontend initailization

```shell
yarn install
yarn dev
yarn build
```

### Backend initailization

```shell
poetry shell
poetry install
flask db init
flask db migrate
flask db upgrade
```
