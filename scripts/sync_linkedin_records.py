"""Synchronize LinkedIn role summaries and FAQ metadata without rewriting curated teaching or evidence sections."""
from html import escape, unescape
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def year_range(role):
    start = str(role["start"])[:4]
    end = role["end"] if role["end"] == "Present" else str(role["end"])[:4]
    return f"{start}–{end}"


def replace_once(pattern, replacement, value, label, flags=0):
    matches = list(re.finditer(pattern, value, flags))
    if len(matches) != 1:
        raise ValueError(f"Expected one {label}; found {len(matches)}")
    match = matches[0]
    return value[:match.start()] + replacement(match) + value[match.end():]


def plain(value):
    value = re.sub(r'</li>\s*<li\b[^>]*>', '; ', value)
    value = re.sub(r'</p>\s*<(?:ol|ul)\b[^>]*>', ' ', value)
    value = re.sub(r'</(?:ol|ul)>\s*<p\b[^>]*>', '. ', value)
    value = " ".join(unescape(re.sub(r'<[^>]+>', ' ', value)).split())
    return re.sub(r'\s+([.,;:!?])', r'\1', value)


def sync_role_section(text, current_roles, previous_roles, source_url, name):
    pattern = r'(^## (?:Work experience|LinkedIn Experience)\n)(.*?)(?=^## |\Z)'

    def update_section(match):
        body = match.group(2)
        current = "".join("- " + role["title"] + "\n" for role in current_roles)
        previous = "".join("- " + role["title"] + " — " + year_range(role) + "\n"
                           for role in previous_roles)
        for label, rows in (("Current roles", current), ("Previous roles", previous)):
            body = replace_once(
                r'(^' + label + r':\n)(?:- [^\n]*\n)+',
                lambda m: m.group(1) + rows,
                body, name + " " + label, flags=re.M,
            )
        body = replace_once(r'^Source: [^\n]*$', lambda _: "Source: " + source_url,
                            body, name + " career source", flags=re.M)
        return match.group(1) + body

    return replace_once(pattern, update_section, text, name + " career section",
                        flags=re.M | re.S)


def sync_faq_schema(html):
    # The visible FAQ is the source for its hidden search metadata.
    questions = []
    for summary, answer in re.findall(
        r'<details[^>]*><summary>(.*?)</summary><div class="faq-answer">(.*?)</div></details>',
        html, re.S,
    ):
        summary = re.sub(r'<span>Q\d+</span>', '', summary)
        questions.append({"@type": "Question", "name": plain(summary),
                          "acceptedAnswer": {"@type": "Answer", "text": plain(answer)}})
    if not questions:
        raise ValueError("Expected visible FAQ entries")

    def update_schema(match):
        raw = match.group(2)
        schema = json.loads(raw)
        faq_nodes = [node for node in schema["@graph"] if node.get("@type") == "FAQPage"]
        if len(faq_nodes) != 1:
            raise ValueError("Expected one FAQPage node")
        locations = list(re.finditer(r'\{\s*"@type"\s*:\s*"FAQPage"', raw))
        if len(locations) != 1:
            raise ValueError("Expected one FAQPage source object")
        start = locations[0].start()
        node, end = json.JSONDecoder().raw_decode(raw, start)
        node["mainEntity"] = questions
        indent = raw[:start].rsplit("\n", 1)[-1]
        if indent.strip():
            raise ValueError("Expected FAQPage on its own line")
        rendered = json.dumps(node, ensure_ascii=False, indent=2).replace("\n", "\n" + indent)
        # Preserve every other JSON-LD node and all HTML outside this object.
        return match.group(1) + raw[:start] + rendered + raw[end:] + match.group(3)

    return replace_once(
        r'(<script type="application/ld\+json">\s*)(.*?)(\s*</script>)',
        update_schema, html, "homepage JSON-LD block", flags=re.S,
    )


def render_files():
    identity = json.loads((ROOT / "identity.json").read_text())
    roles = identity["linkedin_aligned_work_experience"]["roles"]
    current_roles = [role for role in roles if role["end"] == "Present"]
    previous_roles = [role for role in roles if role["end"] != "Present"]
    source_url = identity["linkedin_aligned_work_experience"]["source_url"]
    career_html = (
        '<details id="linkedin-experience"><summary><span>Q07</span>LinkedIn Experience</summary>'
        '<div class="faq-answer"><p><strong>Current roles:</strong></p><ul>'
        + "".join("<li>" + escape(role["title"]) + "</li>" for role in current_roles)
        + '</ul><p><strong>Previous roles:</strong></p><ul>'
        + "".join("<li>" + escape(role["title"]) + " — " + escape(year_range(role))
                  + "</li>" for role in previous_roles)
        + '</ul><p><a href="' + escape(source_url, quote=True)
        + '" target="_blank" rel="noopener noreferrer">Role details on LinkedIn</a>.</p></div></details>'
    )
    html = (ROOT / "index.html").read_text()
    html = replace_once(
        r'<details(?: id="linkedin-experience")?><summary><span>Q07</span>.*?</details>',
        lambda _: career_html, html, "Q07 LinkedIn Experience entry", flags=re.S,
    )
    # Q08 is a curated synthesis of education and recovered institutional evidence.
    # This role synchronizer must never append or replace its teaching narrative.
    outputs = {"index.html": sync_faq_schema(html)}
    for name in ("README.md", "llms.txt"):
        outputs[name] = sync_role_section(
            (ROOT / name).read_text(), current_roles, previous_roles, source_url, name,
        )
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate synchronization without writing")
    args = parser.parse_args()
    outputs = render_files()
    changed = [name for name, value in outputs.items() if (ROOT / name).read_text() != value]
    if args.check:
        if changed:
            raise SystemExit("LinkedIn role summaries or FAQ metadata need synchronization: " + ", ".join(changed))
        print("LinkedIn role summaries and visible FAQ metadata are aligned.")
    else:
        for name in changed:
            (ROOT / name).write_text(outputs[name])
        print("Updated: " + (", ".join(changed) or "already aligned"))
