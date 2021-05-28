import collections
import json
import random

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models.query import QuerySet
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Subquery
from rest_framework import generics, filters, status
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework_csv.renderers import CSVRenderer

from .filters import DocumentFilter
from .models import Project, Label, Document, RoleMapping, Role, DocMapping, Relation
from .permissions import IsProjectAdmin, IsAnnotatorAndReadOnly, IsAnnotator, IsAnnotationApproverAndReadOnly, IsAnnotationApprover
from .serializers import ProjectSerializer, LabelSerializer, DocumentSerializer, UserSerializer, ApproverSerializer, RelationSerializer
from .serializers import RoleMappingSerializer, RoleSerializer, DocMappingSerializer
from .utils import CSVParser, ExcelParser, JSONParser, PlainTextParser, CoNLLParser, AudioParser
from .utils import JSONLRenderer
from .utils import JSONPainter, CSVPainter

IsInProjectReadOnlyOrAdmin = (IsAnnotatorAndReadOnly | IsAnnotationApproverAndReadOnly | IsProjectAdmin)
IsInProjectOrAdmin = (IsAnnotator | IsAnnotationApprover | IsProjectAdmin)


class Health(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        return Response({'status': 'green'})


class Me(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class ProjectList(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Project.objects.all()
        else:
            return self.request.user.projects

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_url_kwarg = 'project_id'
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]


class StatisticsAPI(APIView):
    pagination_class = None
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]

    def get(self, request, *args, **kwargs):
        p = get_object_or_404(Project, pk=self.kwargs['project_id'])

        include = set(request.GET.getlist('include'))
        response = {}

        if not include or 'label' in include:
            label_count, user_count = self.label_per_data(p)
            response['label'] = label_count
            # TODO: Make user_label count chart
            response['user_label'] = user_count

        if not include or 'total' in include or 'remaining' in include or 'user' in include:
            progress = self.progress(project=p)
            response.update(progress)

        if include:
            response = {key: value for (key, value) in response.items() if key in include}

        return Response(response)

    @staticmethod
    def _get_user_completion_data(annotation_class, annotation_filter):
        all_annotation_objects  = annotation_class.objects.filter(annotation_filter)
        set_user_data = collections.defaultdict(set)
        for ind_obj in all_annotation_objects.values('user__username', 'document__id'):
            set_user_data[ind_obj['user__username']].add(ind_obj['document__id'])
        return {i: len(set_user_data[i]) for i in set_user_data}

    def progress(self, project):
        docs = project.documents
        annotation_class = project.get_annotation_class()
        total = docs.count()
        annotation_filter = Q(document_id__in=docs.all())
        user_data = self._get_user_completion_data(annotation_class, annotation_filter)
        done = docs.filter(annotations_approved_by__isnull=False).aggregate(Count('id'))['id__count']
        remaining = total - done
        return {'total': total, 'remaining': remaining, 'user': user_data}

    def label_per_data(self, project):
        annotation_class = project.get_annotation_class()
        return annotation_class.objects.get_label_per_data(project=project)


class ApproveLabelsAPI(APIView):
    permission_classes = [IsAuthenticated & (IsAnnotationApprover | IsProjectAdmin)]

    def post(self, request, *args, **kwargs):
        approved = self.request.data.get('approved', True)
        document = get_object_or_404(Document, pk=self.kwargs['doc_id'])
        document.annotations_approved_by = self.request.user if approved else None
        document.save()
        return Response(ApproverSerializer(document).data)


class LabelList(generics.ListCreateAPIView):
    serializer_class = LabelSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return project.labels

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        serializer.save(project=project)


class LabelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    lookup_url_kwarg = 'label_id'
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]

class RelationList(generics.ListCreateAPIView):
    serializer_class = RelationSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return project.relations

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        serializer.save(project=project)


class RelationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    lookup_url_kwarg = 'relation_id'
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]


class DocumentList(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('text', )
    ordering_fields = ('created_at', 'updated_at', 'doc_annotations__updated_at',
                       'seq_annotations__updated_at')
    filter_class = DocumentFilter
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]

    def is_role_of(self, user_id, project_id, role_name):
        return RoleMapping.objects.filter(
                    user_id=user_id,
                    project_id=project_id,
                    role_id=Subquery(Role.objects.filter(name=role_name).values('id')),
                ).exists()

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        queryset = project.documents
        queryset = queryset.order_by('id')

        user = self.request.user
        if not user.is_superuser:
            # project_admin / annotation_approver / annotator
            isAnnotatorOrApprover  = self.is_role_of(user.id, project.id, 'annotator') \
                                or self.is_role_of(user.id, project.id, 'annotation_approver')
            if isAnnotatorOrApprover:
                queryset = queryset.filter(docmapping__user=user.id)
        return queryset

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        serializer.save(project=project)


class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    lookup_url_kwarg = 'doc_id'
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]


class AnnotationList(generics.ListCreateAPIView):
    pagination_class = None
    permission_classes = [IsAuthenticated & IsInProjectOrAdmin]
    swagger_schema = None

    def get_serializer_class(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        self.serializer_class = project.get_annotation_serializer()
        return self.serializer_class

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        model = project.get_annotation_class()
        queryset = model.objects.filter(document=self.kwargs['doc_id'])
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['document'] = self.kwargs['doc_id']
        return super().create(request, args, kwargs)

    def perform_create(self, serializer):
        if self.request.data['userId']:
            request_user = get_object_or_404(User, pk=self.request.data['userId'])
            serializer.save(document_id=self.kwargs['doc_id'], user=request_user)
        else:
            serializer.save(document_id=self.kwargs['doc_id'], user=self.request.user)


class AnnotationDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'annotation_id'
    swagger_schema = None

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated & IsInProjectOrAdmin]
        return super().get_permissions()

    def get_serializer_class(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        self.serializer_class = project.get_annotation_serializer()
        return self.serializer_class

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        model = project.get_annotation_class()
        self.queryset = model.objects.all()
        return self.queryset

class ConnectionList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated & IsInProjectOrAdmin]
    swagger_schema = None

    def get_serializer_class(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        self.serializer_class = project.get_connection_serializer()
        return self.serializer_class

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        model = project.get_connection_class()
        queryset = model.objects.filter(document=self.kwargs['doc_id'])
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['document'] = self.kwargs['doc_id']
        return super().create(request, args, kwargs)

    def perform_create(self, serializer):
        serializer.save(document_id=self.kwargs['doc_id'])


class ConnectionDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'connection_id'
    swagger_schema = None

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated & IsInProjectOrAdmin]
        return super().get_permissions()

    def get_serializer_class(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        self.serializer_class = project.get_connection_serializer()
        return self.serializer_class

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        model = project.get_connection_class()
        self.queryset = model.objects.all()
        return self.queryset


class TextUploadAPI(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            raise ParseError('Empty content')

        self.save_file(
            user=request.user,
            file=request.data['file'],
            file_format=request.data['format'],
            spliter=request.data['spliter'],
            project_id=kwargs['project_id'],
        )

        return Response(status=status.HTTP_201_CREATED)

    @classmethod
    def save_file(cls, user, file, file_format, spliter, project_id):
        project = get_object_or_404(Project, pk=project_id)
        parser = cls.select_parser(file_format)
        data = parser.parse(file, spliter)
        storage = project.get_storage(data)
        storage.save(user)

    @classmethod
    def select_parser(cls, file_format):
        if file_format == 'plain':
            return PlainTextParser()
        elif file_format == 'csv':
            return CSVParser()
        elif file_format == 'json':
            return JSONParser()
        elif file_format == 'conll':
            return CoNLLParser()
        elif file_format == 'excel':
            return ExcelParser()
        elif file_format == 'audio':
            return AudioParser()
        else:
            raise ValidationError('format {} is invalid.'.format(file_format))


class TextDownloadAPI(APIView):
    permission_classes = TextUploadAPI.permission_classes

    renderer_classes = (CSVRenderer, JSONLRenderer)

    def get(self, request, *args, **kwargs):
        format = request.query_params.get('q')
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        documents = project.documents.all()
        painter = self.select_painter(format)
        if format == "json1":
            labels = project.labels.all()
            data = JSONPainter.paint_labels(documents, labels)
        else:
            data = painter.paint(documents)
        return Response(data)

    def select_painter(self, format):
        if format == 'csv':
            return CSVPainter()
        elif format == 'json' or format == "json1":
            return JSONPainter()
        else:
            raise ValidationError('format {} is invalid.'.format(format))


class Users(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def get(self, request, *args, **kwargs):
        queryset = User.objects.filter(is_superuser=False)
        serialized_data = UserSerializer(queryset, many=True).data
        return Response(serialized_data)


class Roles(generics.ListCreateAPIView):
    serializer_class = RoleSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    queryset = Role.objects.all()


class RoleMappingList(generics.ListCreateAPIView):
    serializer_class = RoleMappingSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return project.role_mappings

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        serializer.save(project=project)


class RoleMappingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoleMapping.objects.all()
    serializer_class = RoleMappingSerializer
    lookup_url_kwarg = 'rolemapping_id'
    permission_classes = [IsAuthenticated & IsProjectAdmin]


class DocMappingList(generics.ListCreateAPIView):
    serializer_class = DocMappingSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def create(self, request, *args, **kwargs):
        request.data['project'] = self.kwargs['project_id']
        return super().create(request, *args, **kwargs)

class DocMappingDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocMappingSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    
    def delete(self, request, *args, **kwargs):
        DocMapping.objects.filter(project=self.kwargs['project_id'], document=self.kwargs['doc_id']).delete()
        return Response({'code':200})


class LabelUploadAPI(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def randomcolor(self):
        colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
        color = ""
        for i in range(6):
            color += colorArr[random.randint(0,14)]
        return "#"+color

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            raise ParseError('Empty content')
        labels = json.load(request.data['file'])
        project = get_object_or_404(Project, pk=kwargs['project_id'])
        try:
            for label in labels:
                if not 'background_color' in label.keys():
                    label['background_color'] = self.randomcolor()
                serializer = LabelSerializer(data=label)
                serializer.is_valid(raise_exception=True)
                serializer.save(project=project)
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError:
            content = {'error': 'IntegrityError: you cannot create a label with same name or shortkey.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

class RelationUploadAPI(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def randomcolor(self):
        colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
        color = ""
        for i in range(6):
            color += colorArr[random.randint(0,14)]
        return "#"+color

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            raise ParseError('Empty content')
        relations = json.load(request.data['file'])
        project = get_object_or_404(Project, pk=kwargs['project_id'])
        try:
            for relation in relations:
                if not 'color' in relation.keys():
                    relation['color'] = self.randomcolor()
                serializer = RelationSerializer(data=relation)
                serializer.is_valid(raise_exception=True)
                serializer.save(project=project)
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError:
            content = {'error': 'IntegrityError: you cannot create a label with same name or shortkey.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
