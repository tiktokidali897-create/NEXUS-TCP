/* Footer: live time + weather (Open-Meteo, no API key). Falls back to Dhaka if location is blocked. */
(function () {
  const $ = s => document.querySelector(s);
  function tickTime() {
    const n = new Date();
    const t = $('#f-time'), d = $('#f-date');
    if (t) t.textContent = n.toLocaleTimeString('en-GB', { hour12: false });
    if (d) d.textContent = n.toLocaleDateString('en-GB', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' });
  }
  tickTime(); setInterval(tickTime, 1000);

  const WMO = {
    0: ['☀️', 'Clear sky'], 1: ['🌤', 'Mostly clear'], 2: ['⛅', 'Partly cloudy'], 3: ['☁️', 'Overcast'],
    45: ['🌫', 'Fog'], 48: ['🌫', 'Rime fog'], 51: ['🌦', 'Light drizzle'], 53: ['🌦', 'Drizzle'], 55: ['🌧', 'Heavy drizzle'],
    61: ['🌧', 'Light rain'], 63: ['🌧', 'Rain'], 65: ['🌧', 'Heavy rain'], 71: ['🌨', 'Light snow'], 73: ['🌨', 'Snow'], 75: ['❄️', 'Heavy snow'],
    80: ['🌦', 'Rain showers'], 81: ['🌧', 'Rain showers'], 82: ['⛈', 'Violent showers'], 95: ['⛈', 'Thunderstorm'], 96: ['⛈', 'Thunder + hail'], 99: ['⛈', 'Thunder + hail']
  };
  async function load(lat, lon, label) {
    try {
      const u = 'https://api.open-meteo.com/v1/forecast?latitude=' + lat + '&longitude=' + lon +
        '&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&timezone=auto';
      const j = await (await fetch(u)).json(), c = j.current;
      const w = WMO[c.weather_code] || ['🌡', 'Weather'];
      $('#w-ic').textContent = w[0];
      $('#w-t').textContent = Math.round(c.temperature_2m) + '°C';
      $('#w-d').innerHTML = w[1] + ' • Feels ' + Math.round(c.apparent_temperature) + '°C<br>💧 ' + c.relative_humidity_2m + '% • 💨 ' + Math.round(c.wind_speed_10m) + ' km/h • ' + label;
    } catch (e) {
      $('#w-ic').textContent = '⚠️'; $('#w-t').textContent = '--°C'; $('#w-d').textContent = 'Weather unavailable (check internet)';
    }
  }
  const dhaka = () => load(23.8103, 90.4125, 'Dhaka');
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(p => load(p.coords.latitude.toFixed(3), p.coords.longitude.toFixed(3), 'Your location'), dhaka, { timeout: 6000 });
  } else dhaka();
  setInterval(() => { navigator.geolocation ? navigator.geolocation.getCurrentPosition(p => load(p.coords.latitude.toFixed(3), p.coords.longitude.toFixed(3), 'Your location'), dhaka, { timeout: 6000 }) : dhaka() }, 15 * 60 * 1000);
})();
