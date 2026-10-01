// EricBeer.ai: lead capture to GoHighLevel (inbound webhook), guide unlock, library filters.
(function () {
  var WEBHOOK = "__WEBHOOK__"; // GoHighLevel inbound webhook URL, set at deploy
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
    payload.submitted_at = new Date().toISOString();
    if (WEBHOOK.indexOf("http") !== 0) return Promise.reject(new Error("not-configured"));
    return fetch(WEBHOOK, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })
      .catch(function () {
        // Fallback when the endpoint does not allow cross-site JSON: a simple form post GoHighLevel still parses.
        var body = new URLSearchParams(); Object.keys(payload).forEach(function (k) { body.append(k, payload[k]); });
        return fetch(WEBHOOK, { method: "POST", mode: "no-cors", body: body });
      });
  }
  function validEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v); }
  function validPhone(v) { return v.replace(/\D/g, "").length >= 10; }

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
      if (!d.first_name) err = "Please add your first name.";
      else if (!validEmail(d.email || "")) err = "That email doesn't look right. Mind checking it?";
      else if (form.dataset.form === "lead" && !validPhone(d.phone || "")) err = "Please add a phone number with area code.";
      if (err) { msg.className = "msg err"; msg.textContent = err; return; }
      d.type = form.dataset.form; d.guide = form.dataset.guide || ""; d.sms_consent = d.sms_consent ? "yes" : "no";
      btn.disabled = true; var label = btn.textContent; btn.textContent = "One sec...";
      send(d).then(function () {
        store(false, { first_name: d.first_name, email: d.email, phone: d.phone || (known && known.phone) || "" });
        msg.className = "msg ok";
        msg.textContent = form.dataset.form === "waitlist" ? "You're on the list, " + d.first_name + ". Watch your inbox for your founding-member price." : "You're in. Your guide is below, and a copy is on its way to your inbox.";
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

  // Library filters
  var bar = document.querySelector(".filters");
  if (bar) bar.addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    bar.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
    var f = b.dataset.filter;
    document.querySelectorAll(".cards .card[data-topics]").forEach(function (c) { c.style.display = f === "all" || c.dataset.topics.indexOf(f) > -1 ? "" : "none"; });
  });
})();
