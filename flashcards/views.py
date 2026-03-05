# flashcards/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Deck, Flashcard, Note
from .forms import FlashcardForm, NoteForm
from .ai_service import (
    generate_flashcards,
    generate_notes,
    extract_text_from_pdf
)


def home(request):
    decks = Deck.objects.all()
    notes = Note.objects.all()
    return render(request, 'home.html', {
        'decks': decks,
        'notes': notes
    })


def create_flashcards(request):
    if request.method == 'POST':
        form = FlashcardForm(request.POST, request.FILES)
        if form.is_valid():
            title     = form.cleaned_data['title']
            text      = form.cleaned_data['text']
            pdf_file  = form.cleaned_data['pdf_file']
            num_cards = form.cleaned_data['num_cards']

            # PDF takes priority
            if pdf_file:
                try:
                    text = extract_text_from_pdf(pdf_file)
                except (ValueError, RuntimeError) as e:
                    form.add_error(None, str(e))
                    return render(request, 'create_flashcards.html', {'form': form})

            try:
                cards_data = generate_flashcards(text, num_cards)
                deck = Deck.objects.create(title=title)
                for card in cards_data:
                    Flashcard.objects.create(
                        deck=deck,
                        question=card['question'],
                        answer=card['answer']
                    )
                messages.success(request, f'✅ {len(cards_data)} flashcards created!')
                return redirect('view_deck', pk=deck.pk)

            except (ValueError, RuntimeError) as e:
                form.add_error(None, f'Generation failed: {str(e)}')

    else:
        form = FlashcardForm(initial={'num_cards': 5})

    return render(request, 'create_flashcards.html', {'form': form})


def view_deck(request, pk):
    deck  = get_object_or_404(Deck, pk=pk)
    cards = deck.cards.all()
    return render(request, 'view_deck.html', {
        'deck': deck,
        'cards': cards
    })


def delete_deck(request, pk):
    deck = get_object_or_404(Deck, pk=pk)
    if request.method == 'POST':
        deck.delete()
        messages.success(request, 'Deck deleted.')
    return redirect('home')


def create_notes(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            title    = form.cleaned_data['title']
            text     = form.cleaned_data['text']
            pdf_file = form.cleaned_data['pdf_file']

            # PDF takes priority
            if pdf_file:
                try:
                    text = extract_text_from_pdf(pdf_file)
                except (ValueError, RuntimeError) as e:
                    form.add_error(None, str(e))
                    return render(request, 'create_notes.html', {'form': form})

            try:
                result = generate_notes(text)
                key_points_str = '\n'.join(
                    f'• {point}' for point in result['key_points']
                )
                note = Note.objects.create(
                    title=title,
                    original_text=text,
                    summary=result['summary'],
                    key_points=key_points_str
                )
                messages.success(request, '✅ Notes generated successfully!')
                return redirect('view_note', pk=note.pk)

            except (ValueError, RuntimeError) as e:
                form.add_error(None, f'Generation failed: {str(e)}')

    else:
        form = NoteForm()

    return render(request, 'create_notes.html', {'form': form})


def view_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    return render(request, 'view_note.html', {
        'note': note,
        'key_points': note.key_points_list()
    })


def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted.')
    return redirect('home')