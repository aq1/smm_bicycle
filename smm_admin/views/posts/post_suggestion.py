import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.utils import IntegrityError
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django import views
from django import http

from smm_admin.models import (
    PostSuggestion,
    Post,
)


class PostSuggestionView(views.View):
    @staticmethod
    def get(request):
        return render(request, 'smm_admin/posts/post_suggestion_form.html')

    @staticmethod
    def post(request):
        data = json.loads(request.body)

        try:
            data = dict(
                links=[link['value'] for link in data['links'] if link['value']],
                name_en=data['name'],
                old_work_year=data['old_work']['year'],
                new_work_year=data['new_work']['year'],
                old_work_url=data['old_work'].get('url', ''),
                new_work_url=data['new_work'].get('url', ''),
                text=data.get('text', ''),
            )
        except KeyError:
            return http.HttpResponse(status=400)

        try:
            post = PostSuggestion.objects.create(**data)
        except IntegrityError:
            return http.HttpResponse(status=400)
        return http.JsonResponse(
            {
                'post_id': post.id,
                'token': post.token,
            },
            status=201,
        )


@require_http_methods(['POST'])
def post_suggestion_file_upload(request, post_id):

    if not request.GET.get('t'):
        return http.HttpResponse(status=400)

    try:
        post = PostSuggestion.objects.get(
            id=post_id,
            token=request.GET['t'],
        )
    except PostSuggestion.DoesNotExist:
        return http.HttpResponse(status=400)

    files = request.FILES
    if not files:
        return http.HttpResponse(status=400)

    post.old_work = files.get('old_work')
    post.new_work = files.get('new_work')
    if not (post.old_work or post.new_work):
        return http.HttpResponse(status=400)

    try:
        post.save()
    except IntegrityError:
        return http.HttpResponse(status=400)

    return http.HttpResponse(reverse('suggested'))


def post_suggestion_view(request):
    try:
        return render(
            request,
            'smm_admin/posts/post_suggestion_view.html',
            {
                'post': PostSuggestion.objects.get(token=request.GET['t']),
                'user': request.user,
            },
        )
    except (KeyError, PostSuggestion.DoesNotExist):
        return http.HttpResponse(status=400)


@require_http_methods(['POST'])
@login_required
def create_post_from_suggested(request, post_id, redirect_to_image_edit=False):
    suggested = get_object_or_404(PostSuggestion, id=post_id)

    if not (suggested.old_work and suggested.new_work):
        return http.JsonResponse(
            {'error': 'Image is not downloaded yet. Try later'},
            status=400,
        )

    try:
        post = Post.objects.create(
            account=request.user.account,
            name_en=suggested.name_en,
            name_ru=suggested.name_ru,
            text=suggested.text,
            old_work_year=suggested.old_work_year,
            new_work_year=suggested.new_work_year,
            old_work=suggested.old_work,
            new_work=suggested.new_work,
        )
    except IntegrityError:
        return http.JsonResponse({'error': 'Failed to save post'}, status=400)
