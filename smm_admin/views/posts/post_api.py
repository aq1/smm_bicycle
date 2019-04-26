from collections import defaultdict

from django.conf import settings

from django_filters import rest_framework as filters
from easy_thumbnails.fields import ThumbnailerImageField
from rest_framework import (
    serializers,
    viewsets,
    permissions,
)

from smm_admin.models import (
    Account,
    Post,
)


class IsAuthorOrToken(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.query_params.get('t'):
            return obj.token == request.query_params['t']
        return obj.account_id == request.user.id


class PostFilter(filters.FilterSet):
    status = filters.ChoiceFilter(
        choices=Post.STATUSES,
    )
    earlier = filters.DateTimeFilter(
        field_name='schedule',
        lookup_expr='lte',
    )
    later = filters.DateTimeFilter(
        field_name='schedule',
        lookup_expr='gte',
    )

    class Meta:
        model = Post
        fields = [
            'status',
            'earlier',
            'later',
        ]


class PreviewsField(serializers.Field):

    def to_representation(self, obj):
        previews = defaultdict(dict)
        for field in obj._meta.fields:
            if isinstance(field, ThumbnailerImageField):
                val = getattr(obj, field.name)
                for thumb in settings.THUMBNAIL_ALIASES[''].keys():
                    if val:
                        previews[field.name][thumb] = val[thumb].url
                    else:
                        previews[field.name][thumb] = ''
        return previews

    def to_internal_value(self, data):
        pass

    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        kwargs['source'] = '*'

        super().__init__(**kwargs)


class PostSerializer(serializers.ModelSerializer):
    previews = PreviewsField()

    class Meta:
        model = Post
        fields = '__all__'
        depth = 1


class PostTokenSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    class Meta:
        model = Post
        exclude = (
            'schedule',
            'rendered_image',
            'text_ru',
            'canvas_json',
        )


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrToken]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filterset_class = PostFilter
    ordering_fields = (
        'schedule',
        'status',
    )

    def perform_create(self, serializer):
        kwargs = {}
        if not serializer.validated_data.get('account_id') and self.request.user.is_authenticated:
            kwargs['account_id'] = self.request.user.id
        serializer.save(**kwargs)

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return PostSerializer

        return PostTokenSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Post.objects.filter(account_id=self.request.user.id)
        return Post.objects.filter(token=self.request.query_params.get('t', ''))
