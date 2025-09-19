# AIA Assessment MCP Server

A comprehensive Model Context Protocol (MCP) server for Canada's regulatory frameworks, including the Algorithmic Impact Assessment (AIA) and OSFI Guideline E-23 Model Risk Management. Designed to work seamlessly with Claude Desktop and other MCP-compatible clients.

## Overview

This MCP server provides tools for conducting regulatory assessments based on Canada's official frameworks:
- **AIA Framework**: Canada's Algorithmic Impact Assessment for automated decision systems
- **OSFI E-23**: Model Risk Management framework for federally regulated financial institutions

It enables AI assistants to help users evaluate risk levels and compliance requirements through structured assessment processes.

## Features

### AIA Framework (Algorithmic Impact Assessment)
- **Official AIA Framework**: Based on Canada's Treasury Board Secretariat guidelines
- **Official AIA Compliance**: 104 questions matching Canada's official framework (63 risk + 41 mitigation)
- **4-Tier Risk Classification**: Levels I-IV (Very Low to Very High Impact)
- **Official Scoring System**: Maximum 224 points aligned with Canada.ca framework
- **Completion Percentage Accuracy**: Fixed critical logic ensuring percentages never exceed 100%
- **Intelligent Workflow**: Guided assessment process with proper tool sequencing

### OSFI E-23 Framework (Model Risk Management)
- **Official OSFI E-23 Framework**: Based on Canada's OSFI Guideline E-23 for financial institutions
- **4-Tier Risk Rating**: Low, Medium, High, Critical risk levels
- **Comprehensive Risk Analysis**: Quantitative and qualitative risk factor assessment
- **Lifecycle Management**: Complete model lifecycle compliance (Design, Review, Deployment, Monitoring, Decommission)
- **Governance Framework**: Risk-based governance requirements and approval authorities
- **Professional Document Export**: 12-chapter comprehensive E-23 compliance reports

### General Features
- **Claude Desktop Integration**: Seamless integration with enhanced workflow guidance
- **Anti-Hallucination Safeguards**: Comprehensive compliance warnings and validation requirements
- **Professional Oversight**: Built-in requirements for qualified personnel validation
- **Audit Trail Support**: Complete documentation and review process tracking

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
   Add to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json`):
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

## MCP Tools (16 Tools Total)

### Transparency & Information Tools

#### 1. `get_server_introduction`
**TRANSPARENCY & CAPABILITIES**: Provides comprehensive introduction to MCP server capabilities, tool categories, workflow guidance, and critical distinction between official framework data (MCP) vs AI-generated interpretations (Claude). Essential for understanding data sources and regulatory compliance requirements.

**Parameters:**
- None required

**Returns:**
- Complete server capabilities overview
- Tool categories and descriptions
- Workflow guidance (recommended vs traditional approaches)
- Critical distinction between MCP official data vs Claude AI analysis
- Compliance warnings and professional validation requirements
- Usage examples (proper vs improper usage)
- Data source attribution and anti-hallucination design

**Visual Markers:**
- 🔧 MCP SERVER (Official): Official government data, validated calculations
- 🧠 CLAUDE ANALYSIS (AI-Generated): Interpretations, recommendations, gap analysis

### Workflow Management Tools

#### 2. `create_workflow`
**WORKFLOW CREATION**: Create and manage assessment workflows with automatic sequencing, state persistence, and smart routing. Provides guided assessment processes for AIA and OSFI E-23 frameworks.

**Parameters:**
- `projectName`: Name of the project for workflow management
- `projectDescription`: Project description for workflow creation
- `assessmentType` (optional): Type of assessment workflow (aia_full, aia_preview, osfi_e23, combined) - auto-detected if not provided

**Returns:**
- Workflow session ID for tracking
- Assessment type and workflow sequence
- Next step recommendations
- Usage instructions for workflow management

#### 3. `execute_workflow_step`
**WORKFLOW EXECUTION**: Execute specific tools within a managed workflow with automatic state tracking, dependency validation, and smart next-step recommendations.

**Parameters:**
- `sessionId`: Workflow session ID from create_workflow
- `toolName`: Name of the tool to execute within the workflow
- `toolArguments`: Arguments for the tool being executed

**Returns:**
- Tool execution results
- Workflow state updates
- Progress tracking
- Next step recommendations

#### 4. `get_workflow_status`
**STATUS TRACKING**: Get comprehensive workflow status including progress, next steps, smart routing recommendations, and session management.

**Parameters:**
- `sessionId`: Workflow session ID

**Returns:**
- Complete workflow progress and state
- Tool execution history
- Smart routing recommendations
- Available management options

#### 5. `auto_execute_workflow`
**AUTO-EXECUTION**: Automatically execute multiple workflow steps where possible, with intelligent dependency management and manual intervention detection.

**Parameters:**
- `sessionId`: Workflow session ID
- `stepsToExecute` (optional): Number of steps to auto-execute (default: 1, max: 5)

**Returns:**
- Auto-execution results for each step
- Success/failure status
- Manual intervention requirements
- Updated workflow state

### Description Validation Tool

#### 6. `validate_project_description`
**FIRST STEP**: Validates project descriptions for adequacy before conducting AIA or OSFI E-23 assessments. Ensures descriptions contain sufficient information across key areas required by both frameworks.

**Parameters:**
- `projectName`: Name of the project being validated
- `projectDescription`: Project description to validate for framework assessment readiness

**Returns:**
- Validation status (pass/fail)
- Coverage analysis for 6 content areas (System/Technology, Business Purpose, Data Sources, Impact Scope, Decision Process, Technical Architecture)
- Progressive feedback showing covered vs missing areas
- Framework readiness assessment for both AIA and OSFI E-23
- Detailed recommendations and content template if validation fails

**Minimum Requirements:**
- Total description: 100+ words
- Cover at least 3/6 content areas (50%+ coverage)
- Include specific, factual details for each covered area

### AIA Framework Tools

#### 7. `analyze_project_description`
Analyzes a project description to categorize questions and identify assessment requirements.

**Parameters:**
- `projectName`: Name of the project
- `projectDescription`: Detailed description of the automated decision-making system

#### 8. `get_questions`
Retrieves AIA questions by category or type for manual assessment.

**Parameters:**
- `category` (optional): Filter by category (Project, System, Algorithm, Decision, Impact, Data, Consultations, De-risking)
- `type` (optional): Filter by type (risk, mitigation)

#### 9. `assess_project`
**FINAL STEP**: Calculates official AIA risk score using actual question responses.

**Parameters:**
- `projectName`: Name of the project
- `projectDescription`: Detailed description
- `responses`: Array of question responses with `questionId` and `selectedOption`

#### 10. `functional_preview`
Early functional risk assessment for AI projects using Canada's AIA framework.

**Parameters:**
- `projectName`: Name of the AI project being assessed
- `projectDescription`: Detailed description of the AI system's technical capabilities

#### 11. `export_assessment_report`
Export AIA assessment results to a Microsoft Word document.

**Parameters:**
- `project_name`: Name of the project being assessed
- `project_description`: Description of the project
- `assessment_results`: Assessment results object from previous assessment
- `custom_filename` (optional): Custom filename (without extension)

### OSFI E-23 Framework Tools

#### 12. `assess_model_risk`
⚠️ **COMPLIANCE WARNING**: Assess model risk using OSFI E-23 framework. Requires professional validation.

**Parameters:**
- `projectName`: Name of the model being assessed
- `projectDescription`: **CRITICAL**: Factual, detailed description with specific technical architecture, documented data sources/volumes, explicit business use cases

#### 13. `evaluate_lifecycle_compliance`
Evaluate model lifecycle compliance against OSFI E-23 requirements across all 5 stages.

**Parameters:**
- `projectName`: Name of the model being evaluated
- `projectDescription`: Detailed description of the model and its current lifecycle stage
- `currentStage` (optional): Current lifecycle stage (Design, Review, Deployment, Monitoring, Decommission)

#### 14. `generate_risk_rating`
Generate detailed risk rating assessment using OSFI E-23 methodology.

**Parameters:**
- `projectName`: Name of the model being rated
- `projectDescription`: Detailed description including technical details, business impact, and usage context

#### 15. `create_compliance_framework`
Create comprehensive compliance framework based on OSFI E-23 requirements.

**Parameters:**
- `projectName`: Name of the model requiring compliance framework
- `projectDescription`: Detailed description of the model, its business purpose, and organizational context
- `riskLevel` (optional): Pre-determined risk level (Low, Medium, High, Critical)

#### 16. `export_e23_report`
⚠️ **COMPLIANCE WARNING**: Export OSFI E-23 assessment results to Microsoft Word document. Requires professional validation.

**Parameters:**
- `project_name`: Name of the model being assessed
- `project_description`: Description of the model and its business application
- `assessment_results`: Assessment results object from previous E-23 assessment
- `custom_filename` (optional): Custom filename (without extension)

## Risk Assessment Frameworks

### AIA Framework (Algorithmic Impact Assessment)

#### Impact Levels
- **Level I (0-30 points)**: Very Low Impact - Minimal oversight required
- **Level II (31-55 points)**: Low Impact - Enhanced oversight required
- **Level III (56-75 points)**: Moderate Impact - Qualified oversight required
- **Level IV (76+ points)**: High Impact - Qualified oversight and approval required

#### Scoring System
- **104 official AIA questions** (63 risk + 41 mitigation questions)
- **Maximum possible score**: 224 points
- **Official Canada.ca framework compliance** based on Tables 3 & 4
- **Design phase filtering** for mitigation questions only
- **Automated calculation** based on official Treasury Board methodology

### OSFI E-23 Framework (Model Risk Management)

#### Risk Rating Levels
- **Low (0-25 points)**: Minimal governance requirements - Basic documentation and annual reviews
- **Medium (26-50 points)**: Standard governance requirements - Regular monitoring and semi-annual reviews
- **High (51-75 points)**: Enhanced governance requirements - Comprehensive oversight and quarterly reviews
- **Critical (76-100 points)**: Maximum governance requirements - Continuous monitoring and monthly reviews

#### Risk Assessment Methodology
- **Quantitative Risk Factors**: Portfolio size, financial impact, operational criticality, customer base, transaction volume
- **Qualitative Risk Factors**: Model complexity, autonomy level, explainability, AI/ML usage, third-party dependencies
- **Risk Amplification**: Applied for dangerous combinations (e.g., AI/ML in financial decisions)
- **Governance Requirements**: Risk-based approach with appropriate approval authorities

#### Model Lifecycle Management
1. **Design**: Clear rationale, data governance, methodology documentation
2. **Review**: Independent validation, performance evaluation, risk rating confirmation
3. **Deployment**: Quality control, production testing, monitoring setup
4. **Monitoring**: Performance tracking, drift detection, escalation procedures
5. **Decommission**: Formal retirement, documentation retention, impact assessment

### Official Framework Compliance Methodology

Our implementation achieves 98% compliance with Canada's official AIA framework by:

1. **Question Selection**: Extracting questions from official survey pages that correspond to Canada.ca Tables 3 & 4:
   - **Risk Questions (63)**: From projectDetails, businessDrivers, riskProfile, projectAuthority, aboutSystem, aboutAlgorithm, decisionSector, impact, and aboutData pages
   - **Mitigation Questions (41)**: From Design phase only - consultationDesign, dataQualityDesign, fairnessDesign, and privacyDesign pages

2. **Scoring Alignment**: 
   - **Actual achievable score**: 224 points (vs theoretical 244)
   - **Impact thresholds adjusted** to work with actual scoring range
   - **Question weighting** preserved from official framework

3. **Framework Fidelity**:
   - **104/106 questions** (98% coverage) - closest possible match to official framework
   - **All 8 official categories** represented with proper question distribution
   - **Design vs Implementation phase** filtering applied correctly for mitigation questions

## Usage Workflows

### Option 1: Server Introduction (Recommended First Step)

⚠️ **NEW**: Start with transparency introduction to understand capabilities and data distinction:

```javascript
use_mcp_tool("aia-assessment", "get_server_introduction", {});
```
- Provides comprehensive server capabilities overview
- Explains MCP official data vs Claude AI analysis distinction
- Shows workflow guidance and best practices
- One-time orientation for new users

### Option 2: Managed Workflow (Recommended)

⚠️ **INTELLIGENT AUTOMATION**: Use workflow management for automated sequencing, state persistence, and smart routing:

1. **Create Workflow Session**:
   ```javascript
   use_mcp_tool("aia-assessment", "create_workflow", {
     "projectName": "AI System",
     "projectDescription": "Detailed description...",
     "assessmentType": "aia_preview"  // or auto-detect
   });
   ```
   - Returns session ID and workflow sequence
   - Auto-detects assessment type (AIA/OSFI E-23/Combined)
   - Provides guided next steps

2. **Execute Steps with Auto-Management**:
   ```javascript
   use_mcp_tool("aia-assessment", "auto_execute_workflow", {
     "sessionId": "session-id-from-step-1",
     "stepsToExecute": 3
   });
   ```
   - Automatically validates dependencies
   - Executes compatible steps in sequence
   - Maintains state between calls
   - Provides smart routing recommendations

3. **Check Progress and Status**:
   ```javascript
   use_mcp_tool("aia-assessment", "get_workflow_status", {
     "sessionId": "session-id"
   });
   ```
   - Shows completion percentage
   - Lists completed and remaining steps
   - Provides next-step recommendations

4. **Manual Step Execution** (when needed):
   ```javascript
   use_mcp_tool("aia-assessment", "execute_workflow_step", {
     "sessionId": "session-id",
     "toolName": "assess_project",
     "toolArguments": {...}
   });
   ```

### Option 3: Manual Workflow (Traditional)

⚠️ **CRITICAL**: Follow this workflow to ensure accurate assessments:

1. **Description Validation** (REQUIRED FIRST STEP):
   ```javascript
   use_mcp_tool("aia-assessment", "validate_project_description", {
     "projectName": "AI System",
     "projectDescription": "Detailed description covering system, business purpose, data, impact, decisions, and architecture..."
   });
   ```
   - **Must pass validation** before proceeding with framework assessments
   - Ensures description covers minimum 3/6 content areas and 100+ words
   - Provides detailed feedback on missing areas and improvement recommendations

2. **Project Analysis** (Optional):
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

### v1.8.0 - MCP Transparency & AI Distinction System (Latest)
- **Feature**: Comprehensive transparency system distinguishing MCP official data from Claude AI interpretations
- **Addition**: Server introduction tool providing complete capabilities overview and usage guidance
- **Enhancement**: Visual markers (🔧 MCP SERVER vs 🧠 CLAUDE ANALYSIS) for content distinction
- **Impact**: Clear regulatory compliance through data source transparency

### v1.7.0 - Intelligent Workflow Management System
- **Feature**: Complete workflow engine with auto-execution, state persistence, and dependency validation
- **Addition**: Smart routing recommendations and session management
- **Enhancement**: Automated tool sequencing with manual intervention detection
- **Impact**: Streamlined assessment processes with guided workflows

### v1.6.0 - Project Description Validation Guardrails
- **Feature**: Mandatory validation system ensuring adequate project descriptions before assessments
- **Addition**: 6 content area coverage analysis with progressive feedback
- **Enhancement**: Framework readiness assessment with detailed recommendations
- **Impact**: Prevents insufficient descriptions from proceeding to regulatory assessments

### v1.4.0 - Official Framework Compliance (Critical)
- **Issue**: System extracted 162 questions instead of official 106 questions from Canada's AIA framework
- **Root Cause**: Survey data contained both official and additional questions beyond the official framework
- **Solution**: Implemented official question filtering to extract exactly 104 questions (63 risk + 41 mitigation) matching Canada.ca Tables 3 & 4
- **Impact**: System now complies with official AIA framework structure and scoring (224 max points)

### v1.3.0 - Completion Percentage Fix (Critical)
- **Issue**: System showed impossible completion percentages over 100% (e.g., 135%)
- **Root Cause**: Answered all 162 questions but calculated completion using only Design phase questions
- **Solution**: Updated all MCP tools to use only official AIA questions (104 questions) consistently
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

## ⚠️ Critical Compliance Notice

**REGULATORY COMPLIANCE WARNING**: This tool provides structured assessment frameworks only. 

### Professional Validation Required
- **All results must be validated** by qualified professionals
- **Risk assessments must be based** on factual, verifiable project information
- **Generated reports are templates** requiring professional review and approval
- **Appropriate governance authorities** must approve all assessments before regulatory use

### Anti-Hallucination Safeguards
- **Rule-based risk detection** using factual keyword matching (not AI interpretation)
- **Transparent scoring methodology** with predetermined formulas
- **Built-in compliance warnings** in all tools and results
- **Professional oversight requirements** embedded in all outputs

### Documentation Requirements
- See `OSFI_E23_COMPLIANCE_GUIDANCE.md` for detailed compliance requirements
- See `AIA_HALLUCINATION_PREVENTION.md` for AIA-specific safeguards
- Maintain complete audit trails for all assessments

## Project Structure

```
aiamcp/
├── server.py                           # Main MCP server
├── aia_processor.py                    # Core AIA processing logic
├── osfi_e23_processor.py              # OSFI E-23 processing logic
├── data/survey-enfr.json              # Official AIA questionnaire
├── config.json                        # Configuration settings
├── requirements.txt                   # Python dependencies
├── README.md                          # This documentation
├── OSFI_E23_COMPLIANCE_GUIDANCE.md   # OSFI E-23 compliance requirements
├── AIA_HALLUCINATION_PREVENTION.md   # AIA anti-hallucination safeguards
├── CLAUDE_DESKTOP_USAGE_GUIDE.md     # Detailed usage instructions
├── SCORING_FIX_DOCUMENTATION.md      # Technical fix documentation
├── claude_desktop_config.json        # Claude Desktop configuration
├── tests/                             # Test scenarios and validation
├── AIA_Assessments/                   # Generated assessment reports
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
