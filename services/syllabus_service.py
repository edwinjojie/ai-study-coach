import re
from typing import List, Dict

from pdfminer.high_level import extract_text as _extract_text


class SyllabusService:
    def extract_text_from_pdf(self, file_path: str) -> str:
        try:
            text = _extract_text(file_path) or ""
            return text
        except Exception:
            return ""

    def clean_text(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        freq = {}
        for ln in lines:
            freq[ln] = freq.get(ln, 0) + 1
        filtered = []
        for ln in lines:
            if re.match(r"^\s*Page\s+\d+\s*$", ln, flags=re.IGNORECASE):
                continue
            if freq.get(ln, 0) >= 3 and len(ln) <= 60:
                continue
            if re.match(r"^[\-_=]{3,}$", ln):
                continue
            filtered.append(ln)
        s = " ".join(filtered)
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    def extract_topics(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []
        topics: List[str] = []
        for m in re.finditer(
            r"\b(Unit|Module|Chapter)\s*(\d+)?\s*[:\-]\s*(.+?)(?=\b(?:Unit|Module|Chapter)\b|\b\d{1,2}(?:\.\d+)*\b|[.;]|$)",
            text,
            flags=re.IGNORECASE,
        ):
            label = m.group(1).title()
            num = m.group(2) or ""
            title = m.group(3).strip()
            if num:
                topics.append(f"{label} {num}: {title}")
            else:
                topics.append(f"{label}: {title}")
        for m in re.finditer(
            r"\b(Unit|Module|Chapter)\s*(\d+)\b",
            text,
            flags=re.IGNORECASE,
        ):
            label = m.group(1).title()
            num = m.group(2)
            topics.append(f"{label} {num}")
        for m in re.finditer(
            r"\b(\d{1,2}(?:\.\d+)*)\s+([A-Z][^\d:;\-]{0,100})",
            text,
            flags=0,
        ):
            num = m.group(1)
            title = m.group(2).strip()
            topics.append(f"{num} {title}")
        dedup: List[str] = []
        seen = set()
        for t in topics:
            k = t.lower().strip()
            if k not in seen:
                seen.add(k)
                dedup.append(t.strip())
        return dedup

    def parse_pdf(self, file_path: str) -> Dict[str, object]:
        raw = self.extract_text_from_pdf(file_path)
        if not raw or not raw.strip():
            return {"raw_text": "", "topics": []}
        cleaned = self.clean_text(raw)
        topics = self.extract_topics(cleaned)
        return {"raw_text": raw, "topics": topics}
