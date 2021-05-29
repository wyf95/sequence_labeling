<template>
  <v-card>
    <v-card-title class="mb-2">
      <document-action-menu />
      <document-deletion-button class="ms-2" />
      <document-random-mapping-button class="ms-2" />
      <document-add-mapping-button class="ms-2" />
      <document-del-mapping-button class="ms-2" />
    </v-card-title>
    <document-list />
  </v-card>
</template>

<script>
import DocumentList from '@/components/containers/documents/DocumentList'
import DocumentActionMenu from '@/components/containers/documents/DocumentActionMenu'
import DocumentDeletionButton from '@/components/containers/documents/DocumentDeletionButton'
import DocumentDelMappingButton from '@/components/containers/documents/DocumentDelMappingButton'
import DocumentAddMappingButton from '@/components/containers/documents/DocumentAddMappingButton'
import DocumentRandomMappingButton from '@/components/containers/documents/DocumentRandomMappingButton'

export default {
  layout: 'project',

  components: {
    DocumentList,
    DocumentActionMenu,
    DocumentDeletionButton,
    DocumentDelMappingButton,
    DocumentAddMappingButton,
    DocumentRandomMappingButton
  },

  validate({ params, query }) {
    return /^\d+$/.test(params.id) && /^\d+|$/.test(query.limit) && /^\d+|$/.test(query.offset)
  }
}
</script>
