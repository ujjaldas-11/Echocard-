from django.urls import path
from . import views

urlpatterns = [
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