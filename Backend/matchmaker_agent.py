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

    # Format profiles for prompt
    profiles_text = "\n".join(
        [f"- Name: {agent['name']}, Tags: {', '.join(agent['tags'])}" for agent in dummy_agents]
    )
    prompt = f"""Given the following creator profiles, recommend the 3 best fits for:
Request: "{request.query}"
Profiles:
{profiles_text}
Respond ONLY with the names in a comma-separated list (e.g. Jane Doe, John Smith, Alice Wong)."""

    # Claude 4 API call
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.content[0].text.strip()
    ctx.logger.info(f"💡 Claude raw output: {raw_text}")

    # Extract names
    match_names = [name.strip() for name in raw_text.split(",")][:3]

    top_matches = []
    for name in match_names:
        match = next((a for a in dummy_agents if a["name"].lower() == name.lower()), None)
        if match:
            top_matches.append({
                "name": match["name"],
                "description": match.get("description", ""),
                "address": match["address"]
            })

    if not top_matches:
        await ctx.send(sender, Message(body="❌ No suitable matches found."))
        return

    # Save top matches to file for `new.py`
    save_path = os.path.join(os.path.dirname(__file__), "top_matches.json")
    with open(save_path, "w") as f:
        json.dump(top_matches, f, indent=2)

    # Send only the best match (first one) to continue the uAgents flow
    await ctx.send(
        sender,
        MatchResult(name=top_matches[0]["name"], address=top_matches[0]["address"])
    )
    ctx.logger.info(f"✅ Top match sent to requester: {top_matches[0]['name']}")

matchmaker.include(protocol)

if __name__ == "__main__":
    matchmaker.run()