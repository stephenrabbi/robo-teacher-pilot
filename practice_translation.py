"""Batch translation for generated Practice Mode teaching content."""

import json
import logging

from google.genai import types

from tutor import GEMINI_MODEL, _get_client

logger = logging.getLogger("robo-teacher.practice-translation")

LANGUAGE_STYLE = {
    "Yoruba": "simple, modern conversational Yorùbá understood by Lagos Junior Secondary learners, including children who did not grow up in their ancestral town; avoid deep, literary, ceremonial and old-fashioned words",
    "Igbo": "simple, modern everyday Igbo understood by Junior Secondary learners who may not have grown up in an Igbo-speaking hometown; avoid deep regional dialect, literary, ceremonial and old-fashioned words",
    "Hausa": "simple, modern everyday Hausa understood by Junior Secondary learners even when Hausa is not their main home language; avoid deep regional, literary, ceremonial and old-fashioned words",
}


def translate_question_batch(questions: list[tuple[str, str, str, str]], language: str):
    """Translate teaching text in one model request while preserving marked answers."""
    if language == "English" or language not in LANGUAGE_STYLE:
        return questions
    payload = [
        {"question": question, "hint": hint, "explanation": explanation}
        for question, hint, _expected, explanation in questions
    ]
    prompt = f"""Translate this Junior Secondary Mathematics practice material into {LANGUAGE_STYLE[language]}.
Return only a JSON array with the same number and order of objects and exactly these keys: question, hint, explanation.
Preserve every numeral, currency amount, algebraic symbol, equation, unit and mathematical meaning exactly.
Use the selected language for at least 90 percent of the words. Translate every heading, instruction, hint, encouragement, step label, transition and explanatory sentence.
Do not leave English scaffolding such as Step, First, Next, Because, Therefore, The answer is, Calculate, Multiply, Divide or Equals.
English is allowed only for a standard Maths term that would become unclear when translated, or for a formula letter, symbol, unit or proper name. Keep the surrounding sentence in the selected language.
Use short sentences and familiar words. Do not use proverbs, idioms, rare dialect words or unnecessarily formal vocabulary.
Before returning the JSON, silently inspect every sentence and replace unnecessary English. Do not solve, alter or add content.

{json.dumps(payload, ensure_ascii=False)}"""
    try:
        response = _get_client().models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", max_output_tokens=8192,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
        translated = json.loads(response.text)
        if not isinstance(translated, list) or len(translated) != len(questions):
            raise ValueError("translation count changed")
        result = []
        for original, item in zip(questions, translated):
            if not isinstance(item, dict) or not all(isinstance(item.get(key), str) and item[key].strip() for key in ("question", "hint", "explanation")):
                raise ValueError("invalid translated practice item")
            result.append((item["question"], item["hint"], original[2], item["explanation"]))
        return result
    except Exception as exc:
        logger.warning("Practice translation fallback: %s", type(exc).__name__)
        return questions


PRACTICE_TEXT = {
    "English": {
        "correct": ("Excellent work! You got it right.", "Well done! Your answer is correct.", "Great thinking! Keep it up.", "Brilliant! You solved that correctly."),
        "attempt": "Good attempt. Let’s work through it step by step.",
        "correct_answer": "Correct answer",
    },
    "Yoruba": {
        "correct": ("Ó dára gan! O rí ìdáhùn náà.", "Káre! Ìdáhùn rẹ tọ̀nà.", "O ronú dáadáa! Máa bá a lọ.", "Káre! O ṣe é dáadáa."),
        "attempt": "O gbìyànjú dáadáa. Jẹ́ ká ṣe é ní ìgbésẹ̀ kọ̀ọ̀kan.",
        "correct_answer": "Ìdáhùn tó tọ́",
    },
    "Igbo": {
        "correct": ("Ọ dị mma! Ị zara ya nke ọma.", "Ndeewo! Azịza gị ziri ezi.", "Ị chere echiche nke ọma! Gaa n'ihu.", "Ọmarịcha! Ị mere ya nke ọma."),
        "attempt": "Ị gbalịrị. Ka anyị kọwaa ya n'otu nzọụkwụ ruo na nke ọzọ.",
        "correct_answer": "Azịza ziri ezi",
    },
    "Hausa": {
        "correct": ("Madalla! Ka ba da amsa daidai.", "Aiki mai kyau! Amsarka daidai ce.", "Ka yi tunani sosai! Ci gaba.", "Madalla! Ka warware shi daidai."),
        "attempt": "Ka yi ƙoƙari. Mu bi bayanin mataki-mataki.",
        "correct_answer": "Amsa daidai",
    },
}
