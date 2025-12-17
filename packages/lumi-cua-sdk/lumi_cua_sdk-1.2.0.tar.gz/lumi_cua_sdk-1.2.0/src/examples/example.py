import asyncio

from lumi_cua_sdk import (LumiCuaClient, Action, THINKING_DISABLED, THINKING_ENABLED, SandboxOsType)

async def main():
    #  Initialize Client
    client = LumiCuaClient()
    # List or start sandboxes
    try:
        sandboxes = await client.list_sandboxes()
        if not sandboxes:
            print("No existing sandboxes found. Starting a new Linux sandbox...")
            sandbox = await client.start_linux()
            print(f"Started Linux sandbox: ID={sandbox.id}, IP={sandbox.ip_address}, ToolServerEndpoint={sandbox.tool_server_endpoint}")
        else:
            sandbox = sandboxes[0] # Use the first available sandbox
            print(f"Using existing sandbox: ID={sandbox.id}, IP={sandbox.ip_address}")

        # For Windows Sandbox, if not use vnc stream url, login to rdp socket session before operate
        if sandbox.os_type == SandboxOsType.WINDOWS.value:
            async with sandbox.rdp_session() as rdp_client:
                if rdp_client is None:
                    print("Failed to establish RDP session, skipping operations")
                    return

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
        else:
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

            # await sandbox.computer(action=Action.CLICK_MOUSE, coordinates=[200, 250], button="right")
            print("Mouse clicked.")

            await sandbox.computer(action=Action.SCROLL, coordinates=[300, 350], scroll_direction="up",
                                   scroll_amount=30)
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

        # Delete sandbox(optional)
        # print(f"Deleting sandbox {sandbox.id}...")
        # await sandbox.delete()
        # print("Sandbox stopped and deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())