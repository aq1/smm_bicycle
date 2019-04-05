from django_filters import rest_framework as filters
from rest_framework import (
    serializers,
    viewsets,
    permissions,
)

from smm_admin.models import (
    Post,
    Link,
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


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        exclude = (
            'post',
        )
        depth = 1


class PostSerializer(serializers.ModelSerializer):
    links = LinkSerializer(read_only=True, many=True)

    class Meta:
        model = Post
        fields = '__all__'
        depth = 1


class PostViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthor]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filterset_class = PostFilter
    ordering_fields = (
        'schedule',
        'status',
    )

    def get_queryset(self):
        return super().get_queryset().filter(
            account_id=self.request.user.id
        )
