<template>
  <v-app>
    <v-content>
      <v-container @keyup.enter="login" grid-list-xs text-xs-center fill-height v-if="hasLogin === false">
        <v-layout row wrap>
          <v-flex xs12 class="mt-5">
            <div class="title">网络剪切板</div>
            <div class="sub-title">多终端同步文字信息, 最多50条</div>
            <div class="sub-title">输入剪切板名称: public，密码: public，可以进行留言</div>
            <div class="sub-title">可以进行留言</div>
            <div class="sub-title">
              <a href="http://fir.akawa.ink/onlinecb" target="_blank">Android客户端</a>&nbsp;&nbsp;
              <a href="https://apps.apple.com/us/app/%E7%BD%91%E7%BB%9C%E5%89%AA%E5%88%87%E6%9D%BF/id1485974770"
                target="_blank">iOS客户端</a>&nbsp;&nbsp;
              <a href="https://github.com/ety001/online-clipboard/blob/master/README.md#cli%E7%AB%AF"
                target="_blank">Cli端</a>&nbsp;&nbsp;
            </div>
          </v-flex>
          <v-flex xs12 md4 sm4 offset-sm4 offset-md4 class="mt-2">
            <v-text-field autofocus label="剪切板名字" v-model="cbName"></v-text-field>
          </v-flex>
          <v-flex xs12 md4 sm4 offset-sm4 offset-md4>
            <v-text-field label="剪切板密码" type="password" v-model="cbPass"></v-text-field>
          </v-flex>
          <v-flex xs6 offset-xs3 md2 sm2 offset-sm5 offset-md5>
            <v-btn block color="info" @click="login" :disabled="loginBtnDisable">登录</v-btn>
          </v-flex>
          <v-flex xs6 offset-xs3 md2 offset-md5 class="mt-2" v-if="isLogining === true">
            <v-progress-circular :size="20" color="primary" indeterminate></v-progress-circular>
          </v-flex>
          <v-flex xs12 class="caption mt-5">
            <a href="https://akawa.ink" target="_block">我的博客</a> |
            <a href="https://akawa.ink/donate/" target="_block">捐助</a> |
            <a href="https://github.com/ety001/online-clipboard" target="_block">源码</a>
          </v-flex>
        </v-layout>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
export default {
  components: {
  },
  data() {
  },
  created() {
  },
  methods: {
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

