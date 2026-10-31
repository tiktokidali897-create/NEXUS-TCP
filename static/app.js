/* HASIB CODEX panel — vanilla JS */
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const IS_ADMIN = document.body.dataset.role === 'admin';
const TITLES = {
  dash: ['Dashboard', 'Overview of your bot and panel'], feat: ['Bot Features', 'Everything the bot can do — with example commands'], ctrl: ['Bot Control', 'Edit bot.txt — UID, password, nick — and start the bot'],
  cons: ['Live Console', 'Real-time output from the bot'], cmds: ['Commands', 'Search every command'],
  pages: ['Menu Pages', '20 pages × 15 commands — same as in-game /help'], time: ['World Time', 'Live clocks · same list as /time'],
  prem: ['Premium Tools', 'Shortcuts & extras'], acct: ['My Account', 'Change your password'], admin: ['Admin Panel', 'Manage who can log in']
};

/* ── helpers ── */
function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
function toast(msg, kind) { const t = el('div', kind || '', msg); $('#toast').appendChild(t); setTimeout(() => { t.style.opacity = 0; t.style.transition = '.4s'; setTimeout(() => t.remove(), 400) }, 3200); }
async function api(path, method = 'GET', body) {
  try {
    const r = await fetch(path, { method, headers: body ? { 'Content-Type': 'application/json' } : {}, body: body ? JSON.stringify(body) : undefined });
    if (r.status === 401) { location.href = '/login'; return { ok: false } }
    return await r.json();
  } catch (e) { return { ok: false, error: 'Network error' } }
}
function fmtUp(s) { if (!s) return '0s'; const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60); return (h ? h + 'h ' : '') + (m ? m + 'm ' : '') + (s % 60) + 's' }
async function busy(btn, fn) { const old = btn.innerHTML; btn.disabled = true; btn.innerHTML = '<span class="spin"></span>'; try { await fn() } finally { btn.disabled = false; btn.innerHTML = old } }

/* ── navigation ── */
function go(v) {
  if (!$('#v-' + v)) return;
  $$('.view').forEach(x => x.classList.toggle('on', x.id === 'v-' + v));
  $$('.nav').forEach(x => x.classList.toggle('on', x.dataset.v === v));
  $('#ttl').textContent = TITLES[v][0]; $('#sub').textContent = TITLES[v][1];
  $('#side').classList.remove('open'); $('#scrim').classList.remove('on');
  if (v === 'ctrl') loadConfig(); if (v === 'admin') loadUsers(); if (v === 'cons') pollLogs(true);
  location.hash = v; window.scrollTo({ top: 0, behavior: 'smooth' });
}
$$('.nav').forEach(b => b.onclick = () => go(b.dataset.v));
$('#burger').onclick = () => { $('#side').classList.add('open'); $('#scrim').classList.add('on') };
$('#scrim').onclick = () => { $('#side').classList.remove('open'); $('#scrim').classList.remove('on') };

/* ── status ── */
function countTo(el, to) { const from = +el.dataset.v || 0; if (from === to) return; el.dataset.v = to; const t0 = performance.now(); (function f(t) { const k = Math.min(1, (t - t0) / 600); el.textContent = Math.round(from + (to - from) * k); if (k < 1) requestAnimationFrame(f) })(t0) }
let ST = {};
async function refreshStatus() {
  const j = await api('/api/status'); if (!j.ok) return; ST = j;
  $('#topdot').classList.toggle('on', j.running); $('#toptxt').textContent = j.running ? 'Bot Online' : 'Bot Offline';
  $('#s-state').textContent = j.running ? 'Online' : 'Offline'; $('#s-state').style.color = j.running ? 'var(--ok)' : 'var(--bad)';
  $('#s-up').textContent = fmtUp(j.uptime); countTo($('#s-cmds'), j.commands || 300);
  $('#s-uid').textContent = j.uid && !/^0+$/.test(j.uid) ? j.uid : 'Not set'; $('#s-nick').textContent = j.nick; $('#s-reg').textContent = j.region; $('#s-mode').textContent = (j.mode || '').toUpperCase();
}
$$('[data-act]').forEach(b => b.onclick = () => busy(b, async () => {
  const j = await api('/api/bot/' + b.dataset.act, 'POST'); toast(j.message || j.error, j.ok ? 'good' : 'bad'); setTimeout(refreshStatus, 600)
}));
$$('[data-mode]').forEach(b => b.onclick = async () => { const j = await api('/api/mode', 'POST', { mode: b.dataset.mode }); toast(j.message || j.error, j.ok ? 'good' : 'bad'); refreshStatus() });

/* ── config ── */
function togglePw() { const p = $('#c-pw'); p.type = p.type === 'password' ? 'text' : 'password' }
async function loadConfig() {
  const j = await api('/api/config'); if (!j.ok) return;
  $('#c-uid').value = /^0+$/.test(j.uid) ? '' : j.uid; $('#c-nick').value = j.nick; $('#c-reg').value = j.region; $('#c-auto').checked = j.autostart;
  $('#pw-hint').textContent = j.has_password ? '✅ A password is saved (hidden). Type a new one only to replace it.' : '⚠ No password saved yet.';
}
async function saveCfg(start, btn) {
  await busy(btn, async () => {
    const body = { uid: $('#c-uid').value.trim(), nick: $('#c-nick').value.trim(), region: $('#c-reg').value, password: $('#c-pw').value.trim(), autostart: $('#c-auto').checked, start };
    const j = await api('/api/config', 'POST', body); toast(j.message || j.error, j.ok ? 'good' : 'bad');
    if (j.ok) { $('#c-pw').value = ''; loadConfig(); setTimeout(refreshStatus, 700) }
  });
}
$('#b-save').onclick = e => saveCfg(false, e.currentTarget);
$('#b-savestart').onclick = e => saveCfg(true, e.currentTarget);
$('#c-auto').onchange = async () => { const j = await api('/api/config', 'POST', { autostart: $('#c-auto').checked }); toast(j.ok ? 'Auto-start ' + ($('#c-auto').checked ? 'ON' : 'OFF') : j.error, j.ok ? 'good' : 'bad') };

/* ── logs ── */
let lastLog = 0, allLogs = [];
function addLine(box, r) {
  const d = el('div'); d.appendChild(el('i', '', r.t)); d.appendChild(el('span', r.src === 'bot' ? 'b' : 'w', r.msg)); box.appendChild(d);
}
async function pollLogs(reset) {
  if (reset) { lastLog = 0; allLogs = []; $('#log').textContent = ''; $('#mini-log').textContent = '' }
  const j = await api('/api/logs?since=' + lastLog); if (!j.ok) return; lastLog = j.last;
  if (!j.logs.length) return;
  allLogs.push(...j.logs); if (allLogs.length > 1500) allLogs = allLogs.slice(-1500);
  for (const r of j.logs) { addLine($('#log'), r); addLine($('#mini-log'), r) }
  for (const b of [$('#log'), $('#mini-log')]) { while (b.childElementCount > 1500) b.firstChild.remove(); if (b.id === 'mini-log' || $('#autoscroll').checked) b.scrollTop = b.scrollHeight }
}
function dlLogs() { const a = el('a'); a.href = URL.createObjectURL(new Blob([allLogs.map(r => `[${r.t}] ${r.msg}`).join('\n')], { type: 'text/plain' })); a.download = 'hasib-console.txt'; a.click() }
$('#dl').onclick = dlLogs; $('#p-dl').onclick = dlLogs;
$('#clr').onclick = async () => { await api('/api/logs/clear', 'POST'); pollLogs(true); toast('Console cleared', 'good') };

/* ── commands ── */
let CMDS = [], CAT = 'ALL';
const CATNAME = { MATCH: 'Squad', EMOTE: 'Emote', EVO: 'Evo', BADGE: 'Badge', INFO: 'Info', ADMIN: 'Admin', SOCIAL: 'Social', GAME: 'Games', ACTION: 'Actions', TOOLS: 'Tools', TIME: 'Time', FUN: 'Fun', ART: 'Art', FONT: 'Fonts', TEXT: 'Text', MATH: 'Math', CONVERT: 'Convert', BOT: 'Bot' };
async function loadCmds() {
  const j = await api('/api/commands'); CMDS = j.commands || [];
  const cats = ['ALL', ...new Set(CMDS.map(c => c.cat))]; const box = $('#cats'); box.textContent = '';
  for (const c of cats) { const t = el('button', 'tab' + (c === CAT ? ' on' : ''), c === 'ALL' ? 'All (' + CMDS.length + ')' : CATNAME[c] || c); t.onclick = () => { CAT = c; loadCmdsView(); $$('.tab', box).forEach(x => x.classList.toggle('on', x === t)) }; box.appendChild(t) }
  loadCmdsView(); buildPages();
}
function loadCmdsView() {
  const q = $('#q').value.toLowerCase().trim(), box = $('#cmdlist'); box.textContent = '';
  const rows = CMDS.filter(c => (CAT === 'ALL' || c.cat === CAT) && (!q || (c.cmd + ' ' + c.desc).toLowerCase().includes(q)));
  rows.slice(0, 400).forEach((c, i) => {
    const d = el('div', 'cmd'); d.style.animationDelay = Math.min(i * 8, 300) + 'ms'; d.appendChild(el('code', '', c.cmd));
    const s = el('small'); s.appendChild(el('span', '', c.desc)); s.appendChild(el('em', '', 'p' + c.page)); d.appendChild(s);
    d.onclick = () => { navigator.clipboard?.writeText(c.cmd.split(' ')[0]); toast('Copied ' + c.cmd.split(' ')[0], 'good') }; box.appendChild(d);
  });
  $('#cmdempty').style.display = rows.length ? 'none' : 'block';
}
$('#q').oninput = loadCmdsView;
function buildPages() {
  const box = $('#pagelist'); box.textContent = ''; const by = {};
  CMDS.forEach(c => (by[c.page] = by[c.page] || []).push(c));
  Object.keys(by).forEach(p => {
    const d = el('div', 'pg'); d.style.animationDelay = (p * 25) + 'ms'; const h = el('h4'); h.appendChild(el('span', '', 'MENU ' + String(p).padStart(2, '0'))); h.appendChild(el('span', '', by[p].length + ' cmds')); d.appendChild(h);
    const ul = el('ul'); by[p].forEach(c => { const li = el('li'); li.appendChild(el('b', '', c.cmd)); li.appendChild(el('span', '', c.desc)); ul.appendChild(li) }); d.appendChild(ul); box.appendChild(d);
  });
}

/* ── clocks ── */
let ZONES = [];
function clockText(tz) {
  const n = new Date();
  try {
    return {
      t: n.toLocaleTimeString('en-GB', { timeZone: tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }),
      d: n.toLocaleDateString('en-GB', { timeZone: tz, weekday: 'short', day: '2-digit', month: 'short' })
    }
  } catch (e) { return { t: '--:--:--', d: '' } }
}
async function loadZones() { const j = await api('/api/zones'); ZONES = j.zones || []; drawClocks(); drawMini() }
function drawClocks() {
  const q = $('#tq').value.toLowerCase().trim(), box = $('#clocks'); box.textContent = '';
  ZONES.filter(z => !q || (z.code + ' ' + z.label + ' ' + z.tz).toLowerCase().includes(q)).forEach((z, i) => {
    const d = el('div', 'clock'); d.style.animationDelay = i * 15 + 'ms'; d.appendChild(el('div', 'n', z.label)); const t = el('div', 't'); t.dataset.tz = z.tz; d.appendChild(t); const dd = el('div', 'd'); dd.dataset.tzd = z.tz; d.appendChild(dd); d.appendChild(el('div', 'd', '/time ' + z.code)); box.appendChild(d);
  }); tick();
}
function drawMini() { const box = $('#mini-clocks'); box.textContent = ''; ['bd', 'in', 'us', 'uk'].map(c => ZONES.find(z => z.code === c)).filter(Boolean).forEach(z => { const d = el('div', 'clock'); d.appendChild(el('div', 'n', z.label)); const t = el('div', 't'); t.dataset.tz = z.tz; d.appendChild(t); const dd = el('div', 'd'); dd.dataset.tzd = z.tz; d.appendChild(dd); box.appendChild(d) }); tick() }
function tick() { $$('[data-tz]').forEach(e => e.textContent = clockText(e.dataset.tz).t); $$('[data-tzd]').forEach(e => e.textContent = clockText(e.dataset.tzd).d) }
$('#tq').oninput = drawClocks;

/* ── premium extras ── */
$('#copylink').onclick = () => { navigator.clipboard?.writeText(location.origin); toast('Panel link copied: ' + location.origin, 'good') };
$('#p-rand').onclick = () => { if (!CMDS.length) return; const c = CMDS[Math.floor(Math.random() * CMDS.length)]; $('#p-out').textContent = '💡 Try  ' + c.cmd + '  —  ' + c.desc + '  (menu page ' + c.page + ')' };
$('#p-theme').onclick = () => {
  for (let i = 0; i < 60; i++) { const s = el('div'); Object.assign(s.style, { position: 'fixed', zIndex: 99, left: Math.random() * 100 + 'vw', top: '-12px', width: '9px', height: '14px', background: ['#00b7ff', '#2f7bff', '#8fe9ff', '#0057ff'][i % 4], borderRadius: '2px', transition: `transform ${1.6 + Math.random()}s ease-in, opacity 2s`, }); document.body.appendChild(s); requestAnimationFrame(() => { s.style.transform = `translateY(${105 + Math.random() * 10}vh) rotate(${Math.random() * 720}deg)`; s.style.opacity = 0 }); setTimeout(() => s.remove(), 3000) }
};

/* ── account / admin ── */
$('#a-save').onclick = e => busy(e.currentTarget, async () => { const j = await api('/api/password', 'POST', { old: $('#a-old').value, new: $('#a-new').value }); toast(j.message || j.error, j.ok ? 'good' : 'bad'); if (j.ok) { $('#a-old').value = ''; $('#a-new').value = '' } });
async function loadUsers() {
  if (!IS_ADMIN) return; const j = await api('/api/users'); const b = $('#u-body'); b.textContent = ''; if (!j.ok) return;
  j.users.forEach(u => { const tr = el('tr'); tr.appendChild(el('td', '', u.name)); const td = el('td'); td.appendChild(el('span', 'role ' + u.role, u.role)); tr.appendChild(td);
    const act = el('td'); if (u.name !== document.body.dataset.user) { const x = el('button', 'btn red sm', 'Delete'); x.onclick = async () => { if (!confirm('Delete ' + u.name + '?')) return; const r = await api('/api/users', 'DELETE', { name: u.name }); toast(r.message || r.error, r.ok ? 'good' : 'bad'); loadUsers() }; act.appendChild(x) } tr.appendChild(act); b.appendChild(tr) });
}
if (IS_ADMIN) $('#u-add').onclick = e => busy(e.currentTarget, async () => { const j = await api('/api/users', 'POST', { name: $('#u-name').value, password: $('#u-pw').value, role: $('#u-role').value }); toast(j.message || j.error, j.ok ? 'good' : 'bad'); if (j.ok) { $('#u-pw').value = ''; loadUsers() } });

/* ── bot features ── */
const FEATS = [
  ['🚀', 'Website Control', 'Enter UID + password on the website → saved in bot.txt → press Start and the bot goes online. Stop / Restart / Auto-start from the panel.', ['Save & Start', 'Restart', 'Auto-start']],
  ['📖', 'Help Menu (300 cmds)', '20 pages × 15 commands, generated from one registry. Open all pages or just one.', ['/help', '/help 7', '/search']],
  ['💃', 'Emotes', '417+ numbered emotes and 470 named emotes. Self emote, team-code emote, copy mode and emote menus.', ['/menu1', '/e', '/copy', '/dance', '/as']],
  ['🔥', 'Evo Emote Cycles', 'Evo gun emote cycles for you and the bot, with simple stop commands.', ['/ob55', '/max', '@max', '@evos', '/s']],
  ['👥', 'Squad Tools', 'Open squad, invite and group commands with the OB55 squad packets.', ['/3', '/4', '/5', '/6']],
  ['🏅', 'Badge & Share Cards', 'Badge commands and group / room / clan / title / workshop share cards sent to the current chat.', ['/s1', '/s5', '.s3', '.s6', '.s7']],
  ['🕒', 'Time & Date', 'World time for 54 countries, time difference, countdown and calendar helpers.', ['/time bd', '/time all', '/timediff', '/date', '/countdown']],
  ['🌦', 'Weather & Info', 'Weather, zodiac, YouTube and TikTok channel lookups and player info.', ['/weather', '/yt', '/tt', '/info', '/zodiac']],
  ['🧮', 'Math & Money', 'Calculator, percent, tip, VAT, EMI, simple & compound interest, geometry and number tools.', ['/calc', '/percent', '/emi', '/sqrt', '/isprime']],
  ['🔁', 'Converters', 'Temperature, distance, weight, volume, speed and data size converters.', ['/c2f', '/km2mi', '/kg2lb', '/gb2mb', '/bmi']],
  ['🔤', 'Text & Fonts', 'Stylish fonts, encoders and text tools: bold, script, gothic, bubble, base64, morse, binary and more.', ['/bold', '/script', '/b64', '/morse', '/translet']],
  ['😂', 'Fun & Games', 'Jokes, love/luck predictions, riddles, quotes, dice, slots, RPSLS, trivia and roasts.', ['/joke', '/love', '/luck', '/dhadha', '/slots', '/roast']],
  ['🎨', 'Art & Banners', 'ASCII art, boxes, pyramids, diamonds, banners and bordered name cards.', ['/banner', '/box', '/pyramid', '/name', '/catart']],
  ['🛡', 'Owner & Admin', 'Owner-only controls: restart, PC/phone login mode, message design swap and admin list.', ['/restart', '/pc', '/phone', '/admin', '/display_msg']],
  ['🤖', 'Bot Status', 'Ping, uptime, version, command count and random command ideas.', ['/ping', '/uptime', '/botinfo', '/cmdcount', '/randcmd']],
  ['🔒', 'Secure Panel', 'Salted-hash logins, rate-limited login, admin user manager and a live console with download.', ['Live Console', 'Admin Panel', 'My Account']]
];
function buildFeats() {
  const box = $('#featlist'); if (!box) return; box.textContent = '';
  FEATS.forEach((f, i) => {
    const d = el('div', 'feat'); d.style.animationDelay = i * 40 + 'ms';
    d.appendChild(el('div', 'fi', f[0])); d.appendChild(el('h4', '', f[1])); d.appendChild(el('p', '', f[2]));
    const cs = el('div', 'cs');
    f[3].forEach(c => { const k = el('code', '', c); if (c.startsWith('/') || c.startsWith('@') || c.startsWith('.')) k.onclick = () => { navigator.clipboard?.writeText(c); toast('Copied ' + c, 'good') }; cs.appendChild(k) });
    d.appendChild(cs); box.appendChild(d);
  });
}
buildFeats();

/* ── boot ── */
refreshStatus(); loadCmds(); loadZones(); pollLogs(true);
setInterval(refreshStatus, 4000); setInterval(pollLogs, 2000); setInterval(tick, 1000);
const h = location.hash.slice(1); if (h && $('#v-' + h)) go(h);
