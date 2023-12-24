<template>
  <!--vuetify 3, horizonally + vertically centered-->
  <v-container fluid class="fill-height justify-center">
    <v-col cols="12" md="8">
      <v-card elevation="16" variant="tonal">
        <v-card-title>
          <span class="headline">Welcome to Clip!</span>
        </v-card-title>
        <v-card-subtitle><!--about button--><a @click="goToAboutPage" style="cursor: pointer;">About</a></v-card-subtitle>
        <v-card-text>
          <v-form @submit.native.prevent>
            <!--https://blog.csdn.net/Livenus_csdn/article/details/119573057-->
            <v-text-field v-model="name" label="Name" required @keydown.enter="goToClipPage"></v-text-field>
            <v-btn color="primary" @click="goToClipPage" :disabled="!name" block>
              Go to Clip
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-col>
  </v-container>
</template>

<script>
export default {
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
        name: "Clip",
        params: {
          name: this.name,
        }
      });
    },
    goToAboutPage() {
      console.log("goToAboutPage");
      this.$router.push({
        name: "About",
      });
    },
  },
}
</script>
