from django.db.models import Count, Q
from django_filters.rest_framework import FilterSet, BooleanFilter

from .models import Document


class DocumentFilter(FilterSet):
    seq_annotations__isnull = BooleanFilter(field_name='seq_annotations', method='filter_annotations')

    def filter_annotations(self, queryset, field_name, value):
        queryset = queryset.annotate(num_annotations=
            Count(field_name, filter=
                Q(**{ f"{field_name}__user": self.request.user})))

        should_have_annotations = not value
        # 过滤：该用户有无标注
        if should_have_annotations:
            queryset = queryset.filter(num_annotations__gte=1)
        else:
            queryset = queryset.filter(num_annotations__lte=0)

        return queryset

    class Meta:
        model = Document
        fields = ('project', 'text', 'meta', 'created_at', 'updated_at',
                  'seq_annotations__label__id',
                  'seq_annotations__isnull')
