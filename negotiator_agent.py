
from uagents import Agent, Context, Model
from uagents.protocol import Protocol
import os
from groq import Groq

# Setup Groq client
client = Groq(api_key="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")

class Proposal(Model):
    content: str
    round: int

negotiator = Agent(name="negotiator_agent", seed="negotiator_seed", endpoint=["http://127.0.0.1:5060/submit"])
protocol = Protocol("negotiation_protocol")

@protocol.on_message(model=Proposal)
async def negotiate(ctx: Context, sender: str, msg: Proposal):
    if msg.round >= 5:
        ctx.logger.info(f"✅ Final proposal received: {msg.content}")
        return

    prompt = f"""You are a music video director agent negotiating a collaboration proposal.
Round: {msg.round}
Proposal: "{msg.content}"
Respond with a concise counter-offer proposal in one paragraph."""

    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": prompt}]
    )
    counter = response.choices[0].message.content.strip()
    ctx.logger.info(f"🔁 Round {msg.round + 1} counter-offer: {counter}")

    await ctx.send(sender, Proposal(content=counter, round=msg.round + 1))

negotiator.include(protocol)

if __name__ == "__main__":
    negotiator.run()
