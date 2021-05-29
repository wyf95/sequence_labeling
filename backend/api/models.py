import string
import numpy as np

from django.db import models
from django.dispatch import receiver
from django.db.models import Count
from django.db.models.signals import post_save, pre_delete, post_delete
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .managers import AnnotationManager

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='')
    guideline = models.TextField(default='', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User, related_name='projects')
    entity_concordance = models.DecimalField(default=1.00, max_digits=6, decimal_places=4)
    relation_concordance = models.DecimalField(default=1.00, max_digits=6, decimal_places=4)

    def get_absolute_url(self):
        return reverse('upload', args=[self.id])

    def __str__(self):
        return self.name
    
    def get_bundle_name(self):
        return 'sequence_labeling'

    def get_bundle_name_upload(self):
        return 'upload_sequence_labeling'

    def get_bundle_name_download(self):
        return 'download_sequence_labeling'

    def get_annotation_serializer(self):
        from .serializers import SequenceAnnotationSerializer
        return SequenceAnnotationSerializer

    def get_annotation_class(self):
        return SequenceAnnotation

    def get_connection_serializer(self):
        from .serializers import ConnectionSerializer
        return ConnectionSerializer

    def get_connection_class(self):
        return Connection
    
    def get_docmapping_serializer(self):
        from .serializers import DocMappingSerializer
        return DocMappingSerializer

    def get_docmapping_class(self):
        return DocMapping

    def get_storage(self, data):
        from .utils import SequenceLabelingStorage
        return SequenceLabelingStorage(data, self)


class Label(models.Model):
    PREFIX_KEYS = (
        ('ctrl', 'ctrl'),
        ('shift', 'shift'),
        ('ctrl shift', 'ctrl shift')
    )
    SUFFIX_KEYS = tuple(
        (c, c) for c in string.digits + string.ascii_lowercase
    )

    text = models.CharField(max_length=100)
    prefix_key = models.CharField(max_length=10, blank=True, null=True, choices=PREFIX_KEYS)
    suffix_key = models.CharField(max_length=1, blank=True, null=True, choices=SUFFIX_KEYS)
    project = models.ForeignKey(Project, related_name='labels', on_delete=models.CASCADE)
    background_color = models.CharField(max_length=7, default='#209cee')
    text_color = models.CharField(max_length=7, default='#ffffff')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

    def clean(self):
        # Don't allow shortcut key not to have a suffix key.
        if self.prefix_key and not self.suffix_key:
            raise ValidationError('Shortcut key may not have a suffix key.')

        # each shortcut (prefix key + suffix key) can only be assigned to one label
        if self.suffix_key or self.prefix_key:
            other_labels = self.project.labels.exclude(id=self.id)
            if other_labels.filter(suffix_key=self.suffix_key, prefix_key=self.prefix_key).exists():
                raise ValidationError('A label with this shortcut already exists in the project')

        super().clean()

    class Meta:
        unique_together = (
            ('project', 'text'),
        )

class Document(models.Model):
    text = models.TextField()
    project = models.ForeignKey(Project, related_name='documents', on_delete=models.CASCADE)
    meta = models.TextField(default='{}')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    annotations_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    entity_concordance = models.DecimalField(default=1.00, max_digits=6, decimal_places=4)
    relation_concordance = models.DecimalField(default=1.00, max_digits=6, decimal_places=4)

    def __str__(self):
        return self.text[:50]

class Annotation(models.Model):
    objects = AnnotationManager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SequenceAnnotation(Annotation):
    document = models.ForeignKey(Document, related_name='seq_annotations', on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    start_offset = models.IntegerField()
    end_offset = models.IntegerField()


    def clean(self):
        if self.start_offset >= self.end_offset:
            raise ValidationError('start_offset is after end_offset')

    class Meta:
        unique_together = ('document', 'user', 'label', 'start_offset', 'end_offset')

class Relation(models.Model):
    text = models.CharField(max_length=100)
    project = models.ForeignKey(Project, related_name='relations', on_delete=models.CASCADE)
    color = models.CharField(max_length=7, default='#209cee')

    def __str__(self):
        return self.text

    class Meta:
        unique_together = (
            ('project', 'text'),
        )

class Connection(models.Model):
    document = models.ForeignKey(Document, related_name='seq_connections', on_delete=models.CASCADE)
    source = models.ForeignKey(SequenceAnnotation, related_name='conn_source', on_delete=models.CASCADE)
    to = models.ForeignKey(SequenceAnnotation, related_name='conn_to', on_delete=models.CASCADE)
    relation = models.ForeignKey(Relation, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        unique_together = ('document', 'relation', 'source', 'to')


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RoleMapping(models.Model):
    user = models.ForeignKey(User, related_name='role_mappings', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='role_mappings', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        other_rolemappings = self.project.role_mappings.exclude(id=self.id)

        if other_rolemappings.filter(user=self.user, project=self.project).exists():
            raise ValidationError('This user is already assigned to a role in this project.')

    class Meta:
        unique_together = ("user", "project", "role")

class DocMapping(models.Model):
    project = models.ForeignKey(Project, related_name='doc_mappings', on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    rolemap = models.ForeignKey(RoleMapping, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("project", "document", "rolemap")



def fleiss(table, n):
    table = 1.0 * np.asarray(table) 
    n_sub, _ = table.shape

    if table.sum() != n * n_sub:
        n_add = n - table.sum(1)
        table = np.insert(table, 0, values=n_add, axis=1)
  
    p_j = table.sum(0) / (n_sub * n)
    table2 = table * table
    p_i = (table2.sum(1) - n) / (n * (n - 1.))

    p_o = p_i.mean()
    p_e = (p_j*p_j).sum()
    if p_e == 1.:
        return 1.
    kappa = (p_o - p_e) / (1 - p_e)
    return kappa

def comput_annotation_concordance(instance):
    documentInstance = instance.document
    if not documentInstance:
        return
    document = Document.objects.get(pk=documentInstance.pk)
    annotations = SequenceAnnotation.objects.filter(document=document.id)
    users = annotations.values('user').annotate(count=Count('user'))
    # 无标签或只有一个用户
    if len(users) < 2:
        document.entity_concordance = 1
        document.save()
        return

    labels = annotations.values('label').annotate(count=Count('label'))

    annotation_json = {}
    for a in annotations:
        key = str(a.start_offset) + '_' + str(a.end_offset)
        if not key in annotation_json.keys():
            annotation_json[key] = {k['label']:0 for k in labels}
        annotation_json[key][a.label.id] = annotation_json[key][a.label.id] + 1
    annotation_list = [[j for i, j in v.items()] for k, v in annotation_json.items()]
    f = fleiss(annotation_list, len(users))
    document.entity_concordance = f
    document.save()

def comput_relation_concordance(instance):
    documentInstance = instance.document
    if not documentInstance:
        return
    document = Document.objects.get(pk=documentInstance.pk)
    connections = Connection.objects.filter(document=document.id)
    
    connection_list = []
    users = []
    labels = []
    for c in connections:
        temp = {}
        source = c.source
        end = c.to
        temp['path'] = str(source.start_offset) + '_' + str(source.end_offset) + '__' + str(end.start_offset) + '_' + str(end.end_offset)
        temp['user'] = source.user.id
        if c.relation:
            temp['label'] = c.relation.id
        else:
            temp['label'] = 0
        if temp['user'] not in users:
            users.append(temp['user'])
        if temp['label'] not in labels:
            labels.append(temp['label'])
        connection_list.append(temp)
    
    if len(users) < 2:
        document.relation_concordance = 1
        document.save()
        return

    connection_json = {}
    for c in connection_list:
        key = c['path']
        if not key in connection_json.keys():
            connection_json[key] = {k:0 for k in labels}
        connection_json[key][c['label']] = connection_json[key][c['label']] + 1
    connection_list2 = [[j for i, j in v.items()] for k, v in connection_json.items()]
    f = fleiss(connection_list2, len(users))
    document.relation_concordance = f
    document.save()

def comput_project_concordance(instance):
    project = instance.project
    if not project:
        return
    documents = Document.objects.filter(project=project.id)
    if len(documents) != 0:
        documents_entity_concordance = np.array([k.entity_concordance for k in documents])
        project.entity_concordance = documents_entity_concordance.mean()
        documents_relation_concordance = np.array([k.relation_concordance for k in documents])
        project.relation_concordance = documents_relation_concordance.mean()
        project.save()
    else:
        project.entity_concordance = 1.0
        project.relation_concordance = 1.0
        project.save()

@receiver(post_save, sender=SequenceAnnotation)
def save_annotation_comput_concordance(sender, instance, created, **kwargs):
    comput_annotation_concordance(instance)
        
@receiver(post_delete, sender=SequenceAnnotation)
def delete_annotation_comput_concordance(sender, instance, using, **kwargs):
    comput_annotation_concordance(instance)

@receiver(post_save, sender=Connection)
def save_connection_comput_concordance(sender, instance, created, **kwargs):
    comput_relation_concordance(instance)
        
@receiver(post_delete, sender=Connection)
def delete_connection_comput_concordance(sender, instance, using, **kwargs):
    comput_relation_concordance(instance)

@receiver(post_save, sender=Document)
def save_document_comput_concordance(sender, instance, created, **kwargs):
    comput_project_concordance(instance)

@receiver(post_delete, sender=Document)
def delete_document_comput_concordance(sender, instance, using, **kwargs):
    comput_project_concordance(instance)


@receiver(post_save, sender=RoleMapping)
def add_linked_project(sender, instance, created, **kwargs):
    if not created:
        return
    userInstance = instance.user
    projectInstance = instance.project
    if userInstance and projectInstance:
        user = User.objects.get(pk=userInstance.pk)
        project = Project.objects.get(pk=projectInstance.pk)
        user.projects.add(project)
        user.save()

@receiver(pre_delete, sender=RoleMapping)
def delete_linked_project(sender, instance, using, **kwargs):
    userInstance = instance.user
    projectInstance = instance.project
    if userInstance and projectInstance:
        user = User.objects.get(pk=userInstance.pk)
        project = Project.objects.get(pk=projectInstance.pk)
        user.projects.remove(project)
        user.save()
