from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# In-memory storage for user accounts
users = {
    "alice": {"pin_number": "1234", "bank_balance": 10000},
    "bob": {"pin_number": "5678", "bank_balance": 5000},
    "charlie": {"pin_number": "9012", "bank_balance": 15000}
}

# Serve frontend files
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# API Routes
@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    name = data.get('name')
    pin_number = data.get('pin_number')
    
    if not name or not pin_number:
        return jsonify({"error": "Name and pin_number are required"}), 400
    
    if name not in users:
        return jsonify({"error": "User not found"}), 404
    
    if users[name]['pin_number'] != pin_number:
        return jsonify({"error": "Invalid PIN"}), 401
    
    return jsonify({
        "message": "Authentication successful",
        "name": name,
        "bank_balance": users[name]['bank_balance']
    }), 200

@app.route('/api/bank-transfer', methods=['POST'])
def bank_transfer():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    sender_name = data.get('sender_name')
    sender_pin = data.get('sender_pin')
    recipient_name = data.get('recipient_name')
    amount = data.get('amount')
    
    if not all([sender_name, sender_pin, recipient_name, amount]):
        return jsonify({"error": "All fields are required"}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
    except ValueError:
        return jsonify({"error": "Amount must be a valid number"}), 400
    
    if sender_name not in users:
        return jsonify({"error": "Sender not found"}), 404
    
    if users[sender_name]['pin_number'] != sender_pin:
        return jsonify({"error": "Invalid sender PIN"}), 401
    
    if recipient_name not in users:
        return jsonify({"error": "Recipient not found"}), 404
    
    if users[sender_name]['bank_balance'] < amount:
        return jsonify({"error": "Insufficient funds"}), 400
    
    # Perform transfer
    users[sender_name]['bank_balance'] -= amount
    users[recipient_name]['bank_balance'] += amount
    
    return jsonify({
        "message": "Transfer successful",
        "sender": sender_name,
        "recipient": recipient_name,
        "amount_transferred": amount,
        "sender_new_balance": users[sender_name]['bank_balance'],
        "recipient_new_balance": users[recipient_name]['bank_balance']
    }), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')