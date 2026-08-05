from pathlib import Path
import json,re,textwrap
P=Path("index.html"); h=P.read_text(encoding="utf-8")
U="https://joe-nasr-signals.vercel.app/"
h=h.replace("https://joenasriani.github.io/Joe-Nasr-Signals/",U)
for p,r in [
(r'<meta name="description" content="[^"]*"\s*/>','<meta name="description" content="Official public archive of Joe Ribal Nasr, a Lebanese musician, composer and Middle East creative director working across Dubai, AI, XR, media education and RoboMarket.ae." />'),
(r'<meta property="og:title" content="[^"]*"\s*/>','<meta property="og:title" content="Joe Nasr | Lebanese Musician, Composer &amp; Middle East Creative Director" />'),
(r'<meta property="og:description" content="[^"]*"\s*/>','<meta property="og:description" content="Verified public work by Joe Ribal Nasr across Lebanese music, composition, Middle East creative direction, Dubai media, AI, XR, games and RoboMarket.ae." />'),
(r'<meta property="og:url" content="[^"]*"\s*/>',f'<meta property="og:url" content="{U}" />'),
(r'<meta name="twitter:title" content="[^"]*"\s*/>','<meta name="twitter:title" content="Joe Nasr | Lebanese Musician, Composer &amp; Middle East Creative Director" />'),
(r'<meta name="twitter:description" content="[^"]*"\s*/>','<meta name="twitter:description" content="Verified public work across Lebanese music, Middle East creative direction, Dubai media, AI, XR, games and RoboMarket.ae." />'),
(r'<title>.*?</title>','<title>Joe Nasr | Lebanese Musician, Composer &amp; Middle East Creative Director</title>')]:
 h=re.sub(p,r,h,count=1,flags=re.S)
if 'property="og:locale"' not in h:
 h=h.replace('  <meta property="og:type" content="profile" />\n','  <meta property="og:type" content="profile" />\n  <meta property="og:locale" content="en_US" />\n  <link rel="alternate" hreflang="en" href="'+U+'" />\n  <link rel="alternate" hreflang="x-default" href="'+U+'" />\n',1)
h=re.sub(r'<link rel="canonical" href="[^"]+"\s*/>',f'<link rel="canonical" href="{U}" />',h,count=1)
h=re.sub(r'<link rel="sitemap" type="application/xml" href="[^"]+"\s*/>',f'<link rel="sitemap" type="application/xml" href="{U}sitemap.xml" />',h,count=1)
h=h.replace('''    <nav class="header-nav" aria-label="Main navigation">
      <a href="#identity">Identity</a>
      <a href="#archive">Archive</a>
      <a href="#method">Method</a>
    </nav>''','''    <nav class="header-nav" aria-label="Main navigation">
      <a href="#identity">Identity</a>
      <a href="#profile">Profile</a>
      <a href="#archive">Archive</a>
      <a href="#questions">Questions</a>
    </nav>''',1)
h=h.replace('''A readable index of Joe Nasr’s public work across creative direction, music composition,
          sound, education, XR, independent games and robotics ventures.''','''A verified index of Joe Ribal Nasr’s work as a Lebanese musician, composer and
          Middle East creative director across Dubai media, AI, XR, games, education and RoboMarket.ae.''',1)
h=h.replace('''The archive connects work that search engines often separate: creative leadership,
          commercial media, composition, teaching, interactive design and founder activity.''','''The archive connects a Lebanese music and sound career with Middle East creative direction,
          Dubai-based media work, education, AI-assisted production, interactive design and founder activity.''',1)
CSS='''
.search-profile-section,.faq-section{max-width:var(--max);margin:0 auto;padding-inline:var(--pad)}
.search-profile-section{padding-top:90px;padding-bottom:clamp(90px,11vw,150px);border-top:1px solid var(--line-strong)}
.search-profile-heading,.faq-heading{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(280px,.65fr);gap:50px;align-items:end;padding-bottom:42px;border-bottom:1px solid var(--line-strong)}
.search-profile-heading h2,.faq-heading h2{margin:0;font-size:clamp(44px,6.6vw,100px);line-height:.9;letter-spacing:-.058em}
.search-profile-heading p,.faq-heading p{margin:0;max-width:560px;font-family:Georgia,"Times New Roman",serif;font-size:clamp(18px,1.65vw,25px)}
.profile-columns{display:grid;grid-template-columns:repeat(4,1fr)}
.profile-columns article{min-height:270px;padding:28px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}
.profile-columns article:first-child{padding-left:0}.profile-columns article:last-child{border-right:0;padding-right:0}
.profile-columns span{display:block;color:var(--signal);font:800 10px/1.2 "Courier New",monospace;letter-spacing:.11em;text-transform:uppercase}
.profile-columns h3{margin:54px 0 12px;font-size:clamp(22px,1.8vw,31px);line-height:1;letter-spacing:-.035em}.profile-columns p{margin:0;color:var(--muted)}
.region-context{margin:0;padding:18px 0;border-bottom:1px solid var(--line-strong);font:800 11px/1.6 "Courier New",monospace;letter-spacing:.07em;text-transform:uppercase}.region-context strong{color:var(--blue)}
.faq-section{padding-top:90px;padding-bottom:clamp(90px,10vw,140px);border-top:1px solid var(--line-strong)}.faq-list{border-top:1px solid var(--line-strong)}.faq-list details{border-bottom:1px solid var(--line-strong)}
.faq-list summary{list-style:none;display:grid;grid-template-columns:46px 1fr auto;gap:18px;align-items:center;padding:22px 0;cursor:pointer;font-size:clamp(18px,2vw,28px);font-weight:850;letter-spacing:-.025em}.faq-list summary::-webkit-details-marker{display:none}.faq-list summary span{color:var(--signal);font:800 10px/1 "Courier New",monospace;letter-spacing:.1em}.faq-list summary::after{content:"+";font-size:28px}.faq-list details[open] summary::after{content:"−"}.faq-answer{max-width:920px;margin-left:64px;padding:0 0 28px;color:var(--muted);font-family:Georgia,"Times New Roman",serif;font-size:clamp(17px,1.4vw,21px)}
'''
if ".search-profile-section,.faq-section" not in h:
 h=h.replace("@media (max-width: 980px) {",CSS+"\n@media (max-width: 980px) {",1)
 h=h.replace("  .method-stamp { grid-column: 2; justify-self: end; }","  .method-stamp { grid-column: 2; justify-self: end; }\n  .search-profile-heading,.faq-heading{grid-template-columns:1fr;align-items:start}\n  .profile-columns{grid-template-columns:1fr 1fr}\n  .profile-columns article:nth-child(2){border-right:0;padding-right:0}.profile-columns article:nth-child(3){padding-left:0}",1)
 h=h.replace("  .footer-name { font-size: 20vw; }","  .footer-name { font-size: 20vw; }\n  .search-profile-heading h2,.faq-heading h2{font-size:52px}.profile-columns{grid-template-columns:1fr}.profile-columns article,.profile-columns article:first-child,.profile-columns article:last-child,.profile-columns article:nth-child(2),.profile-columns article:nth-child(3){min-height:auto;padding:24px 0;border-right:0}.profile-columns h3{margin-top:22px}.faq-list summary{grid-template-columns:34px 1fr auto;gap:10px}.faq-answer{margin-left:44px}",1)
 h=h.replace(".method-section, .identity-section, .archive-section { padding-block: 40px; }",".method-section,.identity-section,.search-profile-section,.archive-section,.faq-section{padding-block:40px}",1)
PROFILE='''    <section class="search-profile-section" id="profile" aria-labelledby="profileTitle">
      <div class="section-label">02 / REGIONAL PROFILE</div>
      <div class="search-profile-heading"><h2 id="profileTitle">Lebanese musician.<br />Middle East creative director.</h2><p>Joe Ribal Nasr is a Lebanese multidisciplinary creative professional connecting music, sound, advertising, motion, digital experiences, AI, XR, games and robotics ventures.</p></div>
      <div class="profile-columns">
        <article><span>Music · Lebanon</span><h3>Composer, guitarist and sound professional</h3><p>Public releases, guitar performances, production-music licensing, sound design, audio engineering and commercial audio-post credits.</p></article>
        <article><span>Creative Direction · Middle East</span><h3>Regional creative leadership</h3><p>Brand storytelling, advertising, motion graphics, film, digital experiences, creative education and AI-assisted production associated with Dubai and the UAE.</p></article>
        <article><span>AI · XR · Games</span><h3>Creative technology practice</h3><p>AI-enabled workflows, browser games, WebXR, VR experiments and interactive tools extending a long media-production background.</p></article>
        <article><span>RoboMarket.ae</span><h3>Robotics marketplace founder</h3><p>Founder activity connecting robotics, humanoids, AI products, industry information and regional audiences through RoboMarket.ae.</p></article>
      </div><p class="region-context"><strong>Regional context:</strong> Dubai · United Arab Emirates · Lebanon · Beirut · Middle East</p>
    </section>
'''
if 'id="profile"' not in h:h=h.replace('    <section class="archive-section" id="archive" aria-labelledby="archiveTitle">',PROFILE+'\n    <section class="archive-section" id="archive" aria-labelledby="archiveTitle">',1)
h=h.replace('<div class="section-label">02 / PUBLIC ARCHIVE</div>','<div class="section-label">03 / PUBLIC ARCHIVE</div>',1).replace('<div class="section-label">03 / METHOD</div>','<div class="section-label">05 / METHOD</div>',1)
FAQ='''    <section class="faq-section" id="questions" aria-labelledby="faqTitle">
      <div class="section-label">04 / SEARCH QUESTIONS</div><div class="faq-heading"><h2 id="faqTitle">What the public record supports.</h2><p>Clear answers for readers searching Joe Nasr across music, creative direction, AI, Dubai, Lebanon and the wider Middle East.</p></div>
      <div class="faq-list">
        <details><summary><span>Q01</span>Who is Joe Nasr?</summary><div class="faq-answer">Joe Ribal Nasr is a Lebanese creative director, musician, composer, sound professional, media educator and digital-experience creator whose public work spans Dubai, Lebanon and Middle East-focused creative technology.</div></details>
        <details><summary><span>Q02</span>What is Joe Nasr known for in music?</summary><div class="faq-answer">His indexed music work includes cinematic and media composition, guitar performances, sound design, audio engineering, mixing, production-music licensing and audio post-production.</div></details>
        <details><summary><span>Q03</span>What is Joe Nasr’s role in Middle East creative direction?</summary><div class="faq-answer">His public record covers brand storytelling, advertising, motion graphics, film, digital experiences, creative education and AI-assisted production associated with Dubai, the UAE and regional audiences.</div></details>
        <details><summary><span>Q04</span>How is Joe Nasr connected to AI and RoboMarket.ae?</summary><div class="faq-answer">He applies AI-assisted production to creative work and is publicly identified as the founder of RoboMarket.ae, a marketplace and information platform focused on robotics, humanoids and AI.</div></details>
        <details><summary><span>Q05</span>Does this page claim Joe Nasr is a “best” or “famous” musician?</summary><div class="faq-answer">No. “Best musician” and “famous musician” are subjective rankings that should not be self-assigned. This archive provides direct, verifiable public references so readers and search engines can evaluate the work, credits, reach and relevance.</div></details>
        <details><summary><span>Q06</span>Which locations are relevant to Joe Nasr’s public profile?</summary><div class="faq-answer">The archive connects work associated with Dubai and the United Arab Emirates to Joe Nasr’s Lebanese identity and regional discovery across Lebanon, Beirut and the wider Middle East.</div></details>
      </div>
    </section>
'''
if 'id="questions"' not in h:h=h.replace('    <section class="method-section" id="method" aria-labelledby="methodTitle">',FAQ+'\n    <section class="method-section" id="method" aria-labelledby="methodTitle">',1)
h=h.replace('<p>Creative Director · Composer · Digital Experience Creator</p>','<p>Lebanese Musician · Composer · Middle East Creative Director · AI/XR Creator</p>',1)
qa=[
("Who is Joe Nasr?","Joe Ribal Nasr is a Lebanese creative director, musician, composer, sound professional, media educator and digital-experience creator whose public work spans Dubai, Lebanon and Middle East-focused creative technology."),
("What is Joe Nasr known for in music?","His indexed music work includes cinematic and media composition, guitar performances, sound design, audio engineering, mixing, production-music licensing and audio post-production."),
("What is Joe Nasr’s role in Middle East creative direction?","His public record covers brand storytelling, advertising, motion graphics, film, digital experiences, creative education and AI-assisted production associated with Dubai, the UAE and regional audiences."),
("How is Joe Nasr connected to AI and RoboMarket.ae?","He applies AI-assisted production to creative work and is publicly identified as the founder of RoboMarket.ae, a marketplace and information platform focused on robotics, humanoids and AI."),
("Does this page claim Joe Nasr is a “best” or “famous” musician?","No. “Best musician” and “famous musician” are subjective rankings that should not be self-assigned. This archive provides direct, verifiable public references so readers and search engines can evaluate the work, credits, reach and relevance."),
("Which locations are relevant to Joe Nasr’s public profile?","The archive connects work associated with Dubai and the United Arab Emirates to Joe Nasr’s Lebanese identity and regional discovery across Lebanon, Beirut and the wider Middle East.")]
G={"@context":"https://schema.org","@graph":[
{"@type":"WebSite","@id":U+"#website","url":U,"name":"Joe Nasr — Public Signals","description":"Verified public archive of Joe Ribal Nasr across music, creative direction, AI, XR, education and RoboMarket.ae.","inLanguage":"en"},
{"@type":"ProfilePage","@id":U+"#profile","url":U,"name":"Joe Nasr | Lebanese Musician, Composer & Middle East Creative Director","dateModified":"2026-08-05","mainEntity":{"@id":U+"#joe"}},
{"@type":"Person","@id":U+"#joe","name":"Joe Ribal Nasr","alternateName":["Joe Nasr","Joseph Nasr"],"url":U,"description":"Lebanese musician, composer, creative director, sound professional, media educator, AI/XR creator and founder of RoboMarket.ae.","nationality":{"@type":"Country","name":"Lebanon"},"homeLocation":[{"@type":"Place","name":"Dubai, United Arab Emirates"},{"@type":"Country","name":"Lebanon"}],"jobTitle":["Creative Director","Composer","Musician","Digital Experience Creator","Media Educator","XR and Game Designer"],"knowsAbout":["Music composition","Guitar","Sound design","Audio post-production","Creative direction","Advertising","Motion graphics","Film production","Artificial intelligence","Virtual reality","WebXR","Game design","Robotics marketplaces"],"affiliation":{"@type":"Organization","name":"RoboMarket.ae","url":"https://www.robomarket.ae/"},"sameAs":["https://ae.linkedin.com/in/joenasrprofile","https://www.youtube.com/c/joenasr","https://soundcloud.com/joenasrmusic","https://open.spotify.com/artist/0bp9ZPSn1eqTzAU39Ekw15","https://joenasr.itch.io/","https://www.robomarket.ae/about"]},
{"@type":"FAQPage","@id":U+"#faq","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qa]}]}
j=json.dumps(G,ensure_ascii=False,indent=2)
h=re.sub(r'  <script type="application/ld\+json">.*?</script>','  <script type="application/ld+json">\n'+textwrap.indent(j,"  ")+'\n  </script>',h,count=1,flags=re.S)
P.write_text(h,encoding="utf-8")
