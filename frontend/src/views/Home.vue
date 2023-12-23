<template>
  <!--vuetify 3, horizonally + vertically centered-->
  <v-container fluid class="fill-height justify-center">
    <v-col cols="12" md="8">
      <v-card>
        <v-card-title>
          <span class="headline">Welcome to Clip!</span>
        </v-card-title>
        <v-card-text>
          <v-form>
            <v-text-field v-model="name" label="Name" required></v-text-field>
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
        name: "Clip",
        params: {
          name: this.name,
        }
      });
    },
  },
}
</script>
