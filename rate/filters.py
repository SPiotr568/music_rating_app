import django_filters
from django_filters import CharFilter
from .models import *

class SongFilter(django_filters.FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")
    author = CharFilter(field_name="author", lookup_expr="icontains")
    class Meta:
        model = Song
        fields = ['url']