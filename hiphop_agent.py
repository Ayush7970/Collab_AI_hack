from uagents import Agent, Context, Model, Protocol
import asyncio

# FIX 1: Import all models from the single, shared 'models.py' file
from models import Message, Proposal

# The address of the local Video Director agent
VIDEO_DIRECTOR_ADDRESS = "agent1qglmpjee5qm0thzxx0mkc6wnmw8ufmd983m7s5ukr753uycdjtyxcpdd49y"

hiphop_artist = Agent(
    name="hiphop_artist",
    port=8001,
    seed="hiphop_artist_local_seed",
    endpoint=["http://127.0.0.1:8001/submit"]
)

# FIX 2: Ensure the protocol name is identical to the video_director's
protocol = Protocol("negotiation")
hiphop_artist.include(protocol)

@hiphop_artist.on_event("startup")
async def send_initial_message(ctx: Context):
    ctx.logger.info(f"🎤 Hip-Hop Artist Agent started on port 8001.")
    ctx.logger.info(f"My address is: {ctx.agent.address}")
    
    await asyncio.sleep(2)
    
    intro_message = "Hey! I'm a hip-hop artist looking to make a visualizer for my new single. Interested in collaborating?"
    ctx.logger.info(f"📤 Sending intro message: '{intro_message}'")
    await ctx.send(
        VIDEO_DIRECTOR_ADDRESS,
        Message(body=intro_message) # Sends the 'Message' model, which the director expects first
    )

# This handler now correctly understands the 'Proposal' model from models.py
@protocol.on_message(model=Proposal)
async def handle_proposal(ctx: Context, sender: str, msg: Proposal):
    ctx.logger.info(f"✅ SUCCESS: Received proposal (round {msg.round}) from director: '{msg.content}'")

    if msg.round >= 5:
        ctx.logger.info("✅ Negotiation complete from my side.")
        return

    # In a full app, you would generate a counter-proposal here
    my_counter = "Thanks for the proposal, I like the energy. Let's talk about the visual concepts."
    ctx.logger.info(f"📤 Sending counter-proposal: '{my_counter}'")
    
    await ctx.send(sender, Proposal(content=my_counter, round=msg.round + 1))

if __name__ == "__main__":
    hiphop_artist.run()