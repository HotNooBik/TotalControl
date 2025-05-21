// Скрипт для определения часового пояса пользователя
const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

fetch(urls.setTimezone, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf,
        'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({ timezone: timeZone })
});