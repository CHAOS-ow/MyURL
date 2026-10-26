# My URL

Personal site. Jekyll on GitHub Pages, no build step: push to `main`, GitHub builds it.

Live at https://chaos-ow.github.io/MyURL (set `baseurl: ""` in `_config.yml` if it moves to a root domain).

## Layout

```
_posts/        one .md per post, named YYYY-MM-DD-slug.md
_drafts/       unpublished (not built unless you run `jekyll serve --drafts`)
_notes/        reference notes: _notes/<section>/<name>.md -> /notes/<section>/<name>/ (undated; see below)
_layouts/      default.html (masthead + sections), post.html, note.html (TOC + mentioned-in)
notes/         the Notes index page
assets/css/    main.css — light grey ground, white sheets, Source Serif 4 + Libre Franklin
assets/img/    images, by year/month
_import/       the WordPress export, the import script, and get_images.ps1 (one-time)
index.html     front page (newspaper layout; picking a section in the nav shows that topic as a plain grid)
_includes/     item.html — one post as a front-page item
_data/         instagram.yml — URL of the single Instagram post shown in the rail
about.md       /about/
```

## Writing a post

Create `_posts/2026-10-26-some-title.md`:

```yaml
---
title: "Some title"
date: 2026-10-26
topic: thoughts          # one word; new topics appear in the filters automatically
image: /assets/img/2026/10/photo.jpg   # photo posts only; makes it an image card
related: [choshim, free-spirited]      # optional; slugs of other posts
---
Body in markdown. Images: ![alt]({{ site.baseurl }}/assets/img/2026/10/photo.jpg)  (baseurl part required while the site lives under /MyURL)
YouTube: <div class="video"><iframe src="https://www.youtube.com/embed/VIDEO_ID" allowfullscreen></iframe></div>
```

Topic colors live in `_config.yml` under `topic_colors`. A new topic with no color falls back to ink; add a line there to give it one.

Front page rules (automatic): quotes and posts under 60 words go to the right rail; the newest of the rest is the lead; next three sit in the left column; everything else runs four-across below. Under 40 words renders as a quote. `topic: photo` + `image` shows the image.

Instagram: paste the latest post/reel URL into `_data/instagram.yml` to show it at the foot of the rail; empty string hides it.

`related` is one-directional in the file but shows both ways on the site (a "linked from" list appears on the target post).

## Writing a note

Notes are reference pages, not posts: no date in the filename, no card on the wall. Create `_notes/<section>/<name>.md`:

```yaml
---
title: Anger and the stories behind it
section: drk              # folder name = section; new sections appear in the index automatically
updated: 2026-10-26       # shown as "updated"; bump it when you edit
summary: One line under the title (optional)
tags: [anger, ego]        # searchable from the index (optional)
related: [observing-without-concluding]   # slugs of posts or notes (optional)
---
## Headings become the table of contents
Body in markdown.
```

Quotes: one note per source (`_notes/quotes/chekhov.md`), many quotes per page, blockquote + attribution line.

## Local preview (optional)

```
bundle install
bundle exec jekyll serve --drafts
```
