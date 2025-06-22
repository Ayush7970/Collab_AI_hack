from uagents import Agent, Context, Model
from uagents.protocol import Protocol
from groq import Groq
import json
from models import Request, Message, Proposal, MatchResult




# Load video director profile
with open("dummy_profiles/video_director.json", "r") as f:
    director_profile = json.load(f)


# Groq client
groq = Groq(api_key="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")



video_director = Agent(
    name="video_director",
    seed="video_director_seed",
    endpoint=["http://127.0.0.1:5057/submit"],
    port=5057
)

protocol = Protocol("negotiation")

@protocol.on_message(model=Message)
async def handle_intro(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"🎥 Received intro message: {msg.body}")
    # (Optional) Log or store request — no need to send a proposal here anymore


    # Generate initial proposal using Groq
    prompt = f"""
You are a video director with this profile:
{json.dumps(director_profile, indent=2)}
A user has requested collaboration: "{msg.body}"
Craft an enthusiastic and creative response in 1-2 sentences.
"""
    res = groq.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    proposal = res.choices[0].message.content
    ctx.logger.info(f"📤 Initial proposal: {proposal}")

    # Send back to user (you may want to send to a negotiator instead)
    await ctx.send(sender, Proposal(content=proposal, round=1))


@protocol.on_message(model=Proposal)
async def handle_proposal(ctx: Context, sender: str, msg: Proposal):
    ctx.logger.info(f"🎬 Round {msg.round}: Got proposal: {msg.content}")

    if msg.round >= 5:
        ctx.logger.info("✅ Negotiation complete.")
        return

    prompt = f"""
You are a video director with this profile:
{json.dumps(director_profile, indent=2)}
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

video_director.include(protocol)




if __name__ == "__main__":
    video_director.run()
