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

})();
