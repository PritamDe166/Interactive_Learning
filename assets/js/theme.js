/* =========================================================================
   theme.js — light/dark mode for every page.
   - Dark by default; the viewer's choice is remembered in localStorage.
   - Load it in <head> (not deferred) so the saved theme applies before paint.
   - Any element with  data-theme-toggle  becomes the toggle button.
   - Pages can listen for  document.addEventListener('themechange', ...)
   ========================================================================= */
(function () {
  var KEY = 'ie-theme';
  var root = document.documentElement;

  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function write(v) { try { localStorage.setItem(KEY, v); } catch (e) { /* storage blocked: still works for this visit */ } }

  root.setAttribute('data-theme', read() === 'light' ? 'light' : 'dark');

  var ICONS = {
    sun: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    moon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/></svg>'
  };

  function current() { return root.getAttribute('data-theme'); }

  function paint(btn) {
    var next = current() === 'dark' ? 'light' : 'dark';
    btn.innerHTML = (next === 'light' ? ICONS.sun : ICONS.moon) + '<span>' + (next === 'light' ? 'Light' : 'Dark') + '</span>';
    btn.setAttribute('aria-label', 'Switch to ' + next + ' mode');
    btn.title = 'Switch to ' + next + ' mode';
  }

  function apply(theme) {
    root.setAttribute('data-theme', theme);
    write(theme);
    document.querySelectorAll('[data-theme-toggle]').forEach(paint);
    document.dispatchEvent(new CustomEvent('themechange', { detail: { theme: theme } }));
  }

  window.ExplainerTheme = { get: current, set: apply };

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      paint(btn);
      btn.addEventListener('click', function () { apply(current() === 'dark' ? 'light' : 'dark'); });
    });
  });
})();
