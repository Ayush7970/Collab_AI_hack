from uagents import Agent, Context, Model
from uagents.protocol import Protocol
import json
from groq import Groq
import anthropic
from models import Request, Message, Proposal, MatchResult  # Make sure models.py is shared

# Initialize clients
groq = Groq(api_key="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")
claude = anthropic.Anthropic()

# User profile for LLM prompts
user_profile = {
    "role": "visual artist",
    "style": "hip-hop inspired, urban-themed",
    "goal": "collaborate with video creatives"
}

# Agent setup
user = Agent(name="user_requestor", seed="user_seed", endpoint=["http://127.0.0.1:5056/submit"], port=5056)
protocol = Protocol("collab")


# Send request to matchmaker
@user.on_event("startup")
async def startup(ctx: Context):
    try:
        with open("collab_query.json", "r") as f:
            query_data = json.load(f)
            query2 = query_data.get("query", "Looking for a collaborator")
    except Exception:
        query2 = "Looking for a collaborator"

    ctx.logger.info("📤 Sent request to matchmaker", )
    await ctx.send("agent1qv3tkmaqp56zgx9gf6g6dgpxh0q5zw7e8x8wa6cqf675txayl2fczccvxqq", Request(query=query2))
    ctx.logger.info(f"query sent , {query2}")

# Receive match result
@protocol.on_message(model=MatchResult)
async def receive_match(ctx: Context, sender: str, msg: MatchResult):
    match_name = msg.name
    match_address = msg.address
    ctx.logger.info(f"🎯 Matched withnsdiovnsdipvnsdiovsnbdviosndivdsn: {match_name} ({match_address})")

    if not match_name or not match_address:
        ctx.logger.error("❌ Match result is incomplete!")
        return

    # Generate first proposal
    prompt = f"""
You are a user with profile:
{json.dumps(user_profile, indent=2)}
You want to propose a collaboration on a hip-hop visualizer.
Craft an enthusiastic and creative message to the video director.
"""
    res = groq.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    proposal = res.choices[0].message.content.strip()
    await ctx.send(match_address, Proposal(content=proposal, round=1))
    ctx.logger.info(f"📩 Sent initial proposal to {match_name}: {proposal}")

# Handle counter proposals
@protocol.on_message(model=Proposal)
async def receive_counter(ctx: Context, sender: str, msg: Proposal):
    ctx.logger.info(f"🔁 Round {msg.round}: Got counter proposal: {msg.content}")

    if msg.round >= 5:
        ctx.logger.info("✅ Negotiation completed.")
        return

    # Generate counter-proposal
    prompt = f"""
You are the user with this profile:
{json.dumps(user_profile, indent=2)}
The video director just said: "{msg.content}"
Reply with a polite, creative counter-proposal in 1–2 sentences.
"""
    res = groq.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    counter = res.choices[0].message.content.strip()
    await ctx.send(sender, Proposal(content=counter, round=msg.round + 1))
    ctx.logger.info(f"📤 Sent counter: {counter}")


# @protocol.on_message(model=Message)
# async def receive_message(ctx: Context, sender: str, msg: Message):
#     ctx.logger.info(f"✔️ Got message from matchmaker: {msg.body}")

user.include(protocol)

if __name__ == "__main__":
    user.run()
