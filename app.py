from flask import Flask, jsonify, request, send_from_directory
import os

app = Flask(__name__)

# Initialize the list of 80 seats (7 seats per row, last row with 3 seats)
seats = [{'seat_id': i, 'is_booked': False, 'row_number': (i-1)//7 + 1} for i in range(1, 81)]
seats[-1]['row_number'] = 12  # Last row (seat 78, 79, 80) manually set to row 12

# Function to check availability in a row
def check_row_availability(row, required_seats):
    available_seats = [seat for seat in seats if seat['row_number'] == row and not seat['is_booked']]
    return available_seats[:required_seats] if len(available_seats) >= required_seats else []

# Function to book seats
def book_seats(required_seats):
    # Try to book seats in the same row first
    for row in range(1, 13):  # Rows 1 to 12
        available_in_row = check_row_availability(row, required_seats)
        if available_in_row:
            for seat in available_in_row:
                seat['is_booked'] = True
            return available_in_row

    # If not enough seats in one row, find nearby available seats
    available_seats = [seat for seat in seats if not seat['is_booked']]
    if len(available_seats) >= required_seats:
        booked_seats = available_seats[:required_seats]
        for seat in booked_seats:
            seat['is_booked'] = True
        return booked_seats
    return None

# Route to book seats
@app.route('/book', methods=['POST'])
def book():
    data = request.get_json()
    required_seats = data.get('required_seats', 1)
    
    if required_seats <= 0 or required_seats > 7:
        return jsonify({"message": "You can only book between 1 and 7 seats", "status": "Failure"}), 400
    
    booked_seats = book_seats(required_seats)
    
    if booked_seats:
        return jsonify({"booked_seats": [seat['seat_id'] for seat in booked_seats], "status": "Success"}), 200
    else:
        return jsonify({"message": "Not enough seats available", "status": "Failure"}), 400

# Route to view seat availability status
@app.route('/seats', methods=['GET'])
def view_seats():
    return jsonify(seats), 200

# Route to serve the frontend HTML page
@app.route('/')
def serve_frontend():
    return send_from_directory(os.getcwd(), 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
