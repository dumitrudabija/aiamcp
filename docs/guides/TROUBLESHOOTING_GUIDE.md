# AIA Assessment MCP - Comprehensive Troubleshooting Guide

**Last Updated**: September 9, 2025, 3:04 PM (Toronto)
**Project**: Canada's Algorithmic Impact Assessment MCP Server

## Quick Status Check

### ✅ Verify Everything is Working
```bash
# 1. Check server can start and load data
cd /Users/dumitru.dabija/Documents/aia-assessment-mcp
/usr/bin/python3 server.py
# Should show: "Successfully loaded survey data" and "Loaded 162 questions"
# Press Ctrl+C to stop

# 2. Test MCP protocol
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | /usr/bin/python3 server.py
# Should return valid JSON response with server info

# 3. Test tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | /usr/bin/python3 server.py
# Should return 3 tools: assess_project, analyze_project_description, get_questions
```

## Common Issues and Solutions

### 1. **Data Files Not Loading**

#### Symptoms:
```
ERROR:aia_processor:Survey data file not found: data/survey-enfr.json
INFO:__main__:Loaded 0 questions
```

#### Root Cause:
Server not running from correct directory

#### Solution:
✅ **Already Fixed** - Server automatically changes to correct directory on startup
```python
# In server.py __init__ method:
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
```

#### Verification:
```bash
/usr/bin/python3 /Users/dumitru.dabija/Documents/aia-assessment-mcp/server.py
# Should show: "DEBUG: Changed working directory to: /Users/dumitru.dabija/Documents/aia-assessment-mcp"
```

### 2. **Claude Desktop Connection Issues**

#### Symptoms:
```
Server started and connected successfully
Server transport closed unexpectedly
Server disconnected
```

#### Root Causes & Solutions:

##### A. **Double Slash Path Error**
**Problem**: `//server.py` in logs
**Solution**: ✅ **Fixed** - Use absolute paths in configuration
```json
{
  "mcpServers": {
    "aia-assessment": {
      "command": "/usr/bin/python3",
      "args": ["/Users/dumitru.dabija/Documents/aia-assessment-mcp/server.py"],
      "env": {
        "PYTHONPATH": "/Users/dumitru.dabija/Documents/aia-assessment-mcp",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

##### B. **Zod Validation Errors**
**Problem**: Invalid JSON-RPC responses causing validation failures
**Solution**: ✅ **Fixed** - Proper notification handling
```python
# In server.py handle_request method:
elif method == "notifications/initialized":
    return None  # No response for notifications
```

### 3. **Schema Validation Errors**

#### Symptoms:
```
name 'false' is not defined
ZodError: Expected boolean, received undefined
```

#### Root Cause:
Using JavaScript `false` instead of Python `False`

#### Solution:
✅ **Already Fixed** - All schemas use Python `False`
```python
# Correct format in tool schemas:
"additionalProperties": False  # Not false
```

### 4. **Protocol Version Mismatch**

#### Symptoms:
Server responds with different protocol version than client expects

#### Solution:
✅ **Already Fixed** - Server accepts client's protocol version
```python
# In _initialize method:
client_protocol_version = params.get("protocolVersion", "2024-11-05")
```

## Configuration Verification

### Claude Desktop Config Location
```bash
# macOS
/Users/dumitru.dabija/Library/Application Support/Claude/claude_desktop_config.json

# Windows
%APPDATA%\Claude\claude_desktop_config.json

# Linux
~/.config/Claude/claude_desktop_config.json
```

### Correct Configuration Format
```json
{
  "mcpServers": {
    "aia-assessment": {
      "command": "/usr/bin/python3",
      "args": ["/Users/dumitru.dabija/Documents/aia-assessment-mcp/server.py"],
      "env": {
        "PYTHONPATH": "/Users/dumitru.dabija/Documents/aia-assessment-mcp",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Configuration Validation
```bash
# Validate JSON syntax
python3 -m json.tool "/Users/dumitru.dabija/Library/Application Support/Claude/claude_desktop_config.json"

# Check file exists
ls -la "/Users/dumitru.dabija/Library/Application Support/Claude/claude_desktop_config.json"

# Check server file exists and is executable
ls -la "/Users/dumitru.dabija/Documents/aia-assessment-mcp/server.py"
```

## Testing Procedures

### 1. **Manual Server Testing**
```bash
cd /Users/dumitru.dabija/Documents/aia-assessment-mcp

# Start server (will wait for input)
/usr/bin/python3 server.py

# In another terminal, test initialization:
echo '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"claude-ai","version":"0.1.0"}}}' | /usr/bin/python3 server.py
```

### 2. **Complete Protocol Flow Test**
```bash
cd /Users/dumitru.dabija/Documents/aia-assessment-mcp

# Test complete Claude Desktop sequence
(echo '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"claude-ai","version":"0.1.0"}}}'; echo '{"method":"notifications/initialized","jsonrpc":"2.0"}'; echo '{"method":"tools/list","params":{},"jsonrpc":"2.0","id":1}'; echo '{"method":"prompts/list","params":{},"jsonrpc":"2.0","id":2}'; echo '{"method":"resources/list","params":{},"jsonrpc":"2.0","id":3}') | /usr/bin/python3 server.py
```

### 3. **Tool Functionality Test**
```bash
cd /Users/dumitru.dabija/Documents/aia-assessment-mcp

# Test get_questions tool
echo '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_questions","arguments":{"category":"System"}}}' | /usr/bin/python3 server.py
```

## Expected Outputs

### 1. **Server Startup (Success)**
```
DEBUG: Changed working directory to: /Users/dumitru.dabija/Documents/aia-assessment-mcp
INFO:aia_processor:Successfully loaded survey data from data/survey-enfr.json
INFO:aia_processor:Extracted 162 scorable questions
INFO:aia_processor:Question categorization: Technical=115, Impact/Risk=16, Manual=31
INFO:aia_processor:Loaded impact thresholds from config: {1: (0, 30), 2: (31, 55), 3: (56, 75), 4: (76, 999)}
DEBUG: Starting AIA Assessment MCP Server...
INFO:__main__:Starting AIA Assessment MCP Server...
INFO:__main__:Loaded 162 questions
INFO:__main__:Question categories: 115 technical, 16 impact/risk, 31 manual
DEBUG: Server initialized, waiting for requests...
```

### 2. **Initialize Response (Success)**
```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "aia-assessment-server",
      "version": "1.0.0"
    }
  }
}
```

### 3. **Tools List Response (Success)**
Should return 3 tools with proper schemas:
- `assess_project`
- `analyze_project_description`
- `get_questions`

## Debugging Steps

### 1. **If Server Won't Start**
```bash
# Check Python version
/usr/bin/python3 --version

# Check file permissions
ls -la /Users/dumitru.dabija/Documents/aia-assessment-mcp/server.py

# Check data files exist
ls -la /Users/dumitru.dabija/Documents/aia-assessment-mcp/data/
ls -la /Users/dumitru.dabija/Documents/aia-assessment-mcp/config.json

# Run with verbose output
cd /Users/dumitru.dabija/Documents/aia-assessment-mcp
/usr/bin/python3 -v server.py
```

### 2. **If Claude Desktop Won't Connect**
```bash
# Check Claude Desktop logs (macOS)
tail -f ~/Library/Logs/Claude/claude.log

# Restart Claude Desktop completely
# 1. Quit Claude Desktop
# 2. Wait 5 seconds
# 3. Relaunch Claude Desktop

# Test configuration syntax
python3 -c "import json; print(json.load(open('/Users/dumitru.dabija/Library/Application Support/Claude/claude_desktop_config.json')))"
```

### 3. **If Tools Don't Work**
```bash
# Test individual tool manually
cd /Users/dumitru.dabija/Documents/aia-assessment-mcp
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_questions","arguments":{"category":"System"}}}' | /usr/bin/python3 server.py

# Check parameter format (must be camelCase)
# Correct: {"projectName": "test", "projectDescription": "test"}
# Wrong: {"project_name": "test", "project_description": "test"}
```

## Recovery Procedures

### 1. **Reset to Working State**
```bash
# Verify server file is correct
cd /Users/dumitru.dabija/Documents/aia-assessment-mcp
/usr/bin/python3 server.py
# Should show successful data loading

# Reset Claude Desktop config
cp claude_desktop_config.json "/Users/dumitru.dabija/Library/Application Support/Claude/claude_desktop_config.json"

# Restart Claude Desktop
```

### 2. **If All Else Fails**
```bash
# Check project status
cd /Users/dumitru.dabija/Documents/aia-assessment-mcp
cat PROJECT_STATUS.md

# Run comprehensive test
python3 test_mcp_comprehensive.py

# Manual verification of all components
echo "Testing server startup..."
timeout 5 /usr/bin/python3 server.py || echo "Server starts correctly"

echo "Testing data loading..."
/usr/bin/python3 -c "from aia_processor import AIAProcessor; p = AIAProcessor(); print(f'Loaded {len(p.scorable_questions)} questions')"
```

## Contact Information

If issues persist:
- **Project Location**: `/Users/dumitru.dabija/Documents/aia-assessment-mcp`
- **Status File**: `PROJECT_STATUS.md`
- **This Guide**: `TROUBLESHOOTING_GUIDE.md`
- **Main Server**: `server.py`
- **Configuration**: Claude Desktop config at `/Users/dumitru.dabija/Library/Application Support/Claude/claude_desktop_config.json`

## Success Indicators

✅ **Everything Working Correctly When:**
1. Server starts and shows "Loaded 162 questions"
2. Manual JSON-RPC calls return valid responses
3. Claude Desktop shows AIA assessment tools available
4. Tools return actual AIA question data
5. No Zod validation errors in Claude Desktop logs
6. No double slash (`//`) errors in paths

## ✅ CONFIRMED WORKING STATUS (September 9, 2025, 3:28 PM)

**Integration Status**: FULLY OPERATIONAL
- ✅ Claude Desktop successfully connects to MCP server
- ✅ All 3 tools (`assess_project`, `analyze_project_description`, `get_questions`) are discoverable
- ✅ Tools execute successfully and return proper AIA data
- ✅ No communication issues or protocol errors
- ✅ Server loads all 162 AIA questions correctly
- ✅ MCP logs show successful tool execution

**Current Configuration**: STABLE AND TESTED
```json
{
  "mcpServers": {
    "aia-assessment": {
      "command": "/usr/bin/python3",
      "args": ["/Users/dumitru.dabija/Documents/aia-assessment-mcp/server.py"],
      "env": {
        "PYTHONPATH": "/Users/dumitru.dabija/Documents/aia-assessment-mcp",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**No Known Issues**: All previously identified problems have been resolved.
