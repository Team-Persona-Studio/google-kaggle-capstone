import google.generativeai as genai
from datetime import datetime
import os
from database import get_db_conn

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# ------------------ Context Agent ------------------
class ContextManagerAgent:
    def __init__(self, model="gemini-2.0-flash"):
        self.model = genai.GenerativeModel(model)

    def build_context(self, history):
        text = "\n".join([f"{h['sender']}: {h['message']}" for h in history])

        prompt = f"""
        Create a compact conversation summary that preserves continuity.
        
        Requirements:
        - Summarize the whole conversation in 2–3 sentences.
        - Then include the last 2–3 actual messages word-for-word.
        - This ensures no greeting repetition.
        - Do NOT invent anything.

        Conversation:
        {text}

        Return format:
        <summary>
        <recent_messages>
        """
        res = self.model.generate_content(prompt)
        return res.text.strip()


# ------------------ Character Agent ------------------
class CharacterAgent:
    def __init__(self, character_name, tone="friendly", model="gemini-2.0-flash"):
        self.character_name = character_name
        self.tone = tone
        self.model = genai.GenerativeModel(model)

    def reply(self, context_summary, user_msg):
        prompt = f"""
        You are {self.character_name}.
        Tone: {self.tone}.

        RULES:
        - Continue the conversation naturally.
        - DO NOT restart the conversation.
        - DO NOT greet unless the user greets first.
        - Do not summarize the conversation.
        - Keep responses consistent with the last few turns included in the summary.
        - Stay 100% in character.

        Conversation Summary + Recent Turns:
        {context_summary}

        User: {user_msg}

        Reply as {self.character_name}.
        """
        res = self.model.generate_content(prompt)
        return res.text.strip()


# ------------------ Moderator Agent ------------------
class ModeratorAgent:
    def __init__(self, model="gemini-2.0-flash"):
        self.model = genai.GenerativeModel(model)

    def check(self, reply):
        prompt = f"""
        Clean the reply WITHOUT changing its meaning.
        Do NOT add greetings.
        Do NOT restart the conversation.
        Only fix:
        - unsafe content
        - hallucinated details
        - grammar if needed

        Keep style, tone, and message content.

        Reply to clean:
        {reply}
        """
        res = self.model.generate_content(prompt)
        return res.text.strip()


# ------------------ Helpers ------------------
def fetch_last_messages_api(persona_id, limit=10):
    limit = max(3, min(limit, 30))  # safety

    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT sender, message FROM persona_messages
        WHERE persona_id=%s ORDER BY id DESC LIMIT %s
    """, (persona_id, limit))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return list(reversed(rows))


def save_message_api(persona_id, sender, message):
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO persona_messages (persona_id, sender, message, created_at)
        VALUES (%s, %s, %s, NOW())
    """, (persona_id, sender, message))

    conn.commit()
    cursor.close()
    conn.close()


class MultiAgentPipeline:
    def __init__(self, character_name, tone):
        self.ctx = ContextManagerAgent()
        self.char = CharacterAgent(character_name, tone)
        self.mod = ModeratorAgent()

    def run(self, persona_id, user_msg):
        history = fetch_last_messages_api(persona_id)
        
        # If conversation is new, avoid summary hallucination:
        if len(history) == 0:
            ctx = "Summary: New conversation. Recent turns: None"
        else:
            ctx = self.ctx.build_context(history)
            
        raw = self.char.reply(ctx, user_msg)
        return self.mod.check(raw)

