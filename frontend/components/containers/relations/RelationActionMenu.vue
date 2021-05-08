<template>
  <div>
    <action-menu
      :items="menuItems"
      :text="$t('dataset.actions')"
      @create="createDialog=true"
      @upload="importDialog=true"
      @download="handleDownload"
    />
    <v-dialog
      v-model="createDialog"
      width="800"
    >
      <relation-creation-form
        :create-relation="createRelation"
        @close="createDialog=false"
      />
    </v-dialog>
    <v-dialog
      v-model="importDialog"
      width="800"
    >
      <relation-import-form
        :upload-relation="uploadRelation"
        @close="importDialog=false"
      />
    </v-dialog>
  </div>
</template>

<script>
import { mapActions} from 'vuex'
import ActionMenu from '@/components/molecules/ActionMenu'
import RelationCreationForm from '@/components/organisms/relations/RelationCreationForm'
import RelationImportForm from '@/components/organisms/relations/RelationImportForm'

export default {
  components: {
    ActionMenu,
    RelationCreationForm,
    RelationImportForm
  },

  data() {
    return {
      createDialog: false,
      importDialog: false,
      menuItems: [
        { title: this.$t('relations.createRelation'), icon: 'mdi-pencil', event: 'create' },
        { title: this.$t('relations.importRelations'), icon: 'mdi-upload', event: 'upload' },
        { title: this.$t('relations.exportRelations'), icon: 'mdi-download', event: 'download' }
      ]
    }
  },

  created() {
    this.setCurrentProject(this.$route.params.id)
  },

  methods: {
    ...mapActions('relations', ['createRelation', 'uploadRelation', 'exportRelations']),
    ...mapActions('projects', ['setCurrentProject']),

    handleDownload() {
      this.exportRelations({
        projectId: this.$route.params.id
      })
    }
  }
}
</script>
