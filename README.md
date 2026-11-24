# Creator Hub: a money page for your YouTube channel

> **Live:** https://thedumplingboy.netlify.app (hosted on Netlify)
> **Start here:** `CHANNEL_KIT.md` (channel texts) · `scripts/` (episode scripts) · `production/` (character prompts, workflow, Ko-fi text) · `brand/` (profile picture, banner)

A free, single-page website you link from your YouTube channel and every video
description. It turns viewers into income through:

| Section | How it earns |
|---|---|
| **Subscribe button** | Opens YouTube's subscribe prompt directly (`?sub_confirmation=1`). More subscribers lead to more views and ad revenue. |
| **Latest videos** | Embeds your newest uploads automatically, so visitors keep watching. |
| **Support the channel** | Channel memberships, Buy Me a Coffee / Ko-fi, Patreon, PayPal. |
| **Shop** | Merch or digital products (presets, guides, courses). |
| **Gear I use** | Affiliate links (Amazon Associates etc.), with the legally required disclosure. |
| **Join the list** | Email signup, an audience you own. |
| **Work with me** | A one-click sponsorship email for brands, plus an optional media kit. |

Sections you leave empty are hidden, so you can start small.

No build step, no server, no cost. It's plain HTML/CSS/JS.

---

## 1. Fill in your details (5 minutes)

Edit **`config.js`**. It's the only file you need to touch. Set `language` to `"he"` (Hebrew, right-to-left) or `"en"`. Replace each
`CHANGE ME` and paste in your links. To find your **channel ID** (it starts
with `UC`), go to YouTube Studio → Settings → Channel → Advanced settings.

To preview, open `index.html` in a browser.

## 2. Put it online for free (GitHub Pages)

1. Merge this branch into `main` (or push the files to `main`).
2. On GitHub, open the repo → **Settings → Pages**.
3. Under *Build and deployment*, choose **Deploy from a branch**, branch `main`, folder `/ (root)`, then **Save**.
4. After about a minute your page is live at
   `https://<your-github-username>.github.io/<repo-name>/`.

Note: GitHub Pages on a free account requires the repository to be **public**.
Netlify Drop (drag-and-drop the folder) and Cloudflare Pages are free
alternatives. A custom domain (about $10/year) looks more trustworthy to sponsors.

## 3. Connect it to YouTube

- **Channel links:** In YouTube Studio → Customization → Profile → *Links*, add your hub URL as the first link. It shows on your channel header.
- **Every video description:** Put the link in the first 2 lines, above the "…more" cut:
  ```
  ☕ Support the channel + gear I use → https://YOUR-HUB-URL
  ```
- **Pinned comment** on each new video with the same link.
- **Shorts:** Shorts can't have clickable description links, so say "link on my channel page" and point to the channel header link.

---

## 4. Money playbook: what actually earns, in order

A page doesn't make money by itself. **Views** do, and the page converts
them. Focus on uploading consistently, and use this page to capture value
from every viewer.

### Stage 0: from day one (no requirements)
- **Affiliate links:** The fastest first dollar. Recommend only products you actually use. Sign up for Amazon Associates or the brand's own program.
- **Tips:** Buy Me a Coffee / Ko-fi take a few minutes to set up.
- **Email list:** Start collecting now. A free tier of Buttondown, Kit (ConvertKit) or Mailchimp is enough. Paste the form's action URL into `newsletterFormAction`.
- **Digital product:** A guide, template or preset pack sold through Gumroad or Lemon Squeezy, linked in `products`.

### Stage 1: YouTube Partner Program, early tier
Unlocks **memberships, Super Thanks/Chat/Stickers, YouTube Shopping**.
Approximate requirements as of late 2026 (check YouTube Studio → *Earn* for your exact numbers):
- 500 subscribers
- 3 public uploads in the last 90 days
- 3,000 public watch hours in the last 12 months **or** 3M Shorts views in the last 90 days

### Stage 2: full YPP (ad revenue)
- 1,000 subscribers
- 4,000 public watch hours in the last 12 months **or** 10M Shorts views in the last 90 days
- Shorts-feed watch time does **not** count toward the 4,000 hours.
- ⚠️ Reports say these thresholds rise for **new applicants from Feb 1, 2027** (8,000 watch hours or 20M Shorts views; existing members are grandfathered). Apply before then if you qualify.
- Meeting the numbers doesn't guarantee approval. You need no active Community Guidelines strikes, and your content must follow the monetization policies (no reused/unoriginal content).

### Stage 3: sponsorships
Once you get steady views (often from about 5–10k views per video in a good
niche), brands pay per video. Fill in `businessEmail` and make a one-page
media kit with your niche, average views, audience age/country (from YouTube
Analytics) and rates.

### Things that move the needle most
1. **Niche with buyers:** Tech, personal finance, software tutorials, business and education earn several times more per view than gaming or vlogs.
2. **Consistency:** For example, 1 long video plus 2–3 Shorts per week. Shorts bring subscribers, long videos bring watch hours and ad revenue.
3. **Title + thumbnail:** These decide whether anyone clicks. Test them with YouTube's built-in *Test & Compare*.
4. **A call to action in every video:** "Link in the description to support / get the gear."

### Rules to stay safe
- Always disclose affiliate links and paid promotions. Tick **"includes paid promotion"** in YouTube Studio for sponsored videos.
- Never buy subscribers or views, and never use sub4sub. It gets channels demonetized or terminated.
- Income is taxable. Keep records and fill in the tax info AdSense asks for.

---

## Files

| File | Purpose |
|---|---|
| `config.js` | **Your settings.** Edit this. |
| `index.html` | Page structure |
| `style.css` | Look and feel (auto light/dark mode) |
| `app.js` | Renders the page from your config; only allows safe `https:`/`mailto:` links |
