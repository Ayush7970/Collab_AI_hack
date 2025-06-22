from uagents import Agent, Context
from uagents.protocol import Protocol
from groq import Groq
import json
from models import Message, Proposal # Ensure all relevant models are imported

# --- START OF FIX ---

# FIX 1: The user agent sends the first message on the "collab" protocol.
# This agent MUST listen on the same protocol name to hear the message.
protocol = Protocol("collab")

# FIX 2: Your Groq API Key
GROQ_API_KEY = "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" # Replace if needed

# --- END OF FIX ---


# Load profile
try:
    with open("dummy_profiles/leo_profile.json", "r") as f:
        profile = json.load(f)
except FileNotFoundError:
    print("FATAL ERROR: `dummy_profiles/leo_profile.json` not found.")
    exit()

# Groq client
groq = Groq(api_key=GROQ_API_KEY)

# Agent setup
agent = Agent(
    name="lofi_leo",
    seed="leo_seed_phrase",
    port=5072,
    endpoint=["http://127.0.0.1:5072/submit"]
)

agent.include(protocol)


@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🎧 Lofi Leo Agent started!")
    ctx.logger.info(f"My address is: {ctx.agent.address}")


# FIX 3: The user agent's first message is a `Proposal`.
# This handler is now the single entry point for all negotiation rounds.
@protocol.on_message(model=Proposal)
async def handle_proposal(ctx: Context, sender: str, msg: Proposal):
    if msg.round == 1:
        ctx.logger.info(f"🎧 Received initial proposal: '{msg.content}'")
    else:
        ctx.logger.info(f"🎧 Round {msg.round}: Got proposal: '{msg.content}'")

    if msg.round >= 5:
        ctx.logger.info("✅ Negotiation complete.")
        return

    # This prompt works for both the initial response and all subsequent counter-proposals.
    prompt = f"""
You are a music producer with this profile:
{json.dumps(profile, indent=2)}

You just received this proposal: "{msg.content}"

Reply with a relaxed, creative, and easy-going counter-proposal in 1-2 sentences.
"""
    try:
        res = groq.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = res.choices[0].message.content
        ctx.logger.info(f"📤 Sending counter: {reply}")
        await ctx.send(sender, Proposal(content=reply, round=msg.round + 1))
    except Exception as e:
        ctx.logger.error(f"Groq API call failed: {e}")


if __name__ == "__main__":
    agent.run()
