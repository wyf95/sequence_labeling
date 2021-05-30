import numpy as np
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Subquery
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (Connection, DocMapping, Document, Label, Project,
                     Relation, Role, RoleMapping, SequenceAnnotation)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_superuser')

class LabelSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        prefix_key = attrs.get('prefix_key')
        suffix_key = attrs.get('suffix_key')

        # In the case of user don't set any shortcut key.
        if prefix_key is None and suffix_key is None:
            return super().validate(attrs)

        # Don't allow shortcut key not to have a suffix key.
        if prefix_key and not suffix_key:
            raise ValidationError('Shortcut key may not have a suffix key.')

        # Don't allow to save same shortcut key when prefix_key is null.
        try:
            context = self.context['request'].parser_context
            project_id = context['kwargs']['project_id']
            label_id = context['kwargs'].get('label_id')
        except (AttributeError, KeyError):
            pass  # unit tests don't always have the correct context set up
        else:
            conflicting_labels = Label.objects.filter(
                suffix_key=suffix_key,
                prefix_key=prefix_key,
                project=project_id,
            )

            if label_id is not None:
                conflicting_labels = conflicting_labels.exclude(id=label_id)

            if conflicting_labels.exists():
                raise ValidationError('Duplicate shortcut key.')

        return super().validate(attrs)

    class Meta:
        model = Label
        fields = ('id', 'text', 'prefix_key', 'suffix_key', 'background_color', 'text_color')


class DocumentSerializer(serializers.ModelSerializer):
    annotations = serializers.SerializerMethodField()
    connections = serializers.SerializerMethodField()
    annotation_approver = serializers.SerializerMethodField()
    annotator_assign = serializers.SerializerMethodField()
    approver_assign = serializers.SerializerMethodField()

    def is_role_of(self, user_id, project_id, role_name):
        return RoleMapping.objects.filter(
                    user_id=user_id,
                    project_id=project_id,
                    role_id=Subquery(Role.objects.filter(name=role_name).values('id')),
                ).exists()

    def get_annotations(self, instance):
        project = instance.project
        model = project.get_annotation_class()
        serializer = project.get_annotation_serializer()
        annotations = model.objects.filter(document=instance.id)
        
        request = self.context.get("request")
        if request and self.is_role_of(request.user.id, project.id, 'annotator'):
            annotations = annotations.filter(user=request.user)

        serializer = serializer(annotations, many=True)
        return serializer.data
    
    def get_connections(self, instance):
        project = instance.project
        model = project.get_connection_class()
        serializer = project.get_connection_serializer()
        connections = model.objects.filter(document=instance.id)
        serializer = serializer(connections, many=True)
        return serializer.data
    
    def get_annotator_assign(self, instance):
        project = instance.project
        model = project.get_docmapping_class()
        serializer = project.get_docmapping_serializer()
        assign = model.objects.filter(document=instance.id, rolemap__role__name='annotator')
        serializer = serializer(assign, many=True)
        users = []
        for i in serializer.data:
            users.append(i['username'])
        return users

    def get_approver_assign(self, instance):
        project = instance.project
        model = project.get_docmapping_class()
        serializer = project.get_docmapping_serializer()
        assign = model.objects.filter(document=instance.id, rolemap__role__name='annotation_approver')
        serializer = serializer(assign, many=True)
        users = []
        for i in serializer.data:
            users.append(i['username'])
        return users

    @classmethod
    def get_annotation_approver(cls, instance):
        approver = instance.annotations_approved_by
        return approver.username if approver else None

    class Meta:
        model = Document
        fields = ('id', 'text', 'annotations', 'connections', 'annotation_approver', 'approver_assign', 'annotator_assign', 'entity_concordance', 'relation_concordance')


class ApproverSerializer(DocumentSerializer):

    class Meta:
        model = Document
        fields = ('id', 'annotation_approver')


class ProjectSerializer(serializers.ModelSerializer):
    current_users_role = serializers.SerializerMethodField()
    entity_concordance = serializers.SerializerMethodField()
    relation_concordance = serializers.SerializerMethodField()

    def get_current_users_role(self, instance):
        role_abstractor = {
            "is_project_admin": settings.ROLE_PROJECT_ADMIN,
            "is_annotator": settings.ROLE_ANNOTATOR,
            "is_annotation_approver": settings.ROLE_ANNOTATION_APPROVER,
        }
        queryset = RoleMapping.objects.values("role_id__name")
        if self.context.get("request").user.is_superuser:
            role_abstractor = {
                "is_project_admin": True,
                "is_annotator": False,
                "is_annotation_approver": False,
            }
            return role_abstractor
        if queryset:
            users_role = get_object_or_404(
                queryset, project=instance.id, user=self.context.get("request").user.id
            )
            for key, val in role_abstractor.items():
                role_abstractor[key] = users_role["role_id__name"] == val
        return role_abstractor
    
    def get_entity_concordance(self, instance):
        documents = Document.objects.filter(project=instance.id)
        if len(documents) != 0:
            documents_entity_concordance = np.array([k.entity_concordance for k in documents])
            return round(documents_entity_concordance.mean(), 4)
        else:
            return 1.0

    def get_relation_concordance(self, instance):
        documents = Document.objects.filter(project=instance.id)
        if len(documents) != 0:
            documents_relation_concordance = np.array([k.relation_concordance for k in documents])
            return round(documents_relation_concordance.mean(), 4)
        else:
            return 1.0


    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'guideline', 'users', 'entity_concordance', 'relation_concordance', 'current_users_role', 'updated_at')
        read_only_fields = ('updated_at', 'users', 'current_users_role')



class ProjectFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def get_queryset(self):
        view = self.context.get('view', None)
        request = self.context.get('request', None)
        queryset = super(ProjectFilteredPrimaryKeyRelatedField, self).get_queryset()
        if not request or not queryset or not view:
            return None
        return queryset.filter(project=view.kwargs['project_id'])


class SequenceAnnotationSerializer(serializers.ModelSerializer):
    label = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all())
    document = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all())
    username = serializers.SerializerMethodField()

    def get_username(cls, instance):
        user = instance.user
        return user.username if user else None

    class Meta:
        model = SequenceAnnotation
        fields = ('id', 'label', 'start_offset', 'end_offset', 'user', 'username', 'document', 'created_at', 'updated_at')
        read_only_fields = ('user',)

class RelationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Relation
        fields = ('id', 'text', 'color')

class ConnectionSerializer(serializers.ModelSerializer):
    document = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all())

    class Meta:
        model = Connection
        fields = ('id', 'document', 'source', 'to', 'relation')


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name')


class RoleMappingSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    rolename = serializers.SerializerMethodField()

    @classmethod
    def get_username(cls, instance):
        user = instance.user
        return user.username if user else None

    @classmethod
    def get_rolename(cls, instance):
        role = instance.role
        return role.name if role else None

    class Meta:
        model = RoleMapping
        fields = ('id', 'user', 'role', 'username', 'rolename')

class DocMappingSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    rolename = serializers.SerializerMethodField()

    @classmethod
    def get_username(cls, instance):
        user = instance.rolemap.user
        return user.username if user else None

    @classmethod
    def get_rolename(cls, instance):
        role = instance.rolemap.role
        return role.name if role else None

    class Meta:
        model = DocMapping
        fields = ('id', 'document', 'project', 'rolemap', 'username', 'rolename')
