/* === appbar.js: include chung appbar admin/customer qua fetch === */
(function () {
  // find or create placeholder at the top of <body>
  function mountAppbar(role) {
    const placeholder = document.querySelector('[data-appbar-placeholder]');
    if (!placeholder) return;
    fetch('/static/components/appbar.html')
      .then(r => r.text())
      .then(html => {
        // Tách đoạn <header> cho role phù hợp
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const target = doc.querySelector(`header[data-appbar="${role}"]`);
        if (!target) return;
        placeholder.replaceWith(target);
        // active highlight
        const current = location.pathname.replace(/\/$/, '');
        target.querySelectorAll('nav a').forEach(a => {
          try {
            const u = new URL(a.getAttribute('href'), location.origin);
            if (u.pathname.replace(/\/$/, '') === current) {
              a.style.background = 'rgba(56, 189, 248, 0.15)';
              a.style.color = 'var(--primary-light)';
            }
          } catch (e) {}
        });
      });
  }
  window.mountAppbar = mountAppbar;
})();
