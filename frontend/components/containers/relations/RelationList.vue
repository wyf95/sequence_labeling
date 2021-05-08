<template>
  <v-data-table
    :value="selected"
    :headers="headers"
    :items="relationItems"
    :search="search"
    :loading="loading"
    :loading-text="$t('generic.loading')"
    :no-data-text="$t('vuetify.noDataAvailable')"
    :footer-props="{
      'showFirstLastPage': true,
      'items-per-page-options': [5, 10, 15, 50],
      'items-per-page-text': $t('vuetify.itemsPerPageText'),
      'page-text': $t('dataset.pageText')
    }"
    item-key="id"
    show-select
    @input="updateSelected"
  >
    <template v-slot:top>
      <v-text-field
        v-model="search"
        prepend-inner-icon="search"
        :label="$t('generic.search')"
        single-line
        hide-details
        filled
      />
    </template>
    <template v-slot:item.text="{ item }">
      <v-edit-dialog>
        {{ item.text }}
        <template v-slot:input>
          <v-text-field
            :value="item.text"
            :rules="relationNameRules($t('rules.relationNameRules'))"
            :label="$t('generic.edit')"
            single-line
            @change="handleUpdateRelation({ id: item.id, text: $event })"
          />
        </template>
      </v-edit-dialog>
    </template>
    <template v-slot:item.color="{ item }">
      <v-edit-dialog>
        <v-chip
          :color="item.color"
          :text-color="textColor(item.color)"
          dark
        >
          {{ item.color }}
        </v-chip>
        <template v-slot:input>
          <v-color-picker
            :value="item.color"
            :rules="colorRules($t('rules.colorRules'))"
            show-swatches
            hide-mode-switch
            width="800"
            mode="hexa"
            class="ma-2"
            @update:color="handleUpdateRelation({ id:item.id, color: $event.hex })"
          />
        </template>
      </v-edit-dialog>
    </template>
  </v-data-table>
</template>

<script>
import { mapState, mapActions, mapMutations } from 'vuex'
import { colorRules, relationNameRules } from '@/rules/index'
import { idealColor } from '~/plugins/utils'

export default {
  data() {
    return {
      search: '',
      headers: [
        {
          text: this.$t('generic.name'),
          align: 'left',
          value: 'text'
        },
        {
          text: this.$t('relations.color'),
          sortable: false,
          value: 'color'
        }
      ],
      colorRules,
      relationNameRules
    }
  },

  computed: {
    ...mapState('relations', ['relationItems', 'selected', 'loading'])
  },

  created() {
    this.getRelationList({
      projectId: this.$route.params.id
    })
  },

  methods: {
    ...mapActions('relations', ['getRelationList', 'updateRelation']),
    ...mapMutations('relations', ['updateSelected']),

    handleUpdateRelation(payload) {
      const data = {
        projectId: this.$route.params.id,
        ...payload
      }
      this.updateRelation(data)
    },

    textColor(backgroundColor) {
      return idealColor(backgroundColor)
    }
  }
}
</script>
