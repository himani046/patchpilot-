from openai import OpenAI

from app.config import settings


client = OpenAI(
    api_key=settings.nebius_api_key,
    base_url=settings.nebius_base_url,
    timeout=60.0,
    max_retries=1,
)


def ask_nemotron(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model=settings.nebius_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=3000,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Nemotron returned an empty response.")
    return content
