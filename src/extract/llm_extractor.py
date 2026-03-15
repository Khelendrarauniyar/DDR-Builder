from __future__ import annotations

import json
import os
from pathlib import Path
from urllib import error as urllib_error
from urllib import request

from src.common.logging_utils import log_event
from src.models import FindingClaim, SourceDocument


def parse_llm_claims(
    documents: list[SourceDocument],
    model: str = "llama-3.3-70b-versatile",
    enabled: bool = False,
    provider: str = "groq",
    api_base_url: str = "https://api.groq.com/openai/v1",
    timeout_seconds: int = 60,
) -> list[FindingClaim]:
    if not enabled or provider.lower() != "groq":
        return []

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return []

    prompt_text = _load_prompt_text()
    input_text = _build_documents_payload(documents)

    messages = [
        {"role": "system", "content": prompt_text},
        {"role": "user", "content": input_text},
    ]

    endpoint = f"{api_base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": messages,
    }

    req = request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout_seconds) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        content = body["choices"][0]["message"]["content"]
        parsed_payload = _parse_json_payload(content)
        raw_claims = _extract_claim_array(parsed_payload)

        claims: list[FindingClaim] = []
        for item in raw_claims:
            try:
                claims.append(FindingClaim.model_validate(item))
            except Exception:
                continue
        return claims
    except (urllib_error.URLError, urllib_error.HTTPError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
        log_event("llm_extraction", "fallback_to_rules", provider=provider, reason=str(exc))
        return []


def _load_prompt_text() -> str:
    prompt_path = Path("prompts") / "extract_claims.txt"
    if not prompt_path.exists():
        return "Return only JSON object with key 'claims' (array of finding claim objects)."
    return prompt_path.read_text(encoding="utf-8")


def _build_documents_payload(documents: list[SourceDocument]) -> str:
    lines: list[str] = []
    lines.append("Extract claims from these documents.")
    lines.append("If no claims, return {\"claims\": []}.")
    for doc in documents:
        lines.append(f"Document: {doc.doc_id} ({doc.doc_type})")
        for block in doc.text_blocks:
            snippet = block.text[:2000]
            lines.append(f"Page {block.page}: {snippet}")
    return "\n".join(lines)


def _parse_json_payload(content: str) -> dict:
    content = content.strip()
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = content.find("{")
    end = content.rfind("}")
    if start >= 0 and end > start:
        parsed = json.loads(content[start : end + 1])
        if isinstance(parsed, dict):
            return parsed
    return {"claims": []}


def _extract_claim_array(payload: dict) -> list[dict]:
    if isinstance(payload.get("claims"), list):
        return [item for item in payload["claims"] if isinstance(item, dict)]

    # Backward-compatible fallback for array payloads wrapped differently.
    for value in payload.values():
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return value
    return []
