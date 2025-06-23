document.addEventListener('DOMContentLoaded', function() {
    loadReservations();
    document.getElementById('form').addEventListener('submit', reserveSlot);
});

function getReservations() {
    return JSON.parse(localStorage.getItem('reservations') || '{}');
}

function saveReservations(reservations) {
    localStorage.setItem('reservations', JSON.stringify(reservations));
}

function loadReservations() {
    const data = getReservations();
    const list = document.getElementById('reservations');
    list.innerHTML = '';
    Object.keys(data).forEach(date => {
        data[date].forEach(r => {
            const li = document.createElement('li');
            li.className = 'reservation-item';
            li.textContent = `${date} | ${r.start} - ${r.end} | ${r.user}`;
            const cancelBtn = document.createElement('button');
            cancelBtn.textContent = 'Cancel';
            cancelBtn.onclick = () => cancelReservation(date, r.start, r.end, r.user);
            li.appendChild(cancelBtn);
            list.appendChild(li);
        });
    });
}

function reserveSlot(e) {
    e.preventDefault();
    const date = document.getElementById('date').value;
    const start = document.getElementById('start').value;
    const end = document.getElementById('end').value;
    const user = document.getElementById('user').value;
    let reservations = getReservations();
    if (!reservations[date]) reservations[date] = [];
    // Check for conflicts
    for (const r of reservations[date]) {
        if (!(end <= r.start || start >= r.end)) {
            document.getElementById('form-message').textContent = 'Time slot already reserved.';
            return;
        }
    }
    reservations[date].push({start, end, user});
    saveReservations(reservations);
    document.getElementById('form-message').textContent = 'Reservation successful!';
    loadReservations();
}

function cancelReservation(date, start, end, user) {
    let reservations = getReservations();
    if (reservations[date]) {
        const before = reservations[date].length;
        reservations[date] = reservations[date].filter(r => !(r.start === start && r.end === end && r.user === user));
        if (reservations[date].length !== before) {
            saveReservations(reservations);
            loadReservations();
            return;
        }
    }
    alert('Reservation not found.');
}
