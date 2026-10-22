"""Build the static website into ./docs from ./content.

Usage:  python build.py
Edit content/site.json, content/publications.json and content/projects/*.md,
then re-run. Output in docs/ is ready for GitHub Pages (or any static host).
No third-party packages required (Python 3.7+).
"""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs"

SITE = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
PUBS = json.loads((CONTENT / "publications.json").read_text(encoding="utf-8"))
PHD = json.loads((CONTENT / "phd_research.json").read_text(encoding="utf-8"))

NAV = [("index.html", "Home"), ("about.html", "About"), ("research.html", "Research"),
       ("publications.html", "Publications"),
       ("skills.html", "Skills & training"), ("cv.html", "CV"), ("contact.html", "Contact")]

esc = html.escape


# ------------------------------------------------------------ mini markdown
def inline(text, root):
    t = esc(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)

    def link(m):
        label, url = m.group(1), m.group(2)
        external = url.startswith(("http://", "https://", "mailto:"))
        href = url if external or url.startswith("#") else root + url
        attrs = ' rel="noopener" target="_blank"' if external else ""
        return '<a href="{}"{}>{}</a>'.format(href, attrs, label)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)


def markdown(src, root, blocks=None):
    blocks = blocks or {}
    out, para, items = [], [], []

    def flush():
        if para:
            out.append("<p>{}</p>".format(inline(" ".join(para), root)))
            para.clear()
        if items:
            out.append("<ul>{}</ul>".format("".join("<li>{}</li>".format(inline(i, root)) for i in items)))
            items.clear()

    for line in src.splitlines():
        s = line.strip()
        if not s:
            flush()
        elif s in blocks:
            flush(); out.append(blocks[s])
        elif s.startswith("## "):
            flush(); out.append("<h2>{}</h2>".format(inline(s[3:], root)))
        elif s.startswith("- "):
            if para: flush()
            items.append(s[2:])
        else:
            if items: flush()
            para.append(s)
    flush()
    return "\n".join(out)


def load_projects():
    projects = []
    for path in sorted((CONTENT / "projects").glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        _, front, body = raw.split("---", 2)
        meta = {}
        for line in front.strip().splitlines():
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
        meta["slug"] = path.stem
        meta["body"] = body
        meta["order"] = int(meta.get("order", 99))
        meta["featured"] = meta.get("featured", "no").lower() == "yes"
        meta["tools"] = [t.strip() for t in meta.get("tools", "").split(",") if t.strip()]
        projects.append(meta)
    return sorted(projects, key=lambda p: p["order"])


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# ------------------------------------------------------------ layout
def page(path, title, body, active="", description=None, scripts=()):
    depth = path.count("/")
    root = "../" * depth
    desc = esc(description or SITE["description"])
    full_title = esc(title + " | " + SITE["name"]) if title else esc(SITE["name"] + " | " + SITE["headline"])
    nav = "".join(
        '<li><a href="{r}{h}"{c}>{l}</a></li>'.format(
            r=root, h=h, l=l, c=' aria-current="page"' if h == active else "")
        for h, l in NAV)
    canonical = SITE["site_url"].rstrip("/") + "/" + path
    social = ('<link rel="canonical" href="{}">\n<meta property="og:image" content="{}/assets/img/portrait.jpg">'
              .format(esc(canonical), esc(SITE["site_url"].rstrip("/")))) if SITE["site_url"] else ""
    person = {
        "@context": "https://schema.org", "@type": "Person", "name": SITE["name"],
        "jobTitle": "Ph.D. Student, Civil Engineering", "affiliation": {"@type": "CollegeOrUniversity", "name": "University of Kansas"},
        "email": "mailto:" + SITE["emails"][0], "sameAs": [l["url"] for l in SITE["links"]],
    }
    script_tags = "".join('<script src="{}assets/js/{}" defer></script>'.format(root, s) for s in scripts)
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{social}
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}assets/css/style.css">
<script>document.documentElement.classList.add('js');try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{root}index.html">{name}</a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav id="site-nav" aria-label="Main"><ul>{nav}</ul></nav>
    <button class="theme-toggle" type="button" aria-label="Toggle dark mode" title="Toggle dark mode">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
    </button>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <p>© {year} {name} · {aff}</p>
    <p class="footer-links">{links}</p>
  </div>
</footer>
<script src="{root}assets/js/main.js" defer></script>
{scripts}
</body>
</html>
""".format(title=full_title, desc=desc, social=social,
           root=root, ld=json.dumps(person), name=esc(SITE["name"]), nav=nav, body=body,
           year=date.today().year, aff=esc(SITE["affiliation"]), scripts=script_tags,
           links=" · ".join('<a href="mailto:{0}">{0}</a>'.format(esc(e)) for e in SITE["emails"][:1]) + " · " +
                 " · ".join('<a href="{}" rel="noopener" target="_blank">{}</a>'.format(esc(l["url"]), esc(l["label"])) for l in SITE["links"]))


def page_head(eyebrow, title, lede="", wide=False):
    return ('<section class="page-head wrap{}"><p class="eyebrow">{}</p><h1>{}</h1>{}</section>'
            .format(' page-head-wide' if wide else '', esc(eyebrow), esc(title),
                    '<p class="lede">{}</p>'.format(esc(lede)) if lede else ""))


def kpi_access_button(p):
    if p["slug"] != "recovery-kpi-studio":
        return ""
    return '<p class="kpi-access"><button class="btn btn-primary" type="button" disabled aria-describedby="kpi-access-note">Open Recovery KPI Studio</button><span id="kpi-access-note" class="kpi-access-note">Not connected yet</span></p>'


def project_card(p, root):
    return """<article class="card project-card reveal" data-category="{cat}">
  <p class="card-meta"><span class="tag">{category}</span><span>{status}</span></p>
  <h3><a href="{root}projects/{slug}.html">{title}</a></h3>
  <p>{summary}</p>
  {access}
</article>""".format(cat=slugify(p["category"]), category=esc(p["category"]), status=esc(p.get("status", "")),
                     root=root, slug=p["slug"], title=esc(p["title"]), summary=esc(p["summary"]), access=kpi_access_button(p))


def entries(rows, format_text=esc):
    out = []
    for r in rows:
        pts = "".join("<li>{}</li>".format(format_text(x)) for x in r["points"])
        out.append('<article class="entry reveal"><div class="entry-head"><h3>{}</h3><span class="years">{}</span></div>'
                   '<p class="entry-org">{}</p><ul>{}</ul></article>'.format(esc(r["role"]), esc(r["years"]), esc(r["org"]), pts))
    return "\n".join(out)


# ------------------------------------------------------------ pages
def build_home(projects):
    root = ""
    intro = "".join("<p>{}</p>".format(esc(p)) for p in SITE["intro"])
    interests = "".join('<li class="card reveal"><h3>{}</h3><p>{}</p></li>'.format(esc(i["title"]), esc(i["text"]))
                        for i in SITE["interests"])
    featured = "".join(project_card(p, root) for p in projects if p["featured"])
    featured_columns = 2 if sum(p["featured"] for p in projects) % 2 == 0 else 3
    highlights = "".join("<li>{}</li>".format(esc(h)) for h in SITE["highlights"])
    expertise = "".join("<li>{}</li>".format(esc(s["group"])) for s in SITE["skills"])
    body = """
<section class="hero wrap">
  <div class="hero-text">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{headline}</h1>
    <div class="hero-intro">{intro}</div>
    <p class="actions">
      <a class="btn btn-primary" href="research.html">Explore my work</a>
      <a class="btn" href="{cv}" download>Download CV (PDF)</a>
      <a class="btn btn-quiet" href="contact.html">Get in touch</a>
    </p>
  </div>
  <figure class="hero-photo">
    <img src="assets/img/portrait.jpg" width="640" height="768" alt="Portrait of Marzieh Allahyari">
    <figcaption>Marzieh Allahyari<span>Ph.D. researcher · Lawrence, Kansas</span></figcaption>
  </figure>
</section>

<section class="band">
  <div class="wrap">
    <h2 class="section-title">Research interests</h2>
    <ul class="grid grid-3 plain">{interests}</ul>
  </div>
</section>

<section class="wrap section">
  <div class="section-head"><h2 class="section-title">Featured work</h2><a href="research.html">All research →</a></div>
  <div class="grid grid-{featured_columns}">{featured}</div>
</section>

<section class="wrap section two-col">
  <div>
    <h2 class="section-title">Selected highlights</h2>
    <ul class="ticks">{highlights}</ul>
  </div>
  <div>
    <h2 class="section-title">Technical expertise</h2>
    <ul class="ticks">{expertise}</ul>
    <p><a href="skills.html">See skills in detail →</a></p>
  </div>
</section>
""".format(name=esc(SITE["name"]), eyebrow=esc(SITE["eyebrow"]), headline=esc(SITE["headline"]), intro=intro, cv=SITE["cv_pdf"],
           interests=interests, featured=featured, featured_columns=featured_columns, highlights=highlights, expertise=expertise)
    return page("index.html", "", body, "index.html")


def build_about():
    emphasis_terms = [
        "University of Kansas", "structural engineering", "data engineering",
        "statistical modeling", "machine learning", "data analytics", "data science",
        "AI", "Recovery KPI Studio", "disaster resilience",
        "Dynamic Time Warping (DTW)", "latent class growth analysis (LCGA)",
        "linear mixed-effects models", "sensitivity analysis",
        "NHERI SPARC program (2025)", "Texas Advanced Computing Center (TACC)",
        "Society for Risk Analysis (SRA) Travel Award (2026)",
        "Phi Kappa Phi Honor Society (2026)", "Full scholarship",
    ]
    emphasis_pattern = re.compile("|".join(re.escape(esc(t)) for t in sorted(emphasis_terms, key=len, reverse=True)))

    def emphasize(text):
        return emphasis_pattern.sub(lambda m: "<strong>{}</strong>".format(m.group()), esc(text))

    paras = "".join("<p>{}</p>".format(emphasize(p)) for p in SITE["about"])
    edu = "".join('<article class="entry reveal"><div class="entry-head"><h3>{}</h3><span class="years">{}</span></div>'
                  '<p class="entry-org">{}</p>{}</article>'.format(
                      esc(e["degree"]), esc(e["years"]), esc(e["school"]),
                      "<p>{}</p>".format(emphasize(e["note"])) if e["note"] else "") for e in SITE["education"])
    awards = "".join("<li>{}</li>".format(emphasize(a)) for a in SITE["awards"])
    body = page_head("About", "Connecting data, AI, and disaster resilience") + """
<section class="wrap prose-layout">
  <div class="prose">{paras}</div>
  <aside class="side">
    <img src="assets/img/about-sparc.png" width="1199" height="1312" alt="Marzieh Allahyari beside the SPARC program sign at the Texas Advanced Computing Center" loading="lazy">
  </aside>
</section>
<section class="wrap section"><h2 class="section-title">Education</h2>{edu}</section>
<section class="wrap section about-experience"><h2 class="section-title">Research experience</h2>{exp}</section>
<section class="wrap section about-awards"><h2 class="section-title">Awards &amp; honors</h2><ul class="ticks">{awards}</ul></section>
""".format(paras=paras, edu=edu, exp=entries(SITE["experience"], emphasize), awards=awards)
    return page("about.html", "About", body, "about.html")


def streams_html(root, heading_level="h3", show_tools=True, extra_cards=""):
    out = []
    for i, s in enumerate(PHD["streams"], 1):
        tools = "".join("<li>{}</li>".format(esc(t)) for t in s["tools"])
        out.append("""<article class="stream card reveal">
  <p class="card-meta"><span class="stream-num">{n:02d}</span><span class="tag">{area}</span></p>
  <{h}>{title}</{h}>
  <p class="stream-narrative">{narrative}</p>
  {tool_list}
</article>""".format(n=i, area=esc(s["area"]), h=heading_level, title=esc(s["title"]),
                     narrative=esc(s["narrative"]),
                     tool_list='<ul class="chips" aria-label="Tools">{}</ul>'.format(tools) if show_tools else ""))
    return '<div class="grid grid-2 streams">{}{}</div>'.format("".join(out), extra_cards)


def build_research(projects):
    groups = [
        ("Structural engineering, risk & uncertainty", {"Structural Reliability", "Computational Methods", "Structural Engineering"}),
    ]
    grouped_sections = []
    for title, categories in groups:
        members = [p for p in projects if p["category"] in categories]
        if not members:
            continue
        cards = "".join(project_card(p, "") for p in members)
        columns = ' grid-3' if len(members) >= 3 else (' grid-2' if len(members) == 2 else '')
        grouped_sections.append('<section class="wrap section"><h2 class="section-title">{}</h2>'
                                '<div class="grid{}">{}</div></section>'.format(esc(title), columns, cards))
    body = page_head("Research", "Research & projects",
                     "Explore my work in disaster resilience and AI, data engineering and analytics, "
                     "and structural engineering and uncertainty.", wide=True) + """
<section class="wrap section phd">
  <div class="phd-head">
    <h2 class="section-title">Disaster resilience &amp; AI</h2>
    <p class="eyebrow">{kicker}</p>
    <h3>{title}</h3>
    <p class="lede">{summary}</p>
    <p><a class="btn" href="projects/{slug}.html">Read more about this research</a></p>
  </div>
  <h3 class="streams-title">Research workstreams</h3>
  {streams}
</section>
{grouped_sections}""".format(kicker=esc(PHD["kicker"]), title=esc(PHD["title"]), summary=esc(PHD["summary"]),
                     slug=PHD["project_slug"], streams=streams_html("", show_tools=False,
                         extra_cards="".join(project_card(p, "") for p in projects if p["slug"] == "recovery-kpi-studio")),
                     grouped_sections="".join(grouped_sections))
    return page("research.html", "Research", body, "research.html")


DEMO_HTML = """
<div class="demo" id="uq-demo">
  <div class="demo-controls">
    <fieldset>
      <legend>Input uncertainty (coefficient of variation)</legend>
      <label>Tip load P <output data-for="P">10%</output><input type="range" min="2" max="30" value="10" data-var="P"></label>
      <label>Distributed load w <output data-for="w">10%</output><input type="range" min="2" max="30" value="10" data-var="w"></label>
      <label>Elastic modulus E <output data-for="E">5%</output><input type="range" min="2" max="30" value="5" data-var="E"></label>
      <label>Moment of inertia I <output data-for="I">5%</output><input type="range" min="2" max="30" value="5" data-var="I"></label>
    </fieldset>
    <div class="demo-run">
      <label>Monte Carlo samples
        <select id="uq-n"><option value="200">200</option><option value="1000">1,000</option><option value="5000" selected>5,000</option><option value="20000">20,000</option></select>
      </label>
      <button type="button" class="btn btn-primary" id="uq-run">Run Monte Carlo</button>
    </div>
  </div>
  <figure class="viz">
    <figcaption><strong>Tip deflection distribution (mm)</strong>
      <span class="legend"><span class="key key-bar"></span>Monte Carlo histogram <span class="key key-line"></span>M-DRM estimate (17 runs)</span>
    </figcaption>
    <div class="chart" id="uq-hist" role="img" aria-label="Histogram of Monte Carlo tip deflections with the M-DRM distribution overlaid"></div>
    <div class="tooltip" id="uq-tip" hidden></div>
  </figure>
  <figure class="viz">
    <figcaption><strong>Monte Carlo running mean vs. number of model runs</strong>
      <span class="legend"><span class="key key-line key-s1"></span>Monte Carlo mean <span class="key key-line dashed"></span>M-DRM mean</span>
    </figcaption>
    <div class="chart chart-short" id="uq-conv" role="img" aria-label="Running Monte Carlo mean converging toward the M-DRM mean"></div>
  </figure>
  <table class="stats" id="uq-table">
    <caption>Estimated response statistics</caption>
    <thead><tr><th scope="col">Method</th><th scope="col">Model runs</th><th scope="col">Mean (mm)</th><th scope="col">Std. dev. (mm)</th></tr></thead>
    <tbody></tbody>
  </table>
</div>
"""


def build_project(p):
    path = "projects/{}.html".format(p["slug"])
    root = "../"
    content = markdown(p["body"], root, {"{{demo}}": DEMO_HTML, "{{streams}}": streams_html(root)})
    tools = "".join("<li>{}</li>".format(esc(t)) for t in p["tools"])
    body = """
<article class="wrap project">
  <p class="crumbs"><a href="../research.html">Research</a> / {category}</p>
  <header class="project-head">
    <p class="eyebrow">{category}</p>
    <h1>{title}</h1>
    <p class="lede">{summary}</p>
    {access}
    <dl class="facts"><div><dt>Status</dt><dd>{status}</dd></div><div><dt>Tools</dt><dd><ul class="chips">{tools}</ul></dd></div></dl>
  </header>
  <div class="prose">{content}</div>
</article>""".format(category=esc(p["category"]), title=esc(p["title"]), summary=esc(p["summary"]),
                     status=esc(p.get("status", "")), tools=tools, content=content, access=kpi_access_button(p))
    scripts = ("demo.js",) if "{{demo}}" in p["body"] else ()
    return path, page(path, p["title"], body, "research.html", p["summary"], scripts)


def build_publications():
    sections = []
    for s in PUBS["sections"]:
        if not s["items"]:
            continue
        lis = "".join("<li>{}{}</li>".format(inline(i["text"], ""),
                                             ' <a href="{}" rel="noopener" target="_blank">{}</a>'.format(esc(i["link"]), esc(i.get("link_label", "[link]"))) if i.get("link") else "")
                      for i in s["items"])
        sections.append('<section class="pub-section reveal"><h2>{}</h2><ol class="pubs">{}</ol></section>'.format(esc(s["title"]), lis))
    body = page_head("Publications", "Publications & presentations") + '<div class="wrap section">{}</div>'.format("".join(sections))
    return page("publications.html", "Publications", body, "publications.html")


def build_teaching():
    body = page_head("Teaching & experience", "Teaching",
                     "Helping students connect engineering mechanics, probability, and programming to real problems.") + \
        '<section class="wrap section teaching-list">{}</section>'.format(entries(SITE["teaching"]))
    return page("teaching.html", "Teaching", body, "teaching.html")


def build_skills():
    groups = []
    for g in SITE["skills"]:
        core = "".join("<li>{}</li>".format(esc(x)) for x in g["core"] + g["familiar"])
        groups.append('<article class="card reveal"><h2>{}</h2>'
                      '<ul class="chips">{}</ul></article>'.format(esc(g["group"]), core))
    certificates = "".join(
        '<article class="certificate-cell"><h3>{title}</h3>'
        '<p class="certificate-meta">{display_date} · {issuer}</p><p>{display_detail}</p><a href="files/certificates/{file}" target="_blank" '
        'rel="noopener">View certificate (PDF)<span class="sr-only">: {title}</span></a></article>'.format(
            **{k: esc(v) for k, v in c.items()}) for c in SITE.get("certifications", []))
    body = page_head("Skills & training", "Technical skills & continued learning",
                     "Skills and methods grouped by area.", wide=True) + \
        '<section class="wrap section grid grid-2 skills-grid">{}</section>'.format("".join(groups)) + \
        '<section class="wrap section" id="training"><p class="eyebrow">Continued learning</p>' \
        '<h2 class="section-title">Training &amp; certificates</h2><p class="lede">Completed courses in data engineering, data integration, AI, and research ethics.</p>' \
        '<div class="certificate-grid">{}</div></section>'.format(certificates)
    return page("skills.html", "Skills", body, "skills.html")


def build_cv():
    body = page_head("Curriculum vitae", "CV") + """
<section class="wrap section cv-box">
  <p class="muted">Updated October 16, 2026</p>
  <p>My complete CV covers education, research and teaching experience, Recovery KPI Studio, publications and manuscripts, technical skills, awards, and training.</p>
  <p class="actions"><a class="btn btn-primary" href="{cv}" download>Download CV (PDF)</a>
  <a class="btn" href="{cv}" target="_blank" rel="noopener">Open in browser</a></p>
  <object class="cv-preview" data="{cv}" type="application/pdf" aria-label="Complete CV preview">
    <p>Your browser cannot display the PDF here. <a href="{cv}">Open the complete CV</a>.</p>
  </object>
</section>""".format(cv=SITE["cv_pdf"])
    return page("cv.html", "CV", body, "cv.html")


def build_contact():
    icons = {
        "email": '<svg viewBox="0 0 48 48" aria-hidden="true" focusable="false"><rect x="5" y="10" width="38" height="28" rx="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="m6 12 18 15 18-15" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
        "LinkedIn": '<svg viewBox="0 0 48 48" aria-hidden="true" focusable="false"><rect x="3" y="3" width="42" height="42" rx="5" fill="currentColor"/><text x="24" y="34" text-anchor="middle" fill="var(--surface)" font-family="Arial, sans-serif" font-size="32" font-weight="bold">in</text></svg>',
        "ResearchGate": '<svg viewBox="0 0 48 48" aria-hidden="true" focusable="false"><rect x="3" y="3" width="42" height="42" rx="5" fill="currentColor"/><text x="11" y="35" fill="var(--surface)" font-family="Times New Roman, serif" font-size="32">R</text><text x="30" y="20" fill="var(--surface)" font-family="Times New Roman, serif" font-size="15">G</text></svg>',
    }
    cards = []
    for i, email in enumerate(SITE["emails"]):
        label = "University email" if i == 0 else "Personal email"
        cards.append('<li><a class="contact-card" href="mailto:{email}"><span class="contact-icon">{icon}</span>'
                     '<span class="contact-copy"><span class="contact-title">{label}</span>'
                     '<span class="contact-detail">{email}</span></span></a></li>'.format(
                         email=esc(email), icon=icons["email"], label=label))
    for link in SITE["links"]:
        cards.append('<li><a class="contact-card" href="{url}" target="_blank" rel="noopener">'
                     '<span class="contact-icon">{icon}</span><span class="contact-copy">'
                     '<span class="contact-title">{label}</span><span class="contact-detail">View my profile ↗</span>'
                     '</span></a></li>'.format(url=esc(link["url"]), icon=icons.get(link["label"], icons["email"]), label=esc(link["label"])))
    body = page_head("Contact", "Get in touch",
                     "I welcome conversations about research collaborations and opportunities in disaster resilience, "
                     "data engineering, analytics, and AI.") + """
<section class="wrap section">
  <ul class="contact-grid plain" aria-label="Ways to connect">{cards}</ul>
  <dl class="contact-context"><div><dt>Affiliation</dt><dd>{aff}</dd></div>
  <div><dt>Location</dt><dd>{loc}</dd></div></dl>
</section>""".format(cards="".join(cards), aff=esc(SITE["affiliation"]), loc=esc(SITE["location"]))
    return page("contact.html", "Contact", body, "contact.html")


def build_404():
    body = page_head("404", "Page not found") + '<section class="wrap section"><p><a href="index.html">Return home →</a></p></section>'
    return page("404.html", "Not found", body)


# ------------------------------------------------------------ main
def main():
    # Clear old files but keep folders (Windows/OneDrive can lock directories).
    if OUT.exists():
        for f in OUT.rglob("*"):
            if f.is_file():
                f.unlink()
    (OUT / "projects").mkdir(parents=True, exist_ok=True)
    for folder in ("assets", "files"):
        for src in (ROOT / folder).rglob("*"):
            if src.is_file():
                dst = OUT / src.relative_to(ROOT)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    projects = load_projects()
    pages = {
        "index.html": build_home(projects), "about.html": build_about(), "research.html": build_research(projects),
        "publications.html": build_publications(), "teaching.html": build_teaching(), "skills.html": build_skills(),
        "cv.html": build_cv(), "contact.html": build_contact(), "404.html": build_404(),
    }
    for p in projects:
        path, text = build_project(p)
        pages[path] = text
    for path, text in pages.items():
        (OUT / path).write_text(text, encoding="utf-8")

    base = SITE["site_url"].rstrip("/")
    if base:
        urls = "".join("<url><loc>{}/{}</loc></url>".format(esc(base), p) for p in pages if p != "404.html")
        (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>'
                                         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{}</urlset>'.format(urls), encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n" + ("Sitemap: {}/sitemap.xml\n".format(base) if base else ""), encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print("Built {} pages into {}".format(len(pages), OUT))


if __name__ == "__main__":
    main()
