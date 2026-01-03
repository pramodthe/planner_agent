import asyncio
from openagents.agents.worker_agent import WorkerAgent
from openagents.models.event_context import EventContext

class MyAgent(WorkerAgent):
    """Custom agent that responds to messages."""

    default_agent_id = "my-agent"

    async def on_startup(self):
        print("Agent is running! Press Ctrl+C to stop.")

    async def react(self, context: EventContext):
        event = context.incoming_event
        content = event.payload.get("content") or event.payload.get("text") or ""
        if not content:
            return

        # Get the messaging adapter and respond
        messaging = self.client.mod_adapters.get("openagents.mods.workspace.messaging")
        if messaging:
            channel = event.payload.get("channel") or "general"
            await messaging.send_channel_message(
                channel=channel,
                text=f"Response: {content}"
            )

async def main():
    agent = MyAgent()
    try:
        await agent.async_start(
            network_id="chef-network-2025",
        )
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await agent.async_stop()

if __name__ == "__main__":
    asyncio.run(main())