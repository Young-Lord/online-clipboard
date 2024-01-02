# online-clipboard

[netcut.cn](https://netcut.cn) style, minimal editable online clipboard.

![Preview image](https://github.com/Young-Lord/online-clipboard/assets/51789698/5178dc37-e64e-4bb1-81a0-b3c59ff42805)

Developed using Flask, Vue 3, Vuetify 3. Full i18n support.

Runs on Node.js v18.16.0, Python 3.11.3.

## Install

1. Install `poetry` and `yarn`.
2. Install Python and Node.js dependencies.

```shell
# Install python dependencies
pushd server
poetry install
popd
# Install nodejs dependencies
pushd frontend
yarn install
popd
```

## Config

1. Edit `server/app/note_const.py`, `server/app/config.py`.
2. Copy `.env.development` to `.env.production` and edit it.
3. Generate `APP_SECRET` as described in `server/app/config.py` and save it to `.env.production`.
4. Init database using `flask db upgrade` in `server` directory.

## Run

First, you need to build frontend files.

```shell
cd frontend
yarn build
```

Then, you can run the server.

```shell
cd server
FLASK_ENV=production poetry run  python wsgi.py
```

## Note

### Debug

```shell
# frontend
cd frontend
yarn dev
# backend
cd server
poetry run flask run --debug
```

### Backend database initailization

```shell
poetry shell
flask db init
flask db migrate
flask db upgrade
```
