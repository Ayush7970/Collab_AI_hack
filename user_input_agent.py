from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import re
import anthropic

# Try to load .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    env_file = ".env"
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")

# Load .env file
load_env_file()

# Initialize Claude client
client = anthropic.Anthropic()  # Automatically picks up ANTHROPIC_API_KEY from environment

# Define data models
class UserProfileRequest(Model):
    user_id: str
    name: str
    bio: str
    interests: List[str]
    skills: List[str]
    location: Optional[str] = "Unknown"
    profession: Optional[str] = "Unknown"

class UserProfileResponse(Model):
    success: bool
    message: str
    user_id: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None

class MatchRequest(Model):
    query: str
    limit: Optional[int] = 3

class UserProfileData(Model):
    user_id: str
    name: str
    bio: str
    interests: List[str]
    skills: List[str]
    location: str
    profession: str
    timestamp: str
    metadata: Dict[str, Any]

class MatchResponse(Model):
    success: bool
    matches: List[UserProfileData]
    count: int
    recommendations: List[UserProfileData]
    error: Optional[str] = None

class HealthResponse(Model):
    status: str
    agent: str
    storage_path: str
    total_users: int

# Create the user input agent
user_input_agent = Agent(
    name="user_input_agent",
    port=8003,
    seed="user_input_secret_seed",
    endpoint=["http://127.0.0.1:8003/submit"]
)

# Fund agent if low on balance
fund_agent_if_low(user_input_agent.wallet.address())

# Storage configuration
USERS_FILE = "user_profiles.json"

def load_users() -> Dict[str, Any]:
    """Load user profiles from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"users": {}, "metadata": {"total": 0, "last_updated": None}}
    return {"users": {}, "metadata": {"total": 0, "last_updated": None}}

def save_users(data: Dict[str, Any]):
    """Save user profiles to JSON file"""
    data["metadata"]["last_updated"] = datetime.now().isoformat()
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_claude_match(query: str, users: Dict[str, Any], limit: int = 3) -> List[str]:
    """Use Claude to find the best matches for a query"""
    try:
        # Build profiles text for Claude
        profiles_text = "\n".join([
            f"- Name: {user_data['name']}, Bio: {user_data['bio']}, Skills: {', '.join(user_data['skills'])}, Interests: {', '.join(user_data['interests'])}, Profession: {user_data['profession']}, Location: {user_data['location']}"
            for user_data in users.values()
        ])
        
        prompt = f"""Given the following user profiles, recommend the best {limit} matches for this request:
Request: "{query}"

Available Profiles:
{profiles_text}

Respond with only the names of the best {limit} matches, one per line, in order of best fit."""

        # Claude API call
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=200,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        match_names = [name.strip() for name in response.content[0].text.strip().split('\n') if name.strip()]
        return match_names[:limit]
        
    except Exception as e:
        print(f"Claude API error: {e}")
        return []

@user_input_agent.on_event("startup")
async def startup_event(ctx: Context):
    ctx.logger.info(f"User Profile Agent {user_input_agent.name} started!")
    ctx.logger.info(f"Agent address: {user_input_agent.address}")
    ctx.logger.info(f"Users file: {USERS_FILE}")
    
    # Initialize storage if needed
    if not os.path.exists(USERS_FILE):
        save_users({"users": {}, "metadata": {"total": 0, "last_updated": None}})
        ctx.logger.info("Initialized new users file")

@user_input_agent.on_rest_post("/create_profile", UserProfileRequest, UserProfileResponse)
async def create_user_profile(ctx: Context, req: UserProfileRequest) -> UserProfileResponse:
    """
    Create or update user profile
    Expected request format: {"user_id": "user123", "name": "John Doe", "bio": "...", "interests": ["music", "tech"], "skills": ["python", "guitar"], "location": "NYC", "profession": "Developer"}
    """
    try:
        # Load existing users
        data = load_users()
        
        # Create user profile
        user_profile = {
            "user_id": req.user_id,
            "name": req.name,
            "bio": req.bio,
            "interests": req.interests or [],
            "skills": req.skills or [],
            "location": req.location or "Unknown",
            "profession": req.profession or "Unknown",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "agent_address": str(user_input_agent.address),
                "profile_length": len(req.bio),
                "interests_count": len(req.interests or []),
                "skills_count": len(req.skills or []),
                "created_at": datetime.now().isoformat()
            }
        }
        
        # Store the profile
        data["users"][req.user_id] = user_profile
        data["metadata"]["total"] = len(data["users"])
        
        # Save to file
        save_users(data)
        
        ctx.logger.info(f"Created/updated profile for user {req.user_id}")
        
        return UserProfileResponse(
            success=True,
            message=f"Profile {'updated' if req.user_id in data['users'] else 'created'} successfully",
            user_id=req.user_id,
            timestamp=user_profile["timestamp"]
        )
        
    except Exception as e:
        ctx.logger.error(f"Error creating profile: {str(e)}")
        return UserProfileResponse(
            success=False,
            message="Failed to create profile",
            error=f"Profile creation error: {str(e)}"
        )

@user_input_agent.on_rest_post("/match_users", MatchRequest, MatchResponse)
async def match_users(ctx: Context, req: MatchRequest) -> MatchResponse:
    """
    Use Claude to find the best matches for a query
    Expected request format: {"query": "search terms", "limit": 3}
    """
    try:
        # Load existing users
        data = load_users()
        users = data["users"]
        
        if not users:
            return MatchResponse(
                success=True,
                matches=[],
                count=0,
                recommendations=[]
            )
        
        # Get Claude recommendations
        match_names = get_claude_match(req.query, users, req.limit or 3)
        
        # Get the actual user data for matches
        matches = []
        for name in match_names:
            for user_data in users.values():
                if user_data['name'] == name:
                    matches.append(UserProfileData(**user_data))
                    break
        
        # Get top 3 as recommendations
        recommendations = matches[:3]
        
        ctx.logger.info(f"Claude found {len(matches)} matches for query: {req.query}")
        
        return MatchResponse(
            success=True,
            matches=matches,
            count=len(matches),
            recommendations=recommendations
        )
        
    except Exception as e:
        ctx.logger.error(f"Error matching users: {str(e)}")
        return MatchResponse(
            success=False,
            matches=[],
            count=0,
            recommendations=[],
            error=f"Match error: {str(e)}"
        )

@user_input_agent.on_rest_post("/get_profile", UserProfileRequest, UserProfileResponse)
async def get_user_profile(ctx: Context, req: UserProfileRequest) -> UserProfileResponse:
    """
    Get specific user profile
    Expected request format: {"user_id": "user123"}
    """
    try:
        # Load existing users
        data = load_users()
        users = data["users"]
        
        if req.user_id not in users:
            return UserProfileResponse(
                success=False,
                message="User not found",
                error=f"User {req.user_id} does not exist"
            )
        
        user_data = users[req.user_id]
        ctx.logger.info(f"Retrieved profile for user {req.user_id}")
        
        return UserProfileResponse(
            success=True,
            message="Profile retrieved successfully",
            user_id=req.user_id,
            timestamp=user_data["timestamp"]
        )
        
    except Exception as e:
        ctx.logger.error(f"Error getting profile: {str(e)}")
        return UserProfileResponse(
            success=False,
            message="Failed to get profile",
            error=f"Profile retrieval error: {str(e)}"
        )

@user_input_agent.on_rest_get("/health", HealthResponse)
async def health_check(ctx: Context) -> HealthResponse:
    """Health check endpoint with storage information"""
    try:
        users_data = load_users()
        total_users = users_data["metadata"]["total"]
        
        return HealthResponse(
            status="healthy",
            agent="user_profile_agent",
            storage_path=os.path.abspath(USERS_FILE),
            total_users=total_users
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            agent="user_profile_agent",
            storage_path=os.path.abspath(USERS_FILE),
            total_users=0
        )

if __name__ == "__main__":
    user_input_agent.run() 