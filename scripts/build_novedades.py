#!/usr/bin/env python3
"""Build the news section from scripts/novedades.json.

Writes novedades.html, novedades/<slug>.html, en/novedades.html, en/novedades/<slug>.html
and sitemap.xml. To publish an article: add it to novedades.json (newest first or not,
it is sorted by date), put its images under img/novedades/ and img/share/, run
`python3 scripts/build_novedades.py` and commit the result.
"""
import html
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://elcaprichodecostadelsilencio.com'
NAME = 'El Capricho de Costa del Silencio'
FONTS = ('https://fonts.googleapis.com/css2?family=Alex+Brush&family=Playfair+Display:wght@600;700;800;900'
         '&family=Poppins:wght@300;400;500;600;700&display=swap')

MONTHS_ES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
             'septiembre', 'octubre', 'noviembre', 'diciembre']
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
             'September', 'October', 'November', 'December']

T = {
    'es': {
        'home': '/', 'news': '/novedades.html', 'post': '/novedades/{}.html',
        'other_lang': 'en', 'other_label': '🇬🇧 EN', 'other_title': 'Read in English',
        'locale': 'es_ES', 'nav_home': 'Inicio', 'nav_menu': 'Carta', 'nav_news': 'Novedades',
        'nav_contact': 'Contacto', 'book': 'Reserva tu cata', 'skip': 'Saltar al contenido',
        'eyebrow': 'Últimas noticias', 'list_title': 'Novedades', 'list_accent': 'de la casa',
        'list_lead': 'Lo que entra nuevo en la estantería, lo que sale de la cocina de lata y cualquier cambio de horario. Contado sin prisa, como todo aquí.',
        'list_page_title': 'Novedades · ' + NAME,
        'list_description': 'Novedades de El Capricho de Costa del Silencio: productos nuevos, catas, horarios y lo que pasa en la tienda gourmet del C.C. Chaparral.',
        'more': 'Leer más →', 'share': 'Compartir', 'copy': 'Copiar enlace', 'copied': 'Enlace copiado',
        'all': 'Todas las novedades',
        'cta_title': '¿Te apetece probarlo?', 'cta_text': 'De miércoles a sábado, de 18:00 a 22:30. Aforo reducido: mejor reservar.',
        'legal': [('Aviso legal', 'aviso'), ('Política de privacidad', 'privacidad'), ('Política de cookies', 'cookies')],
        'menu_label': 'Abrir menú',
    },
    'en': {
        'home': '/?lang=en', 'news': '/en/novedades.html', 'post': '/en/novedades/{}.html',
        'other_lang': 'es', 'other_label': '🇪🇸 ES', 'other_title': 'Leer en español',
        'locale': 'en_GB', 'nav_home': 'Home', 'nav_menu': 'Menu', 'nav_news': 'News',
        'nav_contact': 'Contact', 'book': 'Book your tasting', 'skip': 'Skip to content',
        'eyebrow': 'Latest news', 'list_title': 'News', 'list_accent': 'from the shop',
        'list_lead': "What's new on the shelf, what comes out of the tinned kitchen and any change to our hours. Told without rushing, like everything here.",
        'list_page_title': 'News · ' + NAME,
        'list_description': "News from El Capricho de Costa del Silencio: new products, tastings, opening hours and what's happening at the gourmet shop in C.C. Chaparral.",
        'more': 'Read more →', 'share': 'Share', 'copy': 'Copy link', 'copied': 'Link copied',
        'all': 'All news',
        'cta_title': 'Fancy trying it?', 'cta_text': 'Wednesday to Saturday, 18:00 to 22:30. Limited seating: booking recommended.',
        'legal': [('Legal notice', 'aviso'), ('Privacy policy', 'privacidad'), ('Cookie policy', 'cookies')],
        'menu_label': 'Open menu',
    },
}

ICONS = {
    'whatsapp': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.5 2 2 6.5 2 12c0 1.8.5 3.5 1.4 5L2 22l5.2-1.4c1.4.8 3.1 1.2 4.8 1.2 5.5 0 10-4.5 10-10S17.5 2 12 2zm0 18.2c-1.6 0-3.1-.4-4.4-1.2l-.3-.2-3.1.8.8-3-.2-.3C4 14 3.5 13 3.5 12c0-4.7 3.8-8.5 8.5-8.5s8.5 3.8 8.5 8.5-3.8 8.5-8.5 8.5zm5.1-5.8c-.3-.1-1.6-.8-1.9-.9-.2-.1-.4-.1-.6.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.6-2.1-.2-.3 0-.5.1-.6l.4-.5c.1-.2.2-.3.2-.5.1-.2 0-.4 0-.5-.1-.1-.6-1.5-.9-2.1-.2-.5-.5-.5-.6-.5h-.6c-.2 0-.5.1-.7.4-.3.3-1 1-1 2.4s1 2.8 1.2 3c.1.2 2.1 3.3 5.2 4.6.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.6-.7 1.9-1.3.2-.6.2-1.2.2-1.3-.1-.1-.3-.2-.6-.4z"/></svg>',
    'facebook': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 13.5h2.5l1-4H14v-2c0-1 0-2 2-2h1.5V2.1c-.3 0-1.6-.1-2.9-.1C11.8 2 10 3.7 10 6.8v2.7H7v4h3V22h4v-8.5z"/></svg>',
    'x': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.8 3h3.1l-6.8 7.8L22 21h-6.2l-4.9-6.4L5.3 21H2.2l7.3-8.3L2 3h6.4l4.4 5.8L17.8 3zm-1.1 16.2h1.7L7.4 4.7H5.6l11.1 14.5z"/></svg>',
    'link': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/></svg>',
}

e = html.escape


def fmt_date(iso, lang):
    d = date.fromisoformat(iso)
    if lang == 'es':
        return f'{d.day} de {MONTHS_ES[d.month - 1]} de {d.year}'
    return f'{d.day} {MONTHS_EN[d.month - 1]} {d.year}'


def head(lang, title, description, path, other_path, image, image_alt, og_type, extra_ld, published=None):
    t = T[lang]
    url = SITE + path
    es_path, en_path = (path, other_path) if lang == 'es' else (other_path, path)
    lines = [
        '<!DOCTYPE html>',
        f'<html lang="{lang}">',
        '<head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'<title>{e(title)}</title>',
        f'<meta name="description" content="{e(description)}">',
        f'<link rel="canonical" href="{url}">',
        f'<link rel="alternate" hreflang="es" href="{SITE}{es_path}">',
        f'<link rel="alternate" hreflang="en" href="{SITE}{en_path}">',
        f'<link rel="alternate" hreflang="x-default" href="{SITE}{es_path}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{NAME}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(description)}">',
        f'<meta property="og:image" content="{SITE}{image}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{e(image_alt)}">',
        f'<meta property="og:locale" content="{t["locale"]}">',
    ]
    if published:
        lines.append(f'<meta property="article:published_time" content="{published}">')
    lines += [
        '<meta name="twitter:card" content="summary_large_image">',
        '<link rel="icon" href="/favicon.ico" sizes="48x48">',
        '<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png">',
        '<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">',
        '<link rel="manifest" href="/manifest.webmanifest">',
        '<meta name="theme-color" content="#14192B">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'<link href="{FONTS}" rel="stylesheet">',
        '<link rel="stylesheet" href="/assets/novedades.css">',
    ]
    for ld in extra_ld:
        lines.append('<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=1) + '\n</script>')
    lines += [
        '<!-- Biscotti CMP Consent Banner -->',
        '<script src="https://api.biscotti-cmp.com/scripts/biscotti-boot.js"></script>',
        '<script>',
        '  window.BiscottiConfig = {',
        '    websiteId: "3cb3f3db-aba1-4e80-b52c-1565b251f432",',
        '    apiUrl: "https://api.biscotti-cmp.com/api/v1"',
        '  };',
        '</script>',
        '<script src="https://api.biscotti-cmp.com/scripts/biscotti.min.js" defer></script>',
        '</head>',
    ]
    return '\n'.join(lines)


def header(lang, other_path):
    t = T[lang]
    return f'''<body>
<a class="skip" href="#contenido">{t["skip"]}</a>
<header class="site-header">
  <div class="wrap">
    <nav>
      <a href="{t["home"]}" class="brand" aria-label="{NAME}">
        <span class="badge"><img src="/img/logo-hero.png" alt="{NAME}" width="40" height="31"></span>
      </a>
      <ul class="nav-links" id="navLinks">
        <li><a href="{t["home"]}">{t["nav_home"]}</a></li>
        <li><a href="{t["home"]}#carta">{t["nav_menu"]}</a></li>
        <li><a href="{t["news"]}" aria-current="page">{t["nav_news"]}</a></li>
        <li><a href="{t["home"]}#contacto">{t["nav_contact"]}</a></li>
        <li><a href="{t["home"]}#contacto" class="btn">{t["book"]}</a></li>
      </ul>
      <a class="lang-link" href="{other_path}" hreflang="{t["other_lang"]}" lang="{t["other_lang"]}" title="{t["other_title"]}" data-lang="{t["other_lang"]}">{t["other_label"]}</a>
      <button class="burger" id="burgerBtn" aria-label="{t["menu_label"]}" aria-controls="navLinks" aria-expanded="false">☰</button>
    </nav>
  </div>
</header>'''


def footer(lang):
    t = T[lang]
    legal = '\n'.join(f'      <a href="{t["home"]}#legal-{key}">{label}</a>' for label, key in t['legal'])
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="f-brand">
      <span class="badge"><img src="/img/logo-hero.png" alt="" width="30" height="23" loading="lazy"></span>
      <span>© <span id="year">{date.today().year}</span> {NAME}</span>
    </div>
    <div class="legal">
{legal}
    </div>
    <a href="{t["home"]}#contacto" class="book">{t["book"]}</a>
  </div>
</footer>
<script>
  document.getElementById('year').textContent = new Date().getFullYear();
  const burger = document.getElementById('burgerBtn'), navLinks = document.getElementById('navLinks');
  burger.addEventListener('click', () => {{
    const open = navLinks.classList.toggle('open');
    burger.setAttribute('aria-expanded', open);
  }});
  // Keep the home page in the language the visitor picked here.
  try {{ localStorage.setItem('capricho_lang', '{lang}'); }} catch (err) {{}}
  document.querySelectorAll('.lang-link').forEach(a => a.addEventListener('click', () => {{
    try {{ localStorage.setItem('capricho_lang', a.dataset.lang); }} catch (err) {{}}
  }}));
</script>
</body>
</html>
'''


def breadcrumbs(lang, crumbs):
    return {
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + p}
                            for i, (n, p) in enumerate(crumbs)],
    }


def render_block(block):
    if 'p' in block:
        return f'      <p>{block["p"]}</p>'
    if 'h2' in block:
        return f'      <h2>{e(block["h2"])}</h2>'
    if 'destacado' in block:
        return f'      <p class="post-destacado">{block["destacado"]}</p>'
    if 'img' in block:
        return (f'      <figure><img src="{block["img"]}" alt="{e(block["alt"])}" loading="lazy" decoding="async"></figure>')
    raise ValueError(f'Unknown block: {block}')


def article_page(lang, art, prev_art, next_art):
    t = T[lang]
    c = art[lang]
    other = T[t['other_lang']]
    path = t['post'].format(art['slug'])
    other_path = other['post'].format(art['slug'])
    url = SITE + path
    title = f'{c["title"]} · {NAME}'
    ld = [
        {
            '@context': 'https://schema.org', '@type': 'BlogPosting',
            'headline': c['title'], 'description': c['description'],
            'image': [SITE + art['share'], SITE + art['image']],
            'datePublished': art['date'], 'dateModified': art.get('modified', art['date']),
            'inLanguage': lang, 'mainEntityOfPage': url,
            'author': {'@type': 'Organization', 'name': NAME, 'url': SITE + '/'},
            'publisher': {'@type': 'Organization', 'name': NAME, 'logo': {'@type': 'ImageObject', 'url': SITE + '/icons/icon-512.png'}},
        },
        breadcrumbs(lang, [(t['nav_home'], t['home']), (t['nav_news'], t['news']), (c['title'], path)]),
    ]
    out = [head(lang, title, c['description'], path, other_path, art['share'], c['alt'], 'article', ld, art['date']),
           header(lang, other_path)]
    # newer article (or the list) on the left, older article on the right
    nav = [f'<a href="{t["post"].format(next_art["slug"])}">{e("← " + next_art[lang]["title"])}</a>' if next_art
           else f'<a href="{t["news"]}">← {t["all"]}</a>']
    if prev_art:
        nav.append(f'<a href="{t["post"].format(prev_art["slug"])}">{e(prev_art[lang]["title"] + " →")}</a>')
    share_text = e(c['title'])
    out.append(f'''<main id="contenido">
  <section class="post-hero">
    <div class="wrap">
      <span class="eyebrow"><a href="{t["news"]}">{t["nav_news"]}</a></span>
      <h1>{e(c["title"])}</h1>
      <div class="post-meta"><time datetime="{art["date"]}">{fmt_date(art["date"], lang)}</time></div>
    </div>
  </section>
  <article class="post-body">
    <div class="wrap">
      <img class="post-cover" src="{art["image"]}" alt="{e(c["alt"])}" decoding="async" fetchpriority="high">
{chr(10).join(render_block(b) for b in c["body"])}
      <div class="post-cta">
        <p><strong>{t["cta_title"]}</strong>{t["cta_text"]}</p>
        <a class="btn" href="{t["home"]}#contacto">{t["book"]}</a>
      </div>
      <div class="post-share">
        <span class="label">{t["share"]}</span>
        <div class="socials" id="shareBox" data-url="{url}" data-title="{share_text}">
          <a data-share="whatsapp" href="https://wa.me/?text={e(c["title"])}%20{url}" target="_blank" rel="noopener" aria-label="WhatsApp">{ICONS["whatsapp"]}</a>
          <a data-share="facebook" href="https://www.facebook.com/sharer/sharer.php?u={url}" target="_blank" rel="noopener" aria-label="Facebook">{ICONS["facebook"]}</a>
          <a data-share="x" href="https://twitter.com/intent/tweet?url={url}" target="_blank" rel="noopener" aria-label="X">{ICONS["x"]}</a>
          <button type="button" id="copyLink" aria-label="{t["copy"]}" title="{t["copy"]}">{ICONS["link"]}</button>
        </div>
      </div>
      <nav class="post-nav" aria-label="{t["nav_news"]}">
        {(chr(10) + "        ").join(nav)}
      </nav>
    </div>
  </article>
</main>
<script>
  (function(){{
    const box = document.getElementById('shareBox');
    const url = box.dataset.url, title = box.dataset.title;
    const links = {{
      whatsapp: 'https://wa.me/?text=' + encodeURIComponent(title + ' ' + url),
      facebook: 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url),
      x: 'https://twitter.com/intent/tweet?text=' + encodeURIComponent(title) + '&url=' + encodeURIComponent(url),
    }};
    box.querySelectorAll('[data-share]').forEach(a => {{ a.href = links[a.dataset.share]; }});
    document.getElementById('copyLink').addEventListener('click', e => {{
      const btn = e.currentTarget;
      (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(() => {{
        btn.title = '{t["copied"]}'; btn.setAttribute('aria-label', '{t["copied"]}');
      }}).catch(() => {{ window.prompt('{t["copy"]}', url); }});
    }});
  }})();
</script>''')
    out.append(footer(lang))
    return '\n'.join(out)


def list_page(lang, arts):
    t = T[lang]
    other = T[t['other_lang']]
    cards = []
    for i, a in enumerate(arts):
        c = a[lang]
        lazy = '' if i < 3 else ' loading="lazy"'
        cards.append(f'''      <a class="news-card" href="{t["post"].format(a["slug"])}">
        <div class="thumb"><img src="{a["image"]}" alt="{e(c["alt"])}" decoding="async"{lazy}></div>
        <div class="body">
          <time datetime="{a["date"]}">{fmt_date(a["date"], lang)}</time>
          <h2>{e(c["title"])}</h2>
          <p>{e(c["excerpt"])}</p>
          <span class="more">{t["more"]}</span>
        </div>
      </a>''')
    ld = [
        {
            '@context': 'https://schema.org', '@type': 'Blog', 'name': t['list_page_title'],
            'url': SITE + t['news'], 'inLanguage': lang,
            'blogPost': [{'@type': 'BlogPosting', 'headline': a[lang]['title'], 'datePublished': a['date'],
                          'url': SITE + t['post'].format(a['slug'])} for a in arts],
        },
        breadcrumbs(lang, [(t['nav_home'], t['home']), (t['nav_news'], t['news'])]),
    ]
    out = [head(lang, t['list_page_title'], t['list_description'], t['news'], other['news'],
                arts[0]['share'], arts[0][lang]['alt'], 'website', ld),
           header(lang, other['news'])]
    out.append(f'''<main id="contenido">
  <section class="news-hero">
    <div class="wrap">
      <span class="eyebrow">{t["eyebrow"]}</span>
      <h1>{t["list_title"]}<span class="accent">{t["list_accent"]}</span></h1>
      <p>{t["list_lead"]}</p>
    </div>
  </section>
  <section class="news-list">
    <div class="wrap news-grid">
{chr(10).join(cards)}
    </div>
  </section>
</main>''')
    out.append(footer(lang))
    return '\n'.join(out)


def sitemap(arts):
    pairs = [('/', '/?lang=en')] + [('/novedades.html', '/en/novedades.html')] + \
            [(T['es']['post'].format(a['slug']), T['en']['post'].format(a['slug'])) for a in arts]
    urls = []
    for es_path, en_path in pairs:
        alts = (f'    <xhtml:link rel="alternate" hreflang="es" href="{SITE}{es_path}"/>\n'
                f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}{en_path}"/>\n'
                f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{es_path}"/>\n')
        for loc in (es_path, en_path):
            urls.append(f'  <url>\n    <loc>{SITE}{e(loc)}</loc>\n{alts}  </url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + '\n'.join(urls) + '\n</urlset>\n')


def write(rel, content):
    path = os.path.join(ROOT, rel.lstrip('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    with open(os.path.join(ROOT, 'scripts', 'novedades.json'), encoding='utf-8') as f:
        arts = sorted(json.load(f), key=lambda a: a['date'], reverse=True)
    for lang in ('es', 'en'):
        write(T[lang]['news'], list_page(lang, arts))
        for i, art in enumerate(arts):
            newer = arts[i - 1] if i > 0 else None
            older = arts[i + 1] if i + 1 < len(arts) else None
            write(T[lang]['post'].format(art['slug']), article_page(lang, art, older, newer))
    write('/sitemap.xml', sitemap(arts))
    print(f'{len(arts)} articles x 2 languages written')


if __name__ == '__main__':
    main()
