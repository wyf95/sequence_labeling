<template>
  <div>
    <v-btn
      :disabled="!isDocumentSelected"
      class="text-capitalize"
      outlined
      @click="dialog=true"
    >
      {{ $t('dataset.addMapping') }}
    </v-btn>
    <v-dialog
      v-model="dialog"
      width="800"
    >
      <base-card
        v-if="dialog"
        :disabled="!selectedUser"
        :title="$t('members.addMember')"
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
              v-model="selectedUser"
              :items="thisItems"
              :loading="isLoading"
              :search-input.sync="username"
              item-text="username"
              color="white"
              hide-no-data
              hide-selected
              :label="$t('members.userSearchAPIs')"
              :placeholder="$t('members.userSearchPrompt')"
              prepend-icon="mdi-account"
              return-object
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
      username: '',
      selectedUser: null
    }
  },

  computed: {
    ...mapState('members', ['items']),
    ...mapState('documents', ['selected']),
    ...mapGetters('documents', ['isDocumentSelected']),

    thisItems() {
      return this.items.filter(item => item.rolename !== 'project_admin')
    }
  },

  created() {
    this.getMemberList({
      projectId: this.$route.params.id
    })
  },

  methods: {
    ...mapActions('members', ['getMemberList']),
    ...mapActions('documents', ['addDocMapping', 'getDocumentList']),
    

    cancel() {
      this.dialog=false
    },
    reset() {
      this.$refs.form.reset()
    },
    create() {
      this.addDocMapping({
        projectId: this.$route.params.id,
        userId: this.selectedUser.user,
        username: this.selectedUser.username
      })
      this.reset()
      this.cancel()
      this.getDocumentList({
        projectId: this.$route.params.id
      })
    }
  }
}
</script>
