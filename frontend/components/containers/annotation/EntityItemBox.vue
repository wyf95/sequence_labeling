<template>
  <entity-item-box
    v-if="isReady"
    :user="current_user"
    :labels="items"
    :relations="relationItems"
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
    ...mapState('relations', ['relationItems', 'loading']),
    ...mapState('documents', { documentLoading: 'loading' }),
    ...mapGetters('documents', ['currentDoc']),
    ...mapGetters('projects', ['getCurrentUserRole']),
    isReady() {
      return !!this.currentDoc && !this.loading && !this.documentLoading
    },
    current_user() {
      return document.getElementById('current_user').innerText
    }
  },

  created() {
    this.getLabelList({
      projectId: this.$route.params.id
    }),
    this.getRelationList({
      projectId: this.$route.params.id
    })
  },

  methods: {
    ...mapActions('labels', ['getLabelList']),
    ...mapActions('relations', ['getRelationList']),
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
    addEntity(startOffset, endOffset, labelId, userId) {
      const payload = {
        start_offset: startOffset,
        end_offset: endOffset,
        label: labelId,
        userId: userId,
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
    updateConn(connectionId, relationId) {
      const payload = {
        connectionId,
        relation: relationId,
        projectId: this.$route.params.id
      }
      this.updateConnection(payload)
    },
    addConn(source, to) {
      const payload = {
        source: source,
        to: to,
        relation: null,
        projectId: this.$route.params.id
      }
      this.addConnection(payload)
    }
  }
}
</script>

<style>
/* 连线中的label 样式*/
.jtk-overlay.flowLabel:not(.aLabel) {
  border-radius: 5px;
}
</style>