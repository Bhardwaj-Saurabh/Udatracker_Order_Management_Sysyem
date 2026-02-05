from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data = request.get_json()
    try:
        order_tracker.add_order(
            data.get("order_id", ""),
            data.get("item_name", ""),
            data.get("quantity", 0),
            data.get("customer_id", ""),
            data.get("status", "pending"),
        )
        order = order_tracker.get_order_by_id(data["order_id"])
        return jsonify(order), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    order = order_tracker.get_order_by_id(order_id)
    if order is None:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    pass

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    pass

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
