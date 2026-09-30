"""Render verified LinkedIn facts from identity.json without touching other branches."""
from html import escape, unescape
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PERSON_ID = "https://joe-nasr-signals.vercel.app/#joe-nasr"


def year_range(role):
    start = str(role["start"])[:4]
    end = role["end"] if role["end"] == "Present" else str(role["end"])[:4]
    return f"{start}–{end}"


def render_files():
    identity = json.loads((ROOT / "identity.json").read_text())
    career = identity["linkedin_aligned_work_experience"]
    roles = career["roles"]
    current_roles = [role for role in roles if role["end"] == "Present"]
    previous_roles = [role for role in roles if role["end"] != "Present"]
    teaching = identity["teaching_and_training"]
    organizations = teaching["organizations_named_on_linkedin"]
    organization_text = ", ".join(organizations[:-1]) + " and " + organizations[-1]
    teaching_text = (
        "Joe Nasr has worked as a Guest Lecturer & Corporate Trainer since May 2016, "
        "with more than 100 sessions delivered through universities, training providers, "
        "government organizations, media teams and companies. "
        "His LinkedIn teaching entry lists " + organization_text + "."
    )
    historical = teaching["historical_institutional_evidence"][0]
    source_url = career["source_url"]
    career_html = (
        '<details id="linkedin-experience"><summary><span>Q07</span>LinkedIn Experience</summary>'
        '<div class="faq-answer"><p><strong>Current roles:</strong></p><ul>'
        + "".join("<li>" + escape(role["title"]) + "</li>" for role in current_roles)
        + '</ul><p><strong>Previous roles:</strong></p><ul>'
        + "".join("<li>" + escape(role["title"]) + " — " + escape(year_range(role)) + "</li>" for role in previous_roles)
        + '</ul><p><a href="' + escape(source_url, quote=True)
        + '" target="_blank" rel="noopener noreferrer">Role details on LinkedIn</a>.</p></div></details>'
    )
    html = (ROOT / "index.html").read_text()
    html, count = re.subn(
        r'<details(?: id="linkedin-experience")?><summary><span>Q07</span>.*?</details>',
        lambda _: career_html, html, count=1, flags=re.S,
    )
    if count != 1:
        raise ValueError("Expected one Q07 LinkedIn Experience entry")

    match = re.search(r'(<details><summary><span>Q08</span>.*?<div class="faq-answer">)(.*?)(</div></details>)', html, re.S)
    if not match:
        raise ValueError("Expected one Q08 education and teaching entry")
    education = match.group(2).split("Joe Nasr has", 1)[0].rstrip()
    teaching_html = escape(teaching_text) + (
        ' A separate <a href="' + escape(historical["source_url"], quote=True)
        + '" target="_blank" rel="noopener noreferrer">SAE UAE institutional post</a>'
        ' documents his mentorship in a six-month Design and Motion Graphics program.'
    )
    html = html[:match.start(2)] + education + " " + teaching_html + html[match.end(2):]

    schema_match = re.search(r'(<script type="application/ld\+json">\s*)(.*?)(\s*</script>)', html, re.S)
    schema = json.loads(schema_match.group(2))
    questions = []
    for summary, answer in re.findall(r'<details[^>]*><summary>(.*?)</summary><div class="faq-answer">(.*?)</div></details>', html, re.S):
        summary = re.sub(r'<span>Q\d+</span>', '', summary)
        def plain(value):
            value = re.sub(r'</li>\s*<li>', '; ', value)
            value = re.sub(r'</p>\s*<(?:ol|ul)>', ' ', value)
            value = re.sub(r'</(?:ol|ul)>\s*<p>', '. ', value)
            return " ".join(unescape(re.sub(r'<[^>]+>', ' ', value)).split())
        questions.append({"@type": "Question", "name": plain(summary), "acceptedAnswer": {"@type": "Answer", "text": plain(answer)}})
    for node in schema["@graph"]:
        if node.get("@type") == "FAQPage":
            node["mainEntity"] = questions
    html = html[:schema_match.start(2)] + json.dumps(schema, ensure_ascii=False, indent=2) + html[schema_match.end(2):]
    outputs = {"index.html": html}

    block = (
        "## LinkedIn Experience\n\n"
        "Current roles:\n"
        + "".join("- " + role["title"] + "\n" for role in current_roles)
        + "\nPrevious roles:\n"
        + "".join("- " + role["title"] + " — " + year_range(role) + "\n" for role in previous_roles)
        + "\nSource: " + source_url + "\n"
        + "Updated from the LinkedIn structure confirmed by Joe Nasr on " + career["verified_live_on"] + ". "
        + "Concurrent contract/freelance dates are preserved; named contract clients are not recast as employers.\n\n"
    )
    for name in ("README.md", "llms.txt"):
        text = (ROOT / name).read_text()
        text, count = re.subn(r'## (?:Work experience|LinkedIn Experience)\n.*?(?=## Education and teaching)', lambda _: block, text, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f"Expected one career section in {name}")
        text = re.sub(r'- (?:The current LinkedIn teaching entry names|The LinkedIn teaching entry lists).*',
                      lambda _: "- The LinkedIn teaching entry lists " + organization_text + ".", text)
        history_line = "- Separate institutional evidence: SAE UAE credits Joe Nasr’s mentorship in a six-month Design and Motion Graphics program: " + historical["source_url"]
        if "- Separate institutional evidence:" in text:
            text = re.sub(r'- Separate institutional evidence:.*', lambda _: history_line, text)
        else:
            text = text.replace("- The LinkedIn teaching entry lists " + organization_text + ".", "- The LinkedIn teaching entry lists " + organization_text + ".\n" + history_line)
        outputs[name] = text
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate synchronization without writing")
    args = parser.parse_args()
    outputs = render_files()
    changed = [name for name, value in outputs.items() if (ROOT / name).read_text() != value]
    if args.check:
        if changed:
            raise SystemExit("LinkedIn records need synchronization: " + ", ".join(changed))
        print("LinkedIn roles, teaching sources and visible FAQ schema are aligned.")
    else:
        for name in changed:
            (ROOT / name).write_text(outputs[name])
        print("Updated: " + (", ".join(changed) or "already aligned"))
