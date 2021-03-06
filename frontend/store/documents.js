import DocumentService from '@/services/document.service'
import AnnotationService from '@/services/annotation.service'
import ConnectionService from '@/services/connection.service'

export const state = () => ({
  items: [],
  selected: [],
  loading: false,
  current: 0,
  total: 0,
  searchOptions: {
    limit: 10,
    offset: 0,
    q: '',
    isChecked: '',
    filterName: ''
  }
})

export const getters = {
  isDocumentSelected(state) {
    return state.selected.length > 0
  },
  approved(state) {
    if (state.items[state.current]) {
      return state.items[state.current].annotation_approver !== null
    } else {
      return false
    }
  },
  currentDoc(state) {
    return state.items[state.current]
  }
}

export const mutations = {
  setCurrent(state, payload) {
    state.current = payload
  },
  setDocumentList(state, payload) {
    state.items = payload
  },
  addDocument(state, document) {
    state.items.unshift(document)
  },
  deleteDocument(state, documentId) {
    state.items = state.items.filter(item => item.id !== documentId)
  },
  updateSelected(state, selected) {
    state.selected = selected
  },
  updateDocument(state, document) {
    const item = state.items.find(item => item.id === document.id)
    Object.assign(item, document)
  },
  resetSelected(state) {
    state.selected = []
  },
  setLoading(state, payload) {
    state.loading = payload
  },
  setTotalItems(state, payload) {
    state.total = payload
  },
  addAnnotation(state, payload) {
    state.items[state.current].annotations.push(payload)
  },
  deleteAnnotation(state, annotationId) {
    state.items[state.current].annotations = state.items[state.current].annotations.filter(item => item.id !== annotationId)
    state.items[state.current].connections = state.items[state.current].connections.filter(item => item.source !== annotationId && item.to !== annotationId)
  },
  updateAnnotation(state, payload) {
    const item = state.items[state.current].annotations.find(item => item.id === payload.id)
    Object.assign(item, payload)
  },

  addConnection(state, payload) {
    state.items[state.current].connections.push(payload)
  },
  deleteConnection(state, connectionId) {
    state.items[state.current].connections = state.items[state.current].connections.filter(item => item.id !== connectionId)
  },
  updateConnection(state, payload) {
    const item = state.items[state.current].connections.find(item => item.id === payload.id)
    Object.assign(item, payload)
  },

  updateSearchOptions(state, payload) {
    state.searchOptions = Object.assign(state.searchOptions, payload)
  },
  initSearchOptions(state) {
    state.searchOptions = {
      limit: 10,
      offset: 0,
      q: '',
      isChecked: '',
      filterName: ''
    }
  }
}

export const actions = {
  getDocumentList({ commit, state }, payload) {
    commit('setLoading', true)
    return DocumentService.getDocumentList(payload)
      .then((response) => {
        commit('setDocumentList', response.data.results)
        commit('setTotalItems', response.data.count)
      })
      .catch((error) => {
        alert(error)
      })
      .finally(() => {
        commit('setLoading', false)
      })
  },
  uploadDocument({ commit, dispatch }, data) {
    commit('setLoading', true)
    const formData = new FormData()
    formData.append('file', data.file)
    formData.append('format', data.format)
    formData.append('spliter', data.spliter)
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
    return DocumentService.uploadFile(data.projectId, formData, config)
      .then((response) => {
        dispatch('getDocumentList', data)
      })
      .finally(() => {
        commit('setLoading', false)
      })
  },
  exportDocument({ commit }, data) {
    commit('setLoading', true)
    DocumentService.exportFile(data.projectId, data.format)
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'file.' + data.format)
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
  updateDocument({ commit }, data) {
    DocumentService.updateDocument(data.projectId, data.id, data)
      .then((response) => {
        commit('updateDocument', response.data)
      })
      .catch((error) => {
        alert(error)
      })
  },
  deleteDocument({ commit, state }, projectId) {
    for (const document of state.selected) {
      DocumentService.deleteDocument(projectId, document.id)
        .then((response) => {
          commit('deleteDocument', document.id)
        })
        .catch((error) => {
          alert(error)
        })
    }
    commit('resetSelected')
  },

  randomDocMapping({ commit, dispatch }, payload) {
    commit('setLoading', true)
    DocumentService.randomDocMapping(payload.projectId, {role:payload.role, number:payload.number})
      .then((response) => {
        dispatch('getDocumentList', payload)
      })
      .finally(() => {
        commit('setLoading', false)
      })
  },

  addDocMapping({ commit, state }, payload) {
    for (const document of state.selected) {
      var annotator_assign = state.items.find(item => item.id === document.id).annotator_assign.find(item => item === payload.username)
      var approver_assign = state.items.find(item => item.id === document.id).approver_assign.find(item => item === payload.username)
      if (annotator_assign || approver_assign) {
        continue
      }
      DocumentService.addDocMapping(payload.projectId, {document:document.id, user:payload.userId})
        .then((response) => {
        })
        .catch((error) => {
          alert(error)
        })
    }
    commit('resetSelected')
  },

  deleteDocMapping({ commit, state }, projectId) {
    for (const document of state.selected) {
      DocumentService.deleteDocMapping(projectId, document.id)
        .then((response) => {
        })
        .catch((error) => {
          alert(error)
        })
    }
    commit('resetSelected')
  },

  addAnnotation({ commit, state }, payload) {
    const documentId = state.items[state.current].id
    AnnotationService.addAnnotation(payload.projectId, documentId, payload)
      .then((response) => {
        commit('addAnnotation', response.data)
      })
      .catch((error) => {
        alert(error)
      })
  },
  updateAnnotation({ commit, state }, payload) {
    const documentId = state.items[state.current].id
    AnnotationService.updateAnnotation(payload.projectId, documentId, payload.annotationId, payload)
      .then((response) => {
        commit('updateAnnotation', response.data)
      })
      .catch((error) => {
        alert(error)
      })
  },
  deleteAnnotation({ commit, state }, payload) {
    const documentId = state.items[state.current].id
    AnnotationService.deleteAnnotation(payload.projectId, documentId, payload.annotationId)
      .then((response) => {
        commit('deleteAnnotation', payload.annotationId)
      })
      .catch((error) => {
        alert(error)
      })
  },

  addConnection({ commit, state }, payload) {
    const documentId = state.items[state.current].id
    ConnectionService.addConnection(payload.projectId, documentId, payload)
      .then((response) => {
        commit('addConnection', response.data)
      })
      .catch((error) => {
        alert(error)
      })
  },
  updateConnection({ commit, state }, payload) {
    const documentId = state.items[state.current].id
    ConnectionService.updateConnection(payload.projectId, documentId, payload.connectionId, payload)
      .then((response) => {
        commit('updateConnection', response.data)
      })
      .catch((error) => {
        alert(error)
      })
  },
  deleteConnection({ commit, state }, payload) {
    const documentId = state.items[state.current].id
    ConnectionService.deleteConnection(payload.projectId, documentId, payload.connectionId)
      .then((response) => {
        commit('deleteConnection', payload.connectionId)
      })
      .catch((error) => {
        alert(error)
      })
  },

  approve({ commit, getters }, payload) {
    const documentId = getters.currentDoc.id
    const data = {
      approved: !getters.currentDoc.annotation_approver
    }
    DocumentService.approveDocument(payload.projectId, documentId, data)
      .then((response) => {
        commit('updateDocument', response.data)
      })
      .catch((error) => {
        alert(error)
      })
  }
}
