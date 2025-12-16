## DC BROKER

A lightweight Python client for the DC-broker message broker system.

## NOTE
As of currently, this system is only usable by whitelisted user, no public account registration is allowed yet  
If you wanna use this message broker system please contact phayuk168@gmail.com so he can make an account for you. Don't abuse the system  

### Installation

```bash
pip install dcbroker
```

### Usage

```python
from dcbroker.client import DCBrokerClient

# Initialize the client
client = DCBrokerClient(base_url="https://friendio.live")

# Login
if client.login("your_username", "your_password"):
    # Create or update an endpoint
    client.create_endpoint("status", "Server is running")

    # List all endpoints
    endpoints = client.list_endpoints()
    if endpoints:
        print(f"Endpoints: {endpoints}")

    # Get a message from a specific endpoint
    msg = client.get_endpoint_message("status")
    if msg:
        print(f"Message: {msg}")

    # Logout
    client.logout()
```

### Features

- Login and session management
- Create or update endpoints
- List endpoints
- Get messages from endpoints
- Logout

---
Replace `"your_username"` and `"your_password"` with your actual credentials.