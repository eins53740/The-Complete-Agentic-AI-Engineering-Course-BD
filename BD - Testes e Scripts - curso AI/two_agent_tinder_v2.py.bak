#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
two_agent_tinder_v2.py
Adds:
- max 50 messages (configurable).
- stop when a physical meeting is combined (simple regex heuristics).
- export to Markdown in a "book dialog" style.
"""

import os
import re
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except Exception:
    pass

try:
    from openai import OpenAI
    HAS_OPENAI = True
except Exception:
    HAS_OPENAI = False

MEETING_PATTERNS = [
    r"\b(encontro|encontrar|ver[- ]?nos|combinar|marcar|vamos (?:tomar|beber|jantar)|café|jantar|almoço)\b",
    r"\b(hoje|amanhã|segunda|terça|terça-feira|quarta|quinta|quinta-feira|sexta|sábado|domingo)\b",
    r"\bàs?\s*\d{1,2}[:h]\d{0,2}\b",
    r"\b19:00|18:30|20:00|17:30\b",
    r"\bfunciona|pode ser|combinado|feito|perfeito|fechado\b"
]
MEETING_RE = re.compile("|".join(MEETING_PATTERNS), flags=re.IGNORECASE)

@dataclass
class AgentConfig:
    name: str
    system_preamble: str
    model: str
    base_url: Optional[str] = None
    api_key_env: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 400

@dataclass
class RunConfig:
    max_messages: int = 50
    turn_delay_s: float = 0.0

class Provider:
    def __init__(self, cfg: AgentConfig):
        self.cfg = cfg
        self._client = None
        self._enabled = False
        key = os.getenv(cfg.api_key_env) if cfg.api_key_env else None
        if HAS_OPENAI and key:
            try:
                if cfg.base_url:
                    self._client = OpenAI(api_key=key, base_url=cfg.base_url)
                else:
                    self._client = OpenAI(api_key=key)
                self._enabled = True
            except Exception:
                self._enabled = False

    def generate(self, messages: List[Dict[str,str]]) -> str:
        if self._enabled and self._client:
            try:
                resp = self._client.chat.completions.create(
                    model=self.cfg.model,
                    messages=messages,
                    temperature=self.cfg.temperature,
                    max_tokens=self.cfg.max_tokens,
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                return self._stub(messages, f"(provider error: {e})")
        return self._stub(messages, "(stub)")

    def _stub(self, messages: List[Dict[str,str]], note:str="") -> str:
        # A tiny, deterministic-ish fallback
        last = ""
        for m in reversed(messages):
            if m["role"] in ("user","assistant"):
                last = m["content"]; break
        if "café" in last.lower() or "encontro" in last.lower():
            s = "Quinta às 19:00 funciona para mim. Combinado?"
        else:
            s = "Gosto da ideia. Preferes conversa calma num café ou passeio curto à beira-rio?"
        return s + (f" {note}" if note else "")

def meeting_agreed(history: List[str]) -> bool:
    if len(history) < 2:
        return False
    last = history[-1]
    prev = history[-2]
    intent = bool(MEETING_RE.search(prev))
    accept = bool(re.search(r"\\b(combinado|feito|perfeito|fechado|ok)\\b", last, flags=re.IGNORECASE)) or bool(MEETING_RE.search(last))
    return intent and accept

class TwoAgentChat:
    def __init__(self, a: AgentConfig, b: AgentConfig, run: RunConfig):
        self.a, self.b, self.run = a, b, run
        self.pa, self.pb = Provider(a), Provider(b)
        self.history: List[Dict[str,str]] = [
            {"role":"system","content":a.system_preamble},
            {"role":"system","content":b.system_preamble},
        ]
        self.transcript: List[str] = []

    def say(self, who:str, text:str, role:str="assistant"):
        self.history.append({"role": role, "content": f"{who}: {text}"})
        self.transcript.append(f"{who}: {text}")

    def build_messages_for(self, speaker: AgentConfig) -> List[Dict[str,str]]:
        msgs = [{"role":"system","content":speaker.system_preamble}]
        for m in self.history:
            if m["role"] != "system":
                msgs.append(m)
        return msgs

    def run_until_meeting_or_max(self):
        # opener by A
        self.say(self.a.name, "Olá! Curti o teu perfil — que tal começarmos por um café com bolo decente? 🙂")
        turn = 1
        while turn < self.run.max_messages and not meeting_agreed(self.transcript):
            # B
            msgs = self.build_messages_for(self.b)
            reply_b = self.pb.generate(msgs)
            self.say(self.b.name, reply_b)
            if meeting_agreed(self.transcript) or len(self.transcript) >= self.run.max_messages:
                break
            # A
            msgs = self.build_messages_for(self.a)
            reply_a = self.pa.generate(msgs)
            self.say(self.a.name, reply_a)
            if self.run.turn_delay_s > 0: time.sleep(self.run.turn_delay_s)
            turn += 2

    def export_markdown(self, path:str, title:str, subtitle:Optional[str]=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\\n\\n")
            if subtitle: f.write(f"_{subtitle}_\\n\\n")
            f.write(f"> Transcript gerado em {now}\\n\\n---\\n\\n")
            for line in self.transcript:
                who, text = line.split(":",1)
                f.write(f"**{who.strip()}**: {text.strip()}\\n\\n")

def main():
    a = AgentConfig(
        name="Homem (40)",
        system_preamble="Portuguese man, 40, friendly, playful, short messages, pt-PT.",
        model=os.getenv("MODEL_A","small-model"),
        base_url=os.getenv("BASE_URL_A",""),
        api_key_env=os.getenv("API_KEY_ENV_A",""),
        temperature=0.8, max_tokens=300
    )
    b = AgentConfig(
        name="Mulher (35)",
        system_preamble="Portuguese woman, 35, witty, curious, short messages, pt-PT.",
        model=os.getenv("MODEL_B","small-model"),
        base_url=os.getenv("BASE_URL_B",""),
        api_key_env=os.getenv("API_KEY_ENV_B",""),
        temperature=0.8, max_tokens=300
    )
    run = RunConfig(max_messages=int(os.getenv("MAX_MESSAGES","50")), turn_delay_s=0.0)
    chat = TwoAgentChat(a,b,run)
    chat.run_until_meeting_or_max()
    out = os.getenv("OUT_MD","tinder_conversation.md")
    chat.export_markdown(out, title="Do Match ao Cappuccino: Um Diálogo", subtitle="pt‑PT")

if __name__ == "__main__":
    main()
