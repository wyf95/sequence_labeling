import ApiService from '@/services/api.service'

class RelationService {
  constructor() {
    this.request = ApiService
  }

  getRelationList(projectId) {
    return this.request.get(`/projects/${projectId}/relations`)
  }

  addRelation(projectId, payload) {
    return this.request.post(`/projects/${projectId}/relations`, payload)
  }

  deleteRelation(projectId, relationId) {
    return this.request.delete(`/projects/${projectId}/relations/${relationId}`)
  }

  updateRelation(projectId, relationId, payload) {
    return this.request.patch(`/projects/${projectId}/relations/${relationId}`, payload)
  }

  uploadFile(projectId, payload, config = {}) {
    return this.request.post(`/projects/${projectId}/relation-upload`, payload, config)
  }
}

export default new RelationService()
