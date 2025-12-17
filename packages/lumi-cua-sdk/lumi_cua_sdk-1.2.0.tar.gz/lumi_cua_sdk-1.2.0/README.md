# Lumi CUA SDK Guide
## Overview

SDK for Lumi Computer Use Application, providing programmatic access to sandbox management and remote control capabilities.

## Installation

```bash
pip install lumi-cua-sdk
```

## Usage
### Setup Environment
1. Deploy your own Remote Computer Use Agent, you can explore more on Volcano Engine's OS Agent Services via deployment links (in Chinese) [Computer Use Agent](https://console.volcengine.com/vefaas/region:vefaas+cn-beijing/application/create?templateId=680b0a890e881f000862d9f0&channel=github&source=ui-tars)
2. After the application deployment is completed, get Sandbox Manager URL, Agent Planner URL and Auth Token from the details page of Computer Use Application in [Volcano Engine's OS Agent Services](https://console.volcengine.com/vefaas/region:vefaas+cn-beijing/application?PageNumber=1&PageSize=10&filterName=&sort=CreateTime-descend):
   - Get Sandbox Manager Url from Computer Use Agent Application
      <picture>
        <img alt="Get sandbox manager url" src="./docs/images/get_sandbox_manager_url.png">
      </picture>
      <br/>
   - Get Agent Planner Url from Computer Use Agent Application
      <picture>
        <img alt="Get agent planner url" src="./docs/images/get_agent_planner_url.png">
      </picture>
      <br/>
   - Get Auth Token from Computer Use Agent Application
      <picture>
        <img alt="Get auth token" src="./docs/images/get_auth_token.png">
      </picture>
      <br/>
3. Export environment variables locally
```bash
  export SANDBOX_MANAGER_URL=${your_sandbox_manager_url} 
  export AGENT_PLANNER_URL=${your_agent_planner_url}   
  export AUTH_TOKEN=${your_auth_token}
```

### Basic Usage
Here's a basic example of using the SDK, \
For Linux Sandbox and Windows Sandbox using VNC stream protocol:

```python
import asyncio
from lumi_cua_sdk import LumiCuaClient, Action, THINKING_DISABLED, THINKING_ENABLED

async def main():
    #  Initialize Client
    client = LumiCuaClient()
    try:
        # List or start sandboxes
        sandboxes = await client.list_sandboxes()
        if not sandboxes:
            print("No existing sandboxes found. Starting a new Linux sandbox...")
            sandbox = await client.start_linux()
            print(f"Started Linux sandbox: ID={sandbox.id}, IP={sandbox.ip_address}, ToolServerEndpoint={sandbox.tool_server_endpoint}")
        else:
            sandbox = sandboxes[0] # Use the first available sandbox
            print(f"Using existing sandbox: ID={sandbox.id}, IP={sandbox.ip_address}")

        # Get sandbox stream url
        stream_url = await sandbox.get_stream_url()
        print(f"Stream URL: {stream_url}")

        # Take screenshot
        screenshot_result = await sandbox.screenshot()
        print(f"Screenshot taken (first 64 chars): {screenshot_result.base_64_image[:64]}...")

        # Sandbox computer operation action
        await sandbox.computer(action=Action.MOVE_MOUSE, coordinates=[100, 150])
        print("Mouse moved.")

        await sandbox.computer(action=Action.TYPE_TEXT, text="Hello from Lumi CUA SDK!")
        print("Text typed.")

        await sandbox.computer(action=Action.CLICK_MOUSE, coordinates=[200, 250], button="right")
        print("Mouse clicked.")

        await sandbox.computer(action=Action.SCROLL, coordinates=[300, 350], scroll_direction="up", scroll_amount=30)
        print("Scrolled.")

        await sandbox.computer(action=Action.PRESS_KEY, keys=["Enter"])
        print("Pressed Enter.")

        await sandbox.computer(action=Action.TAKE_SCREENSHOT)
        print("Screenshot taken.")

        await sandbox.computer(action=Action.WAIT, duration=10)
        print("Waited.")

        # Task Integration
        # Get available models and set thinking mode
        models = await client.list_models()
        thinking_type = THINKING_ENABLED if models[0].is_thinking else THINKING_DISABLED

        # Run task
        task_prompt = "open the browse"
        try:
            async for message in client.run_task(task_prompt, sandbox.id, models[0].name,
                                                 user_system_prompt="", thinking_type=thinking_type):
                print("summary:", message.summary)
                print("action:", message.action)
                print("screenshot:", message.screenshot)
                print("task_id:", message.task_id)
                print("total tokens", message.total_tokens)
        except Exception as e:
            print(f"\nError occured:", str(e))

        # Delete sandbox (optional)
        print(f"Deleting sandbox {sandbox.id}...")
        await sandbox.delete()
        print("Sandbox stopped and deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

For Windows Sandbox using GUACAMOLE stream protocol:

```python
import asyncio
from lumi_cua_sdk import LumiCuaClient, Action, THINKING_DISABLED, THINKING_ENABLED

async def main():
    #  Initialize Client
    client = LumiCuaClient()
    try:
        # List or start sandboxes
        sandboxes = await client.list_sandboxes()
        if not sandboxes:
            print("No existing sandboxes found. Starting a new Linux sandbox...")
            sandbox = await client.start_linux()
            print(f"Started Linux sandbox: ID={sandbox.id}, IP={sandbox.ip_address}, ToolServerEndpoint={sandbox.tool_server_endpoint}")
        else:
            sandbox = sandboxes[0] # Use the first available sandbox
            print(f"Using existing sandbox: ID={sandbox.id}, IP={sandbox.ip_address}")

        # Get sandbox stream url
        stream_url = await sandbox.get_stream_url()
        print(f"Stream URL: {stream_url}")

        async with sandbox.rdp_session() as rdp_client:
            if rdp_client is None:
                print("Failed to establish RDP session, skipping operations")
                return
            
            # Take screenshot
            screenshot_result = await sandbox.screenshot()
            print(f"Screenshot taken (first 64 chars): {screenshot_result.base_64_image[:64]}...")
    
            # Sandbox computer operation action
            await sandbox.computer(action=Action.MOVE_MOUSE, coordinates=[100, 150])
            print("Mouse moved.")
    
            await sandbox.computer(action=Action.TYPE_TEXT, text="Hello from Lumi CUA SDK!")
            print("Text typed.")
    
            await sandbox.computer(action=Action.CLICK_MOUSE, coordinates=[200, 250], button="right")
            print("Mouse clicked.")
    
            await sandbox.computer(action=Action.SCROLL, coordinates=[300, 350], scroll_direction="up", scroll_amount=30)
            print("Scrolled.")
    
            await sandbox.computer(action=Action.PRESS_KEY, keys=["Enter"])
            print("Pressed Enter.")
    
            await sandbox.computer(action=Action.TAKE_SCREENSHOT)
            print("Screenshot taken.")
    
            await sandbox.computer(action=Action.WAIT, duration=10)
            print("Waited.")
    
            # Task Integration
            # Get available models and set thinking mode
            models = await client.list_models()
            thinking_type = THINKING_ENABLED if models[0].is_thinking else THINKING_DISABLED
    
            # Run task
            task_prompt = "open the browse"
            try:
                async for message in client.run_task(task_prompt, sandbox.id, models[0].name,
                                                     user_system_prompt="", thinking_type=thinking_type):
                    print("summary:", message.summary)
                    print("action:", message.action)
                    print("screenshot:", message.screenshot)
                    print("task_id:", message.task_id)
                    print("total tokens", message.total_tokens)
            except Exception as e:
                print(f"\nError occured:", str(e))

        # Delete sandbox (optional)
        print(f"Deleting sandbox {sandbox.id}...")
        await sandbox.delete()
        print("Sandbox stopped and deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- List available sandboxes.
- Start and delete sandboxes (Linux and Windows).
- Get a streaming URL for sandboxe interaction.
- Remote computer control:
    - Mouse movements, clicks, drags, scrolls.
    - Keyboard typing and key presses.
    - Take screenshots.
- Agent integration for computer use task automation.

## Development

Clone the repository and install dependencies for development:

```bash
git clone https://github.com/lelili2021/lumi-cua-sdk.git
cd lumi-cua-sdk
pip install -e .[dev]
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.