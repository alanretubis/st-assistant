<template>
  <div class="app">
    <!-- <h1>Travel Assistant Chat</h1> -->
    <Chat />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Chat from "./components/Chat.vue";

export default defineComponent({
  components: { Chat },
});
</script>

<style>
body {
  font-family: sans-serif;
}
.app {
  /* width: 100%;
  height: 90%; */
  margin-left: 0;
  margin-right: 0;
  padding: 0rem;
}
</style>
