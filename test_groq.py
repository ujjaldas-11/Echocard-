# # test_groq.py (project root)
# import os
# from dotenv import load_dotenv
# load_dotenv()

# from flashcards.ai_service import (
#     generate_flashcards,
#     generate_notes
# )

# sample_text = """
# The water cycle, also known as the hydrological cycle, describes the continuous
# movement of water on, above, and below the surface of the Earth. Water evaporates
# from oceans and lakes, rises into the atmosphere, condenses into clouds, and falls
# back to Earth as precipitation. It then flows into rivers and oceans or soaks into
# the ground to become groundwater. This cycle is driven by solar energy and gravity
# and is essential for distributing fresh water around the planet.
# """

# print("=" * 50)
# print("TEST 1: Flashcard Generation")
# print("=" * 50)
# try:
#     cards = generate_flashcards(sample_text, num_cards=3)
#     for i, card in enumerate(cards, 1):
#         print(f"\nCard {i}:")
#         print(f"  Q: {card['question']}")
#         print(f"  A: {card['answer']}")
#     print("\n✅ Flashcards passed!")
# except Exception as e:
#     print(f"❌ Flashcards failed: {e}")


# print("\n" + "=" * 50)
# print("TEST 2: Notes Generation")
# print("=" * 50)
# try:
#     notes = generate_notes(sample_text)
#     print(f"\nSummary:\n  {notes['summary']}")
#     print("\nKey Points:")
#     for point in notes['key_points']:
#         print(f"  • {point}")
#     print("\n✅ Notes passed!")
# except Exception as e:
#     print(f"❌ Notes failed: {e}")


# check_models.py
import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

models = client.models.list()
for model in models.data:
    print(model.id)