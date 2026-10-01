# ericbeer.ai

Static site for Eric Beer: home, free guide library, guide pages, waitlist, contact.

- Add a guide: drop the PDF and a cover PNG in `assets/guides/`, add an entry to `guides.json`, run `python3 build.py`, commit, push.
- Forms post to the GoHighLevel inbound webhook set in `assets/site.js` (`WEBHOOK`) and in each form's `action` (build writes `__WEBHOOK__`; deploy replaces it).
- Hosted on GitHub Pages at ericbeer.ai (`CNAME`).
