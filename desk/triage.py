"""Urgency triage. Cheap model, runs on every incoming ticket."""

import json

from openai import OpenAI

client = OpenAI()

LABELS = ("low", "normal", "high", "urgent")


def classify_urgency(subject, body):
    response = client.chat.completions.create(
        model="gpt-5.6-terra",
        messages=[
            {
                "role": "system",
                "content": "Classify the ticket's urgency as one of: low, normal, high, urgent. "
                'Reply as JSON: {"urgency": "..."}',
            },
            {"role": "user", "content": f"{subject}\n\n{body}"},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    label = json.loads(response.choices[0].message.content).get("urgency", "normal")
    return label if label in LABELS else "normal"
