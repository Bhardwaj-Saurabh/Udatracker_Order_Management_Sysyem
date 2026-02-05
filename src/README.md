# Udatracker - Order Management System

## Reflection

- I decided to keep all the validation logic inside `OrderTracker` instead of splitting it between the class and the Flask routes. This keeps the API layer really thin. It just parses the request, calls a method, and returns the result. If I ever need to swap Flask for another framework, the business rules stay the same.

- One thing that surprised me during testing was how important it is to validate the status before hitting storage. I originally had `update_order_status` fetch the order first and then check the status, but writing the test for invalid status made me realize I should fail fast. There is no reason to touch storage if the input is already bad.

- Writing tests for `list_orders_by_status` with an empty string vs an invalid string helped me catch that those are two different error cases. Without TDD I probably would have lumped them together and missed the edge case.

- If I had more time I would add a `DELETE /api/orders/<order_id>` endpoint and maybe swap the in-memory storage for something like SQLite so the data actually sticks around between restarts.
