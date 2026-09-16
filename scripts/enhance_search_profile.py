from pathlib import Path
import re

P = Path("index.html")
h = P.read_text(encoding="utf-8")
CANONICAL_PERSON = "https://joe-nasr-signals.vercel.app/v2/#joe-nasr"
CANONICAL_PROFILE = "https://joe-nasr-signals.vercel.app/v2/"

# The root page is a public-work archive. /v2/ is the canonical person profile.
h = re.sub(
    r'<meta name="description" content="[^"]*"\s*/>',
    '<meta name="description" content="Public work archive for Joe Nasr, a Lebanese creative technologist working across XR, AI, interactive systems, visual communication, education, music and experimental software." />',
    h,
    count=1,
)
h = re.sub(
    r'<meta name="author" content="[^"]*"\s*/>',
    '<meta name="author" content="Joe Nasr" />',
    h,
    count=1,
)
h = re.sub(
    r'<meta property="og:title" content="[^"]*"\s*/>',
    '<meta property="og:title" content="Joe Nasr — Public Work Archive | Creative Technology, XR &amp; AI" />',
    h,
    count=1,
)
h = re.sub(
    r'<meta name="twitter:title" content="[^"]*"\s*/>',
    '<meta name="twitter:title" content="Joe Nasr — Public Work Archive | Creative Technology, XR &amp; AI" />',
    h,
    count=1,
)
h = re.sub(
    r'<title>.*?</title>',
    '<title>Joe Nasr — Public Work Archive | Creative Technology, XR &amp; AI</title>',
    h,
    count=1,
    flags=re.S,
)

h = h.replace(
    'Lebanese musician.<br />Middle East creative director.',
    'Creative technologist.<br />One public record.',
)
h = h.replace(
    'Joe Ribal Nasr is a Lebanese creative director, musician, composer, sound professional, media educator and digital-experience creator whose public work spans Dubai, Lebanon and Middle East-focused creative technology.',
    'Joe Ribal Nasr is a Lebanese creative technologist working across XR, AI, interactive systems, spatial computing and experimental software, with professional history in creative direction, visual communication, education and music.',
)
h = h.replace(
    'Lebanese Musician · Composer · Middle East Creative Director · AI/XR Creator',
    'Creative Technologist · XR · AI · Interactive Systems',
)

h = h.replace(
    '"@id": "https://joe-nasr-signals.vercel.app/#joe"',
    f'"@id": "{CANONICAL_PERSON}"',
)
h = re.sub(
    rf'("@id":\s*"{re.escape(CANONICAL_PERSON)}"\s*,\s*"name":\s*)"Joe Ribal Nasr"',
    r'\1"Joe Nasr"',
    h,
)
h = h.replace(
    '"alternateName": [\n          "Joe Nasr",\n          "Joe Ribal Nasr",\n          "Joseph Ribal Nasr"\n        ]',
    '"alternateName": [\n          "Joe Ribal Nasr",\n          "Joseph Ribal Nasr"\n        ]',
)
h = h.replace(
    '"alternateName":["Joe Nasr","Joe Ribal Nasr","Joseph Ribal Nasr"]',
    '"alternateName":["Joe Ribal Nasr","Joseph Ribal Nasr"]',
)
h = h.replace(
    '"alternateName": [\n          "Joe Nasr",\n          "Joseph Nasr"\n        ]',
    '"alternateName": [\n          "Joe Ribal Nasr",\n          "Joseph Ribal Nasr"\n        ]',
)
h = h.replace(
    '"alternateName":["Joe Nasr","Joseph Nasr"]',
    '"alternateName":["Joe Ribal Nasr","Joseph Ribal Nasr"]',
)

pos = 0
while True:
    pos = h.find(f'"@id": "{CANONICAL_PERSON}"', pos)
    if pos == -1:
        break
    end = h.find('}', pos)
    if end == -1:
        break
    block = h[pos:end]
    block = block.replace(
        '"url": "https://joe-nasr-signals.vercel.app/"',
        f'"url": "{CANONICAL_PROFILE}"',
        1,
    )
    h = h[:pos] + block + h[end:]
    pos += len(block)

h = h.replace(
    '"jobTitle": [\n          "Creative Director",\n          "Composer",\n          "Musician",\n          "Digital Experience Creator",\n          "Media Educator",\n          "XR and Game Designer"\n        ]',
    '"jobTitle": [\n          "Creative Technologist",\n          "Creative Director",\n          "Educator",\n          "Composer"\n        ]',
)
h = h.replace(
    '"jobTitle":["Creative Director","Composer","Musician","Digital Experience Creator","Media Educator","XR and Game Designer"]',
    '"jobTitle":["Creative Technologist","Creative Director","Educator","Composer"]',
)
h = h.replace(
    '"description": "Lebanese musician, composer, creative director, sound professional, media educator, AI/XR creator and founder of RoboMarket.ae."',
    '"description": "Lebanese creative technologist working across XR, AI, interactive systems, spatial computing, multimodal interfaces and experimental software."',
)
h = h.replace(
    '"description":"Lebanese musician, composer, creative director, sound professional, media educator, AI/XR creator and founder of RoboMarket.ae."',
    '"description":"Lebanese creative technologist working across XR, AI, interactive systems, spatial computing, multimodal interfaces and experimental software."',
)
h = re.sub(
    r',?\s*"https://(?:www\.)?robomarket\.ae/"',
    '',
    h,
)
P.write_text(h, encoding="utf-8")

# Keep current game lineage/source relations evidence-based and separate
# current published games from public development history.
robosim_same_as = '''            "sameAs": [
              "https://github.com/Joenasriani/robosim"
            ],
'''
robosim_source_link = '<a href="https://github.com/Joenasriani/robosim">Source</a>'
sector_source = "https://github.com/Joenasriani/kids-slider-game"
sector_marker = '''            "creator": {
              "@id": "https://joe-nasr-signals.vercel.app/v2/#joe-nasr"
            },
            "inLanguage": "en",
            "keywords": [
              "cyber puzzle game",'''
sector_replacement = '''            "creator": {
              "@id": "https://joe-nasr-signals.vercel.app/v2/#joe-nasr"
            },
            "sameAs": [
              "https://github.com/Joenasriani/kids-slider-game"
            ],
            "inLanguage": "en",
            "keywords": [
              "cyber puzzle game",'''
sector_visible = '<div class="links"><a href="https://joenasr.itch.io/sector-glow">Play</a></div>'
sector_visible_replacement = '<div class="links"><a href="https://joenasr.itch.io/sector-glow">Play</a><a href="https://github.com/Joenasriani/kids-slider-game">Source</a></div>'

for game_path in (Path("v2/games.html"), Path("v2/games.json")):
    game_text = game_path.read_text(encoding="utf-8")
    game_text = game_text.replace(robosim_same_as, "")
    if sector_source not in game_text:
        game_text = game_text.replace(sector_marker, sector_replacement, 1)
    if game_path.name == "games.html":
        game_text = game_text.replace(robosim_source_link, "")
        game_text = game_text.replace(sector_visible, sector_visible_replacement, 1)
        game_text = game_text.replace(
            'Games / 26 unique public lineages',
            'Games / 26 current published lineages',
        )
        game_text = game_text.replace(
            '26 unique public game lineages. Distribution duplicates are consolidated rather than represented as separate games.',
            '26 current published game lineages. Public prototypes and development records are indexed separately.',
        )
        game_text = game_text.replace(
            '<a href="games.html" aria-current="page">Games</a><a href="https://joenasriani.github.io/joe-research-registry/">Research</a>',
            '<a href="games.html" aria-current="page">Published Games</a><a href="games-development.html">Development Archive</a><a href="https://joenasriani.github.io/joe-research-registry/">Research</a>',
        )
    game_path.write_text(game_text, encoding="utf-8")
