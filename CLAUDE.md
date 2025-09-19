# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server for Canada's regulatory frameworks - the Algorithmic Impact Assessment (AIA) and OSFI Guideline E-23 Model Risk Management. The server provides tools for conducting structured regulatory assessments through Claude Desktop integration.

## Core Architecture

### Main Components
- **server.py**: Main MCP server handling JSON-RPC over stdio
- **workflow_engine.py**: Workflow management, state persistence, and smart routing
- **aia_processor.py**: Core AIA assessment logic and official framework compliance
- **osfi_e23_processor.py**: OSFI E-23 model risk management assessment logic
- **description_validator.py**: Project description validation for framework readiness
- **data/survey-enfr.json**: Official bilingual AIA questionnaire data
- **config.json**: Framework configuration and scoring thresholds

### Key Design Patterns
- **Official Framework Compliance**: Strict adherence to Canada's official AIA (104 questions) and OSFI E-23 frameworks
- **Intelligent Workflow Management**: Auto-sequencing, state persistence, dependency validation, and smart routing
- **Description Validation Gates**: Mandatory validation before framework assessments ensure adequate information coverage
- **Anti-Hallucination Safeguards**: Rule-based risk detection using factual keyword matching, not AI interpretation
- **Professional Validation Requirements**: All tools emphasize that results require professional review
- **Audit Trail Support**: Complete documentation and review process tracking

## Development Commands

### Testing
```bash
# Validate MCP server installation
python validate_mcp.py

# Run comprehensive test suite
python test_mcp_comprehensive.py

# Test specific components
python test_mcp_server.py
python test_functional_preview.py
python test_design_phase_filtering.py

# Test description validation
python test_description_validation.py

# Test workflow enhancements
python test_workflow_enhancements.py
```

### Running the Server
```bash
# Start MCP server (typically called by Claude Desktop)
python server.py

# Debug mode
export DEBUG=1
python server.py
```

### Dependencies
```bash
pip install -r requirements.txt
```

## Workflow Management

### Recommended Approach
- **Use workflow management tools** for automated sequencing and state persistence
- **create_workflow** as the entry point for new assessments
- **auto_execute_workflow** for compatible automated steps
- **execute_workflow_step** for manual intervention steps
- **get_workflow_status** for progress tracking and next-step recommendations

### Session Management
- **2-hour session timeout** for workflow persistence
- **In-memory state storage** with automatic cleanup
- **Progress tracking** across all tool executions
- **Dependency validation** prevents out-of-order execution

### Auto-Detection Features
- **Assessment type detection** based on project description keywords
- **Smart routing recommendations** based on current state
- **Compatible step identification** for auto-execution
- **Manual intervention detection** when human input required

## Framework-Specific Requirements

### Project Description Validation
- **Mandatory First Step**: All framework assessment tools now validate project descriptions
- **6 Content Areas**: System/Technology, Business Purpose, Data Sources, Impact Scope, Decision Process, Technical Architecture
- **Minimum Requirements**: 100+ words total, 3+ content areas covered (50%+ coverage)
- **Progressive Feedback**: Shows covered areas vs missing areas with detailed recommendations
- **Validation Bypass**: Tools return validation failure with guidance instead of proceeding with insufficient descriptions

### AIA Framework Compliance
- **Exact Question Count**: Must maintain 104 official questions (63 risk + 41 mitigation)
- **Scoring Integrity**: Maximum 224 points (not theoretical 244) based on actual achievable scores
- **Design Phase Filtering**: Mitigation questions only apply during Design phase
- **Official Question IDs**: Preserve question IDs matching Canada.ca Tables 3 & 4

### OSFI E-23 Framework Requirements
- **Risk Rating Methodology**: Quantitative and qualitative risk factors with amplification logic
- **Lifecycle Management**: 5-stage model lifecycle (Design, Review, Deployment, Monitoring, Decommission)
- **Governance Framework**: Risk-based approval authorities and oversight requirements
- **Professional Compliance**: Built-in warnings about regulatory validation requirements

## Critical Compliance Notes

### When Working with Assessment Logic
1. **Never modify scoring calculations** without verifying against official frameworks
2. **Preserve question filtering logic** - especially Design phase filtering for AIA mitigation questions
3. **Maintain professional validation warnings** in all tool responses
4. **Use rule-based risk detection** - avoid AI interpretation of risk levels

### File Modification Guidelines
- **aia_processor.py**: Contains official AIA question extraction and scoring - modify with extreme caution
- **osfi_e23_processor.py**: Contains OSFI E-23 risk methodology - changes must align with regulatory requirements
- **config.json**: Scoring thresholds match official frameworks - validate any changes
- **data/survey-enfr.json**: Official government data - should not be modified

### Testing Requirements
- **Always run validate_mcp.py** after server modifications
- **Test scoring accuracy** with test_design_phase_filtering.py for AIA changes
- **Verify MCP protocol compliance** with test_mcp_server.py

## MCP Integration

### Claude Desktop Configuration
- Server runs via Python with absolute paths
- Working directory automatically set to script location
- Protocol version negotiation handled automatically
- All boolean values use Python True/False

### Tool Categories
- **Workflow Management**: create_workflow, execute_workflow_step, get_workflow_status, auto_execute_workflow
- **Validation Tools**: validate_project_description
- **AIA Tools**: analyze_project_description, get_questions, assess_project, functional_preview, export_assessment_report
- **OSFI E-23 Tools**: assess_model_risk, evaluate_lifecycle_compliance, generate_risk_rating, create_compliance_framework, export_e23_report

## Key Architectural Decisions

### Scoring System
- **Official Compliance Over Theoretical Maximums**: Uses actual achievable scores (224 for AIA) rather than theoretical maximums
- **Fixed Completion Percentage Logic**: Prevents impossible >100% completion rates
- **Professional Validation Emphasis**: All results include warnings about required professional review

### Anti-Hallucination Design
- **Rule-Based Risk Detection**: Uses keyword matching and predetermined formulas
- **Transparent Methodology**: All scoring calculations are deterministic and auditable
- **No AI Risk Interpretation**: Server provides structure, Claude Desktop provides reasoning

### Error Handling
- **Graceful Degradation**: Missing data files trigger default framework creation
- **Comprehensive Validation**: Question IDs and choice values validated before scoring
- **Detailed Logging**: All operations logged for troubleshooting and audit trails