import ApiService from '@/services/api.service'

class ConnectionService {
  constructor() {
    this.request = ApiService
  }
  
  getConnectionList(projectId, docId) {
    return this.request.get(`/projects/${projectId}/docs/${docId}/connections`)
  }

  addConnection(projectId, docId, payload) {
    return this.request.post(`/projects/${projectId}/docs/${docId}/connections`, payload)
  }

  deleteConnection(projectId, docId, connectionId) {
    return this.request.delete(`/projects/${projectId}/docs/${docId}/connections/${connectionId}`)
  }

  updateConnection(projectId, docId, connectionId, payload) {
    return this.request.patch(`/projects/${projectId}/docs/${docId}/connections/${connectionId}`, payload)
  }

}

export default new ConnectionService()
