#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
two_agent_tinder_v2.py
Two-agent Tinder style conversation orchestrated via LLM-compatible chat APIs.
- Alternating agents with configurable OpenAI-compatible endpoints.
- Stops when a meeting is agreed (simple regex heuristics) or max turns reached.
- Optionally prints and exports the transcript as Markdown.
"""

import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

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
    r"\bfunciona|pode ser|combinado|feito|perfeito|fechado\b",
]
MEETING_RE = re.compile("|".join(MEETING_PATTERNS), flags=re.IGNORECASE)
ACCEPTANCE_RE = re.compile(r"\b(combinado|feito|perfeito|fechado|ok)\b", flags=re.IGNORECASE)


@dataclass
class AgentConfig:
    name: str
    system_preamble: str
    model: str
    base_url: Optional[str] = None
    api_key_env: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 400
    initial_prompt: Optional[str] = None


@dataclass
class RunConfig:
    max_messages: int = 50
    turn_delay_s: float = 0.0
    print_transcript: bool = True


@dataclass
class ConversationTurn:
    speaker: str
    text: str


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

    def generate(self, messages: List[Dict[str, str]]) -> str:
        if self._enabled and self._client:
            try:
                resp = self._client.chat.completions.create(
                    model=self.cfg.model,
                    messages=messages,
                    temperature=self.cfg.temperature,
                    max_tokens=self.cfg.max_tokens,
                )
                content = resp.choices[0].message.content if resp.choices else ""
                return (content or "").strip()
            except Exception as exc:
                return self._stub(messages, f"(provider error: {exc})")
        return self._stub(messages, "(provider unavailable)")

    def _stub(self, messages: List[Dict[str, str]], note: str = "") -> str:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        if MEETING_RE.search(last_user):
            suggestion = "Vamos combinar um café quinta às 19:00?"
        else:
            suggestion = "Adoro a energia. Que tal marcarmos algo leve para nos conhecermos?"
        return f"{suggestion} {note}".strip()


def meeting_agreed(turns: List[ConversationTurn]) -> bool:
    if len(turns) < 2:
        return False
    previous = turns[-2].text
    latest = turns[-1].text
    intent = bool(MEETING_RE.search(previous))
    acceptance = bool(ACCEPTANCE_RE.search(latest)) or bool(MEETING_RE.search(latest))
    return intent and acceptance


class TwoAgentChat:
    def __init__(self, agent_a: AgentConfig, agent_b: AgentConfig, run: RunConfig):
        self.agents = (agent_a, agent_b)
        self.run = run
        self.providers = {
            agent_a.name: Provider(agent_a),
            agent_b.name: Provider(agent_b),
        }
        self.turns: List[ConversationTurn] = []

    def build_messages_for(self, speaker: AgentConfig) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": speaker.system_preamble}
        ]
        if not self.turns:
            kickoff = speaker.initial_prompt or "Inicia a conversa com uma abertura natural e descontraída."
            messages.append({"role": "user", "content": kickoff})
            return messages
        for turn in self.turns:
            role = "assistant" if turn.speaker == speaker.name else "user"
            messages.append({"role": role, "content": turn.text})
        return messages

    def append_turn(self, speaker: AgentConfig, text: str) -> None:
        cleaned = text.strip()
        self.turns.append(ConversationTurn(speaker=speaker.name, text=cleaned))
        if self.run.print_transcript:
            print(f"{speaker.name}: {cleaned}")

    def run_until_meeting_or_max(self) -> None:
        current_index = 0
        turns_taken = 0
        while turns_taken < self.run.max_messages:
            agent = self.agents[current_index]
            provider = self.providers[agent.name]
            prompt_messages = self.build_messages_for(agent)
            reply = provider.generate(prompt_messages) or ""
            self.append_turn(agent, reply or "...")
            turns_taken += 1
            if meeting_agreed(self.turns):
                break
            if self.run.turn_delay_s > 0:
                time.sleep(self.run.turn_delay_s)
            current_index = 1 - current_index

    def export_markdown(self, path: str, title: str, subtitle: Optional[str] = None) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(f"# {title}\n\n")
            if subtitle:
                handle.write(f"_{subtitle}_\n\n")
            handle.write(f"> Transcript gerado em {now}\n\n---\n\n")
            for turn in self.turns:
                handle.write(f"**{turn.speaker}**: {turn.text.strip()}\n\n")


def main() -> None:
    agent_a = AgentConfig(
        name="Homem (40)",
        system_preamble=(
            "You are a playful Portuguese man in his 40s chatting on Tinder. "
            "Keep replies in pt-PT, warm, confident, concise, and always push the "
            "interaction forward while staying respectful."
        ),
        model=os.getenv("MODEL_A", "small-model"),
        base_url=os.getenv("BASE_URL_A") or None,
        api_key_env=os.getenv("API_KEY_ENV_A") or "OPENAI_API_KEY",
        temperature=float(os.getenv("TEMP_A", "0.8")),
        max_tokens=int(os.getenv("TOKENS_A", "300")),
        initial_prompt=(
            "Estás prestes a enviar a primeira mensagem à tua match. Cria uma abertura "
            "leve, divertida e específica o suficiente para parecer autêntica."
        ),
    )
    agent_b = AgentConfig(
        name="Mulher (35)",
        system_preamble=(
            "You are a witty Portuguese woman in her mid-30s replying on Tinder. "
            "Responde em pt-PT de forma curiosa, divertida e com mensagens curtas."
        ),
        model=os.getenv("MODEL_B", "small-model"),
        base_url=os.getenv("BASE_URL_B") or None,
        api_key_env=os.getenv("API_KEY_ENV_B") or "OPENAI_API_KEY",
        temperature=float(os.getenv("TEMP_B", "0.8")),
        max_tokens=int(os.getenv("TOKENS_B", "300")),
    )
    run = RunConfig(
        max_messages=int(os.getenv("MAX_MESSAGES", "50")),
        turn_delay_s=float(os.getenv("TURN_DELAY_S", "0")),
        print_transcript=os.getenv("PRINT_TRANSCRIPT", "1") not in {"0", "false", "False"},
    )
    chat = TwoAgentChat(agent_a, agent_b, run)
    chat.run_until_meeting_or_max()
    output_path = os.getenv("OUT_MD", "tinder_conversation.md")
    chat.export_markdown(
        output_path,
        title="Do Match ao Cappuccino: Um Diálogo",
        subtitle="pt-PT",
    )


if __name__ == "__main__":
    main()
