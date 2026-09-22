from pathlib import Path
import json
import re

P = Path("index.html")
h = P.read_text(encoding="utf-8")
CANONICAL_PERSON = "https://joe-nasr-signals.vercel.app/#joe-nasr"
CANONICAL_PROFILE = "https://joe-nasr-signals.vercel.app/"

# Existing profile identifiers are preserved here; canonical-route changes must be coordinated with the workflow and published files.
h = re.sub(
    r'<meta name="description" content="[^"]*"\s*/>',
    '<meta name="description" content="Public work archive for Joe Nasr, a Lebanese creative director with more than 20 years of work across advertising, visual communication, multimedia, motion graphics, 3D and production in the UAE and wider GCC, with current work in digital experiences, interactive prototyping, XR, games and experimental software." />',
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
    '<meta property="og:title" content="Joe Nasr — Creative Director | Digital Experiences | Interactive Prototyping" />',
    h,
    count=1,
)
h = re.sub(
    r'<meta name="twitter:title" content="[^"]*"\s*/>',
    '<meta name="twitter:title" content="Joe Nasr — Creative Director | Digital Experiences | Interactive Prototyping" />',
    h,
    count=1,
)
h = re.sub(
    r'<title>.*?</title>',
    '<title>Joe Nasr — Creative Director | Digital Experiences | Interactive Prototyping</title>',
    h,
    count=1,
    flags=re.S,
)

h = h.replace(
    'Lebanese musician.<br />Middle East creative director.',
    'Creative Director.<br />Digital Experiences · Interactive Prototyping.',
)
h = h.replace(
    'Joe Ribal Nasr is a Lebanese creative director, musician, composer, sound professional, media educator and digital-experience creator whose public work spans Dubai, Lebanon and Middle East-focused creative technology.',
    'Joe Ribal Nasr is a Lebanese creative director with more than 20 years of work across advertising, visual communication, multimedia, motion graphics, 3D and production in the UAE and wider GCC, with current work in digital experiences, interactive prototyping, XR, games and experimental software, alongside music and teaching.',
)
h = h.replace(
    'Lebanese Musician · Composer · Middle East Creative Director · AI/XR Creator',
    'Creative Director · Digital Experiences · Interactive Prototyping',
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
    '"jobTitle": [\n          "Creative Director",\n          "Creative Technologist",\n          "Educator",\n          "Composer"\n        ]',
)
h = h.replace(
    '"jobTitle":["Creative Director","Composer","Musician","Digital Experience Creator","Media Educator","XR and Game Designer"]',
    '"jobTitle":["Creative Director","Creative Technologist","Educator","Composer"]',
)
h = h.replace(
    '"description": "Lebanese musician, composer, creative director, sound professional, media educator, AI/XR creator and founder of RoboMarket.ae."',
    '"description": "Lebanese creative director with an established background in advertising, visual communication, multimedia, motion and 3D, with current work in digital experiences, interactive prototyping, XR, games and experimental software."',
)
h = h.replace(
    '"description":"Lebanese musician, composer, creative director, sound professional, media educator, AI/XR creator and founder of RoboMarket.ae."',
    '"description":"Lebanese creative director with an established background in advertising, visual communication, multimedia, motion and 3D, with current work in digital experiences, interactive prototyping, XR, games and experimental software."',
)
h = re.sub(r',?\s*"https://(?:www\.)?robomarket\.ae/"(?=\s*[,\]])', '', h)
P.write_text(h, encoding="utf-8")

# Keep game entities centered on gameplay, platform and genre. Joe Nasr is creator,
# while historical names and alternate repositories are represented only where useful.
for game_path in (Path("v2/games.html"), Path("v2/games.json")):
    if not game_path.exists():
        continue
    game_text = game_path.read_text(encoding="utf-8")
    game_text = game_text.replace("https://joe-nasr-signals.vercel.app/v2/#joe-nasr", CANONICAL_PERSON)

    # RoboSim: canonical source is robo-web-sim; robosim is an alternate development copy.
    game_text = game_text.replace(
        '"name": "RoboSim",\n            "url": "https://joenasr.itch.io/robosim",',
        '"name": "RoboSim",\n            "alternateName": "RoboWebSim",\n            "url": "https://joenasr.itch.io/robosim",',
    )
    game_text = game_text.replace(
        '"sameAs": [\n              "https://github.com/Joenasriani/robosim"\n            ],',
        '"sameAs": [\n              "https://github.com/Joenasriani/robo-web-sim",\n              "https://github.com/Joenasriani/robosim"\n            ],',
    )

    # ZIP IT!: remove legacy LinkedIn/snake classification and describe the real mechanic.
    game_text = game_text.replace(
        '"description": "Independent LinkedIn themed browser snake puzzle and compact arcade game. Not affiliated with LinkedIn.",',
        '"description": "Browser grid path puzzle about covering every cell with one continuous route while visiting numbered checkpoints in order.",',
    )
    game_text = game_text.replace(
        '"genre": [\n              "Puzzle",\n              "Arcade"\n            ],',
        '"genre": [\n              "Puzzle",\n              "Logic"\n            ],',
        1,
    )
    game_text = game_text.replace(
        '"snake puzzle game",\n              "browser arcade game",\n              "LinkedIn themed game",\n              "indie browser game"',
        '"grid path puzzle game",\n              "Hamiltonian path game",\n              "browser logic game",\n              "path planning game"',
    )

    # Historical duplicate names should read naturally, not as internal entity jargon.
    game_text = game_text.replace(
        'Sorting Balls 3D is treated as the same lineage.',
        'Sorting Balls 3D is an alternate public listing of the same game.',
    )

    # Sector Glow source is a public source repository.
    sector_source = "https://github.com/Joenasriani/kids-slider-game"
    sector_marker = '''            "creator": {\n              "@id": "https://joe-nasr-signals.vercel.app/v2/#joe-nasr"\n            },\n            "inLanguage": "en",\n            "keywords": [\n              "cyber puzzle game",'''
    sector_replacement = '''            "creator": {\n              "@id": "https://joe-nasr-signals.vercel.app/v2/#joe-nasr"\n            },\n            "sameAs": [\n              "https://github.com/Joenasriani/kids-slider-game"\n            ],\n            "inLanguage": "en",\n            "keywords": [\n              "cyber puzzle game",'''
    if sector_source not in game_text:
        game_text = game_text.replace(sector_marker, sector_replacement, 1)

    if game_path.name == "games.html":
        game_text = game_text.replace(
            '<a href="./">Identity</a>',
            '<a href="./">Profile</a>',
        )
        game_text = game_text.replace(
            'The catalog is organized by what each game actually is: mechanic, genre, platform and playable surface. Creator identity is attached as provenance, not used as the topic.',
            'Each entry identifies the game mechanic, genre, platform, playable build and available source.',
        )
        game_text = game_text.replace(
            '<div class="game"><div class="num">06</div><div><h2>RoboSim</h2><div class="meta">Educational / Simulation / Early access</div></div><p>Program robot behavior, simulate it and iterate through an educational browser environment.</p><div class="links"><a href="https://joenasr.itch.io/robosim">Play</a></div></div>',
            '<div class="game"><div class="num">06</div><div><h2>RoboSim</h2><div class="meta">Educational / Simulation / Early access</div></div><p>Program robot behavior, simulate it and iterate through an educational browser environment.</p><div class="links"><a href="https://joenasr.itch.io/robosim">Play</a><a href="https://github.com/Joenasriani/robo-web-sim">Source</a></div></div>',
        )
        game_text = game_text.replace(
            '<div class="game"><div class="num">22</div><div><h2>ZIP IT!</h2><div class="meta">Puzzle / Arcade / Snake</div></div><p>An independent LinkedIn themed browser snake puzzle presented as a compact arcade experiment. It is not affiliated with LinkedIn.</p>',
            '<div class="game"><div class="num">22</div><div><h2>ZIP IT!</h2><div class="meta">Puzzle / Grid path / Browser</div></div><p>Trace one continuous route across the grid, cover every cell and visit numbered checkpoints in order.</p>',
        )
        game_text = game_text.replace(
            '<div class="game"><div class="num">12</div><div><h2>Ball Sort 3D</h2><div class="meta">Puzzle / Logic / 3D</div></div><p>Move colored balls between tubes under constrained placement rules until every color is grouped. Sorting Balls 3D is treated as the same lineage.</p>',
            '<div class="game"><div class="num">12</div><div><h2>Ball Sort 3D</h2><div class="meta">Puzzle / Logic / 3D</div></div><p>Move colored balls between tubes under constrained placement rules until every color is grouped. Sorting Balls 3D is an alternate public listing of the same game.</p>',
        )

    game_path.write_text(game_text, encoding="utf-8")

# Keep development-history wording useful to visitors rather than exposing internal entity language.
dev_path = Path("v2/games-development.html")
if dev_path.exists():
    d = dev_path.read_text(encoding="utf-8")
    d = d.replace("https://joe-nasr-signals.vercel.app/v2/#joe-nasr", CANONICAL_PERSON)
    d = d.replace('<a href="./">Identity</a>', '<a href="./">Profile</a>')
    d = d.replace('historical names in the same lineage', 'historical names for the same game')
    d = d.replace('is the same lineage; kids-hero-quest is retained as an alternate development build', 'is the same game; kids-hero-quest is retained as an alternate development build')
    d = d.replace('alternate build of the same game lineage', 'alternate build of the same game')
    d = d.replace('26 current published lineages / this page is development history', '26 published games / this page is development history')
    dev_path.write_text(d, encoding="utf-8")
