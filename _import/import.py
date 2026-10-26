#!/usr/bin/env python3
"""WordPress WXR export -> Jekyll posts.

Usage:  python3 _import/import.py _import/myurl.WordPress.2026-10-26.xml

Writes _posts/*.md and _drafts/*.md, and _import/images.txt (image URL -> local path).
Images are referenced at /assets/img/... ; run _import/get_images.ps1 to download them.
Safe to re-run: it overwrites generated files only.
"""
import re, sys, html, pathlib, xml.etree.ElementTree as ET
from markdownify import markdownify as md

NS = {'wp': 'http://wordpress.org/export/1.2/',
      'content': 'http://purl.org/rss/1.0/modules/content/',
      'excerpt': 'http://wordpress.org/export/1.2/excerpt/'}
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_HOST = 'https://myurl.wordpress.com/wp-content/uploads/'

# WordPress category -> site topic (lowercase, one word)
TOPIC = {'Blog': 'thoughts', 'Blogs': 'thoughts', 'Photo': 'photo', 'Finance': 'finance',
         'Health/Beauty': 'health', 'Uncategorized': 'thoughts'}
SKIP_CATS = {'slideshow', 'Uncategorized', 'Blogs'}  # noise, not topics

def t(it, tag):
    e = it.find(tag, NS)
    return (e.text or '') if e is not None else ''

def slugify(s):
    s = re.sub(r"[‘’'\"“”]", '', s.lower())
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s or 'untitled'

def yt_embed(m):
    vid = m.group(1)
    return (f'\n<div class="video"><iframe src="https://www.youtube.com/embed/{vid}" '
            f'title="YouTube video" loading="lazy" allowfullscreen></iframe></div>\n')

def clean_html(s):
    s = re.sub(r'<!--\s*/?wp:[^>]*-->', '', s)          # gutenberg block comments
    s = re.sub(r'\[/?caption[^\]]*\]', '', s)           # caption shortcodes
    s = re.sub(r'\[gallery[^\]]*\]', '', s)
    # bare youtube links on their own line -> embed
    s = re.sub(r'(?m)^\s*(?:<p>)?\s*https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)[^\s<]*\s*(?:</p>)?\s*$', yt_embed, s)
    s = re.sub(r'\[youtube[^\]]*?(?:v=|youtu\.be/)([\w-]+)[^\]]*\]', yt_embed, s)
    return s

def to_md(s):
    s = clean_html(s)
    keep = re.findall(r'<div class="video">.*?</div>', s, flags=re.S)
    classic = '<p>' not in s
    for i, k in enumerate(keep):
        s = s.replace(k, f'\n\n<p>@@EMBED{i}@@</p>\n\n' if not classic else f'\n\n@@EMBED{i}@@\n\n')
    # classic editor: blank-line separated paragraphs; wrap loose lines so markdownify keeps breaks
    if classic:
        s = '\n\n'.join(f'<p>{p.strip()}</p>' if not p.strip().startswith('<') else p for p in re.split(r'\n\s*\n', s) if p.strip())
    out = md(s, heading_style='ATX', bullets='-', strip=['span'])
    for i, k in enumerate(keep):
        out = out.replace(f'@@EMBED{i}@@', k)
    out = re.sub(r'\n{3,}', '\n\n', out).strip()
    return out

def main(xml):
    ch = ET.parse(xml).getroot().find('channel')
    items = ch.findall('item')
    atts = {}      # post_id -> attachment url
    by_parent = {} # parent post id -> [urls]
    for it in items:
        if t(it, 'wp:post_type') == 'attachment':
            u = t(it, 'wp:attachment_url'); pid = t(it, 'wp:post_id'); par = t(it, 'wp:post_parent')
            atts[pid] = u
            by_parent.setdefault(par, []).append(u)

    images = {}  # remote url -> local path
    def local(u):
        rel = u.replace(SRC_HOST, '')
        images[u] = f'assets/img/{rel}'
        return f'{{{{ site.baseurl }}}}/assets/img/{rel}'

    (ROOT / '_posts').mkdir(exist_ok=True); (ROOT / '_drafts').mkdir(exist_ok=True)
    n = 0
    for it in items:
        if t(it, 'wp:post_type') != 'post':
            continue
        status = t(it, 'wp:status')
        title = html.unescape(t(it, 'title') or '').strip() or 'Untitled'
        title = re.sub(r"^[‘'](.*)[’']$", r'\1', title)  # strip wrapping quotes on photo titles
        date = t(it, 'wp:post_date')[:10]
        slug = t(it, 'wp:post_name') or slugify(title)
        pid = t(it, 'wp:post_id')
        cats = [c.text for c in it.findall('category') if c.get('domain') == 'category']
        tags = [c.text for c in it.findall('category') if c.get('domain') == 'post_tag']
        topic = next((TOPIC.get(c, c.lower()) for c in cats if c not in SKIP_CATS), 'thoughts')
        body = to_md(t(it, 'content:encoded'))

        # featured image / attached images (photo posts)
        thumb = next((m.find('wp:meta_value', NS).text for m in it.findall('wp:postmeta', NS)
                      if m.find('wp:meta_key', NS).text == '_thumbnail_id'), None)
        imgs = []
        if thumb and thumb in atts:
            imgs.append(atts[thumb])
        else:
            imgs += by_parent.get(pid, [])
        # rewrite inline image urls
        for u in re.findall(r'https://myurl\.wordpress\.com/wp-content/uploads/[^\s)"\']+', body):
            base = re.sub(r'-\d+x\d+(?=\.\w+$)', '', u.split('?')[0])  # drop WP size suffix
            body = body.replace(u, local(base))
        cover = local(imgs[0]) if imgs else ''
        if imgs and cover.lstrip('/') not in body and '![' not in body:
            body = ''.join(f'![{title}]({local(u)})\n\n' for u in imgs) + body

        fm = ['---', f'title: "{title.replace(chr(34), chr(39))}"', f'date: {date}', f'topic: {topic}']
        if cover: fm.append(f'image: {cover}')
        if tags: fm.append('tags: [' + ', '.join(tags) + ']')
        fm += ['related: []', f'wordpress: {t(it, "link")}', '---', '']
        folder = '_posts' if status == 'publish' else '_drafts'
        fname = f'{date}-{slug}.md' if status == 'publish' else f'{slug or slugify(title)}.md'
        (ROOT / folder / fname).write_text('\n'.join(fm) + body + '\n', encoding='utf-8')
        n += 1
    (ROOT / '_import' / 'images.txt').write_text('\n'.join(f'{u}\t{p}' for u, p in sorted(images.items())) + '\n')
    print(f'{n} posts written, {len(images)} images listed in _import/images.txt')

if __name__ == '__main__':
    main(sys.argv[1])
