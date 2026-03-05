import os
import re
import json
import pdfplumber
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = 'llama-3.1-8b-instant'

def _run_groq(prompt: str, max_tokens: int = 1024 ) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a study assistant that helps students learn. "
                            "Always respond with valid JSON only. "
                            "No explanation, no markdown, no code blocks, no extra text."
                    )
                },
                
                {
                    "role": 'user',
                    "content": prompt 
                }
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"Grok API error: {str(e)}")


def _safe_parse_json(raw: str):
    if "```" in raw:
        raw = re.sub(r"```(?:json)?", "", raw)
        raw = raw.replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {str(e)}\nRaw: {raw}")


def generate_flashcards(text: str, num_cards: int = 5) -> list[dict]:
    prompt = f"""
        Generate exactly {num_cards} flashcards from the text below.
        Each flashcard must have a clear question and a concise answer.

        Return ONLY a JSON array in this exact format:
        [
        {{"question": "What is ...?", "answer": "..."}},
        {{"question": "...", "answer": "..."}}
        ]

        Text:
        {text[:6000]}
        """

    raw = _run_groq(prompt)
    cards = _safe_parse_json(raw)

    if not isinstance(cards, list):
        raise ValueError('Expected a JSON array of Flashcards')
    
    validated = []

    for card in cards:
        if "question" in card and "answer" in card:
            validated.append({
                "question": card["question"].strip(),
                "answer": card["answer"].strip()
            })

        if not validated:
            raise ValueError("No valid flashcard were generated.")
        
        return validated



def generate_notes(text: str) -> dict:
    prompt = f"""
        Analyze the text below and extract structured study notes.

        Return ONLY a JSON object in this exact format:
        {{
        "summary": "A clear 2-3 sentence summary of the main topic.",
        "key_points": [
            "Key point 1",
            "Key point 2",
            "Key point 3",
            "Key point 4",
            "Key point 5"
        ]
        }}
        Text:
        {text[:6000]}
        """

    raw = _run_groq(prompt)
    notes = _safe_parse_json(raw)

    if "summary" not in notes or "key_points" not in notes:
        raise ValueError("Missing Summary or key points")
    
    if not isinstance(notes["key_points"], list):
        raise ValueError("Key points must be a list.")
        

    return {
        "summary": notes["summary"].strip(),
        "key_points": [point.strip() for point in notes["key_points"] if point.strip()]
    }


def extract_text_from_pdf(file, max_chars: int = 6000) -> str:
    text = ""

    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + '\n'
                if len(text) >= max_chars:
                    break
    except Exception as e:
        raise RuntimeError(f"failed to read pdf {str(e)}")

    if not text.strip():
        raise ValueError(
            "No text could be extracted. "
            "This may be a scanned PDF. Please paste the text manually."
        )
    
    return text[:max_chars].strip()


