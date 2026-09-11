(() => {
  let attempts = 0;

  function applyHomeNavigation() {
    attempts += 1;
    const nav = document.querySelector('.class-tools.nav-redesigned');
    const homeButton = document.getElementById('learnerHomeButton');
    const todayButton = document.getElementById('dailyPlanButton');
    const chatButton = document.getElementById('chatButton');
    const dailyPlanArea = document.getElementById('dailyPlanArea');

    if (!nav || !homeButton || !todayButton || !chatButton) {
      if (attempts < 40) setTimeout(applyHomeNavigation, 150);
      return;
    }
    if (nav.dataset.homeNavReady === 'true') return;

    todayButton.hidden = true;
    todayButton.setAttribute('aria-hidden', 'true');
    todayButton.tabIndex = -1;
    todayButton.style.display = 'none';

    homeButton.textContent = 'Home';
    homeButton.setAttribute('aria-label', 'Open learning home');
    nav.insertBefore(homeButton, chatButton);
    nav.dataset.homeNavReady = 'true';

    function syncDailyPlanHomeState() {
      if (!dailyPlanArea) return;
      const planOpen = !dailyPlanArea.classList.contains('hidden');
      const learnerHome = document.getElementById('learnerHome');
      const homeOpen = learnerHome && !learnerHome.classList.contains('hidden');
      if (planOpen || homeOpen) {
        homeButton.classList.add('active');
        homeButton.setAttribute('aria-current', 'page');
      } else if (homeButton.classList.contains('active')) {
        homeButton.classList.remove('active');
        homeButton.removeAttribute('aria-current');
      }
    }

    if (dailyPlanArea) {
      new MutationObserver(syncDailyPlanHomeState).observe(dailyPlanArea, {
        attributes: true,
        attributeFilter: ['class']
      });
    }
    todayButton.addEventListener('click', () => requestAnimationFrame(syncDailyPlanHomeState));
    homeButton.addEventListener('click', () => requestAnimationFrame(syncDailyPlanHomeState));
  }

  applyHomeNavigation();
})();
