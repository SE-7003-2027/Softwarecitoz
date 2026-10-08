/* =========================================
   CHAOS - Pantalla "Mi biblioteca"
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================
    // 1. TABS PRINCIPALES
    // =========================================
    document.querySelectorAll('[data-tab]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-tab]').forEach(b => {
                b.classList.toggle('active', b === btn);
                b.setAttribute('aria-selected', b === btn);
            });
            document.querySelectorAll('.tab-panel').forEach(p => p.hidden = true);
            const target = document.getElementById(`panel-${btn.dataset.tab}`);
            if (target) target.hidden = false;
        });
    });

    // =========================================
    // 2. SUB-TABS JUEGOS DE MESA
    // =========================================
    document.querySelectorAll('[data-subtab]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-subtab]').forEach(b => {
                b.classList.toggle('active', b === btn);
                b.setAttribute('aria-selected', b === btn);
            });
            const owned = document.getElementById('panel-owned');
            const inter = document.getElementById('panel-interested');
            if (owned) owned.hidden = btn.dataset.subtab !== 'owned';
            if (inter) inter.hidden = btn.dataset.subtab !== 'interested';
        });
    });

    // =========================================
    // 3. MOCK: LIBRARYOUT (videojuegos de Steam)
    // =========================================
    const MOCK_LIBRARY = {
        game_count: 2,
        total_playtime: '120 h',
        games: [
            {
                app_id: 570, name: 'Dota 2',
                icon_url: 'https://placehold.co/220x124/25283b/a78bfa?text=Dota+2',
                playtime_total: '100 h',
                playtime_last_two_weeks: '2 h esta quincena',
                last_played_at: 'hace 3 días',
                platforms: ['Windows', 'Linux']
            },
            {
                app_id: 730, name: 'Counter-Strike 2',
                icon_url: 'https://placehold.co/220x124/25283b/a78bfa?text=CS2',
                playtime_total: '20 h',
                playtime_last_two_weeks: null,
                last_played_at: 'hace 1 mes',
                platforms: ['Windows']
            }
        ]
    };

    const gameCountEl    = document.getElementById('game-count');
    const totalPlaytimeEl = document.getElementById('total-playtime');
    const steamGamesEl   = document.getElementById('steam-games');

    if (gameCountEl)     gameCountEl.textContent = MOCK_LIBRARY.game_count;
    if (totalPlaytimeEl) totalPlaytimeEl.textContent = MOCK_LIBRARY.total_playtime;

    if (steamGamesEl) {
        steamGamesEl.innerHTML = MOCK_LIBRARY.games.map(g => `
            <article class="game-card">
                <a class="game-cover"
                   href="https://store.steampowered.com/app/${g.app_id}"
                   target="_blank" rel="noopener">
                    <img src="${g.icon_url}" alt="${g.name}">
                </a>
                <div class="game-body">
                    <h3 class="game-name">${g.name}</h3>
                    <p class="game-playtime">${g.playtime_total} jugadas</p>
                    ${g.playtime_last_two_weeks
                        ? `<p class="game-recent">${g.playtime_last_two_weeks}</p>`
                        : ''}
                    <p class="game-last">Última vez: ${g.last_played_at}</p>
                    <div class="game-platforms">
                        ${g.platforms.map(p => `<span>${p}</span>`).join('')}
                    </div>
                </div>
            </article>
        `).join('');
    }

    // =========================================
    // 4. JUEGOS DE MESA (mock CRUD)
    // =========================================
    const BOARDGAME_CATALOG = [
        { id: 'catan',       name: 'Catan',          players: '3–4', duration: '60–120 min' },
        { id: 'carcassonne', name: 'Carcassonne',    players: '2–5', duration: '30–45 min' },
        { id: 'azul',        name: 'Azul',           players: '2–4', duration: '30–45 min' },
        { id: 'ticket',      name: 'Ticket to Ride', players: '2–5', duration: '45–60 min' },
        { id: 'gloomhaven',  name: 'Gloomhaven',     players: '1–4', duration: '60–120 min' },
        { id: 'wingspan',    name: 'Wingspan',       players: '1–5', duration: '40–70 min' }
    ];

    const ownedGames = ['catan'];
    const interestedGames = ['carcassonne'];

    function renderOwned() {
        const list = document.getElementById('owned-games');
        const empty = document.getElementById('owned-empty');
        if (!list) return;
        list.innerHTML = ownedGames.map(id => {
            const g = BOARDGAME_CATALOG.find(x => x.id === id);
            if (!g) return '';
            return `
                <article class="boardgame-card">
                    <img src="https://placehold.co/60x60/25283b/a78bfa?text=${encodeURIComponent(g.name[0])}" alt="">
                    <div>
                        <h4>${g.name}</h4>
                        <p>${g.players} jugadores · ${g.duration}</p>
                    </div>
                    <button class="remove-btn" data-remove="${g.id}" aria-label="Quitar">×</button>
                </article>`;
        }).join('');
        if (empty) empty.hidden = ownedGames.length > 0;
    }

    function renderInterested() {
        const list = document.getElementById('interested-games');
        const empty = document.getElementById('interested-empty');
        if (!list) return;
        list.innerHTML = interestedGames.map(id => {
            const g = BOARDGAME_CATALOG.find(x => x.id === id);
            if (!g) return '';
            return `
                <article class="boardgame-card">
                    <img src="https://placehold.co/60x60/25283b/a78bfa?text=${encodeURIComponent(g.name[0])}" alt="">
                    <div>
                        <h4>${g.name}</h4>
                        <p>${g.players} jugadores · ${g.duration}</p>
                    </div>
                    <button class="remove-btn" data-remove-interested="${g.id}" aria-label="Quitar">×</button>
                </article>`;
        }).join('');
        if (empty) empty.hidden = interestedGames.length > 0;
    }

    function wireSearch(inputId, suggestionsId, onPick) {
        const input = document.getElementById(inputId);
        const box   = document.getElementById(suggestionsId);
        if (!input || !box) return;

        input.addEventListener('input', () => {
            const q = input.value.trim().toLowerCase();
            if (!q) { box.hidden = true; return; }
            const matches = BOARDGAME_CATALOG.filter(g => g.name.toLowerCase().includes(q));
            if (!matches.length) { box.hidden = true; return; }
            box.innerHTML = matches.map(g =>
                `<li data-id="${g.id}">${g.name} <small style="opacity:.6">${g.players}p · ${g.duration}</small></li>`
            ).join('');
            box.hidden = false;
        });

        box.addEventListener('click', e => {
            const li = e.target.closest('li');
            if (!li) return;
            onPick(li.dataset.id);
            input.value = '';
            box.hidden = true;
        });

        document.addEventListener('click', e => {
            if (!box.contains(e.target) && e.target !== input) box.hidden = true;
        });
    }

    wireSearch('owned-search', 'owned-suggestions', id => {
        if (!ownedGames.includes(id)) ownedGames.push(id);
        renderOwned();
    });

    wireSearch('interested-search', 'interested-suggestions', id => {
        if (!interestedGames.includes(id)) interestedGames.push(id);
        renderInterested();
    });

    const addOwnedBtn = document.getElementById('add-owned');
    if (addOwnedBtn) {
        addOwnedBtn.addEventListener('click', () => {
            const input = document.getElementById('owned-search');
            const q = (input?.value || '').trim().toLowerCase();
            if (!q) return;
            const g = BOARDGAME_CATALOG.find(x => x.name.toLowerCase() === q)
                   || BOARDGAME_CATALOG.find(x => x.name.toLowerCase().includes(q));
            if (g && !ownedGames.includes(g.id)) ownedGames.push(g.id);
            if (input) input.value = '';
            renderOwned();
        });
    }

    const addInterestedBtn = document.getElementById('add-interested');
    if (addInterestedBtn) {
        addInterestedBtn.addEventListener('click', () => {
            const input = document.getElementById('interested-search');
            const q = (input?.value || '').trim().toLowerCase();
            if (!q) return;
            const g = BOARDGAME_CATALOG.find(x => x.name.toLowerCase() === q)
                   || BOARDGAME_CATALOG.find(x => x.name.toLowerCase().includes(q));
            if (g && !interestedGames.includes(g.id)) interestedGames.push(g.id);
            if (input) input.value = '';
            renderInterested();
        });
    }

    document.addEventListener('click', e => {
        const rmOwned      = e.target.closest('[data-remove]');
        const rmInterested = e.target.closest('[data-remove-interested]');
        if (rmOwned) {
            const i = ownedGames.indexOf(rmOwned.dataset.remove);
            if (i > -1) ownedGames.splice(i, 1);
            renderOwned();
        }
        if (rmInterested) {
            const i = interestedGames.indexOf(rmInterested.dataset.removeInterested);
            if (i > -1) interestedGames.splice(i, 1);
            renderInterested();
        }
    });

    renderOwned();
    renderInterested();
});