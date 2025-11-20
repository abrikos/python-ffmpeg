<script setup>
import {ref} from "vue";
const url = ref()
const error = ref()
const fileInput = ref()
const loading = ref(false)
async function upload(event){
  clear()
  loading.value = true
  event.preventDefault()

  const formData = new FormData();
  formData.append('uploadedVideo',event.target.files[0]);
  fetch('/api/add-emoji', {method: 'POST', body: formData})
      .then(response => response.json())
      .then(data => {
        if(data.code === 200){
          url.value = data.url;
        }else{
          error.value = data.message;
        }

        loading.value = false
      })
      .catch(e => {
        loading.value = false
        error.value = e
      });
  fileInput.value.value = null
}

function clear(){
  loading.value = false
  url.value = null
  error.value = null
}

</script>

<template>

  <div>
    <input type="file" @change="upload" ref="fileInput" xaccept="video/*"/>
    <button @click="clear">Clear</button>
    <h1 v-if="loading" class="loader">...Please wait while the video is being processed. </h1>
    <video v-if="url" :src="url" autoplay loop/>
    <h1 class="error" v-if="error">{{error}}</h1>
  </div>
</template>

<style scoped>
.loader{
  color: green
}
.error{
  color: red
}
</style>
