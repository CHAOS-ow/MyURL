# My URL

Personal site. Jekyll on GitHub Pages, no build step: push to `main`, GitHub builds it.

Live at https://chaos-ow.github.io/MyURL (set `baseurl: ""` in `_config.yml` if it moves to a root domain).

## Layout

```
_posts/        one .md per post, named YYYY-MM-DD-slug.md
_drafts/       unpublished (not built unless you run `jekyll serve --drafts`)
_layouts/      default.html (nav + footer), post.html (single post + related/backlinks)
assets/css/    main.css — palette and type shared with chaos-ow.github.io
assets/img/    images, by year/month
_import/       the WordPress export, the import script, and get_images.ps1 (one-time)
index.html     the wall (gallery of all posts, filter by topic)
about.md       /about/
```

## Writing a post

Create `_posts/2026-10-26-some-title.md`:

```yaml
---
title: "Some title"
date: 2026-10-26
topic: thoughts          # one word; new topics appear in the filters automatically
image: /assets/img/2026/10/photo.jpg   # optional; makes it an image card
related: [choshim, free-spirited]      # optional; slugs of other posts
---
Body in markdown. Images: ![alt](/assets/img/2026/10/photo.jpg)
YouTube: <div class="video"><iframe src="https://www.youtube.com/embed/VIDEO_ID" allowfullscreen></iframe></div>
```

Cards on the wall: a post with `image` becomes an image card; a post under 40 words becomes a quote card; everything else is title + excerpt (first paragraph).

`related` is one-directional in the file but shows both ways on the site (a "linked from" list appears on the target post).

## One-time: old images

The WordPress images are still referenced at `/assets/img/...` but not yet downloaded. From the repo root in PowerShell:

```
powershell -ExecutionPolicy Bypass -File _import\get_images.ps1
```

Then commit `assets/img/`.

## Local preview (optional)

```
bundle install
bundle exec jekyll serve --drafts
```
