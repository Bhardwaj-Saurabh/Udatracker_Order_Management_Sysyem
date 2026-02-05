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
    data = request.get_json()
    new_status = data.get("new_status", "")
    try:
        updated = order_tracker.update_order_status(order_id, new_status)
        return jsonify(updated), 200
    except ValueError as e:
        if "not found" in str(e):
            return jsonify({"error": str(e)}), 404
        return jsonify({"error": str(e)}), 400

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get("status")
    if status:
        try:
            orders = order_tracker.list_orders_by_status(status)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    else:
        orders = order_tracker.list_all_orders()
    return jsonify(orders), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
