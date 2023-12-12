<template>
      <v-app>
        <v-content>
            <v-container grid-list-xs fill-height v-if="hasLogin === true" class="clip-page">
        <v-layout row class="">
          <v-flex xs12>
            <div id="board" class="board pa-3" v-chat-scroll="{ always: false, smooth: true }">
              <div class="mt-3" v-for="(m, i) in msg" v-bind:key="i">
                <code class="code" v-html="m" @click="doCopy(m)"></code>
              </div>
            </div>
            <div class="mt-4">
              <v-layout row wrap>
                <v-flex xs12>
                  <v-textarea solo v-model="inputMsg" @keyup.ctrl.enter="send"
                    placeholder="输入内容, 按 Ctrl + Enter 或者 Command + Return 发送, 最多支持50条记录." autofocus
                    no-resize></v-textarea>
                </v-flex>
                <v-flex xs12>
                  <v-btn block color="info" @click="send">
                    发送
                  </v-btn>
                </v-flex>
              </v-layout>
            </div>
          </v-flex>
        </v-layout>
      </v-container>
    </v-content>
<v-snackbar v-model="snackbarSuccess" :top="true" :vertical="false" :multi-line="false" :color="'success'"
      :timeout="2000">
      复制成功
    </v-snackbar>
<v-snackbar v-model="snackbarFail" :top="true" :vertical="false" :multi-line="false" :color="'danger'"
      :timeout="2000">
      复制失败
    </v-snackbar>
      </v-app>
</template>

<script>
export default {
    components: {
    },
    data() {
        return {
            hasLogin: false,
            loginBtnDisable: false,
            wsUrl: `${protocol}://${hostname}/ws`,
            cbName: null, // clipboard name
            cbPass: null, // clipboard pass
            ws: null,
            msg: [],
            inputMsg: null,
            isLogining: false,
            interval: null,
            thingsToCopy: null,
            snackbarSuccess: false,
            snackbarFail: false,
        }
    },
    created() {
        this.doLogin();
        let that = this;
        window.onhashchange = function (event) {
            window.location.href = event.newURL;
            that.doLogin();
        }
    },
    methods: {
        login() {
            if (this.cbName === null || this.cbPass === null) return;
            if (this.ws) this.ws.close();
            this.ws = new window.WebSocket(`${this.wsUrl}/${this.cbName}/${this.cbPass}`);
            this.ws.onopen = this.onopen;
            this.ws.onmessage = this.onmessage;
            this.ws.onclose = this.onclose;
            this.ws.onerror = this.onerror;
            this.isLogining = true;
            this.loginBtnDisable = true;
            document.location.hash = "/" + this.cbName + "/" + this.cbPass;
        },
        doLogin() {
            if (document.location.hash !== "" || document.location.hash !== "#/") {
                var arr = document.location.hash.split("/");
                this.cbName = arr[1];
                this.cbPass = arr[2];
                if (this.cbName !== undefined && this.cbPass !== undefined) {
                    this.login();
                }
            }
        },
        onopen() {
            this.msg = [];
            this.isLogining = false;
            this.hasLogin = true;
            this.loginBtnDisable = false;
            this.interval = setInterval(() => {
                this.ws.send(JSON.stringify({ type: 'ping', msg: 'ping' }));
            }, 10000);
        },
        onmessage(evt) {
            const m = JSON.parse(evt.data);
            switch (m.type) {
                case 'all':
                    if (m.data === true) return;
                    this.msg = m.data;
                    break;
                case 'single':
                    this.msg.push(m.data);
                    break;
            }
        },
        onclose(evt) {
            this.hasLogin = false;
            this.msg = [];
            clearInterval(this.interval);
            this.interval = null;
            // eslint-disable-next-line
            console.log('onclose', evt);
        },
        onerror(evt) {
            this.hasLogin = false;
            this.msg = [];
            clearInterval(this.interval);
            this.interval = null;
            // eslint-disable-next-line
            console.log('onclose', evt);
        },
        send() {
            if (this.inputMsg) {
                this.ws.send(JSON.stringify({ type: "message", msg: this.inputMsg }));
                this.inputMsg = null;
            }
        },
        doCopy(m) {
            this.$copyText(m).then(() => {
                this.snackbarSuccess = true;
            }, () => {
                this.snackbarFail = true;
            });
        },
    },
}
</script>

<style>
.clip-page {
    position: absolute;
    top: 0;
    bottom: 0;
    right: 0;
    left: 0;
}

.clip-box {
    overflow: hidden;
}

.board {
    background-color: #fff;
    overflow: scroll;
    height: calc(100% - 210px);
}

.sub-title {
    margin-top: 20px;
    color: #666;
}

@media (prefers-color-scheme: dark) {
    body {
        background-color: #000;
        color: #fff;
    }

    .board {
        background-color: #333;
    }

    .sub-title {
        color: #ccc;
    }
}
</style>

