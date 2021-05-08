
<template>
  
</template>
<script>
export default {
  layout: 'project',

  validate({ params }) {
    return /^\d+$/.test(params.id)
  }
}
</script>
