from uagents import Agent, Context, Model
from models import Request, Message, Proposal, MatchResult


class Message(Model):
    body: str

# Define the initiator agent
initiator = Agent(
    name="negotiation_starter",
    seed="starter_seed",
    endpoint=["http://127.0.0.1:5060/submit"]
)

@initiator.on_event("startup")
async def start(ctx: Context):
    # Send initial proposal to video director
    await ctx.send(
        "agent1xyzvideodirector",  # 🔁 Replace with actual video director agent address
        Message(body="Hey! I'm working on a hip-hop visualizer. Interested in collaborating?")
    )
    ctx.logger.info("📤 Initial proposal sent to video director.")

# Run the agent
if __name__ == "__main__":
    initiator.run()