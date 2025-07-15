# GMS2 MCP Server
MCP server for working with GameMaker Studio 2 projects in Cursor IDE.

## What is this?
This MCP server parses and extracts information from GameMaker Studio 2 projects, providing developers and AI agents with quick access to project structure, GML code, and asset metadata.

**Key features:**
- 📊 **For developers**: export all project data in a readable format for study and analysis
- 🤖 **For AI agents**: rapid project structure understanding, significantly accelerating vibe-coding
- 🔍 **Deep analysis**: automatic scanning of objects, scripts, rooms, sprites and their relationships
- ⚡ **Instant access**: get information about any asset without opening GameMaker Studio 2

This solution makes working with GMS2 projects more efficient, especially when collaborating with neural networks.

## Project Structure
```
gms2-mcp-server/
├── mcp-serv/
│   ├── mcp_server.py       # MCP server with 7 tools 
│   ├── gms2_parser.py      # GameMaker Studio 2 project parser 
│   └── config.env          # Project configuration
├── docs/
│   ├── README.md           # Documentation in English
│   └── README_RU.md        # Documentation in Russian
├── requirements.txt        # Dependencies (mcp==1.11.0, python-dotenv==1.1.1)
└── venv/                   # Python virtual environment (created by user)

Additionally, the user creates:
└── .cursor/mcp.json       # Cursor IDE configuration
```

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/Atennebris/gms2-mcp-server
cd gms2-mcp-server
```

### 2. Create virtual environment
```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

**Current dependencies:**
- `mcp==1.11.0` - official Python SDK for Model Context Protocol
- `python-dotenv==1.1.1` - loading configuration from .env files

### 4. Configuration setup
Edit the `mcp-serv/config.env` file:
```env
# Path to your GMS2 project (required!)
GMS2_PROJECT_PATH=C:/Users/YourName/Downloads/Your GMS2 Project

# Example with spaces in path
GMS2_PROJECT_PATH=C:/Users/YourName/Downloads/Crystal Fusion
```

### 5. Cursor IDE configuration

Create a `.cursor/mcp.json` file in your project root with the following content:

#### Simple absolute path configuration (recommended):
```json
{
  "mcpServers": {
    "gms2-mcp": {
      "command": "python",
      "args": ["C:/Users/YourName/Desktop/gms2-mcp-server/mcp-serv/mcp_server.py"]
    }
  }
}
```

#### Option 2: Global configuration (for all projects)
1. In Cursor IDE, open settings
2. Go to **Tools & Integrations** section
3. Click **New MCP Server** button at the bottom
4. This will open the global mcp.json file
5. Add the same configuration there

**⚠️ Important:** Replace the path with the absolute path to your MCP server folder!

**Launch architecture:**
1. Cursor IDE directly launches `python mcp-serv/mcp_server.py`
2. `mcp_server.py` loads configuration from `mcp-serv/config.env` and initializes the parser
3. Parser `gms2_parser.py` provides functionality for working with GMS2 projects

### 6. Restart Cursor IDE
After configuring, restart Cursor IDE.
**In Cursor IDE:** Open command palette and check MCP servers status.

## Features

After successful installation, **7 tools** will be available in Cursor IDE:

- 🔍 **scan_gms2_project** - scan GMS2 project structure (count assets, find GML files)
- 📄 **get_gml_file_content** - read content of specific GML file
- 🏠 **get_room_info** - get detailed information about rooms from .yy files
- 🎯 **get_object_info** - analyze objects and their events from .yy files
- 🖼️ **get_sprite_info** - sprite information (dimensions, frames, settings)
- 📊 **export_project_data** - export all project data to text format
- 📋 **list_project_assets** - list all assets by categories (Objects, Scripts, Rooms, Sprites, etc.)

**Features:**
- Support for projects with spaces in paths (via config.env)
- Automatic project structure detection
- Export in human-readable format
- Full compatibility with .yyp and .yy file formats
- Simplified configuration without wrapper scripts

## Usage Example

In Cursor IDE (AI agent) you can ask:
```
"Show my GMS2 project structure"
"Read obj_player object code"
"What rooms are in the project?"
"Export all project data"
```

## System Requirements

- **Python:** 3.8+ (recommended 3.10+) - tested on 3.12
- **GameMaker Studio 2:** Any version with .yyp projects
- **Cursor IDE:** With MCP support
- **OS:** Windows 10/11 (tested)

## Troubleshooting

### MCP server shows red status
1. Check absolute path in `.cursor/mcp.json`
2. Make sure venv is created and dependencies are installed
3. Check project path in `mcp-serv/config.env`

### Server doesn't find the project
1. Make sure the path in `mcp-serv/config.env` is correct
2. Path should point to folder with .yyp file
3. Use forward slashes `/` even on Windows

### Tools don't display (0 tools)
1. Restart Cursor IDE
2. Check that Python interpreter is accessible
3. Test server manually: `python mcp-serv/mcp_server.py`

### Import errors or path issues
All import and path issues have been resolved in the current version:
- `gms2_parser.py` is now in the same directory as `mcp_server.py`
- `config.env` is located in the `mcp-serv/` directory
- No wrapper scripts needed

## Technical Information

### Dependencies
- `mcp==1.11.0` - official Python SDK for Model Context Protocol
- `python-dotenv==1.1.1` - loading configuration from .env files

### Architecture
The project consists of two main components:
- **mcp-serv/gms2_parser.py** - GameMaker Studio 2 project parser
- **mcp-serv/mcp_server.py** - MCP server with 7 tools for analysis

### What's Changed
**Version 2.0 improvements:**
- ✅ Simplified project structure (no wrapper scripts)
- ✅ Fixed all import and path issues
- ✅ Moved config.env to mcp-serv/ directory
- ✅ Consolidated all server code in mcp-serv/
- ✅ Simplified .cursor/mcp.json configuration
- ✅ Improved error handling and debugging

## Project History

This MCP server was created based on the idea and functionality of the [vibe2gml](https://github.com/zsturg/vibe2gml) project, which was also developed to simplify and accelerate vibe-coding in the GameMaker Studio 2 game engine.

**vibe2gml** is a tool for exporting GMS2 projects to text format for working with AI agents. Our MCP server develops this idea by providing:
- Direct integration with Cursor IDE through the MCP protocol
- A richer set of tools for project analysis
- Real-time data access without file export
- Simplified configuration and setup

## Additional Resources

### Documentation
- **docs/README.md** - main documentation in English
- **docs/README_RU.md** - main documentation in Russian

### Useful Links
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - official SDK
- [MCP Documentation](https://modelcontextprotocol.io/introduction) - protocol documentation
- [GameMaker Studio 2](https://gamemaker.io/) - official GameMaker website
- [vibe2gml](https://github.com/zsturg/vibe2gml) - original project that inspired the creation of this MCP server 
