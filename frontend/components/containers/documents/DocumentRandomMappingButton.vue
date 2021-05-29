<template>
  <div>
    <v-btn
      class="text-capitalize"
      outlined
      @click="dialog=true"
    >
      {{ $t('dataset.randomMapping') }}
    </v-btn>
    <v-dialog
      v-model="dialog"
      width="800"
    >
      <base-card
        v-if="dialog"
        :disabled="!selectedRole || !assignNumber"
        :title="$t('dataset.randomMapping')"
        :agree-text="$t('generic.add')"
        :cancel-text="$t('generic.cancel')"
        @agree="create"
        @cancel="cancel"
      >
        <template #content>
          <v-form
            ref="form"
            v-model="dialog"
          >
            <v-autocomplete
              v-model="selectedRole"
              :items="items"
              :loading="isLoading"
              :search-input.sync="rolename"
              item-text="text"
              color="white"
              hide-no-data
              hide-selected
              :label="$t('dataset.selectRole')"
              :placeholder="$t('dataset.selectRole')"
              prepend-icon="mdi-account"
              return-object
            />
            <v-text-field
              v-model="assignNumber"
              :label="$t('dataset.inputNumber')"
              prepend-icon="label"
            />
          </v-form>
        </template>
      </base-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import BaseCard from '@/components/molecules/BaseCard'

export default {
  components: {
    BaseCard
  },

  data() {
    return {
      dialog: false,
      isLoading: false,
      items: [
        { text: this.$t('dataset.annotator_assign'), name: 'annotator' },
        { text: this.$t('dataset.approver_assign'), name: 'annotation_approver' }
      ],
      selectedRole: null,
      rolename: '',
      assignNumber: null
    }
  },

  created() {
    this.getMemberList({
      projectId: this.$route.params.id
    })
  },

  computed: {
    ...mapGetters('members', ['currentMembers']),

    annotator_menbers() {
      return this.currentMembers.filter(item => item.rolename === "annotator")
    },

    approver_menbers() {
      return this.currentMembers.filter(item => item.rolename === "annotation_approver")
    }
  },

  methods: {
    ...mapActions('members', ['getMemberList']),
    ...mapActions('documents', ['getDocumentList', 'randomDocMapping']),

    validation() {
      var number = parseInt(this.assignNumber)
      var role = this.selectedRole.name
      if (number < 0 || isNaN(number)) {
        alert('输入成员数错误')
        return false
      }
      if (role === "annotator" && number > this.annotator_menbers.length) {
        alert('成员不足')
        return false
      }
      if (role === "annotation_approver" && number > this.approver_menbers.length) {
        alert('成员不足')
        return false
      }
      return true
    },

    cancel() {
      this.dialog=false
    },
    create() {
      if (this.validation()) {
        this.randomDocMapping({
          projectId: this.$route.params.id,
          role: this.selectedRole.name,
          number: parseInt(this.assignNumber)
        })
        this.cancel()
        this.getDocumentList({
          projectId: this.$route.params.id
        })
      }
    }
  }
}
</script>
