// Renders the page from config.js. You shouldn't need to edit this file.
(function () {
  "use strict";
  var c = window.CREATOR_CONFIG || {};
  var $ = function (id) { return document.getElementById(id); };

  // Only allow safe link schemes so a typo in config can't inject script.
  function safeUrl(url, allowMailto) {
    if (typeof url !== "string" || !url.trim()) return "";
    try {
      var u = new URL(url.trim(), window.location.href);
      if (u.protocol === "https:" || u.protocol === "http:") return u.href;
      if (allowMailto && u.protocol === "mailto:") return u.href;
    } catch (e) { /* invalid */ }
    return "";
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }

  function linkCard(title, sub, url) {
    var a = el("a", "card");
    a.href = url;
    a.target = "_blank";
    a.rel = "noopener sponsored";
    var body = el("span", "card-body");
    body.appendChild(el("strong", "", title));
    if (sub) body.appendChild(el("span", "card-sub", sub));
    a.appendChild(body);
    a.appendChild(el("span", "arrow", T.arrow));
    return a;
  }

  function show(id) { $(id).hidden = false; }

  // Interface language: "he" (Hebrew, right-to-left) or "en".
  var STRINGS = {
    en: {
      subscribe: "Subscribe on YouTube", latest: "Latest videos", support: "Support the channel",
      shop: "Shop", gear: "Gear I use", list: "Join the list", emailLabel: "Email address",
      join: "Subscribe", work: "Work with me",
      brands: "Brands and sponsors: let's make something together.",
      bizEmail: "Email for sponsorships", kit: "Media kit", subject: "Sponsorship inquiry: ",
      arrow: "→", player: "Latest uploads",
    },
    he: {
      subscribe: "הרשמה לערוץ ביוטיוב", latest: "סרטונים אחרונים", support: "תמכו בערוץ",
      shop: "חנות", gear: "הציוד שלי", list: "הצטרפו לרשימת התפוצה", emailLabel: "כתובת מייל",
      join: "הרשמה", work: "עבודה משותפת",
      brands: "מותגים ונותני חסות: בואו ניצור משהו ביחד.",
      bizEmail: "פנייה לשיתופי פעולה", kit: "ערכת מדיה", subject: "פנייה לשיתוף פעולה: ",
      arrow: "←", player: "סרטונים אחרונים",
    },
  };
  var lang = STRINGS[c.language] ? c.language : "en";
  var T = STRINGS[lang];
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "he" ? "rtl" : "ltr";
  Array.prototype.forEach.call(document.querySelectorAll("[data-t]"), function (n) {
    if (T[n.getAttribute("data-t")]) n.textContent = T[n.getAttribute("data-t")];
  });
  $("player").title = T.player;

  // Accent colour
  if (c.accent && CSS.supports("color", c.accent)) {
    document.documentElement.style.setProperty("--accent", c.accent);
  }

  // Header
  var name = c.name || "My Channel";
  document.title = name;
  $("name").textContent = name;
  $("footer-name").textContent = name;
  $("tagline").textContent = c.tagline || "";
  $("year").textContent = new Date().getFullYear();

  var avatar = $("avatar");
  var avatarUrl = safeUrl(c.avatar);
  if (avatarUrl) {
    var img = el("img");
    img.src = avatarUrl;
    img.alt = "";
    avatar.appendChild(img);
  } else {
    avatar.textContent = name.split(/\s+/).map(function (w) { return w[0] || ""; }).join("").slice(0, 2).toUpperCase();
  }

  // Subscribe button: ?sub_confirmation=1 opens YouTube's subscribe prompt.
  var yt = safeUrl(c.youtubeUrl);
  var sub = $("subscribe");
  if (yt) {
    var u = new URL(yt);
    u.searchParams.set("sub_confirmation", "1");
    sub.href = u.href;
  } else {
    sub.hidden = true;
  }

  // Latest uploads: a channel's uploads playlist is its ID with UC -> UU.
  if (typeof c.channelId === "string" && /^UC[\w-]{22}$/.test(c.channelId.trim())) {
    var list = "UU" + c.channelId.trim().slice(2);
    $("player").src = "https://www.youtube-nocookie.com/embed/videoseries?list=" + encodeURIComponent(list);
    show("sec-video");
  }

  // Support
  (c.support || []).forEach(function (s) {
    var url = safeUrl(s && s.url);
    if (!url) return;
    $("support").appendChild(linkCard(s.label || "Support", s.description, url));
    show("sec-support");
  });

  // Products
  (c.products || []).forEach(function (p) {
    var url = safeUrl(p && p.url);
    if (!url) return;
    var a = el("a", "product");
    a.href = url;
    a.target = "_blank";
    a.rel = "noopener";
    var imgUrl = safeUrl(p.image);
    var media = el("div", "product-img");
    if (imgUrl) {
      var im = el("img");
      im.src = imgUrl;
      im.alt = p.title || "";
      im.loading = "lazy";
      media.appendChild(im);
    }
    a.appendChild(media);
    a.appendChild(el("strong", "", p.title || "Product"));
    if (p.price) a.appendChild(el("span", "price", p.price));
    $("products").appendChild(a);
    show("sec-products");
  });

  // Affiliates
  (c.affiliates || []).forEach(function (f) {
    var url = safeUrl(f && f.url);
    if (!url) return;
    $("affiliates").appendChild(linkCard(f.name || "Link", f.note, url));
    show("sec-affiliates");
  });
  $("disclosure").textContent = c.affiliateDisclosure || "";

  // Newsletter
  var action = safeUrl(c.newsletterFormAction);
  if (action) {
    $("newsletter").action = action;
    $("newsletter-pitch").textContent = c.newsletterPitch || "";
    show("sec-newsletter");
  }

  // Business
  var email = typeof c.businessEmail === "string" ? c.businessEmail.trim() : "";
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    $("biz-email").href = "mailto:" + email + "?subject=" + encodeURIComponent(T.subject + name);
    var kit = safeUrl(c.mediaKitUrl);
    if (kit) { $("media-kit").href = kit; $("media-kit").hidden = false; }
    show("sec-business");
  }

  // Socials
  (c.socials || []).forEach(function (s) {
    var url = safeUrl(s && s.url);
    if (!url) return;
    var a = el("a", "", s.label || url);
    a.href = url;
    a.target = "_blank";
    a.rel = "noopener me";
    $("socials").appendChild(a);
  });
})();
