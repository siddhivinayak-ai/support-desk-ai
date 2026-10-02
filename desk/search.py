"""Similar-ticket search over embeddings (vectors live in Postgres/pgvector)."""

from openai import OpenAI

client = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"


def embed(texts):
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=list(texts))
    return [item.embedding for item in response.data]


def is_safe_to_auto_reply(text):
    result = client.moderations.create(model="omni-moderation-latest", input=text)
    return not result.results[0].flagged
