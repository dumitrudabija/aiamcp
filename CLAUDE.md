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
- **Introduction Workflow Enforcement**: Mandatory get_server_introduction call before any assessment tools, ensuring users understand frameworks and data sources
- **Explicit Workflow Sequences (v1.15.0)**: Complete 6-step OSFI E-23 and 5-step AIA workflows embedded in get_server_introduction response with step-by-step guidance
- **Step-Numbered Tool Descriptions (v1.15.0)**: All OSFI E-23 tools labeled with their position (STEP X OF 6) and full workflow context
- **Behavioral Directives (v1.15.0)**: Strong instructions to present introduction first, show all workflow steps, and wait for user choice before proceeding
- **Streamlined Risk-Adaptive Reports**: OSFI E-23 exports generate concise 4-6 page documents with risk-adaptive content (tone/depth varies by risk level)
- **Intelligent Workflow Management**: Auto-sequencing, state persistence, dependency validation, and smart routing
- **Enhanced Workflow Visibility**: Complete workflow roadmap with numbered steps, descriptions, and progress tracking
- **Flexible Dependency Resolution**: Export tools can work with either preview or full assessments
- **Lifecycle-Focused OSFI E-23 Reports**: Reports organized by current lifecycle stage (Design/Review/Deployment/Monitoring/Decommission)
- **OSFI E-23 Official Terminology**: Uses actual Principles (1.1-3.6), Outcomes (1-3), and Appendix 1 tracking fields
- **Stage-Specific Compliance**: Only shows requirements relevant to current lifecycle stage
- **Compliance-Centered Design**: Enhanced checklist with OSFI Principle references and deliverable mapping
- **Granular Risk Analysis**: Detailed scoring breakdown with individual factor analysis and transparent calculations
- **Risk Amplification Transparency**: Clear display of when and why risk multipliers are applied
- **Description Validation Gates**: Mandatory validation before framework assessments ensure adequate information coverage
- **Strict Validation Enforcement**: Contradictory validation results eliminated, workflows blocked when validation fails
- **Export Data Validation**: Export tools validate assessment_results, auto-inject from workflow state, prevent misleading default values
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

# Test transparency features
python test_transparency_features.py

# Test validation enforcement (critical bug fix)
python test_validation_enforcement.py

# Test export validation (critical bug fix)
python test_export_validation.py

# Test introduction workflow enforcement
python test_introduction_enforcement.py

# Test streamlined E-23 report generation
python test_streamlined_e23_report.py

# Test workflow guidance (v1.15.0)
python test_workflow_guidance.py
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

## Transparency and Data Source Distinction

### Critical Understanding
- **MCP Server provides OFFICIAL regulatory data** - all calculations, scores, and compliance determinations come from verified government sources
- **Claude provides AI interpretation** - explanations, recommendations, and gap analysis based on official MCP results
- **Anti-hallucination design** - AI cannot modify official scores, risk levels, or compliance determinations

### Visual Markers in Tool Responses
- **🔧 MCP SERVER (Official)**: Canada.ca AIA framework questions/scoring, OSFI E-23 methodology, validated calculations
- **🧠 CLAUDE ANALYSIS (AI-Generated)**: Interpretations, recommendations, gap analysis, planning guidance
- **⚠️ COMPLIANCE WARNINGS**: Professional validation requirements, regulatory compliance notes

### Transparency Tool
- **get_server_introduction**: CRITICAL first-call tool that MUST be called at the START of assessment conversations
- **Mandatory triggers**: User mentions assessment, AIA, OSFI, compliance, or provides project description for evaluation; especially "run through OSFI/AIA framework"
- **Complete Workflow Sequences (v1.15.0)**: Response includes explicit 6-step OSFI E-23 workflow and 5-step AIA workflow with detailed purpose/output for each step
- **Behavioral instructions**: Tool description includes "CALL THIS ALONE" warning to prevent calling other tools simultaneously
- **Enhanced Directives (v1.15.0)**: Response includes "STOP AND PRESENT THIS INTRODUCTION FIRST" to ensure workflow visibility before assessment execution
- **Anti-invention directive**: Tool response includes assistant_directive preventing Claude from adding time estimates or invented content
- **Framework selection guidance**: After calling, present 4 clear options (AIA, OSFI E-23, Workflow Mode, Combined) and WAIT for user to choose before proceeding
- **Step Context**: All tools show their position in the workflow (e.g., "STEP 2 OF 6") for better navigation

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
- **Complete 6-Step Workflow (v1.15.0)**: (1) validate_project_description, (2) assess_model_risk, (3) evaluate_lifecycle_compliance, (4) generate_risk_rating, (5) create_compliance_framework, (6) export_e23_report
- **Risk Rating Methodology**: Quantitative and qualitative risk factors with amplification logic
- **Lifecycle Management**: 5-stage model lifecycle (Design, Review, Deployment, Monitoring, Decommission)
- **Governance Framework**: Risk-based approval authorities and oversight requirements
- **Professional Compliance**: Built-in warnings about regulatory validation requirements
- **Report Structure**: Simplified Chapter 1 with executive summary, detailed calculations in Annex A for improved readability
- **Minimum Viable Assessment**: Steps 1, 2, and 6 provide basic compliance; all 6 steps provide comprehensive coverage

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
- **Transparency Tools**: get_server_introduction
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

### OSFI E-23 Report Structure (v1.8.1+)
- **Simplified Chapter 1**: Focuses on executive summary and overall risk rating for improved readability
- **Comprehensive Annex A**: Contains detailed risk calculations, step-by-step methodology, and factor analysis
- **Enhanced User Experience**: Technical details segregated from executive summary while maintaining full transparency
- **Mathematical Transparency**: All calculation steps preserved in Annex A with explicit factor breakdowns

### Error Handling
- **Graceful Degradation**: Missing data files trigger default framework creation
- **Comprehensive Validation**: Question IDs and choice values validated before scoring
- **Detailed Logging**: All operations logged for troubleshooting and audit trails