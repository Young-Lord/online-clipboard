# online-clipboard

[netcut.cn](https://netcut.cn) style, minimal editable online clipboard.

Developed using Flask, Vue 3, Vuetify 3.

## Run

```bash
# Debug
flask run --debug
# Production
FLASK_ENV=production python wsgi.py

## Note

### Frontend

```bash
yarn install
yarn dev
yarn build
```

### Backend

```bash
poetry install
poetry run flask db init
poetry run flask db migrate
poetry run flask db upgrade
poetry run flask run
```
