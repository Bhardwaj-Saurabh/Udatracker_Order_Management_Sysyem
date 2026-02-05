import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- add_order tests ---
#

def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    mock_storage.save_order.assert_called_once()
    args = mock_storage.save_order.call_args
    saved_order = args[0][1]  # second positional arg is the order dict
    assert saved_order["order_id"] == "ORD001"
    assert saved_order["item_name"] == "Laptop"
    assert saved_order["quantity"] == 1
    assert saved_order["customer_id"] == "CUST001"
    assert saved_order["status"] == "pending"


def test_add_order_with_explicit_status(order_tracker, mock_storage):
    """Tests adding a new order with an explicitly provided valid status."""
    order_tracker.add_order("ORD002", "Phone", 2, "CUST002", status="processing")

    args = mock_storage.save_order.call_args
    saved_order = args[0][1]
    assert saved_order["status"] == "processing"


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")


def test_add_order_raises_error_for_invalid_quantity(order_tracker, mock_storage):
    """Tests that a non-positive quantity raises a ValueError."""
    with pytest.raises(ValueError, match="Quantity must be a positive integer."):
        order_tracker.add_order("ORD003", "Tablet", 0, "CUST003")

    with pytest.raises(ValueError, match="Quantity must be a positive integer."):
        order_tracker.add_order("ORD004", "Tablet", -1, "CUST004")


def test_add_order_raises_error_for_empty_order_id(order_tracker, mock_storage):
    """Tests that an empty order_id raises a ValueError."""
    with pytest.raises(ValueError, match="order_id is required."):
        order_tracker.add_order("", "Item", 1, "CUST005")


def test_add_order_raises_error_for_empty_item_name(order_tracker, mock_storage):
    """Tests that an empty item_name raises a ValueError."""
    with pytest.raises(ValueError, match="item_name is required."):
        order_tracker.add_order("ORD005", "", 1, "CUST005")


def test_add_order_raises_error_for_empty_customer_id(order_tracker, mock_storage):
    """Tests that an empty customer_id raises a ValueError."""
    with pytest.raises(ValueError, match="customer_id is required."):
        order_tracker.add_order("ORD006", "Item", 1, "")


def test_add_order_raises_error_for_invalid_status(order_tracker, mock_storage):
    """Tests that an invalid initial status raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid status 'unknown'."):
        order_tracker.add_order("ORD007", "Item", 1, "CUST007", status="unknown")


#
# --- get_order_by_id tests ---
#

def test_get_order_by_id_existing(order_tracker, mock_storage):
    """Tests retrieving an existing order by ID."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD001", "item_name": "Laptop",
        "quantity": 1, "customer_id": "CUST001", "status": "pending"
    }
    result = order_tracker.get_order_by_id("ORD001")
    mock_storage.get_order.assert_called_with("ORD001")
    assert result["order_id"] == "ORD001"
    assert result["item_name"] == "Laptop"


def test_get_order_by_id_non_existent(order_tracker, mock_storage):
    """Tests that fetching a non-existent order returns None."""
    mock_storage.get_order.return_value = None
    result = order_tracker.get_order_by_id("MISSING")
    assert result is None


def test_get_order_by_id_empty_id_raises(order_tracker):
    """Tests that an empty order_id raises a ValueError."""
    with pytest.raises(ValueError, match="order_id is required."):
        order_tracker.get_order_by_id("")


#
# --- update_order_status tests ---
#

def test_update_order_status_success(order_tracker, mock_storage):
    """Tests successfully updating an order's status."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD001", "item_name": "Laptop",
        "quantity": 1, "customer_id": "CUST001", "status": "pending"
    }
    result = order_tracker.update_order_status("ORD001", "shipped")
    mock_storage.save_order.assert_called_once()
    assert result["status"] == "shipped"
    assert result["order_id"] == "ORD001"


def test_update_order_status_invalid_status(order_tracker, mock_storage):
    """Tests that an invalid status raises ValueError without hitting storage."""
    with pytest.raises(ValueError, match="Invalid status 'bogus'."):
        order_tracker.update_order_status("ORD001", "bogus")
    mock_storage.get_order.assert_not_called()


def test_update_order_status_non_existent_order(order_tracker, mock_storage):
    """Tests that updating a non-existent order raises ValueError."""
    mock_storage.get_order.return_value = None
    with pytest.raises(ValueError, match="Order with ID 'MISSING' not found."):
        order_tracker.update_order_status("MISSING", "shipped")


def test_update_order_status_empty_id_raises(order_tracker):
    """Tests that an empty order_id raises ValueError."""
    with pytest.raises(ValueError, match="order_id is required."):
        order_tracker.update_order_status("", "shipped")


#
# --- list_all_orders tests ---
#

def test_list_all_orders_empty(order_tracker, mock_storage):
    """Tests that an empty storage returns an empty list."""
    mock_storage.get_all_orders.return_value = {}
    result = order_tracker.list_all_orders()
    assert result == []


def test_list_all_orders_multiple(order_tracker, mock_storage):
    """Tests that multiple orders are returned as a list of dicts."""
    mock_storage.get_all_orders.return_value = {
        "ORD001": {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "C1", "status": "pending"},
        "ORD002": {"order_id": "ORD002", "item_name": "Phone", "quantity": 2, "customer_id": "C2", "status": "shipped"},
    }
    result = order_tracker.list_all_orders()
    assert len(result) == 2
    order_ids = {o["order_id"] for o in result}
    assert order_ids == {"ORD001", "ORD002"}
