import os
import re
import json
import pdfplumber
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = 'llama-3.3-70b-versatile'

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
    You are an expert flashcard creator specializing in active recall and spaced repetition.

    Your task is to generate EXACTLY {num_cards} flashcards from the text below.

    Rules:
    - Generate EXACTLY {num_cards} cards — not more, not less
    - One clear idea per card
    - Question: specific, clear, no answer leakage
    - Answer: concise and precise, use bullet points if listing multiple points
    - Cover the most important concepts, definitions, facts, and relationships in the text

    Return ONLY a valid JSON array with EXACTLY {num_cards} objects.
    Each object must have exactly two keys: "question" and "answer".

    Example format:
    [
    {{"question": "What is photosynthesis?", "answer": "The process by which plants convert sunlight, water and CO2 into glucose and oxygen."}},
    {{"question": "What are the two stages of photosynthesis?", "answer": "1. Light-dependent reactions\\n2. Light-independent reactions (Calvin cycle)"}}
    ]

    Text:
    {text[:6000]}

    Remember: Return EXACTLY {num_cards} flashcards. Output ONLY the JSON array, nothing else.
    """
    raw = _run_groq(prompt)
    cards = _safe_parse_json(raw)

    if not isinstance(cards, list):
        raise ValueError("Expected a JSON array of flashcards.")

    validated = []
    for card in cards:
        if "question" in card and "answer" in card:
            validated.append({
                "question": card["question"].strip(),
                "answer": card["answer"]
            })

    if not validated:
        raise ValueError("No valid flashcards were generated.")

    return validated


def generate_notes(text: str) -> dict:
    
    prompt = f"""
        You are an expert study assistant specializing in summarization and knowledge extraction.

        Your task is to analyze the text below and extract structured study notes.

        Rules:
        - Summary: 2-3 clear sentences covering the main topic
        - Key points: exactly 5 most important concepts, facts, or ideas
        - Each key point must be a complete, standalone sentence
        - Be precise and academic in tone

        Return ONLY a valid JSON object with exactly two keys: "summary" and "key_points".

        Example format:
        {{
        "summary": "This text covers the water cycle and its importance to Earth's ecosystem.",
        "key_points": [
            "Water evaporates from oceans and lakes due to solar energy.",
            "Water vapor condenses in the atmosphere to form clouds.",
            "Precipitation returns water to the Earth's surface as rain or snow.",
            "Groundwater is formed when water soaks into the soil and rock layers.",
            "The water cycle distributes fresh water across the planet continuously."
        ]
        }}

        Text:
        {text[:6000]}

        Output ONLY the JSON object, nothing else.

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


