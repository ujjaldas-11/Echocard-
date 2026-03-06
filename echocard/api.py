from ninja import Schema, File
from ninja_extra import NinjaExtraAPI   
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth
from ninja.files import UploadedFile
from django.contrib.auth.models import User 
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from typing import List, Optional
from datetime import datetime
from flashcards.models import Deck, Note, Flashcard
from flashcards.ai_service import (
    generate_flashcards,
    generate_notes,
    extract_text_from_pdf
)




api = NinjaExtraAPI(
    title="EchoCard API",
    version="1.0.0",
    description="AI FlashCard & Notes generator API",
    urls_namespace="api"  
)


api.register_controllers(NinjaJWTDefaultController)

class ResgisterSchema(Schema):
    username: str
    email: str
    password: str
    confirm_password: str

class UserOUt(Schema):
    id: int
    username: str
    email: str

class MessageSchema(Schema):
    message: str

class FlashCardOut(Schema):
    id: int
    question: str
    answer: str
    created_at: datetime

class DeckOut(Schema):
    id: int 
    title: str
    description: str
    created_at: datetime

class DeckDetailOut(Schema):
    id: int 
    title:str 
    strdescription: str
    created_at: datetime
    cards: list[FlashCardOut]


class NoteOut(Schema):
    id: int
    title: str
    summary: str
    key_points: str
    created_at: datetime

class GenerateFlashcardsSchema(Schema):
    title: str
    text: str
    num_cards: Optional[int] = 5


class GenerateNotesSchema(Schema):
    title: str
    text: str


# AUTH Endpoints
@api.post('/auth/register', response=UserOUt, tags=['AUTH'])
def register(request, payload: ResgisterSchema):
    if payload.password != payload.confirm_password:
        return api.create_response(
            request,
            {'message': 'Password do not mathch'},
            status=400
        )
    
    if User.objects.filter(username=payload.username).exists():
        return api.create_response(
            request, 
            {'message': 'username already taken.'},
            status=400
        )

    if User.objects.filter(email=payload.email).exists():
        return api.create_response(
            request,
            {'message': 'Email already Registered.'},
            status=400
        )
    
    try:
        validate_password(payload.password)
    except validators as e:
        return api.create_response(
            request,
            {message: {str(e)}},
            status=400
        )    

    user = User.objects.create_user(
        username=payload.username,
        email=payload.email,
        password=payload.password
    )
    return user

@api.get('/auth/me', response=UserOUt, auth=JWTAuth(),tags=['AUTH'])
def me(request):
    return request.user


#deck endpoint

@api.get('/decks', response=list[DeckOut], auth=JWTAuth(), tags=['Decks'])
def list_deck(request):
    return Deck.objects.filter(user=request.user).order_by('-created_at')


@api.get('/decks/{deck_id}', response=DeckDetailOut, auth=JWTAuth(), tags=['Decks'])
def get_deck(request, deck_id: int):
    try:
        deck = Deck.objects.get(pk=deck_id, user=request.user)
        return {
            'id': deck.id,
            'title': deck.title,
            'description': deck.description,
            'created_at': deck.created_at,
            'cards': list(deck.card.all())
        }
    except Deck.DoesNotExist:
        return api.create_response(
            request,
            {'message': 'Deck not found.'},
            status=404
        )

@api.get('/decks/{deck_id}', response=MessageSchema, auth=JWTAuth(), tags=['DECKS'])
def delete_deck_api(request, deck_id: int):
    try:
        deck = Deck.objects.get(pk=deck_id, user=request.user)
        deck.delete()
        return {'message': 'Defck deleted successfully.'}

    except Deck.DoesNotExist:
        return api.create_response(
            request,
            {'message': 'Deck not found.'},
            status=404
        )
    
#create flashcard endpoints
@api.post('decks/generate/text', response=DeckDetailOut, auth=JWTAuth(), tags=['Generate'])
def generate_flashcards_from_text(request, GenerateFlashcardsSchema):
    if not payload.text.strip:
        return api.create_response(
            request,
            {'message': 'Text cannot be empty.'},
            status=400
        )
    if not payload.title.strip():
        return api.create_response(
            request,
            {'message': 'Title cannot be empty.'},
            status=400
        )
    
    num_cards = max(1, min(20, payload.num_cards or 5))


    try:
        cards_data = generate_flashcards(payload.text, num_cards)

        # Save to database
        deck = Deck.objects.create(
            user=request.user,
            title=payload.title.strip()
        )
        for card in cards_data:
            Flashcard.objects.create(
                deck=deck,
                question=card['question'],
                answer=card['answer']
            )

        return {
            'id': deck.id,
            'title': deck.title,
            'description': deck.description,
            'created_at': deck.created_at,
            'cards': list(deck.cards.all())
        }

    except (ValueError, RuntimeError) as e:
        return api.create_response(
            request,
            {'message': f'Generation failed: {str(e)}'},
            status=500
        )


@api.post('/decks/generate/pdf', response=DeckDetailOut, auth=JWTAuth(), tags=['Generate'])
def generate_flashcards_from_pdf(
    request,
    title: str,
    num_cards: str,
    pdf_file: UploadedFile = File(...)
):

    if not pdf_file.name.endswith('.pdf'):
        return api.create_response(
            request,
            {'message': 'Only pdf file allowed'},
            status=400
        )
    

    try:
        cards_data = generate_flashcards(payload.text, num_cards)

        # Save to database
        deck = Deck.objects.create(
            user=request.user,
            title=payload.title.strip()
        )
        for card in cards_data:
            Flashcard.objects.create(
                deck=deck,
                question=card['question'],
                answer=card['answer']
            )

        return {
            'id': deck.id,
            'title': deck.title,
            'description': deck.description,
            'created_at': deck.created_at,
            'cards': list(deck.cards.all())
        }

    except (ValueError, RuntimeError) as e:
        return api.create_response(
            request,
            {'message': f'Generation failed: {str(e)}'},
            status=500
        )

    num_cards = max(1, min(20, num_cards))

    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_file)

        # Generate cards
        cards_data = generate_flashcards(text, num_cards)

        # Save to database
        deck = Deck.objects.create(
            user=request.user,
            title=title.strip()
        )
        for card in cards_data:
            Flashcard.objects.create(
                deck=deck,
                question=card['question'],
                answer=card['answer']
            )

        return {
            'id': deck.id,
            'title': deck.title,
            'description': deck.description,
            'created_at': deck.created_at,
            'cards': list(deck.cards.all())
        }

    except ValueError as e:
        return api.create_response(
            request,
            {'message': str(e)},
            status=400
        )
    except RuntimeError as e:
        return api.create_response(
            request,
            {'message': f'Generation failed: {str(e)}'},
            status=500
        )
@api.post('/notes/generate/text', response=NoteOut, auth=JWTAuth(), tags=['Generate'])
def generate_notes_from_text(request, payload: GenerateNotesSchema):
    """Generate notes from plain text."""

    if not payload.text.strip():
        return api.create_response(
            request,
            {'message': 'Text cannot be empty.'},
            status=400
        )
    if not payload.title.strip():
        return api.create_response(
            request,
            {'message': 'Title cannot be empty.'},
            status=400
        )

    try:
        result = generate_notes(payload.text)
        key_points_str = '\n'.join(
            f'• {point}' for point in result['key_points']
        )
        note = Note.objects.create(
            user=request.user,
            title=payload.title.strip(),
            original_text=payload.text,
            summary=result['summary'],
            key_points=key_points_str
        )
        return note

    except (ValueError, RuntimeError) as e:
        return api.create_response(
            request,
            {'message': f'Generation failed: {str(e)}'},
            status=500
        )


@api.post('/notes/generate/pdf', response=NoteOut, auth=JWTAuth(), tags=['Generate'])
def generate_notes_from_pdf(
    request,
    title: str,
    pdf_file: UploadedFile = File(...)
):
    """Generate notes from uploaded PDF."""

    if not pdf_file.name.endswith('.pdf'):
        return api.create_response(
            request,
            {'message': 'Only PDF files are allowed.'},
            status=400
        )

    try:
        text = extract_text_from_pdf(pdf_file)
        result = generate_notes(text)
        key_points_str = '\n'.join(
            f'• {point}' for point in result['key_points']
        )
        note = Note.objects.create(
            user=request.user,
            title=title.strip(),
            original_text=text,
            summary=result['summary'],
            key_points=key_points_str
        )
        return note

    except ValueError as e:
        return api.create_response(
            request,
            {'message': str(e)},
            status=400
        )
    except RuntimeError as e:
        return api.create_response(
            request,
            {'message': f'Generation failed: {str(e)}'},
            status=500
        )


# ─────────────────────────────────────────
# NOTES ENDPOINTS
# ─────────────────────────────────────────

@api.get('/notes', response=List[NoteOut], auth=JWTAuth(), tags=['Notes'])
def list_notes(request):
    return Note.objects.filter(user=request.user).order_by('-created_at')


@api.get('/notes/{note_id}', response=NoteOut, auth=JWTAuth(), tags=['Notes'])
def get_note(request, note_id: int):
    try:
        return Note.objects.get(pk=note_id, user=request.user)
    except Note.DoesNotExist:
        return api.create_response(
            request,
            {'message': 'Note not found.'},
            status=404
        )


@api.delete('/notes/{note_id}', response=MessageSchema, auth=JWTAuth(), tags=['Notes'])
def delete_note_api(request, note_id: int):
    try:
        note = Note.objects.get(pk=note_id, user=request.user)
        note.delete()
        return {'message': 'Note deleted successfully.'}
    except Note.DoesNotExist:
        return api.create_response(
            request,
            {'message': 'Note not found.'},
            status=404
        )



        


