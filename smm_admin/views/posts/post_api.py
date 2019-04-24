from django_filters import rest_framework as filters
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

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return PostSerializer

        return PostTokenSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Post.objects.filter(account_id=self.request.user.id)
        return Post.objects.filter(token=self.request.query_params.get('t', ''))
