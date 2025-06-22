from uagents import Agent, Context, Model
from uagents.protocol import Protocol
from groq import Groq
import json
from models import Message, Proposal

# Load profile
with open("dummy_profiles/stella_profile.json", "r") as f:
    profile = json.load(f)

# Groq client
groq = Groq(api_key="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")

# Agent setup
agent = Agent(
    name="synthwave_stella",
    seed="stella_seed_phrase",
    port=5071
)

protocol = Protocol("negotiation")

@protocol.on_message(model=Message)
async def handle_intro(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"🎹 Received intro message: {msg.body}")

    prompt = f"""
You are a music producer with this profile:
{json.dumps(profile, indent=2)}
A user has requested collaboration: "{msg.body}"
Craft an enthusiastic and creative initial proposal in 1-2 sentences to start the negotiation.
"""
    res = groq.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    proposal = res.choices[0].message.content
    ctx.logger.info(f"📤 Initial proposal: {proposal}")
    await ctx.send(sender, Proposal(content=proposal, round=1))

@protocol.on_message(model=Proposal)
async def handle_proposal(ctx: Context, sender: str, msg: Proposal):
    ctx.logger.info(f"🎹 Round {msg.round}: Got proposal: {msg.content}")

    if msg.round >= 5:
        ctx.logger.info("✅ Negotiation complete.")
        return

    prompt = f"""
You are a music producer with this profile:
{json.dumps(profile, indent=2)}
You received this proposal: "{msg.content}"
Reply with a polite, creative counter-proposal in 1-2 sentences.
"""
    res = groq.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    reply = res.choices[0].message.content
    ctx.logger.info(f"📤 Counter: {reply}")
    await ctx.send(sender, Proposal(content=reply, round=msg.round + 1))

agent.include(protocol)

if __name__ == "__main__":
    agent.run()