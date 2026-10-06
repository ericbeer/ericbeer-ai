// EricBeer.ai: lead capture to GoHighLevel (inbound webhook), guide unlock, library filters.
(function () {
  var WEBHOOK = "https://services.leadconnectorhq.com/hooks/Xq2iuMgGjsWRjh9q58Ii/webhook-trigger/6aa5f268-4cb9-4a6b-a068-58cd4b644894"; // GoHighLevel inbound webhook URL, set at deploy
  var KEY = "eb_lead_v1";

  function store(get, val) {
    try { if (get) return JSON.parse(localStorage.getItem(KEY) || "null"); localStorage.setItem(KEY, JSON.stringify(val)); }
    catch (e) { return null; }
  }
  function params() {
    var p = {}; try { new URLSearchParams(location.search).forEach(function (v, k) { p[k] = v; }); } catch (e) {}
    return p;
  }
  function send(payload) {
    var q = params();
    payload.source = payload.source || q.src || q.utm_source || "ericbeer.ai";
    payload.keyword = payload.keyword || q.kw || "";
    payload.page = location.pathname;
    payload.account = "site";
    payload.last_name = payload.last_name || "";
    payload.instagram_username = "";
    if (!payload.keyword && document.body.dataset.keyword) payload.keyword = document.body.dataset.keyword;
    var tg = ["src-ericbeer-ai"];
    if (payload.type === "waitlist") tg.push("skool-waitlist");
    if (payload.type === "contact") tg.push("contact-form");
    if (payload.guide) tg.push("lm-" + payload.guide);
    if (payload.keyword) tg.push("kw-" + String(payload.keyword).toLowerCase());
    if (payload.type === "lead" || payload.type === "waitlist") tg.push("daily-list");
    payload.tags = tg.join(", ");
    payload.submitted_at = new Date().toISOString();
    if (WEBHOOK.indexOf("http") !== 0) return Promise.reject(new Error("not-configured"));
    return fetch(WEBHOOK, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })
      .catch(function () {
        // Fallback when the endpoint does not allow cross-site JSON: a simple form post GoHighLevel still parses.
        var body = new URLSearchParams(); Object.keys(payload).forEach(function (k) { body.append(k, payload[k]); });
        return fetch(WEBHOOK, { method: "POST", mode: "no-cors", body: body });
      });
  }
  var JUNK = /@(mailinator|guerrillamail|10minutemail|tempmail|temp-mail|yopmail|trashmail|sharklasers|getnada|dispostable|throwawaymail|fakeinbox|maildrop)\./i;
  var TYPO = { "gmial.com": "gmail.com", "gmai.com": "gmail.com", "gmail.co": "gmail.com", "gamil.com": "gmail.com", "hotmial.com": "hotmail.com", "yaho.com": "yahoo.com", "outlok.com": "outlook.com", "icloud.co": "icloud.com" };
  function validEmail(v) { return /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(v) && !JUNK.test(v) && !/^(test|fake|asdf|none|no)@/i.test(v); }
  function emailTypo(v) { var d = (v.split("@")[1] || "").toLowerCase(); return TYPO[d] ? v.split("@")[0] + "@" + TYPO[d] : ""; }
  function validPhone(v) { var d = v.replace(/\D/g, ""); if (d.length === 11 && d[0] === "1") d = d.slice(1); return d.length >= 10 && d.length <= 15 && !/^(\d)\1+$/.test(d) && !/^(1234567890|0123456789)$/.test(d) && !/^\d{3}555\d{4}$/.test(d); }

  function unlock(guide) {
    document.querySelectorAll(".unlocked").forEach(function (el) { el.classList.add("show"); });
    document.querySelectorAll(".lock-only").forEach(function (el) { el.style.display = "none"; });
    var lead = store(true);
    document.querySelectorAll("[data-first-name]").forEach(function (el) { if (lead && lead.first_name) el.textContent = ", " + lead.first_name; });
  }

  // Forms: data-form="lead" (guide sign-up) or "waitlist"
  document.querySelectorAll("form[data-form]").forEach(function (form) {
    var known = store(true);
    if (known) {
      ["first_name", "email", "phone"].forEach(function (f) { var i = form.querySelector('[name="' + f + '"]'); if (i && !i.value) i.value = known[f] || ""; });
    }
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var msg = form.querySelector(".msg"), btn = form.querySelector("button[type=submit]");
      var d = {}; new FormData(form).forEach(function (v, k) { d[k] = String(v).trim(); });
      var err = "";
      var typo = emailTypo(d.email || "");
      if (!d.first_name || !/[a-z]/i.test(d.first_name)) err = "Please add your first name.";
      else if (typo) err = "Did you mean " + typo + "?";
      else if (!validEmail(d.email || "")) err = "Please use a real email you check. Your guide link goes there.";
      else if (form.dataset.form === "lead" && !validPhone(d.phone || "")) err = "Please add a phone number with area code.";
      if (err) { msg.className = "msg err"; msg.textContent = err; return; }
      d.type = form.dataset.form; d.guide = form.dataset.guide || ""; d.sms_consent = d.sms_consent ? "yes" : "no";
      btn.disabled = true; var label = btn.textContent; btn.textContent = "One sec...";
      send(d).then(function () {
        store(false, { first_name: d.first_name, email: d.email, phone: d.phone || (known && known.phone) || "" });
        msg.className = "msg ok";
        msg.textContent = form.dataset.form === "waitlist" ? "You're on the list, " + d.first_name + ". Watch your inbox for your founding-member price." : "Done. Your guide is ready below.";
        if (form.dataset.form === "lead") { unlock(d.guide); var m = form.closest(".modal"); if (m) { m.classList.remove("open"); var tgt = document.querySelector(form.dataset.next || ""); if (tgt) location.href = tgt.getAttribute("href"); } }
      }).catch(function () {
        msg.className = "msg err"; msg.textContent = "Something went wrong on our side. Please try again in a minute.";
      }).then(function () { btn.disabled = false; btn.textContent = label; });
    });
  });

  // Guide pages: already signed up on this device? Unlock and log the guide to their contact.
  var gp = document.body.dataset.guide;
  if (gp) {
    var lead = store(true);
    if (lead && lead.email) { unlock(gp); send({ type: "guide_access", guide: gp, first_name: lead.first_name, email: lead.email, phone: lead.phone || "" }).catch(function () {}); }
  }

  // Modal open/close
  document.querySelectorAll("[data-open]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      var lead = store(true), m = document.querySelector(b.dataset.open);
      if (b.dataset.gate === "soft" && lead && lead.email) return; // known: follow the link
      if (m) { e.preventDefault(); m.classList.add("open"); var f = m.querySelector("input"); if (f) f.focus(); }
    });
  });
  document.querySelectorAll(".modal").forEach(function (m) {
    m.addEventListener("click", function (e) { if (e.target === m || e.target.classList.contains("x")) m.classList.remove("open"); });
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") document.querySelectorAll(".modal.open").forEach(function (m) { m.classList.remove("open"); }); });

  // "Send it again": show the form again
  document.querySelectorAll("[data-reset]").forEach(function (a) {
    a.addEventListener("click", function () {
      document.querySelectorAll(".unlocked").forEach(function (el) { el.classList.remove("show"); });
      document.querySelectorAll(".lock-only").forEach(function (el) { el.style.display = ""; });
    });
  });

  // Copy buttons on every prompt in a guide
  document.querySelectorAll(".guide-read .prompt").forEach(function (box) {
    var b = document.createElement("button"); b.type = "button"; b.className = "copy"; b.textContent = "Copy";
    b.addEventListener("click", function () {
      var clone = box.cloneNode(true); clone.querySelectorAll(".tag,.copy").forEach(function (x) { x.remove(); });
      var text = clone.innerText.trim();
      (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(function () {
        b.textContent = "Copied"; b.classList.add("done"); setTimeout(function () { b.textContent = "Copy"; b.classList.remove("done"); }, 1800);
      }).catch(function () { b.textContent = "Select and copy"; });
    });
    box.appendChild(b);
  });

  // Library filters
  var bar = document.querySelector(".filters");
  if (bar) bar.addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    bar.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
    var f = b.dataset.filter;
    document.querySelectorAll(".cards .card[data-topics]").forEach(function (c) { c.style.display = f === "all" || c.dataset.topics.indexOf(f) > -1 ? "" : "none"; });
  });
})();
