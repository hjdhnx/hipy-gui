<script setup>
import {ref} from 'vue'

defineProps({
  msg: String,
})

const count = ref(0)
const url = ref(location.href)
const fpath = ref('')
const fname = ref('')
const code = ref('1');

const show_notification = () => {
  try {
    // code.value = JSON.stringify(Object.keys(window.pywebview))+typeof(window.pywebview)+typeof(window.pywebview.api)+'\n'+JSON.stringify(Object.keys(window.pywebview.api));
    pywebview.api.show_notification();
  } catch (e) {
    alert(e.message)
  }
}

const select_file = () => {
  try {
    pywebview.api.select_file().then(response => {
      fpath.value = response.fpath
      fname.value = response.fname
    });
  } catch (e) {
    alert(e.message)
  }
}

const save_file_dialog = () => {
  try {
    pywebview.api.save_file_dialog();
  } catch (e) {
    alert(e.message)
  }
}

const updateFilePath = (fpath) => {
  fpath.value = fpath
}

</script>

<template>
  <h1>{{ msg }}</h1>

  <div class="card">
    <button type="button" @click="count++">count is {{ count }}</button>
    <button type="button" @click="show_notification">显示通知</button>
    <button type="button" @click="select_file">选择文件</button>
    <button type="button" @click="save_file_dialog">保存文件</button>
    <p>url is {{ url }}</p>
    <p v-show="fpath">fpath is {{ fpath }}</p>
    <p v-show="fname">fname is {{ fname }}</p>
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
