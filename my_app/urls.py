from django.urls import path, include
from django.contrib.auth import views as auth_view
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('tag/<slug:slug>/', views.TaggedPostListView.as_view(), name='tagged_posts'),
    path('category/<slug:slug>/', views.CategoryPostListView.as_view(), name='category_posts'),
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('share-post/', views.share_post, name='share_post'),
    path(
        "password_change/", auth_view.PasswordChangeView.as_view(), name="password_change"
    ),
    path("password_reset/", auth_view.PasswordResetView.as_view(), name="password_reset"),
    path(
        "reset/<uidb64>/<token>/",
        auth_view.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password_change/done/",
        auth_view.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "password_reset/done/",
        auth_view.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/done/",
        auth_view.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]


