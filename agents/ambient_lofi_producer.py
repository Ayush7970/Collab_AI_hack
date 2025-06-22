from uagents import Agent, Context, Model
from uagents.protocol import Protocol
import json
import asyncio

# Define the message schema
class Message(Model):
    body: str

# Load profile
with open("../data/ambient_lofi_profile.json", "r") as f:
    creator_profile = json.load(f)

# Initialize agent
creator = Agent(
    name="ambient_lofi_producer",
    seed="ambient_lofi_producer_seed",
    endpoint=["http://127.0.0.1:5050/submit"],
    port=5050
)

# Define protocol to handle messages
collab_protocol = Protocol(name="collab")

@collab_protocol.on_message(model=Message)
async def on_message(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"🎤 Response from {sender}: {msg.body}")

# Include the protocol
creator.include(collab_protocol)

# Handle startup (and send message here)
@creator.on_event("startup")
async def startup(ctx: Context):
    ctx.storage.set("profile", creator_profile)
    ctx.logger.info("✅ Agent is up with profile:")
    ctx.logger.info(creator_profile)

    # Delay to make sure recipient agent is up
    await asyncio.sleep(2)

    # Send the message
    await ctx.send(
        "agent1qfpet8qu9sf6ejag4knffrtg8ptw4af0vchwfhvmf4wwxxhx56nrgk8u8ee",
        Message(body="Hey! I'm looking for a dreamy ambient vocalist for a lo-fi EP collab 🎵")
    )
    ctx.logger.info("✅ Collaboration request sent!")

# Run
if __name__ == "__main__":
    creator.run()
