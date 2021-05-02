<template>
  <entity-item-box
    v-if="isReady"
    :labels="items"
    :text="currentDoc.text"
    :entities="currentDoc.annotations"
    :connections="currentDoc.connections"
    :update-entity="updateEntity"
    :add-entity="addEntity"
    :remove-entity="removeEntity"
    :remove-connection="removeConn"
    :update-connection="updateConn"
    :add-connection="addConn"
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
    ...mapActions('documents', ['getDocumentList', 'deleteAnnotation', 'updateAnnotation', 'addAnnotation', 'deleteConnection', 'updateConnection', 'addConnection']),
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
    addEntity(startOffset, endOffset, labelId) {
      const payload = {
        start_offset: startOffset,
        end_offset: endOffset,
        label: labelId,
        projectId: this.$route.params.id
      }
      this.addAnnotation(payload)
    },

    removeConn(connectionId) {
      const payload = {
        connectionId,
        projectId: this.$route.params.id
      }
      this.deleteConnection(payload)
    },
    updateConn(connectionId) {
      const payload = {
        connectionId,
        projectId: this.$route.params.id
      }
      this.updateConnection(payload)
    },
    addConn(source, to) {
      const payload = {
        source: source,
        to: to,
        projectId: this.$route.params.id
      }
      this.addConnection(payload)
    }
  }
}
</script>
