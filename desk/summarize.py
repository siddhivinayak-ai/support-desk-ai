"""Ticket summaries for the agent sidebar.

We pinned the dated GPT-4 snapshot in early 2024 because summaries changed tone
whenever the alias moved. Re-check the prompt if you change the model.
"""

from openai import OpenAI

client = OpenAI()

SUMMARY_MODEL = "gpt-4-0613"

SYSTEM_PROMPT = (
    "You summarize customer support tickets for agents. "
    "Return three short bullet points: the problem, what the customer tried, and what they want."
)


def summarize_ticket(subject, body):
    response = client.chat.completions.create(
        model=SUMMARY_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Subject: {subject}\n\n{body}"},
        ],
        temperature=0.2,
        max_tokens=300,
    )
    return response.choices[0].message.content
