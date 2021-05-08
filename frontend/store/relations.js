import RelationService from '@/services/relation.service'

export const state = () => ({
  relationItems: [],
  selected: [],
  loading: false
})

export const getters = {
  isRelationSelected(state) {
    return state.selected.length > 0
  }
}

export const mutations = {
  setRelationList(state, payload) {
    state.relationItems = payload
  },
  addRelation(state, relation) {
    state.relationItems.unshift(relation)
  },
  deleteRelation(state, relationId) {
    state.relationItems = state.relationItems.filter(item => item.id !== relationId)
  },
  updateSelected(state, selected) {
    state.selected = selected
  },
  updateRelation(state, relation) {
    const item = state.relationItems.find(item => item.id === relation.id)
    Object.assign(item, relation)
  },
  resetSelected(state) {
    state.selected = []
  },
  setLoading(state, payload) {
    state.loading = payload
  }
}

export const actions = {
  getRelationList({ commit }, payload) {
    commit('setLoading', true)
    return RelationService.getRelationList(payload.projectId)
      .then((response) => {
        commit('setRelationList', response.data)
      })
      .catch((error) => {
        alert(error)
      })
      .finally(() => {
        commit('setLoading', false)
      })
  },
  createRelation({ commit }, data) {
    return RelationService.addRelation(data.projectId, data)
      .then((response) => {
        commit('addRelation', response.data)
      })
  },
  updateRelation({ commit }, data) {
    RelationService.updateRelation(data.projectId, data.id, data)
      .then((response) => {
        commit('updateRelation', response.data)
      })
      .catch((error) => {
        alert(error)
      })
  },
  deleteRelation({ commit, state }, projectId) {
    for (const relation of state.selected) {
      RelationService.deleteRelation(projectId, relation.id)
        .then((response) => {
          commit('deleteRelation', relation.id)
        })
        .catch((error) => {
          alert(error)
        })
    }
    commit('resetSelected')
  },
  importRelations({ commit }, payload) {
    commit('setLoading', true)
    const formData = new FormData()
    formData.append('file', payload.file)
    const reader = new FileReader()
    reader.onload = (e) => {
      const relations = JSON.parse(e.target.result)
      for (const relation of relations) {
        RelationService.addRelation(payload.projectId, relation)
          .then((response) => {
            commit('addRelation', response.data)
          })
      }
    }
    reader.readAsText(payload.file)
    commit('setLoading', false)
  },
  exportRelations({ commit }, payload) {
    commit('setLoading', true)
    RelationService.getRelationList(payload.projectId)
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([JSON.stringify(response.data)]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `project_${payload.projectId}_relations.json`)
        document.body.appendChild(link)
        link.click()
      })
      .catch((error) => {
        alert(error)
      })
      .finally(() => {
        commit('setLoading', false)
      })
  },
  uploadRelation({ commit, dispatch }, data) {
    commit('setLoading', true)
    const formData = new FormData()
    formData.append('file', data.file)
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
    return RelationService.uploadFile(data.projectId, formData, config)
      .then((response) => {
        dispatch('getRelationList', data)
      })
      .finally(() => {
        commit('setLoading', false)
      })
  }
}
