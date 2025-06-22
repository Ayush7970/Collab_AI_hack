from uagents import Agent, Context, Model
from uagents.protocol import Protocol

class Request(Model):
    query: str

# User Agent
user = Agent(name="user_requestor", seed="user_seed", endpoint=["http://127.0.0.1:5056/submit"], port=5056)

# Protocol to send match request
protocol = Protocol("send_request")

# Include the protocol
user.include(protocol)

# Send the request on agent startup (NOT protocol startup)
@user.on_event("startup")
async def send(ctx: Context):
    await ctx.send(
        "agent1qv3tkmaqp56zgx9gf6g6dgpxh0q5zw7e8x8wa6cqf675txayl2fczccvxqq",  # Replace with your actual matchmaker address
        Request(query="Video director for a hip-hop visualizer")
    )
    ctx.logger.info("📤 Sent request to matchmaker.")

# ✅ Run the agent
if __name__ == "__main__":
    user.run()