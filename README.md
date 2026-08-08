# sandlock.io

Marketing site and documentation for [Sandlock](https://github.com/multikernel/sandlock),
a lightweight Linux process sandbox built on Landlock, seccomp-bpf, and seccomp
user notification.

Built with Jekyll and served by GitHub Pages at <https://sandlock.io>.
Copyright Multikernel Technologies, Inc.

## Deploying

GitHub Pages builds this repository with its own Jekyll toolchain; there is no
Actions workflow to maintain. Push to the default branch and the site is
rebuilt. `CNAME` pins the custom domain, so the repository's Pages settings
must have `sandlock.io` configured with DNS pointing at GitHub.

## Local preview

```bash
jekyll build          # writes _site/
jekyll serve          # http://127.0.0.1:4000
```

## Layout

```
_config.yml            site metadata, plugins, excludes
CNAME                  custom domain
_layouts/
  default.html         header, footer, meta tags; every page uses this
  doc.html             documentation shell: sidebar, breadcrumb, prev/next pager
_data/
  i18n.yml             strings for the header and footer chrome
  docs.yml             documentation order — drives the sidebar AND the pager
assets/
  css/styles.css       design system: tokens, hero, sections, cards, tables, code
  css/docs.css         three-column documentation layout
  js/site.js           mobile nav, copy buttons, on-this-page TOC, scrollspy
  js/icons.js          generated: inline SVG for the icon set this site uses
  images/              logo mark
docs/                  documentation pages (layout: doc)
*.html                 marketing pages (layout: default)
```

### Adding a documentation page

1. Create `docs/<name>.html` with `layout: doc` front matter. The useful keys
   beyond the standard ones are `heading` (the `<h1>`), `lede` (the paragraph
   under it), and `short_title` (used in the breadcrumb).
2. Add an entry to `_data/docs.yml` in the position it should occupy. That file
   is the single source of truth: the sidebar and the previous/next pager are
   both derived from it, so nothing else needs updating.

Write body content as HTML. Headings get anchor links and on-this-page entries
automatically; no ids are needed unless you want to link to a specific heading
from elsewhere, in which case set the `id` explicitly so it cannot drift when
the heading text changes.

### Design system

The visual language is shared with [multikernel.io](https://multikernel.io):
ink-navy ground, ENIG pad-gold accent, cool blue-tinted neutrals, and mono
annotations. The signature element is a solid gold rule under hero headlines
and above section titles. Tokens live at the top of `assets/css/styles.css`;
prefer them over literal values so both sites stay in step.

Code samples are hand-marked with span classes rather than run through a
highlighter, which keeps the build free of a syntax-highlighting dependency:

| Class | Meaning            |
| ----- | ------------------ |
| `c`   | comment            |
| `p`   | shell prompt       |
| `k`   | keyword or command |
| `s`   | string             |
| `o`   | program output     |

### Icons

`assets/js/icons.js` is generated, not hand-edited. It inlines only the
[Lucide](https://lucide.dev) icons the site actually references, so icon
rendering never depends on a CDN. To add an icon, use `<i data-lucide="name">`
in the markup and regenerate the bundle from the `lucide-static` package,
keeping the file to the icons in use.
