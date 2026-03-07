import logging

logger = logging.getLogger(__name__)


def generate_summary(provider, api_key, model_name, system_prompt, transcription_text, reasoning_effort="low"):
    """Génère une synthèse via le provider LLM choisi.

    provider: int (1=OpenAI, 2=Anthropic, 3=Mistral) from AISummarySettings.AISummaryProviders
    """
    if provider == 1:  # OpenAI
        return _generate_via_openai(api_key, model_name, system_prompt, transcription_text, reasoning_effort)
    elif provider == 2:  # Anthropic
        return _generate_via_anthropic(api_key, model_name, system_prompt, transcription_text)
    elif provider == 3:  # Mistral
        return _generate_via_mistral(api_key, model_name, system_prompt, transcription_text)
    raise ValueError(f"Unknown AI summary provider: {provider}")


def _generate_via_openai(api_key, model_name, system_prompt, transcription_text, reasoning_effort="low"):
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    model = model_name or "gpt-5.2"

    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcription_text},
        ],
    }

    # reasoning_effort is only supported on GPT-5.x and o1/o3 models
    # NOT supported on GPT-4o, GPT-4o-mini, etc.
    if reasoning_effort and _model_supports_reasoning(model):
        kwargs["reasoning_effort"] = reasoning_effort

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def _model_supports_reasoning(model_name):
    """Check if the model supports the reasoning_effort parameter."""
    model_lower = model_name.lower()
    # GPT-5.x series all support reasoning_effort
    if model_lower.startswith("gpt-5"):
        return True
    # o1 and o3 reasoning models support it
    if model_lower.startswith(("o1", "o3")):
        return True
    return False


def _generate_via_anthropic(api_key, model_name, system_prompt, transcription_text):
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model_name or "claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": transcription_text}],
    )
    return response.content[0].text


def _generate_via_mistral(api_key, model_name, system_prompt, transcription_text):
    from mistralai import Mistral

    client = Mistral(api_key=api_key)
    response = client.chat.complete(
        model=model_name or "mistral-large-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcription_text},
        ],
    )
    return response.choices[0].message.content
