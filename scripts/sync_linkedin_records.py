"""Render verified LinkedIn facts from identity.json without touching other branches."""
from html import escape, unescape
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PERSON_ID = "https://joe-nasr-signals.vercel.app/#joe-nasr"


def render_files():
    identity = json.loads((ROOT / "identity.json").read_text())
    career = identity["linkedin_aligned_work_experience"]
    titles = [role["title"] for role in career["roles"]]
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
        '<div class="faq-answer"><p>Roles listed on Joe Nasr’s LinkedIn profile:</p><ol>'
        + "".join("<li>" + escape(title) + "</li>" for title in titles)
        + '</ol><p><a href="' + escape(source_url, quote=True)
        + '" target="_blank" rel="noopener noreferrer">Dates and role details on LinkedIn</a>.</p></div></details>'
    )
    html = (ROOT / "index.html").read_text()
    html, count = re.subn(
        r'<details(?: id="linkedin-experience")?><summary><span>Q07</span>.*?</details>',
        lambda _: career_html, html, count=1, flags=re.S,
    )
    if count != 1:
        raise ValueError("Expected one Q07 LinkedIn Experience entry")
    # Preserve the existing education facts; replace only the teaching paragraph.
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
            return " ".join(unescape(re.sub(r'<[^>]+>', ' ', value)).split())
        questions.append({"@type": "Question", "name": plain(summary), "acceptedAnswer": {"@type": "Answer", "text": plain(answer)}})
    for node in schema["@graph"]:
        if node.get("@type") == "FAQPage":
            node["mainEntity"] = questions
    html = html[:schema_match.start(2)] + json.dumps(schema, ensure_ascii=False, indent=2) + html[schema_match.end(2):]
    outputs = {"index.html": html}
    block = (
        "## LinkedIn Experience\n\nTitles in LinkedIn display order:\n\n"
        + "\n".join(f"{i}. {title}" for i, title in enumerate(titles, 1))
        + "\n\nSource: " + source_url + "\n"
        + "Checked: " + career["verified_live_on"] + ". Overlapping dates are preserved in identity.json; display order is not a consecutive chronology.\n\n"
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
        print("LinkedIn titles, teaching sources and visible FAQ schema are aligned.")
    else:
        for name in changed:
            (ROOT / name).write_text(outputs[name])
        print("Updated: " + (", ".join(changed) or "already aligned"))
