from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import asdict
import anthropic

# --- Environment and API Key Setup ---
# Ensures the Anthropic API key is available from your environment variables
try:
    client = anthropic.Anthropic()
except Exception as e:
    print(f"Error initializing Anthropic client: {e}")
    print("Please make sure your ANTHROPIC_API_KEY is set as an environment variable.")
    client = None

# --- Data Models ---
class UserProfileRequest(Model):
    user_id: str
    name: str
    bio: str
    age: Optional[str] = None
    gender: Optional[str] = None
    interests: Optional[List[str]] = []
    skills: Optional[List[str]] = []
    portfolioLinks: Optional[List[str]] = []
    uploads: Optional[Dict[str, Any]] = {}
    isCollaborating: Optional[bool] = True

class UserProfileResponse(Model):
    success: bool
    message: str
    user_id: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None

class MatchRequest(Model):
    query: str
    limit: Optional[int] = 3

class MatchResponse(Model):
    success: bool
    matches: List[Dict[str, Any]]
    error: Optional[str] = None

# --- AGENT SETUP ---
user_input_agent = Agent(
    name="user_input_agent",
    port=8003,
    seed="user_input_secret_seed",
    endpoint=["http://127.0.0.1:8003/submit"]
)

fund_agent_if_low(user_input_agent.wallet.address())

# --- STORAGE CONFIGURATION ---
USERS_FILE = "user.json"

def load_user_list() -> List[Dict[str, Any]]:
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, 'r') as f:
            content = f.read()
            if not content: return []
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_user_list(users: List[Dict[str, Any]]):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@user_input_agent.on_event("startup")
async def startup_event(ctx: Context):
    ctx.logger.info(f"User Profile Agent {user_input_agent.name} started on port 8003!")
    if not os.path.exists(USERS_FILE):
        save_user_list([])
        ctx.logger.info(f"Initialized new empty '{USERS_FILE}'")

# --- API ENDPOINTS ---
@user_input_agent.on_rest_post("/create_profile", UserProfileRequest, UserProfileResponse)
async def create_user_profile(ctx: Context, req: UserProfileRequest) -> UserProfileResponse:
    try:
        users = load_user_list()
        user_profile_dict = req.dict()
        user_profile_dict["timestamp"] = datetime.now().isoformat()
        users.append(user_profile_dict)
        save_user_list(users)
        
        ctx.logger.info(f"Successfully created profile for user_id: {req.user_id}")
        return UserProfileResponse(success=True, message="Profile created successfully", user_id=req.user_id, timestamp=user_profile_dict["timestamp"])
        
    except Exception as e:
        ctx.logger.error(f"Error in create_user_profile: {str(e)}")
        return UserProfileResponse(success=False, message="Internal server error", error=str(e))

@user_input_agent.on_rest_post("/match_users", MatchRequest, MatchResponse)
async def match_users(ctx: Context, req: MatchRequest) -> MatchResponse:
    if not client:
        return MatchResponse(success=False, matches=[], error="Anthropic client not initialized. Check API Key.")

    try:
        ctx.logger.info(f"Received match request for query: '{req.query}'")
        users = load_user_list()
        if not users:
            return MatchResponse(success=False, matches=[], error="No users available to match.")

        # Build the text block of profiles for the AI prompt
        profiles_text = "\n\n".join([
            f"Profile:\n- User ID: {user.get('user_id')}\n- Name: {user.get('name')}\n- Bio: {user.get('bio')}\n- Skills: {', '.join(user.get('skills', []))}\n- Interests: {', '.join(user.get('interests', []))}"
            for user in users
        ])
        
        prompt = f"""From the following list of creator profiles, find the best {req.limit} matches for the request below.

Request: "{req.query}"

Available Profiles:
{profiles_text}

Based on the request and the profiles, respond with ONLY the user_id's of the top {req.limit} best matches, each on a new line. Do not include any other text, explanation, or formatting.
"""

        # Call Claude AI
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse the AI response to get a list of user IDs
        matched_ids = [line.strip() for line in response.content[0].text.strip().split('\n') if line.strip()]
        ctx.logger.info(f"Claude AI matched the following user IDs: {matched_ids}")

        # Find the full profile objects for the matched IDs
        user_map = {user['user_id']: user for user in users}
        matched_profiles = [user_map[user_id] for user_id in matched_ids if user_id in user_map]
        
        if not matched_profiles:
            return MatchResponse(success=False, matches=[], error="AI could not find any suitable matches.")

        return MatchResponse(success=True, matches=matched_profiles)
        
    except Exception as e:
        ctx.logger.error(f"Error in match_users: {str(e)}")
        return MatchResponse(success=False, matches=[], error=str(e))

if __name__ == "__main__":
    user_input_agent.run()
