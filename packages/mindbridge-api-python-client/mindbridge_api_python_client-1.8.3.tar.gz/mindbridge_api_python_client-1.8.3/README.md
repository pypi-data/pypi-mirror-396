<h1 align="center">MindBridge API Python Client</h1>
<p align="center">
    <img alt="Logo of MindBridge" src="https://www.mindbridge.ai/wp-content/uploads/2021/07/MindBridge_Logo_Primary_RGB.png" style="background-color: #fdfdfd;" />
</p>

Interact with the MindBridge API using this Python SDK. Please see [The MindBridge API](https://www.mindbridge.ai/support/api/) for more information about the MindBridge API. You can also [Access MindBridge Customer Support](https://support.mindbridge.ai/hc/en-us/articles/360054147834-Access-MindBridge-Customer-Support) or [Contact us](https://www.mindbridge.ai/contact/).

## Installation

MindBridge API Python Client can be installed with [pip](https://pip.pypa.io):

```sh
pip install mindbridge-api-python-client
```

It is recommended to install and run MindBridge API Python Client from a virtual environment, for example, using the Python standard library's [venv](https://docs.python.org/3/library/venv.html) or using [uv](https://docs.astral.sh/uv/).

## Usage

Before you begin, create an API token within your tenant by following [Create an API token](https://support.mindbridge.ai/hc/en-us/articles/9349943782039-Create-an-API-token). There are several methods to securely store your API token and use it with your Python process, for this short example it's assumed that the following have been set as environment variables:

- `MINDBRIDGE_API_URL`: Your MindBridge tenant URL, like `subdomain.mindbridge.ai`
- `MINDBRIDGE_API_TOKEN`: Your API token

This script connects to your MindBridge tenant and calls the `/v1/users/current` endpoint to retrieve information about the authenticated user:

```py
import os
import mindbridgeapi as mbapi

url = os.environ.get("MINDBRIDGE_URL", "")
token = os.environ.get("MINDBRIDGE_API_TOKEN", "")

server = mbapi.Server(url=url, token=token)

user = server.users.get_current()
print(f"Name: {user.first_name} {user.last_name}")
print(f"Role: {user.role}")
print(f"ID:   {user.id}")
```
