# Verification: YouTube auto-refresh for "Watch & learn" + private-page footer

Reviewer: fresh reviewer, told to assume it is broken. Reviewed 2026-10-08 at commit ca7a967 (main == origin/main).
All runs were in a scratch copy; nothing was pushed, committed or changed live.

## Working means

- Every 6 hours (and on demand) the job reads the YouTube feed for `feed.youtube_channel_id`, adds each video published on/after `feed.since` exactly once (matched by YouTube id, whatever the link form), saves a 360x640 cover, sorts newest first, rebuilds, and commits/pushes only when something changed.
- The home page and every private guide page show the newest `feed.show` (4) videos with a readable title and alt text.
- A bad feed, a bad cover or a missing config never breaks the site and never wedges the job.
- A bot rebuild produces exactly what a local rebuild would (no setting silently reverts).
- Private guide pages end with "More free guides", "Explore ericbeer.ai" and the watch section, and still never contain the locked content.

## Consumers

- Visitors to ericbeer.ai (home `#watch`, and every `/g/<slug>-<key>/` private page).
- Eric / BOSS publishing locally from `~/Sites/ericbeer-ai` (must coexist with bot commits on `main`).
- GitHub Pages legacy build from `main` (`/`), CNAME ericbeer.ai.

## Ran the real thing

- `python3 scripts/update_videos.py` against the live feed, twice: `0 new video(s); showing newest 4 of 5`, no diff either time (idempotent, no format churn in social.json).
- `python3 build.py` on a clean copy: `built 9 pages`, zero diff vs committed HTML (deterministic, no env-dependent drift with the default env).
- Live workflow run 37790327492 (workflow_dispatch, 2026-10-08 14:10Z): success, "0 new video(s)", "No new videos." The commit/push and the Pages POST path have NOT been exercised in production yet (no new video since it shipped).
- Pages config (read-only API): legacy build, `main` `/`, cname ericbeer.ai, https enforced, status built. Repo is PUBLIC. Default workflow token permission is read; the workflow's explicit `contents: write`, `pages: write` overrides that.
- Live private page https://ericbeer.ai/g/your-ai-team-9aea95b89c/ contains the watch section and "Explore ericbeer.ai".
- Existing bot cover `assets/videos/yt-ZMu9OGjeAb4.jpg` is 360x640.

## Break attempts (observed results)

Harness: real `update_videos.py` run with `urllib.request.urlopen` stubbed to serve a crafted feed and crafted cover bytes, Pillow 11.3 in a venv (as in CI).

1. **Hashtag-only title** (`#ai #claude #shorts`): added with `title: ""`. Home page renders `<h3></h3>` and `alt=""` on the only content of the link, so the card has no visible title and the link has no accessible name. BROKEN.
2. **Leading "#1" in a title** (`#1 Rule In Biz: learn C# fast`): becomes `Rule In Biz: learn C# fast`. Meaning lost. The real channel feed already has a video titled "#1 Rule In Biz When You Buy Traffic" (currently before `since`, so not shown). BROKEN.
3. **Entities / emoji / markup in title** (`Tom &amp; Jerry 🚀 &lt;script&gt;... &#39;quoted&#39;`): stored as `Tom & Jerry 🚀 <script>alert(1)</script> 'quoted'`, rendered escaped (`&lt;script&gt;`), emoji intact, no script in the page. OK.
4. **Existing video re-appears in the feed** (wYr0itobRaY, already in social.json): not duplicated, hand-edited title and TikTok/Instagram links kept. `yt_id` regex also matches `youtu.be/ID` and `watch?v=ID` (read and confirmed); `/embed/` and `/live/` forms would NOT match and would duplicate. OK for current data.
5. **Long-form (16:9) video**: cover produced at 360x640 by center-cropping the 16:9 frame (keeps about a third of the picture); link is written as `youtube.com/shorts/<id>`. Works, looks poor. Nice-to-have.
6. **Cover download fails (404 on all three sizes)**: video skipped, nothing else changed, retried on the next run. OK.
7. **Cover URL returns non-image bytes**: `PIL.UnidentifiedImageError` traceback, script exits non-zero, nothing written. Because the same video is retried every run, the job would fail every 6 hours and no other new video would ever be added until someone intervenes. BROKEN.
8. **Run locally without Pillow** (Eric's Mac has no Pillow; the docstring tells people to run it locally): the raw YouTube image is written as the cover with no resize/compress, and since the file then exists it is never reprocessed. Nice-to-have.
9. **social.json without `feed`**: prints "nothing to do", exits 0; build still shows newest 4 (default). OK.
10. **Bot commit retriggering the job**: workflow triggers are only `schedule` and `workflow_dispatch`; a push cannot start it. No loop. OK.
11. **Pages build request permission**: `pages: write` is declared; the POST is guarded with `|| echo`, so a failure cannot fail the job. OK (not yet exercised live).
12. **Two runs at once**: `concurrency: update-videos`, `cancel-in-progress: false` queues the second; it checks out after the first pushed. OK. If Eric pushes between the bot's checkout and push (~15s window), the bot push fails non-fast-forward, job goes red once, next run recovers. Acceptable.
13. **Bot rebuild vs build-time settings**: `build.py` reads `EB_SKOOL_URL` from the environment. Built with `EB_SKOOL_URL=https://www.skool.com/x`: private page has 2 Skool links. Rebuilt with the default env (what the bot does): 0 Skool links, back to "Join the waitlist". BROKEN once the community goes live (see Must-fix 4).
14. **Private page leaking locked content**: private pages contain only the locked section titles (by design) and link only to public `/guides/<slug>/` pages, never to another `/g/<key>/`. Public PDFs (`AI-System-Starter-Kit.pdf`, `Your-AI-Team-Guide.pdf`, 2-3 pages) do not contain the locked steps. No locked body anywhere in the repo. OK.

## Two-weeks-later audit findings

- **Local publishing will collide with the bot.** Every bot commit puts `main` on GitHub ahead of Eric's local folder. His next local `git push` is rejected, and a plain pull conflicts on generated files (`index.html`, every `g/*/index.html`, `social.json`) if he rebuilt locally. Nothing in the README says to pull first.
- **The Skool launch will be silently undone** by the next new video (break attempt 13).
- **Same-day ordering is wrong**: only the date is stored, so two videos on the same day keep append order; in the test a 23:00 upload sorted below a 02:00 one.
- **`exclude` only stops additions.** Adding an id to `exclude` after the bot added it does not remove it; a video deleted or made private on YouTube stays on the site linking to a dead page.
- **Public repo, scheduled job**: GitHub disables schedules in public repos after 60 days with no repo activity. Quiet stretches with no videos and no edits would switch it off without notice.
- **Pre-existing, not from this change (needs Eric's call):** the repo is public, so every private key (`content/*.json` `key`, `g/` folder names) and the email-gated free sections are readable on GitHub without signing up; the public guide pages also carry the `/g/<key>/` link in their HTML (hidden by CSS until signup). `content/five-minute-follow-up.json` (LEADS, "held off the live site until Eric approves") is publicly readable in the repo. The ORG guide commit says "not pushed until Eric approves" but `/guides/ai-org-chart/` is live (HTTP 200) and on the home page; confirm Eric approved it.

## Must-fix (file:line + fix)

1. `scripts/update_videos.py:26` and `:88` (empty title). If `clean_title()` returns empty, fall back to the raw title with only the `#` characters removed (`re.sub(r"#", "", raw).strip()`), and if that is still empty skip the video and print it. Also in `build.py:117` use a fallback alt (`"Video by Eric Beer"`) when the title is empty.
2. `scripts/update_videos.py:26` (strips "#1"). Only strip real hashtags that start with a letter: `re.sub(r"(?<!\w)#[^\W\d_]\w*", "", t)`. Keeps "#1", "C#".
3. `scripts/update_videos.py:43-53` (non-image bytes crash the whole run, every run). Wrap the Pillow block in `except Exception:` (keep ImportError handling separate), delete any partial file, `return None` so the video is skipped and retried, and let the rest of the run finish.
4. `build.py:202` + `.github/workflows/update-videos.yml:24-26` (bot rebuild reverts the Skool URL). Move the Skool URL into a committed file the build reads (e.g. a `site` key in `social.json`, or `site.json`), or at minimum add `env: EB_SKOOL_URL: ${{ vars.EB_SKOOL_URL }}` to the build step and set the repo variable at launch. A setting that only exists in one shell's environment must not decide what the live pages say.
5. `README.md` + Eric's local publish step (collision with bot commits, `.github/workflows/update-videos.yml:36`). Publish must start with `git pull --rebase origin main`, then `python3 build.py`, then commit and push. Add that line to the README and to whatever BOSS uses to publish this site.

## Nice-to-have

- Store the full `published` timestamp (`[:19]`) so same-day videos sort correctly.
- Remove entries whose id is in `exclude`, and optionally drop entries no longer reachable on YouTube.
- Link as `https://www.youtube.com/watch?v=<id>` (or `youtu.be/<id>`) for non-Shorts, or skip non-vertical covers; letterbox instead of center-cropping 16:9 covers.
- When Pillow is missing, skip saving instead of writing the raw full-size image (CI will add it with Pillow).
- Guard the `re.search(...).group(1)` calls (`update_videos.py:66-68`) so one malformed entry is skipped instead of crashing.
- Accept `/embed/` and `/live/` forms in `yt_id`.
- Add a monthly keepalive (or check `gh run list` in the weekly site check) so the schedule is never auto-disabled.

Status: NOT DONE
