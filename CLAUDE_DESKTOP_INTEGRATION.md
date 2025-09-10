# Claude Desktop Integration Guide
## AIA Assessment MCP Server

This guide provides step-by-step instructions for integrating the AIA Assessment MCP server with Claude Desktop.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Finding Claude Desktop Config Location](#finding-claude-desktop-config-location)
3. [Configuration Setup](#configuration-setup)
4. [Integration Testing](#integration-testing)
5. [Troubleshooting](#troubleshooting)
6. [Visual Verification](#visual-verification)

## Prerequisites

Before starting, ensure you have:
- ✅ Claude Desktop installed and working
- ✅ Python 3.7+ installed on your system
- ✅ AIA Assessment MCP server files in place
- ✅ All validation tests passing (run `python3 validate_mcp.py`)

## Finding Claude Desktop Config Location

The Claude Desktop configuration file location varies by operating system:

### macOS
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Windows
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

### Linux
```bash
~/.config/Claude/claude_desktop_config.json
```

### How to Access the Config File

#### Method 1: Direct File Access
1. **macOS**: Open Finder → Press `Cmd+Shift+G` → Enter `~/Library/Application Support/Claude/`
2. **Windows**: Open File Explorer → Enter `%APPDATA%\Claude\` in the address bar
3. **Linux**: Open file manager → Navigate to `~/.config/Claude/`

#### Method 2: Terminal/Command Line
```bash
# macOS/Linux
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows
notepad %APPDATA%\Claude\claude_desktop_config.json
```

## Configuration Setup

### Step 1: Backup Existing Configuration
Before making changes, backup your existing configuration:
```bash
# macOS/Linux
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup

# Windows
copy %APPDATA%\Claude\claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json.backup
```

### Step 2: Choose the Correct Configuration

Select the appropriate configuration file for your system:

#### For macOS (Current System)
Use the configuration from `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aia-assessment": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/Users/dumitru.dabija/Documents/AI MCP playground/AIA MCP playground/aia-assessment-mcp",
      "env": {
        "PYTHONPATH": "/Users/dumitru.dabija/Documents/AI MCP playground/AIA MCP playground/aia-assessment-mcp",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

#### For Windows
Use the configuration from `claude_desktop_config_windows.json`:

```json
{
  "mcpServers": {
    "aia-assessment": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "C:\\Users\\%USERNAME%\\Documents\\aia-assessment-mcp",
      "env": {
        "PYTHONPATH": "C:\\Users\\%USERNAME%\\Documents\\aia-assessment-mcp",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

#### For Linux
Use the configuration from `claude_desktop_config_linux.json`:

```json
{
  "mcpServers": {
    "aia-assessment": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/home/$USER/Documents/aia-assessment-mcp",
      "env": {
        "PYTHONPATH": "/home/$USER/Documents/aia-assessment-mcp",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Step 3: Update Paths for Your System

**IMPORTANT**: Update the `cwd` path to match your actual installation directory:

1. Find your actual project path:
   ```bash
   # In your aia-assessment-mcp directory
   pwd
   ```

2. Replace the `cwd` value in the configuration with your actual path

3. Update the `PYTHONPATH` environment variable to match

### Step 4: Merge with Existing Configuration

If you already have other MCP servers configured, merge the new configuration:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "aia-assessment": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/your/actual/path/to/aia-assessment-mcp",
      "env": {
        "PYTHONPATH": "/your/actual/path/to/aia-assessment-mcp",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Step 5: Validate JSON Syntax

Before saving, validate your JSON syntax:
```bash
# Test JSON validity
python3 -m json.tool claude_desktop_config.json
```

## Integration Testing

### Step 1: Restart Claude Desktop
1. **Completely quit** Claude Desktop (not just close the window)
2. **Wait 5 seconds** for all processes to stop
3. **Restart** Claude Desktop
4. **Wait for full startup** (about 10-15 seconds)

### Step 2: Verify MCP Server Connection

Look for these visual indicators in Claude Desktop:

#### Success Indicators:
- ✅ No error messages on startup
- ✅ Claude Desktop starts normally
- ✅ You can start a new conversation
- ✅ MCP tools are available (see Visual Verification section)

#### Failure Indicators:
- ❌ Error popup on Claude Desktop startup
- ❌ Claude Desktop crashes or won't start
- ❌ "MCP server failed to start" messages
- ❌ Tools not appearing in conversation

### Step 3: Test Tool Availability

In a new Claude Desktop conversation, try these test phrases:

1. **"What MCP tools do you have available?"**
   - Should mention AIA assessment tools

2. **"Use the get_questions_summary tool"**
   - Should return AIA framework summary

3. **"Show me technical questions using get_questions_by_category"**
   - Should return categorized questions

## Visual Verification

### How to Confirm Integration is Working

#### In Claude Desktop Interface:
1. **Start a new conversation**
2. **Type**: "What tools do you have available for algorithmic impact assessment?"
3. **Expected Response**: Claude should mention having access to AIA assessment tools
4. **Tool Usage**: When Claude uses tools, you'll see:
   - Tool name being called
   - Parameters being passed
   - Results being returned

#### Tool Call Examples:
When working correctly, you'll see Claude make calls like:
```
🔧 Using get_questions_summary...
🔧 Using assess_project with parameters: {...}
🔧 Using calculate_assessment_score...
```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "MCP server failed to start"
**Symptoms**: Error popup when starting Claude Desktop

**Solutions**:
1. **Check paths**: Verify `cwd` path exists and is correct
2. **Check Python**: Ensure Python command works: `python3 --version`
3. **Check permissions**: Ensure Claude Desktop can access the directory
4. **Run validation**: Execute `python3 validate_mcp.py` in your project directory

#### Issue 2: "No such file or directory"
**Symptoms**: Server starts but tools don't work

**Solutions**:
1. **Verify server.py exists** in the specified `cwd` directory
2. **Check file permissions**: Ensure files are readable
3. **Validate dependencies**: Run the validation script

#### Issue 3: "Python command not found"
**Symptoms**: Server won't start, Python errors

**Solutions**:
1. **Try different Python commands**: `python3`, `python`, `py`
2. **Check Python installation**: `which python3` or `where python`
3. **Update configuration**: Use the correct Python command for your system

#### Issue 4: "JSON syntax error"
**Symptoms**: Claude Desktop won't start, config file errors

**Solutions**:
1. **Validate JSON**: `python3 -m json.tool claude_desktop_config.json`
2. **Check commas**: Ensure proper comma placement
3. **Check quotes**: All strings must use double quotes
4. **Restore backup**: If needed, restore from backup file

#### Issue 5: Tools not appearing
**Symptoms**: Claude Desktop starts but doesn't mention AIA tools

**Solutions**:
1. **Wait longer**: Give Claude Desktop 30+ seconds to fully initialize
2. **Restart completely**: Quit and restart Claude Desktop
3. **Check logs**: Look for error messages in Claude Desktop
4. **Test manually**: Run `python3 server.py` directly to test

### Advanced Diagnostics

#### Manual Server Testing
```bash
# Test server directly
cd /path/to/aia-assessment-mcp
python3 server.py

# Should start and wait for input
# Press Ctrl+C to stop
```

#### Connection Testing
```bash
# Run the validation script
python3 validate_mcp.py

# Should show all green checkmarks
```

#### Log Analysis
Check Claude Desktop logs (locations vary by OS):
- **macOS**: `~/Library/Logs/Claude/`
- **Windows**: `%LOCALAPPDATA%\Claude\logs\`
- **Linux**: `~/.local/share/Claude/logs/`

### Performance Benchmarks

Expected response times:
- **get_questions_summary**: < 1 second
- **get_questions_by_category**: < 2 seconds  
- **calculate_assessment_score**: < 3 seconds
- **assess_project**: < 5 seconds

If responses are slower, check:
1. System resources (CPU, memory)
2. File I/O performance
3. Python environment setup

## Backup Testing Method

If Claude Desktop integration fails during a demo, you can use the standalone testing method:

### Emergency Fallback
1. **Open terminal** in the `aia-assessment-mcp` directory
2. **Run**: `python3 test_mcp_comprehensive.py`
3. **Show results**: Demonstrates all functionality working
4. **Explain**: "This shows the same tools that would be available in Claude Desktop"

### Demo Recovery Steps
1. **Acknowledge the issue**: "Let me show you the functionality directly"
2. **Switch to terminal**: Run validation or comprehensive tests
3. **Explain capabilities**: Walk through the test results
4. **Promise follow-up**: "We'll get the Claude Desktop integration working after the demo"

## Success Checklist

Before your demo, verify:
- [ ] ✅ `python3 validate_mcp.py` shows all green checkmarks
- [ ] ✅ Claude Desktop starts without errors
- [ ] ✅ New conversation can be created
- [ ] ✅ "What tools do you have?" mentions AIA assessment
- [ ] ✅ `get_questions_summary` tool works
- [ ] ✅ `assess_project` tool works with sample data
- [ ] ✅ Response times are acceptable (< 5 seconds)
- [ ] ✅ Backup testing method ready if needed

## Next Steps

Once integration is confirmed working:
1. **Practice demo conversations** using the test templates
2. **Prepare sample project descriptions** for live assessment
3. **Test end-to-end workflows** from description to JIRA ticket
4. **Have backup plans ready** in case of technical issues

---

**Need Help?** Run `python3 validate_mcp.py` for comprehensive diagnostics, or check the troubleshooting section above.
