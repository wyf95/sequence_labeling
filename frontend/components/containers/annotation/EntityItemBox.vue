<template>
  <entity-item-box
    v-if="isReady"
    :labels="items"
    :text="currentDoc.text"
    :entities="currentDoc.annotations"
    :update-entity="updateEntity"
    :add-entity="addEntity"
    :remove-entity="removeEntity"
    @updateEntityConn="updateEntityConn"
  />
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import EntityItemBox from '~/components/organisms/annotation/EntityItemBox'

export default {
  components: {
    EntityItemBox
  },

  computed: {
    ...mapState('labels', ['items', 'loading']),
    ...mapState('documents', { documentLoading: 'loading' }),
    ...mapGetters('documents', ['currentDoc']),
    isReady() {
      return !!this.currentDoc && !this.loading && !this.documentLoading
    }
  },

  created() {
    this.getLabelList({
      projectId: this.$route.params.id
    })
  },

  methods: {
    ...mapActions('labels', ['getLabelList']),
    ...mapActions('documents', ['getDocumentList', 'deleteAnnotation', 'updateAnnotation', 'updateAnnotationConn', 'addAnnotation']),
    removeEntity(annotationId) {
      const payload = {
        annotationId,
        projectId: this.$route.params.id
      }
      this.deleteAnnotation(payload)
    },
    updateEntity(labelId, annotationId) {
      const payload = {
        annotationId,
        label: labelId,
        projectId: this.$route.params.id
      }
      this.updateAnnotation(payload)
    },
    updateEntityConn(annotationId, conn){
      const payload = {
        annotationId,
        connections: conn,
        projectId: this.$route.params.id
      }
      this.updateAnnotationConn(payload)
    },
    addEntity(startOffset, endOffset, labelId) {
      const payload = {
        start_offset: startOffset,
        end_offset: endOffset,
        label: labelId,
        projectId: this.$route.params.id
      }
      this.addAnnotation(payload)
    }
  }
}
</script>
