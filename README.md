# ericbeer.ai

Static site for Eric Beer: home, free guide library, guide pages, waitlist, contact.

- Add a guide: drop the PDF and a cover PNG in `assets/guides/`, add an entry to `guides.json`, run `python3 build.py`, commit, push.
- Publishing from a computer: always `git pull --rebase origin main` first. A GitHub job (`.github/workflows/update-videos.yml`) commits new videos every 6 hours, so the copy on your computer can be behind.
- Videos: `scripts/update_videos.py` reads the YouTube feed set in `social.json` -> `feed` and adds each new Short once. Add the Instagram/TikTok links to that video's entry in `social.json` so all three show on one card.
- Forms post to the GoHighLevel inbound webhook set in `assets/site.js` (`WEBHOOK`) and in each form's `action` (build writes `__WEBHOOK__`; deploy replaces it).
- Hosted on GitHub Pages at ericbeer.ai (`CNAME`).
