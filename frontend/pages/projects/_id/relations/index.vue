<template>
  <v-card>
    <v-card-title class="mb-2">
      <relation-action-menu />
      <relation-deletion-button class="ms-2" />
    </v-card-title>
    <relation-list />
  </v-card>
</template>

<script>
import RelationList from '@/components/containers/relations/RelationList'
import RelationActionMenu from '@/components/containers/relations/RelationActionMenu'
import RelationDeletionButton from '@/components/containers/relations/RelationDeletionButton'

export default {
  layout: 'project',

  components: {
    RelationList,
    RelationActionMenu,
    RelationDeletionButton
  },

  validate({ params }) {
    return /^\d+$/.test(params.id)
  }
}
</script>
