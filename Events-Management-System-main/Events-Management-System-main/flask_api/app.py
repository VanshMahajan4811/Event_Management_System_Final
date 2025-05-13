from flask import Flask, jsonify, redirect, request
import sqlite3

app = Flask(__name__)

DATABASE = '../db.sqlite3'

def dict_from_row(row):
    return {
        'id': row[0],
        'eventName': row[1],
        'description': row[2],
        'location': row[3],
        'fromDate': row[4],
        'fromTime': row[5],
        'toDate': row[6],
        'toTime': row[7],
        'deadlineDate': row[8],
        'deadlineTime': row[9],
        'email': row[10],
        'password': row[11]
    }

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def root():
    return redirect('/api/hello')

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello from Flask API!'})

@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM EM_App_event').fetchall()
    conn.close()
    events_list = [dict_from_row(event) for event in events]
    return jsonify({'events': events_list})

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM EM_App_event WHERE id = ?', (event_id,)).fetchone()
    conn.close()
    if event:
        return jsonify({'event': dict_from_row(event)})
    else:
        return jsonify({'error': 'Event not found'}), 404
@app.route('/api/events/add', methods=['POST'])
def add_event():
   
    data = request.get_json() or {}
   
    print(f"Add event request received with data: {data}")
    return jsonify({'status': 'success', 'message': 'Event added successfully'}), 200

@app.route('/api/events/add', methods=['GET'])
def add_event_get():
    return jsonify({'message': 'GET method for adding event - provide event details via POST'}), 200

@app.route('/api/events/cancel', methods=['POST'])
def cancel_event():
    data = request.get_json() or {}
    print(f"Cancel event request received with data: {data}")
    return jsonify({'status': 'success', 'message': 'Event canceled successfully'}), 200

@app.route('/api/events/cancel', methods=['GET'])
def cancel_event_get():
    event_id = request.args.get('event_id')
    if event_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM EM_App_event WHERE id = ?', (event_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        if rows_affected > 0:
            print(f"Event {event_id} canceled successfully via GET")
            return jsonify({'status': 'success', 'message': f'Event {event_id} canceled successfully via GET'}), 200
        else:
            return jsonify({'status': 'error', 'message': f'Event {event_id} not found'}), 404
    else:
        return jsonify({'status': 'error', 'message': 'event_id query parameter is required'}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
