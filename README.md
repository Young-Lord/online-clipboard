# online-clipboard

[netcut.cn](https://netcut.cn) style, minimal editable online clipboard.

![Preview image](https://github.com/Young-Lord/online-clipboard/assets/51789698/5178dc37-e64e-4bb1-81a0-b3c59ff42805)

Developed using Flask, Vue 3, Vuetify 3, TypeScript. Full i18n support.

Runs on Node.js v18.16.0, Python 3.11.3.

## Install

1. Install `poetry` and `yarn`.
2. Install Python and Node.js dependencies.

```shell
# Install python dependencies
pushd server
poetry install --no-root
popd
# Install nodejs dependencies
pushd frontend
yarn install
popd
```

## Config

1. Edit `server/app/note_const.py`, `server/app/config.py`.
2. Copy `.env.development` to `.env.production` and edit it. Also edit `.env` if needed.
3. Generate `APP_SECRET` as described in `server/app/config.py` and save it to `.env.production`.
4. Init database using `flask db upgrade` in `server` directory.
5. Modify `server/app/__init__.py` and configure `ProxyFix` if you are deploying behind a reverse proxy.

## Run

First, you need to build frontend files.

```shell
cd frontend
yarn build
```

Then, you can run the server.

```shell
cd server
FLASK_ENV=production poetry run python wsgi.py
# PowerShell: $env:FLASK_ENV='production'; poetry run python wsgi.py
```

## Note

### Use with curl

```shell
# Get clip named my_clip
curl http://example.com/raw/my_clip?pwd=my_password
```

### Debug

```shell
# frontend
cd frontend
yarn dev
# backend
cd server
poetry run python wsgi.py --debug
```

### Backend database initailization

```shell
poetry shell
flask db init
flask db migrate
flask db upgrade
```

### Security

Password protect: `sha512(note.password)` through Internet, `pbkdf2_sha256(sha512(note.password))` in database.

File access: JWT generated with `note.name` and `pbkdf2_sha256(sha512(note.password))` (the hash stored in database as above)

Content encryption: AES-256-CBC/PKCS7 with `sha256(note.password)`, see [CryptoJS behaviour](https://stackoverflow.com/a/64802091)

### IIS

Example rule:

```xml
<?xml version="1.0" encoding="UTF-8"?> 
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <clear />
                <rule name="clip" stopProcessing="true">
                    <match url="^clip-basepath((/(.+)?)|)$" />
                    <conditions logicalGrouping="MatchAll" trackAllCaptures="false">
                        <add input="{CACHE_URL}" pattern="^(.+)?://.+$" />
                    </conditions>
                    <action type="Rewrite" url="{C:1}://127.0.0.1:5000{R:1}" />
                    <serverVariables>
                        <set name="HTTP_SEC_WEBSOCKET_EXTENSIONS" value="" />
                    </serverVariables>
                </rule>
            </rules>
        </rewrite>
        <security>
            <requestFiltering>
                <requestLimits maxAllowedContentLength="209715200" />
            </requestFiltering>
        </security>
    </system.webServer>
</configuration>
```

#### URL Rewrite

- Download and install [URL Rewrite](https://www.iis.net/downloads/microsoft/url-rewrite)
- Regex pattern: `^clip-basepath((/(.+)?)|)$`
- Conditions -> Condition Input: `{CACHE_URL}`
- Conditions -> Pattern: `^(.+)?://.+$`
- Server variable -> name: `HTTP_SEC_WEBSOCKET_EXTENSIONS`; value: (set to empty by editing `web.config`);
- Rewrite URL: `{C:1}://127.0.0.1:5000{R:1}`
- Append query string: `true`

#### Upload size limit

[How to set URL length and HTTP POST content length limits in IIS - WKB240363](https://support.waters.com/KB_Inf/NuGenesis/WKB240363_How_to_set_URL_length_and_HTTP_POST_content_length_limits_in_IIS)

#### WebSocket Server

Clip uses [Socket.IO](https://socket.io/) to support Instant Sync feature, which allows multi users to edit together. A WebSocket server will run on the same port of backend Flask server.

- [使用IIS做HTTP和WebSocket服务的反向代理](https://web.archive.org/web/20190406124734/https://imxieyi.com/2017/11/17/%E4%BD%BF%E7%94%A8iis%E5%81%9Ahttp%E5%92%8Cwebsocket%E6%9C%8D%E5%8A%A1%E7%9A%84%E5%8F%8D%E5%90%91%E4%BB%A3%E7%90%86/)
- [Websocket based website behind a reverse proxy in IIS - Server Fault](https://serverfault.com/a/1038787)
