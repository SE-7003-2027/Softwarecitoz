/* =========================================
   CHAOS - Lógica de la pantalla "Mi perfil"
   ========================================= */

// =========================================
// MOCK: viene de GET /profiles/{steam_id}  →  ProfileOut
// =========================================
const MOCK_PROFILE = {
    steam_id: '76561198000000000',
    name: 'Jugador de ejemplo',
    real_name: null,                       // perfil privado
    profile_url: 'https://steamcommunity.com/',
    avatar_url: 'https://placehold.co/120x120/25283b/ffffff?text=PLAYER',
    status: 'online',                      // PersonaStatus: online | offline | busy | away
    visibility: 'public',                  // Visibility: public | friends_only | private
    country_code: null,                    // 'MX', 'US', ...
    created_at: '2015-06-01T00:00:00Z',
    last_online_at: '2026-10-08T12:00:00Z',
    currently_playing: null               // { app_id, name } o null
    // account_age_years lo calcula el backend, aquí lo derivamos
};

// =========================================
// HELPERS
// =========================================

const STATUS_LABELS = {
    online:  '● En línea',
    offline: '● Desconectado',
    busy:    '● Ocupado',
    away:    '● Ausente'
};

const STATUS_CLASSES = {
    online:  'status-online',
    offline: 'status-offline',
    busy:    'status-busy',
    away:    'status-away'
};

// Bandera a partir del código ISO (funciona con cualquier código de 2 letras)
function flagFromCountry(code) {
    if (!code || code.length !== 2) return null;
    return code.toUpperCase().replace(/./g, c =>
        String.fromCodePoint(127397 + c.charCodeAt(0))
    );
}

// "hace 2 días", "hace 3 h", etc.
function timeAgo(isoString) {
    if (!isoString) return null;
    const then = new Date(isoString).getTime();
    const diff = Date.now() - then;

    const min  = Math.floor(diff / 60000);
    const hrs  = Math.floor(min / 60);
    const days = Math.floor(hrs / 24);

    if (min < 1)  return 'hace unos segundos';
    if (min < 60) return `hace ${min} min`;
    if (hrs < 24) return `hace ${hrs} h`;
    if (days < 30) return `hace ${days} ${days === 1 ? 'día' : 'días'}`;
    const months = Math.floor(days / 30);
    if (months < 12) return `hace ${months} ${months === 1 ? 'mes' : 'meses'}`;
    return `hace ${Math.floor(months / 12)} años`;
}

// Años completos desde una fecha ISO
function yearsSince(isoString) {
    if (!isoString) return null;
    const then = new Date(isoString);
    const now = new Date();
    let years = now.getFullYear() - then.getFullYear();
    const m = now.getMonth() - then.getMonth();
    if (m < 0 || (m === 0 && now.getDate() < then.getDate())) years--;
    return years;
}

// =========================================
// RENDER: ZONA A (Steam, read-only)
// =========================================

function renderSteamProfile(profile) {
    // Avatar
    const avatar = document.getElementById('steam-avatar');
    if (avatar) {
        avatar.src = profile.avatar_url || 'https://placehold.co/120x120/25283b/ffffff?text=?';
        avatar.alt = `Avatar de ${profile.name}`;
    }

    // Nombre y nombre real
    document.getElementById('steam-name').textContent = profile.name || 'Usuario de Steam';
    const realName = document.getElementById('steam-real-name');
    realName.textContent = profile.real_name || 'Nombre real no disponible';
    realName.classList.toggle('muted', !profile.real_name);

    // Estado
    const statusEl = document.getElementById('steam-status');
    statusEl.textContent = STATUS_LABELS[profile.status] || STATUS_LABELS.offline;
    // Limpiar clases previas y poner la correcta
    statusEl.classList.remove('status-online', 'status-offline', 'status-busy', 'status-away');
    statusEl.classList.add(STATUS_CLASSES[profile.status] || 'status-offline');

    // País
    const countryEl = document.getElementById('steam-country');
    if (profile.country_code) {
        const flag = flagFromCountry(profile.country_code);
        countryEl.textContent = `${flag} ${profile.country_code}`;
    } else {
        countryEl.textContent = 'País no disponible';
    }

    // Steam ID
    document.getElementById('steam-id').textContent = profile.steam_id;

    // Antigüedad y última conexión
    const age = yearsSince(profile.created_at);
    document.getElementById('account-age').textContent =
        age !== null ? `Cuenta creada hace ${age} ${age === 1 ? 'año' : 'años'}` :
                       'Antigüedad no disponible';

    const lastOnline = timeAgo(profile.last_online_at);
    document.getElementById('last-online').textContent =
        lastOnline ? `Última conexión ${lastOnline}` :
                     'Última conexión no disponible';

    // Link a Steam
    const link = document.getElementById('steam-profile-link');
    if (profile.profile_url) {
        link.href = profile.profile_url;
        link.hidden = false;
    } else {
        link.hidden = true;
    }

    // Card "Jugando ahora"
    const playing = document.getElementById('currently-playing');
    if (profile.currently_playing) {
        document.getElementById('current-game-name').textContent =
            profile.currently_playing.name;
        playing.hidden = false;
    } else {
        playing.hidden = true;
    }
}

// =========================================
// FORMULARIO (Zona B)
// =========================================

function fillForm(profile) {
    // Visibility
    const vis = document.getElementById('visibility');
    if (vis && profile.visibility) vis.value = profile.visibility;
}

function handleFormSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const data = {
        username: form.username.value.trim(),
        bio: form.bio.value.trim(),
        visibility: form.visibility.value,
        preferred_games: Array.from(
            form.querySelectorAll('input[name="preferred-games"]:checked')
        ).map(cb => Number(cb.value)),
        schedule: {}
    };

    // Horarios: por cada día marcado, lee su rango inicio-fin
    data.schedule = {};
    form.querySelectorAll('input[name="days"]:checked').forEach(dayCb => {
    const day = dayCb.value;
    const start = form.elements[`${day}-start`]?.value || null;
    const end   = form.elements[`${day}-end`]?.value   || null;

    // Solo guarda si ambos extremos existen y el rango es coherente
    if (start && end && start < end) {
        data.schedule[day] = { start, end };
    }
});
    // TODO: reemplazar por fetch('PATCH /profiles/me', { method:'PATCH', body: JSON.stringify(data) })
    console.log('Datos a enviar al backend:', data);

    const msg = document.getElementById('save-message');
    msg.textContent = '✓ Cambios guardados (simulado).';
    msg.style.color = 'var(--success)';
    setTimeout(() => { msg.textContent = ''; }, 3000);
}

function handleFormReset() {
    // Esperar al siguiente tick para que el reset nativo se aplique primero
    setTimeout(() => {
        fillForm(MOCK_PROFILE);
        const msg = document.getElementById('save-message');
        msg.textContent = 'Formulario restablecido.';
        msg.style.color = 'var(--muted)';
        setTimeout(() => { msg.textContent = ''; }, 2500);
    }, 0);
}

// =========================================
// INIT
// =========================================

document.addEventListener('DOMContentLoaded', () => {
    renderSteamProfile(MOCK_PROFILE);
    fillForm(MOCK_PROFILE);

    const form = document.getElementById('profile-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
        form.addEventListener('reset', handleFormReset);
    }
});