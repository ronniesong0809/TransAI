from openai import OpenAI
from .config import settings

client = OpenAI(
    base_url=settings.OPENAI_BASE_URL,
    api_key=settings.OPENAI_API_KEY,
)

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    prompt = f"Translate the following text from {source_lang} to {target_lang}:\n\n{text}"
    completion = client.chat.completions.create(
        model="google/learnlm-1.5-pro-experimental:free",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

def evaluate_translation_quality(original: str, translation: str, source_lang: str, target_lang: str) -> float:
    prompt = f"""Please evaluate the quality of this translation from {source_lang} to {target_lang}.
    Original: {original}
    Translation: {translation}
    Rate the translation quality from 0 to 1, where:
    0 = completely wrong
    1 = perfect translation
    Return only the number."""
    
    completion = client.chat.completions.create(
        model="google/learnlm-1.5-pro-experimental:free",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return float(completion.choices[0].message.content.strip())
    except:
        return 0.0 