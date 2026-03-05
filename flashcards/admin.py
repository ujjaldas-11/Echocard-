from django.contrib import admin
from .models import Deck, Flashcard, Note


class FlashcardInline(admin.TabularInline):
    model = Flashcard
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ['title', 'card_count', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [FlashcardInline]


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ['deck', 'question', 'created_at']
    search_fields = ['question', 'answer']
    list_filter = ['deck']
    readonly_fields = ['created_at']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title', 'summary']
    readonly_fields = ['created_at', 'updated_at']
