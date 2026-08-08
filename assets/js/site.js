(function () {
    'use strict';

    function initIcons() {
        if (typeof window.renderIcons === 'function') {
            window.renderIcons(document);
            return;
        }
        document.querySelectorAll('[data-lucide]').forEach(function (el) {
            el.textContent = '•';
        });
    }

    function initMobileNav() {
        var toggle = document.querySelector('.site-mobile-toggle');
        var nav = document.querySelector('.site-mobile-nav');
        if (!toggle || !nav) return;

        function close() {
            nav.classList.remove('active');
            toggle.classList.remove('active');
            document.body.classList.remove('mobile-nav-open');
            toggle.setAttribute('aria-expanded', 'false');
        }

        toggle.addEventListener('click', function (e) {
            e.stopPropagation();
            var open = nav.classList.toggle('active');
            toggle.classList.toggle('active', open);
            document.body.classList.toggle('mobile-nav-open', open);
            toggle.setAttribute('aria-expanded', String(open));
        });

        nav.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', close);
        });

        document.addEventListener('click', function (e) {
            if (!nav.contains(e.target) && !toggle.contains(e.target)) close();
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') close();
        });
    }

    function initCopyButtons() {
        document.querySelectorAll('.code-block').forEach(function (block) {
            var btn = block.querySelector('.code-copy');
            var pre = block.querySelector('pre');
            if (!btn || !pre) return;

            btn.addEventListener('click', function () {
                var text = pre.innerText;
                var done = function () {
                    var label = btn.querySelector('.code-copy-label') || btn;
                    var previous = label.textContent;
                    label.textContent = 'Copied';
                    btn.classList.add('copied');
                    setTimeout(function () {
                        label.textContent = previous;
                        btn.classList.remove('copied');
                    }, 1600);
                };

                if (navigator.clipboard && window.isSecureContext) {
                    navigator.clipboard.writeText(text).then(done);
                    return;
                }
                // http:// and file:// fall back to the legacy path.
                var ta = document.createElement('textarea');
                ta.value = text;
                ta.style.position = 'fixed';
                ta.style.opacity = '0';
                document.body.appendChild(ta);
                ta.select();
                try { document.execCommand('copy'); done(); } catch (e) { /* no-op */ }
                document.body.removeChild(ta);
            });
        });
    }

    function slugify(text) {
        return text.toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .trim()
            .replace(/\s+/g, '-');
    }

    function initDocsToc() {
        var prose = document.querySelector('.prose');
        var toc = document.querySelector('.docs-toc');
        if (!prose) return;

        var headings = prose.querySelectorAll('h2, h3');
        var list = toc ? toc.querySelector('ul') : null;
        var seen = {};

        headings.forEach(function (h) {
            if (!h.id) {
                var base = slugify(h.textContent);
                seen[base] = (seen[base] || 0) + 1;
                h.id = seen[base] > 1 ? base + '-' + seen[base] : base;
            }

            var anchor = document.createElement('a');
            anchor.className = 'heading-anchor';
            anchor.href = '#' + h.id;
            anchor.textContent = '#';
            anchor.setAttribute('aria-hidden', 'true');
            anchor.tabIndex = -1;
            h.appendChild(anchor);

            if (!list || h.tagName !== 'H2' && h.tagName !== 'H3') return;
            var li = document.createElement('li');
            li.className = 'lvl-' + h.tagName.charAt(1);
            var a = document.createElement('a');
            a.href = '#' + h.id;
            a.textContent = h.textContent.replace(/#$/, '');
            li.appendChild(a);
            list.appendChild(li);
        });

        if (!list || !list.children.length) {
            if (toc) toc.style.display = 'none';
            return;
        }

        var links = Array.prototype.slice.call(list.querySelectorAll('a'));
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                links.forEach(function (a) {
                    a.classList.toggle('active', a.getAttribute('href') === '#' + entry.target.id);
                });
            });
        }, { rootMargin: '-90px 0px -70% 0px', threshold: 0 });

        headings.forEach(function (h) { observer.observe(h); });
    }

    function initDocsNavToggle() {
        var toggle = document.querySelector('.docs-nav-toggle');
        var sidebar = document.querySelector('.docs-sidebar');
        if (!toggle || !sidebar) return;

        toggle.addEventListener('click', function () {
            var open = sidebar.classList.toggle('open');
            toggle.setAttribute('aria-expanded', String(open));
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initIcons();
        initMobileNav();
        initCopyButtons();
        initDocsToc();
        initDocsNavToggle();
    });
})();
