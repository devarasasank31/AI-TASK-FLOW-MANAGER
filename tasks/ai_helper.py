import json
import groq
from django.conf import settings

MODEL = "llama-3.3-70b-versatile"
_client = None


def get_client():
    global _client
    if _client is None:
        _client = groq.Groq(api_key=settings.GROQ_API_KEY)
    return _client


def _chat(messages, system=None, max_tokens=300):
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    response = get_client().chat.completions.create(
        model=MODEL,
        messages=msgs,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def generate_description(title):
    return _chat([{
        "role": "user",
        "content": f"Write a brief professional task description for: '{title}'. Keep it 2-3 sentences, clear and actionable."
    }], max_tokens=300)


def suggest_priority(title, description):
    result = _chat([{
        "role": "user",
        "content": f"Suggest priority for this task. Reply ONLY with one word: High, Medium, or Low.\nTitle: {title}\nDescription: {description}"
    }], max_tokens=10)
    priority = result.strip()
    return priority if priority in ['High', 'Medium', 'Low'] else 'Medium'


def parse_natural_language(text):
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    result = _chat([{
        "role": "user",
        "content": f"""Parse this task request and return ONLY valid JSON, no extra text.
Text: "{text}"
Today: {today}
Return exactly this format: {{"title": "string", "description": "string", "priority": "High/Medium/Low", "due_date": "YYYY-MM-DD or null"}}"""
    }], max_tokens=200)
    try:
        return json.loads(result.strip())
    except Exception:
        return {"title": text, "description": "", "priority": "Medium", "due_date": None}


def generate_subtasks(title, description):
    result = _chat([{
        "role": "user",
        "content": f"""Break this task into 4-5 subtasks. Return ONLY a valid JSON array, no extra text.
Task: "{title}"
Description: "{description}"
Return exactly: [{{"subtask": "string", "estimated_hours": number}}]"""
    }], max_tokens=400)
    try:
        return json.loads(result.strip())
    except Exception:
        return []


def get_ai_insights(stats, task_list):
    return _chat([{
        "role": "user",
        "content": f"""Analyze these task statistics and give exactly 3 specific productivity insights as bullet points.
Stats: {stats}
Tasks: {task_list}
Format: start each insight with • and be specific and actionable."""
    }], max_tokens=400)


def chat_with_ai(user_message, tasks_context):
    return _chat(
        [{"role": "user", "content": f"User tasks: {tasks_context}\n\nUser says: {user_message}"}],
        system="You are TaskFlow AI, a smart task management assistant. Help users manage their tasks efficiently. Be concise and helpful.",
        max_tokens=300,
    )
