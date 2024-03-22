<script setup>
import { ref } from 'vue'

defineProps({
  msg: String,
})

const count = ref(0)
const url = ref(location.href)
const code = ref('1');

const show_notification = ()=>{
  try {
    // code.value = JSON.stringify(Object.keys(window.pywebview))+typeof(window.pywebview)+typeof(window.pywebview.api)+'\n'+JSON.stringify(Object.keys(window.pywebview.api));
    window.pywebview.api.show_notification();
  }catch (e) {
    alert(e.message)
  }
}

</script>

<template>
  <h1>{{ msg }}</h1>

  <div class="card">
    <button type="button" @click="count++">count is {{ count }}</button>
    <button type="button" @click="show_notification">显示通知</button>
    <p>url is {{ url }}</p>
    <p>
      Edit
      <code>components/HelloWorld.vue</code> to test HMR
      <code>{{ code }}}</code>
    </p>
  </div>

  <p>
    Check out
    <a href="https://vuejs.org/guide/quick-start.html#local" target="_blank"
      >create-vue</a
    >, the official Vue + Vite starter
  </p>
  <p>
    Install
    <a href="https://github.com/vuejs/language-tools" target="_blank">Volar</a>
    in your IDE for a better DX
  </p>
  <p class="read-the-docs">Click on the Vite and Vue logos to learn more</p>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
