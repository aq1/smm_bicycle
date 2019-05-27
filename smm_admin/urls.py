from django.urls import path, include
from django.views import generic

from rest_framework.routers import DefaultRouter

from .views import (
    account,
    auth,
    canvas,
)
from smm_admin.views.posts import (
    new_post,
    edit_post,
    post_api,
    list_posts,
    post,
    suggest_post,
)

from .views.services import (
    facebook,
    telegram,
    twitter,
    vk,
)


router = DefaultRouter()
router.register(r'post', post_api.PostViewSet, basename='post')


urlpatterns = [

    path('api/', include(router.urls)),

    path('posts/', list_posts.list_posts, name='list_posts'),

    path('post/<int:post_id>/save_canvas/', canvas.save_canvas),
    path('post/<int:post_id>/save_render/', canvas.save_render),

    path('new/', new_post.new_post, name='new_post'),
    path('p/<int:post_id>/edit/', edit_post.edit_post, name='edit_post'),

    path('p/<int:post_id>/', post.post_view, name='post'),
    path('p/<str:token>/', post.post_view, name='post'),
    path('p/<int:post_id>/canvas/', canvas.canvas, name='canvas'),

    path('suggest/<int:account_id>/', suggest_post.post_suggest_view),

    path('me/', account.account, name='account'),
    path('account_post/', account.account_post, name='account_post'),
    path('account_service_delete/<int:service_id>/', account.delete_service, name='delete_service'),

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
    path('logout/', auth.logout_view, name='logout'),

    path(
        'facebook_terms/',
        generic.TemplateView.as_view(template_name='smm_admin/facebook_terms_of_service.html'),
        name='facebook_terms',
    ),
]
