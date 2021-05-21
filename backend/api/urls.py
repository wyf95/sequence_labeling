from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import Me, Users, Health
from .views import ProjectList, ProjectDetail
from .views import LabelList, LabelDetail, ApproveLabelsAPI, LabelUploadAPI
from .views import RelationList, RelationDetail, RelationUploadAPI
from .views import DocumentList, DocumentDetail
from .views import AnnotationList, AnnotationDetail
from .views import ConnectionList, ConnectionDetail
from .views import TextUploadAPI, TextDownloadAPI
from .views import StatisticsAPI
from .views import RoleMappingList, RoleMappingDetail, Roles

urlpatterns = [
    path('health', Health.as_view(), name='health'),
    path('auth-token', obtain_auth_token),
    path('me', Me.as_view(), name='me'),
    path('projects', ProjectList.as_view(), name='project_list'),
    path('users', Users.as_view(), name='user_list'),
    path('roles', Roles.as_view(), name='roles'),
    path('projects/<int:project_id>', ProjectDetail.as_view(), name='project_detail'),
    path('projects/<int:project_id>/statistics',
         StatisticsAPI.as_view(), name='statistics'),
    path('projects/<int:project_id>/labels',
         LabelList.as_view(), name='label_list'),
    path('projects/<int:project_id>/label-upload',
         LabelUploadAPI.as_view(), name='label_upload'),
    path('projects/<int:project_id>/labels/<int:label_id>',
         LabelDetail.as_view(), name='label_detail'),

    path('projects/<int:project_id>/relations',
         RelationList.as_view(), name='relation_list'),
    path('projects/<int:project_id>/relations/<int:relation_id>',
         RelationDetail.as_view(), name='relation_detail'),
    path('projects/<int:project_id>/relation-upload',
         RelationUploadAPI.as_view(), name='relation_upload'),

    path('projects/<int:project_id>/docs',
         DocumentList.as_view(), name='doc_list'),
    path('projects/<int:project_id>/docs/<int:doc_id>',
         DocumentDetail.as_view(), name='doc_detail'),
    path('projects/<int:project_id>/docs/<int:doc_id>/approve-labels',
         ApproveLabelsAPI.as_view(), name='approve_labels'),
    path('projects/<int:project_id>/docs/<int:doc_id>/annotations',
         AnnotationList.as_view(), name='annotation_list'),
    path('projects/<int:project_id>/docs/<int:doc_id>/annotations/<int:annotation_id>',
         AnnotationDetail.as_view(), name='annotation_detail'),

    path('projects/<int:project_id>/docs/<int:doc_id>/connections',
         ConnectionList.as_view(), name='connection_list'),
    path('projects/<int:project_id>/docs/<int:doc_id>/connections/<int:connection_id>',
         ConnectionDetail.as_view(), name='connection_detail'),
         
    path('projects/<int:project_id>/docs/upload',
         TextUploadAPI.as_view(), name='doc_uploader'),
    path('projects/<int:project_id>/docs/download',
         TextDownloadAPI.as_view(), name='doc_downloader'),
    path('projects/<int:project_id>/roles',
         RoleMappingList.as_view(), name='rolemapping_list'),
    path('projects/<int:project_id>/roles/<int:rolemapping_id>',
         RoleMappingDetail.as_view(), name='rolemapping_detail'),
]
