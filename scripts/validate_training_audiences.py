"""Verify visible training labels agree with the public identity and legacy projections.

This validator reads only local repository content. It does not publish,
rewrite, or expose private training evidence.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / "index.html").read_text()
opening = '<div class="client-bank-group client-bank-group-training">'
start = page.index(opening)
end = page.index('<div class="faq-more">', start)
section = page[start:end]
visible = [
    (html.unescape(name.strip()), html.unescape(audience.strip()))
    for name, audience in re.findall(
        r'<li>([^<]+)<span class="training-audience">([^<]+)</span></li>',
        section,
    )
]
canonical = json.loads((ROOT / "identity.json").read_text())
legacy = json.loads((ROOT / "v2/identity.json").read_text())
records = canonical["client_relationship_bank_2026_10_04"]["workshops_and_training_for"]
aliases = {"Ministry of Culture and Knowledge Development":
           "Ministry of Culture & Knowledge Development"}

assert len(visible) == len(records) == 23, "Training record count mismatch"
assert len({name for name, _ in visible}) == len(visible), "Duplicate organizations"
for entry, (name, audience) in zip(records, visible):
    assert aliases.get(entry["name"], entry["name"]) == name, f"Organization mismatch: {name}"
    field = entry["training_audience"]
    assert field["display_label"] == audience, f"Audience mismatch: {name}"
    assert field["audience_kind"], f"Unclassified audience: {name}"
    assert field["evidence_status"], f"Missing evidence qualification: {name}"
    assert field["boundary"], f"Missing inference boundary: {name}"
assert (legacy["client_relationship_bank_2026_10_04"] ==
        canonical["client_relationship_bank_2026_10_04"]), "Legacy identity drift"
assert "Canon sponsorship is not independently established" in str(records), "Canon evidence boundary missing"
assert "Entire Executive Editors department trained according to user clarification" in str(records), "ITP scope boundary missing"
print("Training relationship alignment passed: 23 audiences; identity and legacy synchronized.")
