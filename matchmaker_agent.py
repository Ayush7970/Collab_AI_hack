from uagents import Agent, Context, Model
from uagents.protocol import Protocol
import json
import os
from dotenv import load_dotenv
import anthropic  # Claude SDK
from models import Request, Message, Proposal, MatchResult

# --- START OF FIX ---
load_dotenv()
# IMPORTANT: Add your Anthropic API key here.
API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Check if the API key has been replaced
if not API_KEY or API_KEY == "REPLACE_WITH_YOUR_ANTHROPIC_API_KEY":
    print("FATAL ERROR: Please add your Anthropic API key to the matchmaker_agent.py file.")
    exit()

# Initialize the client by passing the key directly
client = anthropic.Anthropic(api_key=API_KEY)
# --- END OF FIX ---


# Load dummy agents
try:
    with open("dummy_profiles/agents.json", "r") as f:
        dummy_agents = json.load(f)
except FileNotFoundError:
    print("FATAL ERROR: `dummy_profiles/agents.json` not found. Please create it.")
    exit()


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
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=100,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        match_name = response.content[0].text.strip()
    except Exception as e:
        ctx.logger.error(f"Anthropic API call failed: {e}")
        await ctx.send(sender, Message(body=f"❌ Error during matchmaking: Could not get a recommendation from the AI. Details: {e}"))
        return


    ctx.logger.info(f"💡 Claude recommends: {match_name}")

    selected_agent = next((a for a in dummy_agents if a["name"] == match_name), None)

    if not selected_agent:
        ctx.logger.error(f"Matchmaking failed: Recommended agent '{match_name}' not found in agents.json.")
        await ctx.send(sender, Message(body="❌ No suitable match found."))
        return
    
    await ctx.send(
        sender,
        MatchResult(name=match_name, address=selected_agent["address"])
    )
    ctx.logger.info(f"✅ Sent match result for {match_name} to user.")


matchmaker.include(protocol)

if __name__ == "__main__":
    matchmaker.run()
