# flashcards/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Deck, Flashcard, Note
from .forms import FlashcardForm, NoteForm, EditDeckForm, EditNoteForm
from .ai_service import (
    generate_flashcards,
    generate_notes,
    extract_text_from_pdf
)

@login_required
def home(request):
    query = request.GET.get('q', '').strip()
    decks = Deck.objects.filter(user=request.user)
    notes = Note.objects.filter(user=request.user)

    if query:
        decks = decks.filter(title__icontains=query)
        notes = notes.filter(title__icontains=query)

    return render(request, 'home.html', {
        'decks': decks,
        'notes': notes,
        'query': query,
    })

    
@login_required
def create_flashcards(request):
    if request.method == 'POST':
        form = FlashcardForm(request.POST, request.FILES)
        if form.is_valid():
            title     = form.cleaned_data['title']
            text      = form.cleaned_data.get('text', '') or ''
            pdf_file  = form.cleaned_data['pdf_file']
            # num_cards = form.cleaned_data['num_cards']

            try:
                num_cards = int(request.POST.get('num_cards', 5))
                num_cards =  max(1, min(20, num_cards))
            except (ValueError, TypeError):
                num_cards = 5


            if pdf_file:
                try:
                    text = extract_text_from_pdf(pdf_file)
                except (ValueError, RuntimeError) as e:
                    form.add_error(None, str(e))
                    return render(request, 'create_flashcards.html', {'form': form})

            try:
                cards_data = generate_flashcards(text, num_cards)
                deck = Deck.objects.create(user=request.user,title=title)
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
        form = FlashcardForm()

    return render(request, 'create_flashcards.html', {'form': form})



# def edit_falshcards(request):


@login_required
def view_deck(request, pk):
    deck  = get_object_or_404(Deck, pk=pk, user=request.user)
    cards = deck.cards.filter()
    return render(request, 'view_deck.html', {
        'deck': deck,
        'cards': cards
    })

@login_required
def edit_deck(request, pk):
    deck = get_object_or_404(Deck, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EditDeckForm(request.POST)
        if form.is_valid():
            deck.title = form.cleaned_data['title']
            deck.save()
            messages.success(request, 'Deck Title Edited successfully.')
        return redirect('view_deck', pk=deck.pk)
    else:
        form = EditDeckForm(initial={'title': deck.title})

    return render(request,'edit_deck.html', {'form': form, 'deck': deck})


@login_required
def delete_deck(request, pk):
    deck = get_object_or_404(Deck, pk=pk, user=request.user)
    if request.method == 'POST':
        deck.delete()
        messages.success(request, 'Deck deleted.')
    return redirect('home')


@login_required
def create_notes(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            title    = form.cleaned_data['title']
            text     = form.cleaned_data.get('text', '') or ''
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
                    user=request.user,
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


@login_required
def view_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    return render(request, 'view_note.html', {
        'note': note,
        'key_points': note.key_points_list()
    })


@login_required
def edit_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EditNoteForm(request.POST)
        if form.is_valid():
            note.title = form.cleaned_data['title']
            note.save()
            messages.success(request, 'Note title edited successfullty.')
            return redirect('view_note', pk=note.pk)
    else:
        form = EditNoteForm(initial={'title': note.title})
    
    return render(request, 'edit_note.html',{'form': form, 'note': note})


@login_required
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted.')
    return redirect('home')