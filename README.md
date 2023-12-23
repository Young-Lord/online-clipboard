# online-clipboard

<netcut.cn> style, minimal editable online clipboard.

Developed using Flask, Vue 3, Vuetify 3.

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
