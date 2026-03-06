from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    path('register/', auth_views.register_view, name='register'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),

    path('', views.home, name='home'),

    path('flashcards/create/', views.create_flashcards, name='create_flashcards'),
    path('flashcards/deck/<int:pk>/', views.view_deck, name='view_deck'),
    path('flashcards/deck/<int:pk>/edit', views.edit_deck, name='edit_deck'),
    path('flashcards/deck/<int:pk>/delete', views.delete_deck, name='delete_deck'),

    path('notes/create/', views.create_notes, name='create_notes'),
    path('notes/<int:pk>/', views.view_note, name='view_note'),
    path('notes/<int:pk>/edit', views.edit_note, name='edit_note'),
    path('notes/<int:pk>/delete', views.delete_note, name='delete_note')
]