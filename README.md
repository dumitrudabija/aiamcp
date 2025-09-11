# AIA Assessment MCP Server

A Model Context Protocol (MCP) server for Canada's Algorithmic Impact Assessment (AIA) framework, designed to work seamlessly with Claude Desktop and other MCP-compatible clients.

## Overview

This MCP server provides tools for conducting algorithmic impact assessments based on Canada's official AIA framework. It enables AI assistants to help users evaluate the risk levels of automated decision-making systems through a structured questionnaire process.

## Features

- **Official AIA Framework**: Based on Canada's Treasury Board Secretariat guidelines
- **Design Phase Assessment**: 116 Design phase questions (filtered from 162 total framework questions)
- **4-Tier Risk Classification**: Levels I-IV (Very Low to Very High Impact)
- **Completion Percentage Accuracy**: Fixed critical logic ensuring percentages never exceed 100%
- **Intelligent Workflow**: Guided assessment process with proper tool sequencing
- **Scoring Accuracy**: Fixed critical scoring issues for reliable results
- **Claude Desktop Integration**: Seamless integration with enhanced workflow guidance
- **Hallucination Prevention**: Enhanced tool descriptions prevent LLM clients from inventing information about AIA

## Quick Start

### Prerequisites
- Python 3.8+
- Claude Desktop (for MCP integration)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dumitrudabija/aiamcp.git
   cd aiamcp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Claude Desktop**:
   Add to your Claude Desktop configuration file:
   ```json
   {
     "mcpServers": {
       "aia-assessment": {
         "command": "node",
         "args": ["/absolute/path/to/aiamcp/build/index.js"]
       }
     }
   }
   ```

## MCP Tools

### 1. `analyze_project_description`
Analyzes a project description to categorize questions and identify assessment requirements.

**Parameters:**
- `projectName`: Name of the project
- `projectDescription`: Detailed description of the automated decision-making system

### 2. `get_questions`
Retrieves AIA questions by category or type for manual assessment.

**Parameters:**
- `category` (optional): Filter by category (Project, System, Algorithm, Decision, Impact, Data, Consultations, De-risking)
- `type` (optional): Filter by type (risk, mitigation)

### 3. `assess_project`
**FINAL STEP**: Calculates official AIA risk score using actual question responses.

**Parameters:**
- `projectName`: Name of the project
- `projectDescription`: Detailed description
- `responses`: Array of question responses with `questionId` and `selectedOption`

### 4. `functional_preview`
Early functional risk assessment for AI projects using Canada's AIA framework. Focuses on technical characteristics and planning insights.

**Parameters:**
- `projectName`: Name of the AI project being assessed
- `projectDescription`: Detailed description of the AI system's technical capabilities, data usage, decision-making scope, and affected populations

### 5. `export_assessment_report`
Export AIA assessment results to a Microsoft Word document. Creates a professional AIA compliance report with executive summary, key findings, and recommendations.

**Parameters:**
- `project_name`: Name of the project being assessed
- `project_description`: Description of the project and its automated decision-making components
- `assessment_results`: Assessment results object from previous assessment
- `custom_filename` (optional): Custom filename (without extension)

## Risk Assessment Framework

### Impact Levels
- **Level I (0-15 points)**: Very Low Impact - Minimal oversight required
- **Level II (16-30 points)**: Low Impact - Enhanced oversight required
- **Level III (31-50 points)**: Moderate Impact - Qualified oversight required
- **Level IV (51+ points)**: High Impact - Qualified oversight and approval required

### Scoring System
- **116 Design phase questions** (filtered from 162 total framework questions)
- **Maximum possible score**: 298 points
- **Automated calculation** based on official Treasury Board methodology
- **Accurate completion percentages** (never exceeding 100%)
- **Individual question scoring** with detailed breakdown

## Proper Usage Workflow

⚠️ **CRITICAL**: Follow this workflow to ensure accurate assessments:

1. **Project Analysis** (Optional):
   ```javascript
   use_mcp_tool("aia-assessment", "analyze_project_description", {
     "projectName": "AI System",
     "projectDescription": "Detailed description..."
   });
   ```

2. **Question Retrieval**:
   ```javascript
   use_mcp_tool("aia-assessment", "get_questions", {
     "type": "risk"
   });
   ```

3. **Collect Actual Responses** (Human Input Required):
   - Present questions to stakeholders
   - Collect actual `selectedOption` indices (0, 1, 2, etc.)
   - **Do NOT make assumptions or interpretations**

4. **Calculate Official Score**:
   ```javascript
   use_mcp_tool("aia-assessment", "assess_project", {
     "projectName": "AI System",
     "projectDescription": "Detailed description...",
     "responses": [
       {"questionId": "riskProfile1", "selectedOption": 1},
       {"questionId": "impact30", "selectedOption": 0}
       // ... more actual responses
     ]
   });
   ```

## Key Fixes and Improvements

### v1.3.0 - Completion Percentage Fix (Critical)
- **Issue**: System showed impossible completion percentages over 100% (e.g., 135%)
- **Root Cause**: Answered all 162 questions but calculated completion using only Design phase questions
- **Solution**: Updated all MCP tools to use only Design phase questions (116 questions) consistently
- **Impact**: Completion percentages now correctly show maximum 100%, matching official AIA survey behavior

### Scoring Fix (Critical)
- **Issue**: All assessments returned 0 points due to selectedOption format mismatch
- **Solution**: Proper mapping from numeric indices to choice values (e.g., "item1-3")
- **Impact**: Accurate risk scoring and impact level determination

### Workflow Guidance
- **Enhanced tool descriptions** with explicit warnings
- **Automatic workflow guidance** in responses
- **Prevention of AI assumptions** about risk levels
- **Consistent scoring methodology**

## Project Structure

```
aiamcp/
├── server.py                           # Main MCP server
├── aia_processor.py                    # Core AIA processing logic
├── data/survey-enfr.json              # Official AIA questionnaire
├── config.json                        # Configuration settings
├── requirements.txt                   # Python dependencies
├── README.md                          # This documentation
├── CLAUDE_DESKTOP_USAGE_GUIDE.md     # Detailed usage instructions
├── SCORING_FIX_DOCUMENTATION.md      # Technical fix documentation
├── claude_desktop_config.json        # Claude Desktop configuration
├── tests/                             # Test scenarios and validation
└── sample_reports/                    # Example assessment outputs
```

## Testing

### Validate Installation
```bash
python validate_mcp.py
```

### Test Scenarios
```bash
python test_mcp_server.py
```

### Comprehensive Testing
```bash
python test_mcp_comprehensive.py
```

## Configuration Files

### Claude Desktop Integration
- `claude_desktop_config.json` - Main configuration
- `claude_desktop_config_linux.json` - Linux-specific settings
- `claude_desktop_config_windows.json` - Windows-specific settings

### Assessment Configuration
- `config.json` - Scoring thresholds and framework settings
- `data/survey-enfr.json` - Official bilingual questionnaire data

## Troubleshooting

### Common Issues
1. **Path Resolution**: Use absolute paths in Claude Desktop configuration
2. **Working Directory**: Server automatically changes to script directory
3. **Protocol Version**: Server accepts client's protocol version
4. **Schema Validation**: All boolean values use Python `True`/`False`

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=1
python server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Treasury Board of Canada Secretariat for the AIA framework
- Model Context Protocol specification
- Claude Desktop team for MCP integration support

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/dumitrudabija/aiamcp/issues
- Documentation: See included guides and documentation files
