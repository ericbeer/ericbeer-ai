"""Build ericbeer.ai from guides.json. Run: python3 build.py  (writes the HTML pages in place)."""
import json, html, os

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://ericbeer.ai"
G = json.load(open(os.path.join(ROOT, "guides.json")))
SOCIAL = json.load(open(os.path.join(ROOT, "social.json")))
e = html.escape
import hashlib
CSS_V = hashlib.md5(open(os.path.join(ROOT, "assets", "style.css"), "rb").read()).hexdigest()[:8]

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Lora:wght@600;700&family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">'

TOPICS = {"agents": "AI agents", "getting-started": "Getting started", "prompts": "Prompts"}

CONSENT = ('<label class="consent"><input type="checkbox" name="sms_consent" value="yes"> '
           '<span>Text me too. I agree to receive text messages from Eric Beer about free guides, events and offers. '
           'Message frequency varies. Msg &amp; data rates may apply. Reply STOP to opt out, HELP for help. Not required to get the guide.</span></label>')


def head(title, desc, path, extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/assets/eric-hero.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230F1B2D'/%3E%3Ctext x='32' y='43' font-family='Georgia' font-size='30' font-weight='700' text-anchor='middle' fill='%23C8963E'%3EEB%3C/text%3E%3C/svg%3E">
{FONTS}
<link rel="stylesheet" href="/assets/style.css?v={CSS_V}">
{extra}
</head>"""


def nav(active):
    items = [("/", "Home"), ("/guides/", "Free guides"), ("/contact/", "Contact")]
    lis = "".join(f'<li><a href="{h}"{" aria-current=page" if h == active else ""}>{t}</a></li>' for h, t in items)
    return f'<header class="nav"><div class="wrap"><a class="brand" href="/">Eric Beer<span>.</span></a><nav aria-label="Main"><ul>{lis}</ul></nav></div></header>'


FOOT = f"""<footer><div class="wrap">
<div class="socials">{"".join(f'<a href="{p["url"]}" rel="noopener">{p["name"]}</a>' for p in SOCIAL["profiles"])}<a href="/guides/">Free guides</a><a href="/#waitlist">Waitlist</a></div>
<div>Eric Beer &middot; AI teams for business owners, no tech required</div>
<div style="margin-top:6px">&copy; 2026 Eric Beer &middot; <a href="/privacy/">Privacy</a></div>
</div></footer>
<script src="/assets/site.js" defer></script>"""


def card(g):
    chips = "".join(f'<span class="chip">{TOPICS.get(t, t)}</span>' for t in g["topics"]) + f'<span class="chip tool">{e(g["tool"])}</span>'
    return f"""<article class="card" data-topics="{' '.join(g['topics'])}">
<a class="thumb" href="/guides/{g['slug']}/"><img src="{g['cover']}" alt="Cover of {e(g['short'])}" loading="lazy"></a>
<div class="chips">{chips}</div>
<h3>{e(g['title'])}</h3>
<p>{e(g['blurb'])}</p>
<a class="go" href="/guides/{g['slug']}/">Get the guide &rarr;</a>
</article>"""


def waitlist_form():
    return f"""<form class="form" data-form="waitlist" action="https://services.leadconnectorhq.com/hooks/Xq2iuMgGjsWRjh9q58Ii/webhook-trigger/6aa5f268-4cb9-4a6b-a068-58cd4b644894" method="post">
<input type="hidden" name="type" value="waitlist">
<div><label for="wl-name">First name</label><input id="wl-name" type="text" name="first_name" autocomplete="given-name" required></div>
<div><label for="wl-email">Email</label><input id="wl-email" type="email" name="email" autocomplete="email" required></div>
<button class="btn btn-gold" type="submit">Join the waitlist</button>
<div class="msg" role="status" aria-live="polite"></div>
<p class="note">Founding members get their first month for $47. No spam, unsubscribe anytime.</p>
</form>"""


def lead_form(guide, fid, cta="Send me the guide"):
    return f"""<form class="form" data-form="lead" data-guide="{guide}" action="https://services.leadconnectorhq.com/hooks/Xq2iuMgGjsWRjh9q58Ii/webhook-trigger/6aa5f268-4cb9-4a6b-a068-58cd4b644894" method="post">
<input type="hidden" name="type" value="lead"><input type="hidden" name="guide" value="{guide}">
<div><label for="{fid}-name">First name</label><input id="{fid}-name" type="text" name="first_name" autocomplete="given-name" required></div>
<div><label for="{fid}-email">Email</label><input id="{fid}-email" type="email" name="email" autocomplete="email" required></div>
<div><label for="{fid}-phone">Phone</label><input id="{fid}-phone" type="tel" name="phone" autocomplete="tel" placeholder="(555) 555-5555" required></div>
{CONSENT}
<button class="btn btn-primary" type="submit">{cta}</button>
<div class="msg" role="status" aria-live="polite"></div>
<p class="note">By signing up you'll join my newsletter: one short email a day with what I'm building with AI. Unsubscribe anytime.</p>
</form>"""


CLUB = f"""<section class="block" id="waitlist"><div class="wrap"><div class="club">
<div class="script">launching soon on Skool</div>
<h2>Your AI agent team, handed to you</h2>
<p class="sub" style="color:#C9C2B3">The community where I hand you the AI agents and systems I use to run my business, and show you how to put them to work. Nothing gatekept.</p>
<ul>
<li>Ready-made AI agents you copy into your business</li>
<li>Every guide and system I build, in full detail</li>
<li>Live calls to help you put your agents to work</li>
<li>Business owners doing the same thing, sharing what works</li>
</ul>
<div class="price"><s>$97/month</s> Founding members: <b>$47 first month</b></div>
{waitlist_form()}
</div></div></section>"""


def write(path, content):
    full = os.path.join(ROOT, path.strip("/"), "index.html") if not path.endswith(".html") else os.path.join(ROOT, path.strip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)


def watch_section():
    if not SOCIAL.get("videos"): return ""
    vids = "".join(
        f'<article class="vid"><a class="vthumb" href="{e(next(iter(v["links"].values())))}" rel="noopener" target="_blank">'
        f'<img src="{v["cover"]}" alt="{e(v["title"] or "Video by Eric Beer")}" loading="lazy" width="360" height="640"><span class="play" aria-hidden="true">&#9654;</span></a>'
        f'<h3>{e(v["title"])}</h3><div class="vlinks">'
        + "".join(f'<a href="{e(u)}" rel="noopener" target="_blank">{n}</a>' for n, u in v["links"].items())
        + "</div></article>" for v in SOCIAL["videos"][:int(SOCIAL.get("feed", {}).get("show", 4))])
    follow = "".join(f'<a class="btn btn-ghost" href="{p["url"]}" rel="noopener" target="_blank">{p["name"]} <span class="h">{e(p["handle"])}</span></a>' for p in SOCIAL["profiles"])
    return f"""<section class="block" id="watch"><div class="wrap">
<div class="script">watch &amp; learn</div>
<h2>See how I put AI to work</h2>
<p class="sub">Short videos on how I run my business with an AI team. Watch on whichever app you like.</p>
<div class="vids">{vids}</div>
<div class="follow">{follow}</div>
</div></section>"""


# ---------- home ----------
featured = [g for g in G if g.get("featured")][:3]
home = head("Eric Beer | AI teams for business owners", "Free guides, prompts and AI agent systems for business owners who want results from AI without learning the tech.", "/") + f"""
<body>
{nav('/')}
<main>
<section class="hero"><div class="wrap grid">
<div>
<div class="script">hi, I'm</div>
<h1>Eric <em>Beer</em></h1>
<div class="tag">AI teams for business owners, no tech required</div>
<p class="lead">I help business owners put AI agents to work: more leads, faster follow-up, less busywork. No coding and no 50 tools. Just the exact prompts, systems and agent teams I use to run my own business, broken down so you can copy them.</p>
<div class="cta-row"><a class="btn btn-primary" href="#waitlist">Join the waitlist</a><a class="btn btn-ghost" href="/guides/">Browse free guides</a></div>
<div class="script ps" style="font-size:24px">p.s. the waitlist is open &rarr;</div>
<div class="pills"><span class="pill"><b>20+ yrs</b> in performance marketing</span><span class="pill">founder of <b>BeChosen</b></span><span class="pill">runs his business with an <b>AI team</b></span></div>
</div>
<div><figure class="polaroid"><span class="tape"></span><img src="/assets/eric-hero.jpg" alt="Eric Beer" width="720" height="900"><span class="sticker">AI obsessed</span><figcaption class="cap">building my AI team</figcaption></figure></div>
</div></section>
<hr class="divider">
{CLUB}
<hr class="divider">
<section class="block"><div class="wrap">
<div class="script">most loved</div>
<h2>Start with these free guides</h2>
<p class="sub">The exact prompts and setups I use. All free, all copy-paste.</p>
<div class="cards">{''.join(card(g) for g in featured)}<div class="card soon"><div class="script">more coming every week</div><p>Comment the keyword on any reel and I'll DM you the guide.</p></div></div>
<p style="margin-top:28px"><a class="btn btn-ghost" href="/guides/">See all free guides</a></p>
</div></section>
<hr class="divider">
{watch_section()}
<hr class="divider">
<section class="block about"><div class="wrap grid">
<figure class="polaroid"><span class="tape"></span><img src="/assets/eric-about.jpg" alt="Eric Beer" loading="lazy" width="720" height="900"><figcaption class="cap">hi again</figcaption></figure>
<div>
<div class="script">about me</div>
<h2>A marketer who handed his busywork to AI</h2>
<p>I've spent 20+ years in performance marketing and lead generation, and I'm the founder of BeChosen. I'm not a developer. I got tired of learning tool after tool, so I built an AI team that runs parts of my business: a manager for each outcome, agents that each do one job, and decisions that come straight to me.</p>
<p>Here I share exactly how I do it, so you can do it too.</p>
<a class="btn btn-ghost" href="/contact/">Get in touch</a>
</div>
</div></section>
</main>
{FOOT}
</body></html>"""
write("/", home)

# ---------- library ----------
filters = '<button type="button" data-filter="all" aria-pressed="true">All</button>' + "".join(
    f'<button type="button" data-filter="{k}" aria-pressed="false">{v}</button>' for k, v in TOPICS.items())
lib = head("Free AI guides | Eric Beer", "Every free AI guide, prompt pack and agent setup Eric Beer has shared, in one place.", "/guides/") + f"""
<body>
{nav('/guides/')}
<main><section class="block"><div class="wrap">
<div class="script">the whole library</div>
<h2>Free guides</h2>
<p class="sub">Every prompt pack, agent setup and cheat sheet I've shared, in one place. All free, all copy-paste.</p>
<p class="script" style="font-size:22px">looking for a specific guide? comment the keyword under the reel on @ericbeerofficial and I'll DM it</p>
<div class="filters" role="toolbar" aria-label="Filter guides">{filters}</div>
<p class="note">Showing {len(G)} guides</p>
<div class="cards">{''.join(card(g) for g in G)}</div>
</div></section>
<hr class="divider">
{CLUB}
</main>
{FOOT}
</body></html>"""
write("/guides/", lib)

# ---------- guide pages ----------
# Public page = teaser + sign-up. The free part lives on a private page that is only sent by email
# (or in a DM to someone ManyChat already captured). The locked part is never in any page's HTML.
SKOOL_URL = os.environ.get("EB_SKOOL_URL", "/#waitlist")
SKOOL_LIVE = SKOOL_URL.startswith("http")
SKOOL_CTA = "Start my 7-day free trial" if SKOOL_LIVE else "Join the waitlist"


def content(slug):
    return json.load(open(os.path.join(ROOT, "content", f"{slug}.json")))


def full_access_card(g):
    line = ("Get the full guide, every other guide, the AI agents I use and live calls inside my community. "
            "Free for 7 days, then $97/month. Cancel anytime." if SKOOL_LIVE else
            "The full guide, every other guide, the AI agents I use and live calls are going inside my community. "
            "Join the waitlist for the founding-member price.")
    return f"""<div class="full-card"><h2>Want the complete guide?</h2><p>{line}</p>
<a class="btn btn-gold" href="{SKOOL_URL}">{SKOOL_CTA} &rarr;</a></div>"""


def unlock_block(g, c):
    locked = "".join(f"<li>{e(x)}</li>" for x in c["locked"])
    bars = "".join('<span class="bar" style="width:%d%%"></span>' % w for w in (96, 88, 92, 70, 95, 84, 60, 90, 78))
    price = ('7 days free, then <b>$97/month</b>. Cancel anytime.' if SKOOL_LIVE else
             'Founding members: <b>$47 first month</b>, then $97/month.')
    return f"""<section class="locked"><div class="fade" aria-hidden="true">{bars}</div>
<div class="lockbox">
<div class="script">the rest of this guide is inside the community</div>
<h2>Unlock the full guide</h2>
<ul class="lock-list">{locked}</ul>
<p>Get this guide in full, every other guide, the AI agents I use, and live calls, inside my community.</p>
<div class="price">{price}</div>
<a class="btn btn-gold" href="{SKOOL_URL}">{SKOOL_CTA}</a>
</div></section>"""


for g in G:
    c = content(g["slug"])
    inside = "".join(f"<li>{e(s['title'])}</li>" for s in c["free"]) + "".join(f'<li class="lk">{e(x)}</li>' for x in c["locked"])
    page = head(f"{g['short']} | free guide by Eric Beer", g["blurb"], f"/guides/{g['slug']}/") + f"""
<body data-guide="{g['slug']}" data-keyword="{g.get('keyword','').lower()}">
{nav('/guides/')}
<main>
<section class="guide-hero"><div class="wrap grid">
<div>
<div class="script">free guide</div>
<h1>{e(g['title'])}</h1>
<p class="lead">{e(g['blurb'])}</p>
<div class="inside"><h2>What's inside</h2><ol>{inside}</ol><p class="note" style="text-align:left;margin-top:10px">The first {len(c['free'])} parts are free. The rest is inside the community.</p></div>
</div>
<div>
<div class="panel lock-only" id="get">
<h3 style="text-align:center">Get the free guide</h3>
<p class="note" style="margin:0 0 14px">Tell me where to send it and you'll get it right here.</p>
{lead_form(g['slug'], 'g')}
</div>
<div class="unlocked unlock-box">
<h3>You're in<span data-first-name></span>.</h3>
<p>Here's your free guide. Bookmark it so you can come back to it.</p>
<p><a class="btn btn-gold" href="/g/{g['slug']}-{c['key']}/">Open the guide &rarr;</a></p>
<p style="font-size:14px;color:#C9C2B3;margin:14px 0 0">You're also on my short daily email with what I'm building with AI. Unsubscribe anytime.</p>
</div>
<figure class="cover" style="margin:28px 0 0"><img src="{g['cover']}" alt="Cover of {e(g['short'])}"></figure>
</div>
</div></section>
<hr class="divider">
<section class="block"><div class="wrap">
<div class="script">keep going</div>
<h2>More free guides</h2>
<div class="cards">{''.join(card(x) for x in G if x['slug'] != g['slug'])}<div class="card soon"><div class="script">new guides every week</div><p><a href="/guides/">See the library</a></p></div></div>
</div></section>
</main>
{FOOT}
</body></html>"""
    write(f"/guides/{g['slug']}/", page)

    free = "".join(f'<section class="gsec"><div class="gnum">{i + 1}</div><h2>{e(s["title"])}</h2>{s["body"]}</section>' for i, s in enumerate(c["free"]))
    private = head(f"{g['short']} | Eric Beer", g["blurb"], f"/g/{g['slug']}-{c['key']}/", '<meta name="robots" content="noindex, nofollow">') + f"""
<body class="reading">
{nav('/guides/')}
<main><article class="guide-read wrap">
{full_access_card(g)}
<div class="script">your free guide</div>
<h1>{e(g['title'])}</h1>
<div class="gintro">{c['intro']}</div>
{free}
{unlock_block(g, c)}
</article>
<hr class="divider">
<section class="block"><div class="wrap">
<div class="script">keep going</div>
<h2>More free guides</h2>
<div class="cards">{''.join(card(x) for x in G if x['slug'] != g['slug'])}<div class="card soon"><div class="script">new guides every week</div><p><a href="/guides/">See the library</a></p></div></div>
<p style="margin-top:24px"><a class="btn btn-primary" href="/">Explore ericbeer.ai</a> <a class="btn btn-ghost" href="/#waitlist">Join the waitlist</a></p>
</div></section>
{watch_section()}
</main>
{FOOT}
</body></html>"""
    write(f"/g/{g['slug']}-{c['key']}/", private)

# ---------- contact ----------
contact = head("Contact | Eric Beer", "Partnerships, speaking and collaborations with Eric Beer.", "/contact/") + f"""
<body>
{nav('/contact/')}
<main><section class="block contact"><div class="wrap">
<div class="script">say hello</div>
<h2>Let's talk</h2>
<p class="sub">Partnerships, speaking, podcasts and collaborations. Every message comes to me.</p>
<div class="grid">
<div class="panel"><h3>I'd love to hear about</h3><p>Partnerships and joint ventures, podcast and stage invites, and anything that helps more business owners actually use AI.</p><p><a class="btn btn-ghost" href="/guides/">Browse free guides</a></p></div>
<div class="panel">
<form class="form" data-form="contact" action="https://services.leadconnectorhq.com/hooks/Xq2iuMgGjsWRjh9q58Ii/webhook-trigger/6aa5f268-4cb9-4a6b-a068-58cd4b644894" method="post">
<input type="hidden" name="type" value="contact">
<div><label for="c-name">First name</label><input id="c-name" type="text" name="first_name" required></div>
<div><label for="c-email">Email</label><input id="c-email" type="email" name="email" required></div>
<div><label for="c-msg">What's on your mind?</label><input id="c-msg" type="text" name="message" required></div>
<button class="btn btn-primary" type="submit">Send</button>
<div class="msg" role="status" aria-live="polite"></div>
</form>
</div>
</div>
</div></section></main>
{FOOT}
</body></html>"""
write("/contact/", contact)

# ---------- privacy ----------
privacy = head("Privacy | Eric Beer", "How Eric Beer handles your information.", "/privacy/") + f"""
<body>
{nav('')}
<main><section class="block"><div class="wrap" style="max-width:720px;text-align:left">
<h2>Privacy</h2>
<p>When you sign up for a guide, the waitlist or my emails, I collect the name, email and phone number you give me, plus which guide you asked for. I use it to send you what you asked for, my daily email, and occasional offers. You can unsubscribe from email at any time with the link in every email, and stop texts by replying STOP.</p>
<p>I store your information in my CRM (GoHighLevel). I don't sell your information. This site doesn't use advertising trackers; it remembers on your own device that you've signed up, so you don't have to fill the form twice.</p>
<p>To have your information removed, use the <a href="/contact/">contact form</a>.</p>
</div></section></main>
{FOOT}
</body></html>"""
write("/privacy/", privacy)

# ---------- 404, CNAME, robots, sitemap ----------
write("/404.html", head("Not found | Eric Beer", "Page not found.", "/404") + f"<body>{nav('')}<main><section class='block'><div class='wrap'><div class='script'>oops</div><h2>That page wandered off</h2><p class='sub'>Try the free guides instead.</p><a class='btn btn-primary' href='/guides/'>Browse free guides</a></div></section></main>{FOOT}</body></html>")
# CNAME is written once ericbeer.ai DNS points at GitHub Pages
if os.environ.get("EB_DOMAIN"): open(os.path.join(ROOT, "CNAME"), "w").write("ericbeer.ai\n")
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
urls = ["/", "/guides/", "/contact/", "/privacy/"] + [f"/guides/{g['slug']}/" for g in G]
open(os.path.join(ROOT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{SITE}{u}</loc></url>" for u in urls) + "</urlset>\n")
print("built", len(urls), "pages")
