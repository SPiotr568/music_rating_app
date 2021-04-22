from django.urls import path
from rate import views
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('saved/', views.ratedSongs, name='rated_songs'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('song/<str:pk>/', views.song, name='song'),
    path('search_to_add/', views.searchToAdd, name='search_to_add'),
    path('add_song/<str:song_id>/', views.addSong, name='add_song'),
    path('search/', views.search, name='search'),
    # path('reeset_password/', auth_views.PasswordResetView.as_view(), name="reset_password"),
    # path('reeset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    # path('reeset_password/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    # path('reeset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]