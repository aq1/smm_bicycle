from django.urls import path

from .views import (
    account,
    auth,
    edit_image,
    post,
    post_suggestion,
)

from .views.services import (
    facebook,
    telegram,
    twitter,
    vk,
)

urlpatterns = [
    path('post/<int:post_id>/', post.post),
    path('post/<int:post_id>/save_canvas/', post.save_canvas),
    path('post/<int:post_id>/save_render/', post.save_render),
    path('p/', post.PostView.as_view()),
    path('p/<int:post_id>/upload_files/', post.post_file_upload),
    path('post/<int:post_id>/edit_image/', edit_image.edit_image),

    path('suggest/', post_suggestion.PostSuggestionView.as_view()),
    path('suggest/<int:post_id>/upload_files/', post_suggestion.post_suggestion_file_upload),
    path('suggested/', post_suggestion.post_suggestion_view, name='suggested'),
    path('suggested/create_post/<int:post_id>/', post_suggestion.create_post_from_suggested, name='suggested_to_post'),
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
