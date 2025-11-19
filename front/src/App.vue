<script setup>
import {ref} from "vue";

const fileupload = ref()
async function upload(event){
  event.preventDefault(); // Prevent
  const formData = new FormData();
  formData.append('uploadedVideo',event.target.files[0]);
  fetch('/api/add-emoji', {method: 'POST', body: formData})
      .then(response => {
        console.log(response)
        if (response.ok) {
          console.log('File uploaded successfully!');
          // Handle success (e.g., show a message to the user)
        } else {
          console.error('File upload failed.');
          // Handle errors
        }
      })
      .catch(error => {
        console.error('Error during file upload:', error);
      });
  fileupload.value.value = null
}
</script>

<template>

  <main>
    <input type="file" @change="upload" ref="fileupload"/>
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
