---
name: deploy-site
description: Update the public creator page (thedumplingboy.netlify.app) after editing config.js or the site files, by zip-uploading to the Netlify API.
---

# Deploy the creator page

1. Edit `config.js` (language, links; empty sections are hidden) or the page files. Test locally with Playwright (open `index.html`, check links and that the creator's personal name appears nowhere).
2. Zip the files flat: `index.html app.js config.js style.css avatar.svg og-image.png`.
3. `curl -X POST -H "Authorization: Bearer proxy-injected" -H "Content-Type: application/zip" --data-binary @site.zip "https://api.netlify.com/api/v1/sites/9af8b629-a2e6-448f-96ab-4eb54fe09622/deploys"` (the real token is injected by the environment proxy). Poll `GET /api/v1/deploys/<id>` until `state` is `ready`.
4. The site is linked to the repo's `master` branch, which only has an old test file: do not rely on git pushes to deploy. Commit and push the files to the working branch as well.
5. Never publish unapproved videos or personal information on the site.
