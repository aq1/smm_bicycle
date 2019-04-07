from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    account,
    auth,
    canvas,
)
from smm_admin.views.posts import (
    new_post,
    post_api,
    list_posts,
    post,
    post_suggestion,
)

from .views.services import (
    facebook,
    telegram,
    twitter,
    vk,
)


router = DefaultRouter()
router.register(r'posts', post_api.PostViewSet, basename='post')


urlpatterns = [

    path('api/', include(router.urls)),

    path('posts/', list_posts.list_posts, name='list_posts'),

    path('post/<int:post_id>/save_canvas/', canvas.save_canvas),
    path('post/<int:post_id>/save_render/', canvas.save_render),

    path('new/', new_post.PostView.as_view()),
    path('new/<int:post_id>/upload_files/', new_post.post_file_upload),

    path('p/<int:post_id>/', post.post_view, name='post'),
    path('p/<int:post_id>/edit_image/', canvas.edit_image, name='edit_image'),

    path('suggest/', post_suggestion.PostSuggestionView.as_view()),
    path('suggest/<int:post_id>/upload_files/', post_suggestion.post_suggestion_file_upload),
    path('suggested/', post_suggestion.post_suggestion_view, name='suggested'),
    path(
        'suggested/create_post/<int:post_id>/<str:redirect_to_image_edit>/',
        post_suggestion.create_post_from_suggested,
        name='suggested_to_post_redirect',
    ),

    path('me/', account.account, name='account'),
    path('account_post/', account.account_post, name='account_post'),

    path('vk_auth/', vk.vk_auth, name='vk_auth'),
    path('vk_auth_post/', vk.vk_auth_post, name='vk_auth_post'),
    path('vk_groups/', vk.vk_groups, name='vk_groups'),
    path('vk_auth/g/', vk.vk_group_selected, name='vk_group_selected'),

    path('tg_form/', telegram.telegram_channel_form, name='telegram_channel_form'),
    path('telegram_auth/', telegram.telegram_auth, name='telegram_auth'),

    path('twitter_auth/', twitter.twitter_auth, name='twitter_auth'),

    path('fb_auth/', facebook.fb_auth, name='fb_auth'),
    path('fb_groups/', facebook.fb_groups_select, name='fb_groups_select'),
    path('fb_auth/p/', facebook.fb_group_selected, name='fb_group_selected'),

    path('', auth.login_view, name='login'),
    path('login/', auth.login_post, name='login_post'),
]
