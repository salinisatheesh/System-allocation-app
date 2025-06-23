from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timedelta
import json
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)

# In-memory storage for reservations: {date: [{start, end, user}]}
reservations = {}

RESERVATION_FILE = 'reservations.json'

# Helper to save reservations to file
def save_reservations_to_file():
    with open(RESERVATION_FILE, 'w') as f:
        json.dump(reservations, f, indent=2)

# Helper to send reservation file via email
def send_reservation_email():
    EMAIL_ADDRESS = 'your_email@example.com'  # TODO: Replace with your email
    EMAIL_PASSWORD = 'your_password'          # TODO: Replace with your password
    RECIPIENT_EMAIL = 'recipient@example.com' # TODO: Replace with recipient email
    
    msg = EmailMessage()
    msg['Subject'] = 'Updated Reservations File'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg.set_content('Attached is the latest reservations file.')

    # Attach the file
    with open(RESERVATION_FILE, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(RESERVATION_FILE)
    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    # Send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:  # Change SMTP server if needed
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    return jsonify(reservations)

@app.route('/api/reserve', methods=['POST'])
def reserve():
    data = request.json
    date = data['date']
    start = data['start']
    end = data['end']
    user = data['user']
    if date not in reservations:
        reservations[date] = []
    # Check for conflicts
    for r in reservations[date]:
        if not (end <= r['start'] or start >= r['end']):
            return jsonify({'success': False, 'message': 'Time slot already reserved.'}), 409
    reservations[date].append({'start': start, 'end': end, 'user': user})
    save_reservations_to_file()
    try:
        send_reservation_email()
    except Exception as e:
        return jsonify({'success': True, 'warning': f'Email not sent: {str(e)}'})
    return jsonify({'success': True})

@app.route('/api/cancel', methods=['POST'])
def cancel():
    data = request.json
    date = data['date']
    start = data['start']
    end = data['end']
    user = data['user']
    if date in reservations:
        before = len(reservations[date])
        reservations[date] = [r for r in reservations[date] if not (r['start'] == start and r['end'] == end and r['user'] == user)]
        after = len(reservations[date])
        if before != after:
            return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Reservation not found.'}), 404

if __name__ == '__main__':
    # Run on all network interfaces for web access
    app.run(host="0.0.0.0", port=5000, debug=False)
