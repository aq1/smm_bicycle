from django_filters import rest_framework as filters
from rest_framework import (
    serializers,
    viewsets,
    mixins,
    permissions,
)

from smm_admin.models import (
    Account,
    Post,
)


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
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


class PostSerializer(serializers.ModelSerializer):
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
            'name_ru',
            'text_ru',
            'canvas_json',
        )


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthor]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filterset_class = PostFilter
    ordering_fields = (
        'schedule',
        'status',
    )


class PostTokenViewSet(viewsets.ModelViewSet):

    queryset = Post.objects.all()
    serializer_class = PostTokenSerializer
    lookup_field = 'token'

    def destroy(self, request, *args, **kwargs):
        pass

    def list(self, request, *args, **kwargs):
        pass
