# User Profile Management System

A Flask-based web application with a Fetch.ai agent for creating, managing, and AI-powered matchmaking of user profiles using Claude.

## Features

- **User Profile Creation**: Create detailed user profiles with bio, interests, skills, location, and profession
- **AI-Powered Matchmaking**: Use Claude to find the best matches based on natural language queries
- **Smart Recommendations**: Get personalized user recommendations using advanced AI understanding
- **Profile Retrieval**: Retrieve specific user profiles by ID
- **Modern UI**: Beautiful, responsive web interface with AI badges
- **Real-time Health Monitoring**: System status indicator

## Architecture

The system consists of two main components:

1. **User Profile Agent** (`user_input_agent.py`): A Fetch.ai agent that handles profile storage and Claude-based matchmaking
2. **Flask Frontend** (`frontend_app.py`): Web interface for interacting with the agent

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip
- Anthropic API key (for Claude AI)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd user-input-agent
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 🔑 Setting Up the Anthropic API Key

**Option 1: Interactive Setup (Recommended)**
```bash
python setup_api_key.py
```
This will guide you through the setup process and test your API key.

**Option 2: Manual Setup**

1. **Get an API key from Anthropic:**
   - Visit: https://console.anthropic.com/
   - Sign up or log in
   - Create a new API key

2. **Set the API key using one of these methods:**

   **Method A: Environment Variable**
   ```bash
   # macOS/Linux
   export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
   
   # Windows Command Prompt
   set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
   
   # Windows PowerShell
   $env:ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
   ```

   **Method B: .env File**
   ```bash
   # Create a .env file in the project directory
   echo "ANTHROPIC_API_KEY=sk-ant-api03-your-key-here" > .env
   ```

   **Method C: Permanent Environment Variable**
   ```bash
   # macOS/Linux - Add to ~/.bashrc or ~/.zshrc
   echo 'export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Test your API key:**
   ```bash
   python test_matchmaking.py
   ```

### Running the System

1. **Start the User Profile Agent:**
   ```bash
   python user_input_agent.py
   ```
   The agent will start on port 8003.

2. **Start the Flask Frontend (in a new terminal):**
   ```bash
   python frontend_app.py
   ```
   The web interface will be available at `http://localhost:5000`.

## Usage

### Web Interface

1. **Create User Profile:**
   - Fill in the required fields (User ID, Name, Bio)
   - Optionally add interests, skills, location, and profession
   - Click "Create Profile"

2. **AI Matchmaking:**
   - Describe what you're looking for in natural language
   - Set the number of matches you want
   - Click "Find Matches" to get AI-powered recommendations
   - View results with "BEST MATCH" indicators

3. **Get Specific Profile:**
   - Enter a user ID
   - Click "Get Profile" to retrieve the complete profile

### API Endpoints

The agent provides the following REST endpoints:

#### Create Profile
```bash
POST http://127.0.0.1:8003/create_profile
Content-Type: application/json

{
    "user_id": "user123",
    "name": "John Doe",
    "bio": "Software developer passionate about AI",
    "interests": ["technology", "music", "travel"],
    "skills": ["Python", "JavaScript", "Machine Learning"],
    "location": "San Francisco, CA",
    "profession": "Software Engineer"
}
```

#### AI Matchmaking
```bash
POST http://127.0.0.1:8003/match_users
Content-Type: application/json

{
    "query": "Video director for a hip-hop visualizer",
    "limit": 3
}
```

#### Get Profile
```bash
POST http://127.0.0.1:8003/get_profile
Content-Type: application/json

{
    "user_id": "user123",
    "name": "",
    "bio": "",
    "interests": [],
    "skills": []
}
```

#### Health Check
```bash
GET http://127.0.0.1:8003/health
```

### Frontend API Endpoints

The Flask frontend provides these endpoints:

- `POST /create_profile` - Create a new user profile
- `POST /match_users` - AI-powered user matching
- `POST /get_profile` - Get a specific user profile
- `GET /health` - System health check
- `GET /api/users` - List all users (debug endpoint)

## AI Matchmaking Algorithm

The system uses Claude 3 Opus for intelligent matchmaking:

1. **Natural Language Understanding**: Claude analyzes the query in natural language
2. **Profile Analysis**: Claude evaluates all user profiles against the request
3. **Contextual Matching**: Considers bio, skills, interests, profession, and location
4. **Ranked Recommendations**: Returns matches in order of best fit
5. **Best Match Highlighting**: Frontend highlights the top recommendation

### Example Queries

- "Video director for a hip-hop visualizer"
- "Python developer for AI project"
- "Graphic designer for startup branding"
- "Musician for jazz collaboration"

## Data Storage

User profiles are stored in `user_profiles.json` with the following structure:

```json
{
    "users": {
        "user123": {
            "user_id": "user123",
            "name": "John Doe",
            "bio": "Software developer...",
            "interests": ["technology", "music"],
            "skills": ["Python", "JavaScript"],
            "location": "San Francisco, CA",
            "profession": "Software Engineer",
            "timestamp": "2024-01-15T10:30:00",
            "metadata": {
                "agent_address": "fetch1...",
                "profile_length": 45,
                "interests_count": 2,
                "skills_count": 2,
                "created_at": "2024-01-15T10:30:00"
            }
        }
    },
    "metadata": {
        "total": 1,
        "last_updated": "2024-01-15T10:30:00"
    }
}
```

## Example Workflows

### Creating and Finding Users

1. **Create several user profiles:**
   ```
   User 1: John (Python developer, San Francisco)
   User 2: Sarah (Data scientist, New York)
   User 3: Mike (Frontend developer, Los Angeles)
   ```

2. **Search for "Python developer for AI project":**
   - AI Analysis: Claude understands the context
   - Results: John (best match), Sarah (good match)
   - Recommendations: John, Sarah

3. **Search for "Video director for music video":**
   - AI Analysis: Claude looks for creative/video skills
   - Results: Based on available profiles
   - Recommendations: Best matching profiles

### Profile Management

- Each profile has a unique user ID
- Profiles can be updated by creating with the same user ID
- All profile data is analyzed by Claude for matching
- Timestamps track creation/update times

## Troubleshooting

### Common Issues

1. **Agent not responding:**
   - Check if the agent is running on port 8003
   - Verify the agent address in the frontend configuration

2. **Claude API errors:**
   - Ensure ANTHROPIC_API_KEY is set correctly
   - Check API key permissions and quota
   - Verify internet connectivity
   - Run `python setup_api_key.py` to test your key

3. **Import errors:**
   - Ensure all dependencies are installed
   - Check Python version compatibility

4. **Storage issues:**
   - Verify write permissions in the project directory
   - Check if `user_profiles.json` is accessible

### API Key Troubleshooting

**Check if API key is set:**
```bash
echo $ANTHROPIC_API_KEY  # macOS/Linux
echo %ANTHROPIC_API_KEY% # Windows
```

**Test API key manually:**
```bash
python setup_api_key.py
```

**Common API key issues:**
- Key format should start with `sk-ant-`
- Check for extra spaces or characters
- Ensure the key is active in your Anthropic console
- Verify you have sufficient API credits

### Health Monitoring

The system includes real-time health monitoring:
- Frontend status indicator (top-right corner)
- Agent health endpoint
- Automatic health checks every 30 seconds

## Development

### Project Structure

```
user-input-agent/
├── user_input_agent.py      # Fetch.ai agent with Claude integration
├── frontend_app.py          # Flask web application
├── templates/
│   └── index.html          # Web interface with AI badges
├── user_profiles.json      # Profile storage
├── requirements.txt        # Python dependencies (includes anthropic)
├── setup_api_key.py       # API key setup script
├── test_matchmaking.py    # Test suite
├── env_template.txt       # Environment template
└── README.md              # This file
```

### Adding Features

To extend the system:

1. **New Profile Fields**: Add fields to the `UserProfileRequest` model
2. **Enhanced AI Matching**: Modify the Claude prompt in `get_claude_match()`
3. **Additional Endpoints**: Add new REST endpoints to the agent
4. **UI Improvements**: Update the HTML template and JavaScript

## License

This project is part of the Innovation Lab Examples collection.

## Support

For issues or questions, check the troubleshooting section or review the agent logs for detailed error information. 