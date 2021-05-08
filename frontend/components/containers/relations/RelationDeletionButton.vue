<template>
  <div>
    <v-btn
      :disabled="!isRelationSelected"
      class="text-capitalize"
      outlined
      @click="dialog=true"
    >
      {{ $t('generic.delete') }}
    </v-btn>
    <v-dialog
      v-model="dialog"
      width="800"
    >
      <confirm-form
        :items="selected"
        title="Delete Relation"
        :message="$t('relations.deleteMessage')"
        item-key="text"
        @ok="deleteRelation($route.params.id);dialog=false"
        @cancel="dialog=false"
      />
    </v-dialog>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import ConfirmForm from '@/components/organisms/utils/ConfirmForm'

export default {
  components: {
    ConfirmForm
  },

  data() {
    return {
      dialog: false
    }
  },

  computed: {
    ...mapState('relations', ['selected']),
    ...mapGetters('relations', ['isRelationSelected'])
  },

  methods: {
    ...mapActions('relations', ['deleteRelation']),

    handleDeleteRelation() {
      const projectId = this.$route.params.id
      this.deleteRelation(projectId)
    }
  }
}
</script>
