from uagents import Agent, Context, Model
from uagents.protocol import Protocol
import json
import os
import anthropic  # ✅ Claude 4 SDK
from models import Request, Message, Proposal, MatchResult




client = anthropic.Anthropic()  # Automatically picks up ANTHROPIC_API_KEY from environment

# Claude 4 API Setup



# Load dummy agents
with open("dummy_profiles/agents.json", "r") as f:
    dummy_agents = json.load(f)

# Matchmaker Agent
matchmaker = Agent(
    name="matchmaker",
    seed="matchmaker_seed",
    endpoint=["http://127.0.0.1:5055/submit"],
    port=5055
)

protocol = Protocol(name="matchmaking")

@protocol.on_message(model=Request)
async def handle_request(ctx: Context, sender: str, request: Request):
    ctx.logger.info(f"🎯 Received request: {request.query}")
    
    # Build LLM prompt
    profiles_text = "\n".join(
        [f"- Name: {agent['name']}, Tags: {', '.join(agent['tags'])}" for agent in dummy_agents]
    )
    prompt = f"""Given the following creator profiles, recommend the best fit for:
Request: "{request.query}"
Profiles:
{profiles_text}
Respond with the name only."""

    # Claude 4 API call
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=100,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    match_name = response.content[0].text.strip()
    ctx.logger.info(f"💡 Claude recommends: {match_name}")

    selected_agent = next((a for a in dummy_agents if a["name"] == match_name), None)

    if not selected_agent:
        await ctx.send(sender, Message(body="❌ No suitable match found."))
        return

    

    await ctx.send(
    sender,
    MatchResult(name=match_name, address=selected_agent["address"]) ) # ✅ Correct model now)
    ctx.logger.info(f"checking")
matchmaker.include(protocol)

if __name__ == "__main__":
    matchmaker.run()
