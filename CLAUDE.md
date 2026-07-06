# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server for Canada's regulatory frameworks - the Algorithmic Impact Assessment (AIA) and OSFI Guideline E-23 Model Risk Management. The server provides tools for conducting structured regulatory assessments through Claude Desktop integration.

## Core Architecture

### Main Components (v2.0.0 Modular Structure)

**Core Server**
- **server.py**: Main MCP server handling JSON-RPC over stdio
- **workflow_engine.py**: Workflow management, state persistence, and smart routing

**Framework Processors**
- **aia_processor.py**: Core AIA assessment logic and official framework compliance
- **osfi_e23_processor.py**: Governance requirement and compliance recommendation generation for OSFI E-23 (risk scoring itself lives in risk_dimension_extraction.py)
- **description_validator.py**: Project description validation for framework readiness

**AIA Modules** (v2.0.0)
- **aia_analysis.py**: Centralized AIA intelligence, question handling, and scoring
- **aia_report_generator.py**: Professional Word document generation for AIA compliance

**OSFI E-23 Modules**
- **osfi_e23_risk_dimensions.py**: 8 Risk Dimensions framework with 47 factors (v3.4)
- **risk_dimension_extraction.py**: AI-assisted contextual extraction with deterministic scoring (v3.1)
- **osfi_e23_structure.py**: Official OSFI Principles, lifecycle definitions, and dimension-to-lifecycle mapping
- **osfi_e23_report_generators.py**: Stage-specific report generation

**Shared Modules** (v2.0.0)
- **utils/data_extractors.py**: Unified data extraction for AIA and OSFI assessments
- **introduction_builder.py**: Framework-specific workflow guidance and introductions
- **utils/framework_detection.py**: Smart context detection for AIA/OSFI/Combined
- **config/tool_registry.py**: Tool metadata and MCP protocol registration

**Data Files**
- **data/survey-enfr.json**: Official bilingual AIA questionnaire data
- **config/config.json**: Framework configuration and scoring thresholds

### Key Design Patterns
- **Modular Architecture (v2.0.0)**: Clean separation of concerns with specialized modules; server.py is a thin orchestration layer
- **Delegation Pattern (v2.0.0)**: Server.py orchestrates through dependency injection to specialized modules
- **Lazy Processor Loading**: All heavy processors initialize on first tool call (not at startup) via `_load_processors()`, keeping server startup fast
- **Official Framework Compliance**: Strict adherence to Canada's official AIA (104 questions) and OSFI E-23 frameworks
- **Introduction Workflow Enforcement**: Mandatory get_server_introduction call before any assessment tools, ensuring users understand frameworks and data sources
- **Explicit Workflow Sequences (v3.0)**: 3-step OSFI E-23 workflow (validate → assess → export) and 5-step AIA workflow in get_server_introduction response
- **Behavioral Directives (v1.15.0)**: Strong instructions embedded in tool responses (via introduction_builder.py) to present introduction first, show all workflow steps, and wait for user choice before proceeding
- **Streamlined Risk-Adaptive Reports**: OSFI E-23 exports generate ~8-12 page documents with standardized structure (Executive Summary, Risk by Dimension, Stage Requirements, Annex A Factor Details, Annex B Principles)
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
python scripts/validate_mcp.py

# Run comprehensive integration test suite
python tests/integration/test_mcp_comprehensive.py

# Test specific components
python tests/integration/test_mcp_server.py
python tests/functional/test_functional_preview.py
python tests/unit/test_design_phase_filtering.py

# Test description validation
python tests/unit/test_description_validation.py

# Test workflow enhancements
python tests/functional/test_workflow_enhancements.py

# Test transparency features
python tests/functional/test_transparency_features.py

# Test validation enforcement
python test_validation_enforcement.py

# Test export validation
python test_export_validation.py

# Test introduction workflow enforcement
python test_introduction_enforcement.py

# Test workflow guidance
python test_workflow_guidance.py

# Test extraction integration (v3.1.0)
python test_extraction_integration.py
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

### Critical Understanding (v2.2.10)
- **⚠️ PROOF OF CONCEPT**: This MCP server uses official framework structures but implements exemplification logic requiring institutional customization
- **What is OFFICIAL**: AIA questions (104 from Canada.ca), OSFI E-23 Principles (1.1-3.6), lifecycle stages, framework structure
- **What is PROOF OF CONCEPT**: Risk scoring weights, thresholds, formulas, governance mappings, amplification factors, requirements interpretation
- **Claude provides AI interpretation** - explanations, recommendations, and gap analysis based on MCP framework results
- **Customization REQUIRED** - Financial institutions must validate and adapt all implementation logic to their institutional framework

### Visual Markers in Tool Responses
- **🔧 MCP SERVER**: Official framework structures (AIA questions, OSFI principles) + Proof of concept implementation logic (scoring, calculations)
- **🧠 CLAUDE ANALYSIS (AI-Generated)**: Interpretations, recommendations, gap analysis, planning guidance
- **⚠️ COMPLIANCE WARNINGS**: Professional validation requirements, customization needs, regulatory compliance notes
- **⚙️ TUNABLE PARAMETERS**: Risk weights, thresholds, governance mappings require institutional adaptation

### Transparency Tool
- **get_server_introduction**: CRITICAL first-call tool that MUST be called at the START of assessment conversations
- **Mandatory triggers**: User mentions assessment, AIA, OSFI, compliance, or provides project description for evaluation; especially "run through OSFI/AIA framework"
- **Complete Workflow Sequences (v3.0)**: Response includes explicit 3-step OSFI E-23 workflow and 5-step AIA workflow with detailed purpose/output for each step
- **Behavioral instructions**: Tool response (from introduction_builder.py) includes "STOP AND PRESENT THIS INTRODUCTION FIRST" directive to ensure workflow visibility before assessment execution
- **Anti-invention directive**: Tool response includes assistant_directive preventing Claude from adding time estimates or invented content
- **Framework selection guidance**: After calling, present options (AIA, OSFI E-23, or both) and WAIT for user to choose before proceeding
- **Smart detection**: Pass `user_context` to auto-detect relevant framework from user's message

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
- **Smart Auto-Injection (v3.3.1)**: Export tools check for required keys (`factor_scores`, `dimension_assessments`) and auto-inject from session if data is partial or missing
- **Defensive JSON Handling (v3.3.1)**: Extraction validation accepts JSON with or without `dimensions` wrapper for robustness

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
- **Complete 3-Step Workflow (v3.0)**: (1) validate_project_description, (2) assess_model_risk (user confirms lifecycle stage), (3) export_e23_report
- **Two-Phase Extraction Workflow (v3.3)**: assess_model_risk uses AI-assisted extraction:
  - **Phase 1**: MCP returns extraction prompt → Claude analyzes and extracts 47 factor values
  - **Phase 2**: Claude immediately calls assess_model_risk with `extracted_factors` → MCP validates and scores deterministically
  - **No user confirmation step** - transparency achieved through Annex A in final report
- **8 Risk Dimensions (v3.4)**: Risk assessment uses 8 dimensions with 47 factors (15 quantitative, 32 qualitative) - adds Data Provenance & Supply Chain Risk (4 factors) and Systemic & Concentration Risk (3 factors) to the original 6 dimensions, plus 9 new factors (GenAI confabulation risk, GenAI output benchmarking, pre-deployment fairness testing, adversarial/prompt-injection testing, AI system classification, GenAI scope constraint, automation bias, AI incident response, kill switch) folded into the original 6
- **NOT_STATED Handling**: Missing factors default to Medium risk (score=2), tracked for transparency in Annex A
- **NOT_APPLICABLE Handling (v3.4)**: Factors that opt in via `allow_na` (e.g. synthetic data quality, GenAI-conditional factors) score as Low when explicitly marked not applicable, distinct from NOT_STATED
- **PORTFOLIO_REVIEW_REQUIRED Handling (v3.4)**: The portfolio-level AI estate concentration factor is excluded from its dimension's average when institution-wide inventory data is unavailable (rather than defaulting to Medium), and is tracked in a `follow_up_actions` list
- **Lifecycle Management**: 5-stage model lifecycle (Design, Review, Deployment, Monitoring, Decommission)
- **Governance Framework**: Risk-based approval authorities and oversight requirements
- **Professional Compliance**: Built-in warnings about regulatory validation requirements
- **Report Structure (v3.3)**: Sections 1-3 + Annex A (Factor Details) + Annex B (OSFI Principles)

## Critical Compliance Notes

### When Working with Assessment Logic
1. **Never modify scoring calculations** without verifying against official frameworks
2. **Preserve question filtering logic** - especially Design phase filtering for AIA mitigation questions
3. **Maintain professional validation warnings** in all tool responses
4. **Use rule-based risk detection** - avoid AI interpretation of risk levels

### File Modification Guidelines (v2.0.0 Updated)

**Framework Processors (Official Logic - Modify with Extreme Caution)**
- **aia_processor.py**: Official AIA question extraction and scoring - regulatory compliance required
- **osfi_e23_processor.py**: Governance requirement and compliance recommendation generation (risk scoring lives in osfi_e23_risk_dimensions.py / risk_dimension_extraction.py) - changes must align with regulatory requirements
- **osfi_e23_structure.py**: Official OSFI Principles (1.1-3.6) and lifecycle definitions - verify against OSFI E-23 guideline

**AIA Modules (v2.0.0)**
- **aia_analysis.py**: AIA intelligence, question handling, and scoring logic - test thoroughly with validate_functionality.py
- **aia_report_generator.py**: AIA document generation - changes affect compliance report format

**OSFI E-23 Modules**
- **osfi_e23_risk_dimensions.py**: 8 Risk Dimensions with 47 factors - core risk framework definition
- **risk_dimension_extraction.py**: AI-assisted extraction module - generates prompts and scores deterministically
- **osfi_e23_report_generators.py**: Stage-specific report generation - changes affect regulatory document output

**Configurable Prompt Templates (v3.2.0)**
- **config/extraction_prompts.yaml**: Tunable extraction prompt templates for OSFI E-23 risk factor extraction
  - Edit this YAML file to tune Claude's extraction behavior without changing Python code
  - Supports: header text, instructions, factor templates, JSON output format, behavioral instructions
  - Changes take effect on server restart (or call `reload_prompt_config()` for hot reload)
  - Falls back to built-in defaults if config is missing or malformed

**Shared Modules (v2.0.0)**
- **utils/data_extractors.py**: Data extraction patterns for both frameworks - changes affect both AIA and OSFI tools
- **utils/framework_detection.py**: Context detection logic - changes affect workflow routing
- **config/tool_registry.py**: Tool metadata and MCP registration - changes affect Claude Desktop integration
- **introduction_builder.py**: Workflow guidance - changes affect user experience and framework selection

**Core Orchestration**
- **server.py**: Main orchestration layer (delegations only) - modifications should be minimal, most logic in modules
- **workflow_engine.py**: Workflow management and state - changes affect automated assessment progression
- **description_validator.py**: Validation logic - changes affect quality gates

**Data & Configuration**
- **data/survey-enfr.json**: Official government AIA questionnaire - should NEVER be modified (official source)
- **config/config.json**: Scoring thresholds matching official frameworks - validate any changes against official sources
- **config/extraction_prompts.yaml**: Tunable prompt templates - safe to modify for institutional customization (v3.2.0)

### Testing Requirements (v2.0.0 Updated)
- **Always run validate_functionality.py** after any module modifications - comprehensive 8/8 validation suite
- **Run scripts/validate_mcp.py** to verify MCP server installation and configuration
- **Test scoring accuracy** with `tests/unit/test_design_phase_filtering.py` for AIA changes
- **Verify MCP protocol compliance** with `tests/integration/test_mcp_server.py`
- **Module-specific tests**: Changes to individual modules should maintain all validation tests passing

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
- **OSFI E-23 Tools**: assess_model_risk (8 Risk Dimensions + lifecycle stage), export_e23_report (stage-specific requirements + checklists; assessment data retrieved automatically from server-side session — do NOT pass assessment_results)

## Key Architectural Decisions

### Scoring System
- **Official Compliance Over Theoretical Maximums**: Uses actual achievable scores (224 for AIA) rather than theoretical maximums
- **Fixed Completion Percentage Logic**: Prevents impossible >100% completion rates
- **Professional Validation Emphasis**: All results include warnings about required professional review

### Anti-Hallucination Design
- **Rule-Based Risk Detection**: Uses keyword matching and predetermined formulas
- **Transparent Methodology**: All scoring calculations are deterministic and auditable
- **No AI Risk Interpretation**: Server provides structure, Claude Desktop provides reasoning

### OSFI E-23 Report Structure (v3.3.0)
- **Session-Based Data Retrieval**: `export_e23_report` does NOT accept `assessment_results` as a parameter — the server retrieves assessment data automatically from server-side session state populated by `assess_model_risk`. Do not pass assessment data in the tool call.
- **Streamlined Format**: Executive Summary, Risk Assessment by Dimension, Stage Requirements, Annex A (Factor Details), Annex B (OSFI Principles)
- **Section 1: Executive Summary**: Risk level, governance requirements, key risk drivers from dimension assessment
- **Section 2: Risk Assessment by Dimension**: Summary table showing 8 dimensions with risk level (Low/Medium/High/Critical) and core question
- **Section 3: [STAGE] Stage Requirements**: Lifecycle-specific checklist items scaled to risk level per OSFI Principle 2.3
- **Annex A: Detailed Factor Assessment** (v3.3.0 NEW): Full transparency with 8 tables (one per dimension) showing:
  - Factor name
  - Scoring Matrix (Low/Medium/High/Critical thresholds)
  - Determined Value with risk level (e.g., "500000 (Low)", "NOT_STATED (Medium - default)", "N/A (Low - Not Applicable)" for `allow_na` factors, or "Portfolio Review Required (Insufficient inventory data)" for the portfolio-concentration factor)
  - Evidence quote from project description (empty for NOT_STATED)
- **Annex B: OSFI E-23 Principles**: All Principles 1.1-3.6 organized by Outcome
- **Target Length**: Approximately 8-12 pages with professional formatting
- **Customizable Weights**: Explicit note that scoring weights are exemplification - can be tuned to institutional specifications

### Error Handling
- **Graceful Degradation**: Missing data files trigger default framework creation
- **Comprehensive Validation**: Question IDs and choice values validated before scoring
- **Detailed Logging**: All operations logged for troubleshooting and audit trails
- **Diagnostic Logging (v3.3.1)**: Export and report generation include detailed data flow logging to help troubleshoot issues with missing or partial data
- **MCP-Compliant Errors**: Tool errors return MCP result objects with `isError: True` (not JSON-RPC error codes), ensuring Claude Desktop surfaces error messages correctly