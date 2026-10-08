"""Keep the 'Watch & learn' section fresh: read the YouTube channel feed, add each new video to social.json once,
newest first. Instagram/TikTok links for a video live on the same entry, so a video posted everywhere shows once.
Run: python3 scripts/update_videos.py   (then python3 build.py). Exits 0 and changes nothing if the feed is unreachable."""
import json, os, re, sys, urllib.request, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOCIAL = os.path.join(ROOT, "social.json")
VID_DIR = os.path.join(ROOT, "assets", "videos")

data = json.load(open(SOCIAL))
feed = data.get("feed", {})
CHANNEL = feed.get("youtube_channel_id")
SINCE = feed.get("since", "2000-01-01")
EXCLUDE = set(feed.get("exclude", []))
SHOW = int(feed.get("show", 4))


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 ericbeer.ai video updater"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def clean_title(t):
    t = html.unescape(t)
    t = re.sub(r"#\w+", "", t)            # hashtags
    t = re.sub(r"\s+", " ", t).strip(" :-|")
    return t


def save_cover(vid, slug):
    path = os.path.join(VID_DIR, f"{slug}.jpg")
    if os.path.exists(path):
        return f"/assets/videos/{slug}.jpg"
    raw = None
    for name in ("oardefault", "maxresdefault", "hqdefault"):   # oardefault = original vertical frame for Shorts
        try:
            raw = get(f"https://i.ytimg.com/vi/{vid}/{name}.jpg"); break
        except Exception:
            continue
    if raw is None:
        return None
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        tw, th = 360, 640                       # 9:16, same as the hand-made covers
        s = max(tw / im.width, th / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x, y = (im.width - tw) // 2, (im.height - th) // 2
        im.crop((x, y, x + tw, y + th)).save(path, quality=82, optimize=True)
    except ImportError:
        open(path, "wb").write(raw)
    return f"/assets/videos/{slug}.jpg"


def main():
    if not CHANNEL:
        print("no feed.youtube_channel_id in social.json; nothing to do"); return 0
    try:
        xml = get(f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL}").decode("utf-8", "replace")
    except Exception as ex:
        print(f"feed unreachable ({ex}); leaving the site as it is"); return 0
    entries = []
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        vid = re.search(r"<yt:videoId>(.*?)</yt:videoId>", e).group(1)
        pub = re.search(r"<published>(.*?)</published>", e).group(1)[:10]
        title = clean_title(re.search(r"<title>(.*?)</title>", e).group(1))
        if pub >= SINCE and vid not in EXCLUDE:
            entries.append((pub, vid, title))
    if not entries:
        print("feed had no videos in range; leaving the site as it is"); return 0

    videos = data.setdefault("videos", [])
    def yt_id(v):
        m = re.search(r"(?:shorts/|v=|youtu\.be/)([\w-]{11})", v.get("links", {}).get("YouTube", ""))
        return m.group(1) if m else None
    known = {yt_id(v): v for v in videos if yt_id(v)}
    added = 0
    for pub, vid, title in entries:
        if vid in known:
            known[vid].setdefault("published", pub)
            continue
        slug = "yt-" + vid
        cover = save_cover(vid, slug)
        if not cover:
            continue
        videos.append({"title": title, "cover": cover, "published": pub,
                       "links": {"YouTube": f"https://www.youtube.com/shorts/{vid}"}})
        added += 1
    videos.sort(key=lambda v: v.get("published", "0000"), reverse=True)
    json.dump(data, open(SOCIAL, "w"), indent=2, ensure_ascii=False)
    print(f"{added} new video(s); showing newest {SHOW} of {len(videos)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
