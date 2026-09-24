/**
 * In-place list navigation.
 *
 * Pagination links and search forms fetch the next page as normal HTML and
 * replace only the regions marked with `data-swap-region` (matched by id),
 * so the page never jumps back to the top. The URL is updated with
 * history.pushState, so reload, bookmarks and Back/Forward keep working.
 *
 * Progressive enhancement: without JS, or if a request fails or is
 * redirected (e.g. an expired session), it falls back to a full page load.
 */
(function () {
  'use strict';

  var REGION = '[data-swap-region][id]';
  if (!document.querySelector(REGION) || !window.fetch || !window.DOMParser || !history.pushState) return;

  var inflight = null;

  function regions() {
    return Array.prototype.slice.call(document.querySelectorAll(REGION));
  }

  function setBusy(busy) {
    regions().forEach(function (el) {
      if (busy) el.setAttribute('aria-busy', 'true');
      else el.removeAttribute('aria-busy');
    });
  }

  // After a swap, bring the list's heading into view only if it is above the
  // viewport (e.g. the user clicked "Next" under a long table). Otherwise the
  // scroll position is left exactly where it was.
  function keepAnchorVisible(anchorId) {
    var anchor = anchorId && document.getElementById(anchorId);
    if (!anchor) return;
    if (anchor.getBoundingClientRect().top < 0) {
      anchor.scrollIntoView({ block: 'start', behavior: 'smooth' });
    }
  }

  function navigate(url, options) {
    options = options || {};
    if (inflight) inflight.abort();
    var controller = new AbortController();
    inflight = controller;
    var scrollY = window.scrollY;
    setBusy(true);

    return fetch(url, { credentials: 'same-origin', signal: controller.signal })
      .then(function (res) {
        // Anything unexpected: let the browser handle it as a normal visit.
        if (!res.ok || res.redirected) { window.location.href = res.url || url; return null; }
        return res.text().then(function (html) { return { html: html, url: res.url || url }; });
      })
      .then(function (page) {
        if (!page) return;
        var doc = new DOMParser().parseFromString(page.html, 'text/html');
        var focusedId = document.activeElement && document.activeElement.id;
        var swapped = 0;
        regions().forEach(function (current) {
          var next = doc.getElementById(current.id);
          if (next && next.hasAttribute('data-swap-region')) {
            current.replaceWith(document.importNode(next, true));
            swapped++;
          }
        });
        if (!swapped) { window.location.href = page.url; return; }

        // Keep keyboard focus (e.g. in the search box) across the swap.
        var refocus = focusedId && document.getElementById(focusedId);
        if (refocus && refocus !== document.activeElement) refocus.focus({ preventScroll: true });

        if (doc.title) document.title = doc.title;
        if (options.push !== false) history.pushState({ swapNav: true }, '', page.url);

        // Instant, so the page's smooth-scroll CSS does not animate the restore.
        window.scrollTo({ top: scrollY, behavior: 'instant' });
        keepAnchorVisible(options.anchorId);
        document.dispatchEvent(new CustomEvent('swapnav:updated', { detail: { url: page.url } }));
      })
      .catch(function (err) {
        if (err && err.name === 'AbortError') return;
        window.location.href = url;
      })
      .then(function () {
        if (inflight === controller) { inflight = null; setBusy(false); }
      });
  }

  function isPlainLeftClick(e) {
    return e.button === 0 && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey;
  }

  // Pagination links, and any link opted in with data-swap-link.
  document.addEventListener('click', function (e) {
    var link = e.target.closest('.pagination a[href], a[data-swap-link][href]');
    if (!link || !isPlainLeftClick(e) || link.target === '_blank') return;
    var url = new URL(link.href, window.location.href);
    if (url.origin !== window.location.origin) return;
    e.preventDefault();
    var region = link.closest(REGION);
    navigate(url.href, { anchorId: region && region.id });
  });

  // GET search forms (role="search").
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form.matches('form[role="search"]') || (form.method || 'get').toLowerCase() !== 'get') return;
    e.preventDefault();
    var url = new URL(form.action || window.location.href, window.location.href);
    url.search = new URLSearchParams(new FormData(form)).toString();
    navigate(url.href);
  });

  // Back / Forward between swapped pages.
  history.replaceState({ swapNav: true }, '', window.location.href);
  window.addEventListener('popstate', function (e) {
    if (e.state && e.state.swapNav) navigate(window.location.href, { push: false });
  });
})();
