<template>
  <div>
    <v-btn
      :disabled="!isDocumentSelected"
      class="text-capitalize"
      outlined
      @click="dialog=true"
    >
      {{ $t('dataset.delMapping') }}
    </v-btn>
    <v-dialog
      v-model="dialog"
      width="800"
    >
      <confirm-form
        :title="$t('dataset.deleteDocMappingTitle')"
        :message="$t('dataset.deleteDocMappingMessage')"
        :button-true-text="$t('generic.yes')"
        :button-false-text="$t('generic.cancel')"
        item-key="text"
        @ok="deleteAssign($route.params.id);dialog=false"
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
    ...mapState('documents', ['selected']),
    ...mapGetters('documents', ['isDocumentSelected'])
  },

  methods: {
    ...mapActions('documents', ['deleteDocMapping', 'getDocumentList']),

    deleteAssign(id) {
      this.deleteDocMapping(id)
      this.getDocumentList({
        projectId: this.$route.params.id
      })
    }
  }
}
</script>
