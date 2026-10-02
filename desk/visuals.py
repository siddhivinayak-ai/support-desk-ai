"""Help-center illustrations generated for new knowledge-base articles."""

from openai import OpenAI

client = OpenAI()


def illustrate_article(title):
    result = client.images.generate(
        model="gpt-image-1",
        prompt=f"A friendly flat illustration for a help-center article titled '{title}'. No text.",
        size="1024x1024",
    )
    return result.data[0].b64_json
