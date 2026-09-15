from pathlib import Path
import re
P=Path("index.html")
h=P.read_text(encoding="utf-8")
CANONICAL_PERSON="https://joe-nasr-signals.vercel.app/v2/#joe-nasr"
CANONICAL_PROFILE="https://joe-nasr-signals.vercel.app/v2/"
h=re.sub(r'<meta name="description" content="[^"]*"\s*/>', '<meta name="description" content="Public work archive for Joe Ribal Nasr, a Lebanese creative technologist working across XR, AI, interactive systems, visual communication, education, music and experimental software." />', h, count=1)
h=re.sub(r'<meta property="og:title" content="[^"]*"\s*/>', '<meta property="og:title" content="Joe Nasr — Public Work Archive | Creative Technology, XR &amp; AI" />', h, count=1)
h=re.sub(r'<meta name="twitter:title" content="[^"]*"\s*/>', '<meta name="twitter:title" content="Joe Nasr — Public Work Archive | Creative Technology, XR &amp; AI" />', h, count=1)
h=re.sub(r'<title>.*?</title>', '<title>Joe Nasr — Public Work Archive | Creative Technology, XR &amp; AI</title>', h, count=1, flags=re.S)
h=h.replace('Lebanese musician.<br />Middle East creative director.','Creative technologist.<br />One public record.')
h=h.replace('Joe Ribal Nasr is a Lebanese creative director, musician, composer, sound professional, media educator and digital-experience creator whose public work spans Dubai, Lebanon and Middle East-focused creative technology.','Joe Ribal Nasr is a Lebanese creative technologist working across XR, AI, interactive systems, spatial computing and experimental software, with professional history in creative direction, visual communication, education and music.')
h=h.replace('Lebanese Musician · Composer · Middle East Creative Director · AI/XR Creator','Creative Technologist · XR · AI · Interactive Systems')
P.write_text(h,encoding="utf-8")
