import ApiService from '@/services/api.service'

class DocumentService {
  constructor() {
    this.request = ApiService
  }

  getDocumentList({ projectId, limit = 10, offset = 0, q = '', isChecked = '', filterName = '' }) {
    return this.request.get(`/projects/${projectId}/docs?limit=${limit}&offset=${offset}&q=${q}&${filterName}=${isChecked}`)
  }

  addDocument(projectId, payload) {
    return this.request.post(`/projects/${projectId}/docs`, payload)
  }

  deleteDocument(projectId, docId) {
    return this.request.delete(`/projects/${projectId}/docs/${docId}`)
  }

  addDocMapping(projectId, payload) {
    return this.request.post(`/projects/${projectId}/docmappings`, payload)
  }

  randomDocMapping(projectId, payload) {
    // {role: "approver" /annotator, number: 1}
    return this.request.post(`/projects/${projectId}/randomdocmapping`, payload)
  }

  deleteDocMapping(projectId, docId) {
    return this.request.delete(`/projects/${projectId}/docmappings/${docId}`)
  }

  updateDocument(projectId, docId, payload) {
    return this.request.patch(`/projects/${projectId}/docs/${docId}`, payload)
  }

  uploadFile(projectId, payload, config = {}) {
    return this.request.post(`/projects/${projectId}/docs/upload`, payload, config)
  }

  exportFile(projectId, format) {
    const headers = {}
    if (format === 'csv') {
      headers.Accept = 'text/csv; charset=utf-8'
      headers['Content-Type'] = 'text/csv; charset=utf-8'
    } else {
      headers.Accept = 'application/json'
      headers['Content-Type'] = 'application/json'
    }
    const config = {
      responseType: 'blob',
      params: {
        q: format
      },
      headers
    }
    return this.request.get(`/projects/${projectId}/docs/download`, config)
  }

  approveDocument(projectId, docId, payload) {
    return this.request.post(`/projects/${projectId}/docs/${docId}/approve-labels`, payload)
  }
}

export default new DocumentService()
