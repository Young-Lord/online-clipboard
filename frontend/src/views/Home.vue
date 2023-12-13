<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-text-field
          v-model="name"
          label="Clipboard Name"
          placeholder="example"
        ></v-text-field>
      </v-col>
    </v-row>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-btn
          color="primary"
          @click="goToClipPage"
          :disabled="!name"
          block
        >Clip</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  components: {
  },
  data() {
    return {
      name: "",
    }
  },
  created() {
  },
  methods: {
    goToClipPage() {
      this.$router.push({
        name: "ClipPage",
        params: {
          name: this.name,
        }
      });
    },
  },
}
</script>

<!--
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
-->
