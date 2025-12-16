# kinetimail client

A Python client for interacting with the KinetiMail API service.

## Installation

```bash
pip install kinetimail
```

## Usage

```python
from kinetimail import KinetiMail

# Setup client
client = KinetiMail(api_key="your_api_key")

# Create a new inbox
client.create_inbox(email="john-doe-free@kinetimail.com", name="John Doe")

# Send message
client.send_message(
    from_address="john-doe-free@kinetimail.com",
    to_address="your-address@example.com",
    subject=f'Hello World!',
    body='Hey, how are you?'
)

# List messages
client.list_messages(inbox_id="john-doe-free@kinetimail.com")

# Read a specifc message
get_message(
    inbox_id="john-doe-free@kinetimail.com",
    message_id="<message_id>"
)

## License

MIT License
