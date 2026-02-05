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
