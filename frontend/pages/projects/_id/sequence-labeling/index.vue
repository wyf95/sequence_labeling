<template>
  <entity-item-box />
</template>

<script>
import EntityItemBox from '~/components/containers/annotation/EntityItemBox'

export default {
  layout: 'annotation',

  components: {
    EntityItemBox
  },

  validate({ params, query }) {
    return /^\d+$/.test(params.id) && /^\d+$/.test(query.page)
  }
}
</script>

<style>
.v-navigation-drawer{
  z-index: 300;
}
</style>
