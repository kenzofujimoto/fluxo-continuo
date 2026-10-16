#!/usr/bin/env python3
"""Pure parsers for official syllabus layouts. No network, no inference.

Every value returned here is read from an explicit field of the document. Missing fields stay None.
ECTS are never converted into contact hours, and an hour of unknown length stays unknown.
"""
from __future__ import annotations

import re

_METHOD_LINE = re.compile(
    r"^(?:Exposure|Dialogue|Lecture|Exposition|Explanation|Presentation|Interactive|Conversation|"
    r"Problem|Guided|Debate|examples|discovery|description|Practical|Case|Teamwork|Seminar presentation)\b",
    re.I,
)


def _num(s):
    if s is None:
        return None
    s = str(s).replace(",", ".")
    try:
        v = float(s)
    except ValueError:
        return None
    return int(v) if v.is_integer() else v


def _first(pattern, text, flags=re.I | re.S):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None


def _clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def _list_items(section, prefix):
    """Split a UBB content table (8.1 / 8.2) into numbered items, dropping the method column."""
    items = []
    current = None
    for raw in section.splitlines():
        line = raw.strip()
        if not line or line.startswith("[...]") or re.match(r"^(?:Bibliography|Teaching and learning|Remarks|\d+ For example)", line, re.I):
            if line.lower().startswith("bibliography"):
                current = None
            continue
        m = re.match(rf"^({prefix}\s*\d+(?:\s*[-–,]\s*{prefix}?\s*\d+)?)\s*[.,:]?\s*(.*)$", line)
        if m:
            current = {"id": re.sub(r"\s+", "", m.group(1)).replace("–", "-"), "text": m.group(2).strip()}
            items.append(current)
            continue
        if current is None:
            continue
        if _METHOD_LINE.match(line) or re.match(r"^(?:examples|discovery)", line, re.I):
            # The teaching-method column begins; ignore until next numbered item.
            current["_closed"] = True
            continue
        if not current.get("_closed"):
            current["text"] = (current["text"] + " " + line).strip()
    for it in items:
        it.pop("_closed", None)
        it["text"] = _clean(it["text"]).strip(" .;")
    return [i for i in items if i["text"]]


def _triple(label: str, text: str):
    """Read 'total / course / seminar-lab' hour triples; reject rows whose parts do not add up."""
    m = re.search(label + r"\s*(\d+)\s*(?:of which:?)?\s*(?:3\.[25]\.?)?\s*(?:course)?\s*(\d+)\s*(?:3\.[36]\.?)?\s*(?:seminar[^0-9\n]*)?\s*(\d+)", text, re.I)
    if not m:
        return None
    total, course, sem = (int(m.group(i)) for i in (1, 2, 3))
    if total != course + sem:
        return None
    return {"total": total, "course": course, "seminarLab": sem}


def parse_ubb(text: str, sorted_text: str | None = None) -> dict:
    """Babeș-Bolyai 'Course description' form (sections 1-9).

    ``text`` is PyMuPDF reading-order text (keeps table cells apart); ``sorted_text`` is the
    geometry-sorted text, where the hour table of section 3 stays on single lines.
    """
    t = text
    ht = (sorted_text or "") + "\n" + text
    weekly = _triple(r"3\.1\.?\s*(?:Number of\s*)?hours per week", ht)
    contact = _triple(r"3\.4\.?\s*Total (?:of )?hours in the(?: curriculum)?", ht)
    hours = {
        "weekly": weekly,
        "contact": contact,
        "selfStudy": _num(_first(r"3\.7\.?\s*Total (?:hours of )?individual study[^0-9]*?(\d+)", ht)),
        "totalWorkload": _num(_first(r"3\.8\.?\s*Total hours per semester\s*(\d+)", ht)),
        "ects": _num(_first(r"3\.9\.?\s*Number of (?:ECTS )?credits\s*(\d+(?:[.,]\d+)?)", ht)),
        "contactBasis": "semestre" if contact else None,
        "hourLengthMinutes": None,  # not declared on the UBB form
    }
    prereq = _first(r"4\.1\.\s*curriculum-?\s*(.*?)4\.2", t)
    prereq = _clean(re.sub(r"\brelated\b", " ", prereq or "")) or None
    skills = _clean(_first(r"4\.2\.?\s*skills-related\s*(.*?)(?:5\.|\[\.\.\.\]|$)", t) or "") or None
    sec81 = t[t.find("8.1."):] if "8.1." in t else ""
    end81 = sec81.find("8.2.")
    course_section = sec81[: end81 if end81 > 0 else None]
    sec82 = t[t.find("8.2."):] if "8.2." in t else ""
    end82 = re.search(r"\n\s*9\.\s*Evaluation", sec82)
    lab_section = sec82[: end82.start() if end82 else None]
    return {
        "layout": "ubb_course_description",
        "academicYear": _year(ht),
        "code": _first(r"Course code\s*([A-Z]{2,4}\d{3,5})", t),
        "title": _clean(_first(r"2\.1\.\s*Course title\s*(.*?)\s*Course code", t)) or None,
        "faculty": _clean(_first(r"1\.2\.\s*Faculty\s*(.*?)\s*1\.3\.", t)) or None,
        "department": _clean(_first(r"1\.3\.\s*Department\s*(.*?)\s*1\.4\.", t)) or None,
        "level": _clean(_first(r"1\.5\.?\s*(?:Level of study|Study cycle)\s*(.*?)\s*1\.6\.?", t)) or None,
        "programme": _clean(_first(r"1\.6\.\s*Degree programme\s*/?\s*Qualification\s*(.*?)\s*1\.7\.", t)) or None,
        "yearOfStudy": _num(_first(r"2\.4\.?\s*Year of study\s*(\d)", ht)),
        "semester": _num(_first(r"2\.5\.?\s*Semester\s*(\d)", ht)),
        "assessment": _clean(_first(r"2\.6\.\s*Type of assessment\s*(\w+)", t)) or None,
        "courseStatus": _clean(_first(r"2\.7\.\s*Course status\s*(\w+)", t)) or None,
        "courseType": _clean(_first(r"2\.8\.\s*Course type\s*(.*?)\s*(?:3\.|\n\n)", t)) or None,
        "hours": hours,
        "prerequisites": prereq,
        "skillsPrerequisites": skills,
        "courseTopics": _list_items(course_section, "C"),
        "labTopics": _list_items(lab_section, r"(?:L|S|P)"),
    }


def _year(text: str):
    m = re.search(r"(?:Academic|University) year\s*(\d{4})\s*[-/–]\s*(\d{4})", text, re.I)
    return f"{m.group(1)}/{m.group(2)}" if m else None


_MACK_HEADER = re.compile(r"(?:^|\n)[ \t]*Curso[ \t]*\n([^\n]+)\n\s*N[uú]cleo Tem[aá]tico\s*(.*?)\s*Etapa\s*(\d+)\S*\s*\n\s*Comp\. Curricular\s*(.*?)\s*C[oó]digo", re.S)


def parse_mackenzie_blocks(text: str) -> list[dict]:
    """Mackenzie FCI 'ementário' component blocks (2025 layout)."""
    out = []
    headers = list(_MACK_HEADER.finditer(text))
    for i, m in enumerate(headers):
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        seg = text[m.end():end]
        hours = _num(_first(r"Carga hor[aá]ria \(horas\)\s*\n\s*([0-9]{1,3}(?:,[0-9]{1,2})?)", seg))
        weekly = None
        # Only trust the three cells (teórica/prática/ateliê) when the layout keeps blank cells,
        # i.e. exactly three lines between 'Presencial' and 'Específico' (FCI CC layout).
        pres = re.search(r"\nPresencial[ \t]*\n((?:[^\n]*\n){3})\s*Espec[ií]fico", seg)
        if pres:
            cells = [c.strip() for c in pres.group(1).split("\n")[:3]]
            vals = [int(c) if c.isdigit() else 0 for c in cells]
            if all(c == "" or c.isdigit() for c in cells) and sum(vals) > 0:
                weekly = {"teorica": vals[0], "pratica": vals[1], "atelie": vals[2]}
        ext = _first(r"Percentual\s*\n\s*([0-9]{1,3}(?:,[0-9]{1,2})?)\s*\n?\s*%", seg)
        opt = re.search(r"Optativo\s*\n\s*(X?)\s*\n", seg)
        ementa = _first(r"\bEmenta\s*\n(.*?)\n\s*Bibliografia", seg) or ""
        out.append({
            "course": _clean(m.group(1)),
            "theme": _clean(m.group(2)),
            "stage": int(m.group(3)),
            "name": _clean(m.group(4)),
            "hours": hours,
            "hourUnit": "hora_relogio" if hours is not None else None,
            "weekly": weekly,
            "optional": bool(opt and opt.group(1) == "X"),
            "extensionPercent": _num(ext),
            "ementa": _clean(ementa),
        })
    return out


def split_ementa(ementa: str) -> list[str]:
    """Split a short Brazilian ementa into its enumerated topics, keeping the official wording."""
    ementa = _clean(ementa)
    if not ementa:
        return []
    sep = ";" if ementa.count(";") >= max(1, ementa.count(". ")) else "."
    parts = [p.strip(" .;") for p in re.split(r";" if sep == ";" else r"\.(?:\s+|$)", ementa)]
    return [p for p in parts if len(p) >= 3]


# The name may wrap lines but never contains another label; this stops a 'Código da Disciplina:' label
# from swallowing the next component's header.
_FICHA_NAME = re.compile(r"(?:Nome\s+do\s+Componente\s+Curricular|\bDisciplina)\s*:\s*((?:(?!Carga\s*hor|Disciplina\s*:|Ementa\s*:).){0,200}?)\s*C[oó]digo", re.S | re.I)


def _items(block: str) -> list[str]:
    """Numbered or line items of a 'Conteúdo Programático' section, keeping official wording."""
    out = []
    for line in block.splitlines():
        line = _clean(line)
        if not line or len(line) < 3:
            continue
        m = re.match(r"^(?:\d+(?:\.\d+)*[.)]?|[•\-–])\s*(.+)$", line)
        if m:
            out.append(m.group(1).strip(" .;"))
        elif out and line[:1].islower():
            out[-1] = (out[-1] + " " + line).strip(" .;")  # wrapped continuation of previous item
        else:
            out.append(line.strip(" .;"))
    return [o for o in out if len(o) >= 3]


def parse_ficha_blocks(text: str) -> list[dict]:
    """CCSA (Administração) and Faculdade de Direito 'ficha' layout: one block per component.

    'Carga horária: 63,3 horas' is a semester clock-hour total; 'N aulas' / 'N horas aula' is a weekly
    class-period count and is kept apart (never multiplied into semester hours).
    """
    out = []
    heads = [h for h in _FICHA_NAME.finditer(text)
             if not re.search(r"C[oó]digo\s+(?:da|do)\s*$", text[max(0, h.start() - 25):h.start()], re.I)]
    for i, m in enumerate(heads):
        name = _clean(m.group(1))
        if not name or re.match(r"(?i)c[oó]digo", name):
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        seg = text[m.end():end]
        hours = _num(_first(r"Carga\s*hor[aá]ria\s*:\s*([0-9]{1,3}(?:,[0-9]{1,2})?)\s*horas(?!\s*-?\s*aula)", seg))
        weekly = _num(_first(r"Carga\s*hor[aá]ria\s*:\s*([0-9]{1,2})\s*(?:aulas|horas?\s*-?\s*aulas?)\b", seg))
        if hours is not None and hours < 10:
            # e.g. 'Carga horária: 4 horas' on a semester form is a weekly count, not a semester total
            weekly, hours = weekly or int(hours), None
        stage = _num(_first(r"Etapa\s*:\s*([0-9]{1,2})", seg))
        # Section labels only end a section at line start ('objetivos do governo' inside an ementa must not).
        em = re.search(r"\bEmenta\s*:?\s*\n?(.*?)(?=\n\s*(?:Conte[uú]do\s+Program[aá]tico|Bibliografia|Objetivos?(?:\s+\w+)?\s*:)|$)", seg, re.S | re.I)
        cp = re.search(r"Conte[uú]do\s+Program[aá]tico\s*:?\s*(.*?)(?=\n\s*(?:Bibliografia|Metodologia|Crit[eé]rios?\s+de\s+avalia)|$)", seg, re.S | re.I)
        out.append({
            "name": name,
            "stage": int(stage) if stage else None,
            "hours": hours,
            "hourUnit": "hora_relogio" if hours is not None else None,
            "weeklyClassPeriods": int(weekly) if weekly else None,
            "ementa": _clean(em.group(1)) if em else "",
            "programContent": _items(cp.group(1)) if cp else [],
        })
    return out


def split_ementa_fine(ementa: str) -> list[str]:
    """Split long ficha ementas (Direito/Administração) on sentence ends AND semicolons."""
    ementa = _clean(ementa)
    parts = [p.strip(" .;") for p in re.split(r";|\.(?:\s+|$)", ementa)]
    return [p for p in parts if len(p) >= 3]
