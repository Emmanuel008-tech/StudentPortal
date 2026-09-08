/**
 * CampusPulse — Student Dashboard Interactivity (dashboard.js)
 * Mobile sidebar drawer, active view toggling, and alerts handling.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Sidebar Toggle
  const menuBtn = document.getElementById('mobile-drawer-toggle');
  const sidebar = document.getElementById('dashboard-sidebar');

  if (menuBtn && sidebar) {
    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('is-open');
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('is-open') && !sidebar.contains(e.target) && e.target !== menuBtn) {
        sidebar.classList.remove('is-open');
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && sidebar.classList.contains('is-open')) {
        sidebar.classList.remove('is-open');
      }
    });
  }

  // 2. Tab / Anchor navigation highlighting
  const sidebarLinks = document.querySelectorAll('.sidebar-link[data-target]');
  sidebarLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      sidebarLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');

      if (window.innerWidth < 992 && sidebar) {
        sidebar.classList.remove('is-open');
      }
    });
  });

  // 3. Alert dismissal
  const alertCloseBtns = document.querySelectorAll('.alert-close-btn');
  alertCloseBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-6px)';
        alert.style.transition = 'all 200ms ease';
        setTimeout(() => alert.remove(), 220);
      }
    });
  });
});
