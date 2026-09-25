import re
from typing import Optional

def parse_pitch_lines(pitch_text: str) -> dict[int, str]:
    result = {}
    pattern = r"\[(\d+)\]\s*(.+?)(?=\s*\[\d+\]|\s*$)"
    matches = re.findall(pattern, pitch_text, re.DOTALL)
    for step_str, answer in matches:
        step = int(step_str)
        if 1 <= step <= 5:
            result[step] = answer.strip()
    return result

def build_pitch_text(answers: dict[int, str]) -> str:
    lines = []
    for step in range(1, 6):
        if step in answers:
            lines.append(f"[{step}] {answers[step]}")
    return "\n".join(lines)