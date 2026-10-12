// Native links and details remain usable when JavaScript is unavailable.
(() => {
  const menu = document.querySelector('.site-menu');
  const summary = menu.querySelector('summary');
  const closeMenuButton = menu.querySelector('.menu-close');
  closeMenuButton.hidden = false;

  const closeMenu = (restoreFocus = false) => {
    menu.open = false;
    if (restoreFocus) summary.focus();
  };
  closeMenuButton.addEventListener('click', () => closeMenu(true));
  document.addEventListener('click', event => {
    if (menu.open && !menu.contains(event.target)) closeMenu();
  });
  menu.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      closeMenu(true);
      event.preventDefault();
    }
  });
  // The menu is a non-modal disclosure. Tab can continue to the page normally.
  menu.addEventListener('focusout', () => {
    requestAnimationFrame(() => {
      if (menu.open && !menu.contains(document.activeElement)) closeMenu();
    });
  });

  const dialog = document.querySelector('.lightbox');
  const image = dialog.querySelector('.lightbox-img');
  const caption = dialog.querySelector('.lightbox-caption');
  const closeButton = dialog.querySelector('.lightbox-close');
  let opener = null;
  if (typeof dialog.showModal !== 'function') return;

  document.querySelectorAll('[data-photo]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      const thumbnail = link.querySelector('img');
      opener = link;
      image.src = link.href;
      image.alt = thumbnail.alt;
      caption.textContent = thumbnail.alt;
      dialog.showModal();
      closeButton.focus();
    });
  });
  closeButton.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target === dialog || event.target.classList.contains('lightbox-content')) dialog.close();
  });
  dialog.addEventListener('close', () => {
    image.removeAttribute('src');
    if (opener) opener.focus({ preventScroll: true });
  });
})();
