# Changelog

All notable changes to the AIA Assessment MCP Server project are documented in this file.

## [1.1.0] - 2025-09-09

### 🔧 Critical Fixes

#### Scoring System Fix
- **Fixed critical scoring issue** where all assessments returned 0 points
- **Root Cause**: `selectedOption` indices (0, 1, 2) were not being properly mapped to choice values ("item1-3", "item2-0")
- **Solution**: Implemented proper index-to-value mapping in `_assess_project` method
- **Impact**: Assessments now return accurate risk scores and impact levels

#### Test Results
- **High-Risk Scenario**: 49 points → Impact Level IV (Very High Impact) ✅
- **Low-Risk Scenario**: 5 points → Impact Level I (Little to no impact) ✅

### 🚀 Workflow Enhancements

#### Claude Desktop Integration Improvements
- **Enhanced tool descriptions** with explicit workflow warnings
- **Added workflow guidance** in tool responses to prevent AI assumptions
- **Implemented proper tool sequencing** to ensure accurate assessments

#### Tool Description Updates
- `assess_project`: Added "FINAL STEP" and "CRITICAL" warnings
- `responses` parameter: Marked as "REQUIRED" with clear expectations
- Added explicit warnings against making assumptions about risk levels

#### Automatic Workflow Guidance
- **Without responses**: Shows warning message and step-by-step workflow
- **With responses**: Confirms valid assessment completion
- **Prevents inconsistencies** between AI interpretations and calculated scores

### 📚 Documentation Overhaul

#### New Documentation
- `README.md`: Comprehensive project documentation with proper MCP focus
- `CLAUDE_DESKTOP_USAGE_GUIDE.md`: Detailed usage instructions and workflow
- `SCORING_FIX_DOCUMENTATION.md`: Technical documentation of the scoring fix
- `CHANGELOG.md`: This changelog file

#### Removed Outdated Files
- `DEMO_CONVERSATION_TEMPLATES.md`: Outdated demo content
- `DEMO_VERIFICATION_CHECKLIST.md`: Superseded by comprehensive testing
- `WORKFLOW_GUIDANCE.md`: Consolidated into usage guide
- `SCHEMA_FIXES_LOG.md`: Consolidated into this changelog

### 🔄 Configuration Updates

#### MCP Server Configuration
- **Protocol Version Handling**: Server accepts client's protocol version
- **Working Directory**: Automatic change to script directory for data file access
- **Schema Validation**: Fixed Python boolean syntax (`True`/`False` vs `true`/`false`)
- **Error Handling**: Improved notification handling and response validation

#### Claude Desktop Configuration
- Updated configuration examples for all platforms (Linux, Windows, macOS)
- Added absolute path requirements and troubleshooting guidance
- Provided working configuration templates

### 🧪 Testing Improvements

#### Validation Scripts
- `validate_mcp.py`: MCP server validation and diagnostics
- `test_mcp_comprehensive.py`: Comprehensive testing suite
- `test_mcp_server.py`: Core server functionality testing

#### Test Scenarios
- High-risk assessment scenarios with expected outcomes
- Low-risk assessment scenarios for validation
- Edge case handling and error condition testing

### 📊 Framework Compliance

#### AIA Framework Implementation
- **162 total questions** from official Treasury Board questionnaire
- **4-tier risk classification** (Levels I-IV)
- **Maximum score**: 298 points
- **Proper impact level thresholds**: 0-15, 16-30, 31-50, 51+ points

#### Question Categorization
- **115 technical questions**: Auto-answerable from project descriptions
- **16 impact/risk questions**: Require analysis and reasoning
- **31 manual questions**: Require human stakeholder input

## [1.0.0] - 2025-09-08

### 🎉 Initial Release

#### Core Features
- MCP server implementation for AIA assessments
- Integration with Canada's official AIA framework
- Basic question retrieval and project assessment tools
- Claude Desktop integration support

#### Known Issues (Fixed in 1.1.0)
- Scoring system returned 0 points for all assessments
- Workflow guidance insufficient for proper tool usage
- Documentation focused on outdated FastAPI implementation

---

## Upgrade Guide

### From 1.0.0 to 1.1.0

1. **Update server.py**: The scoring fix is critical for accurate assessments
2. **Review workflow**: Follow the new 4-step workflow for proper assessments
3. **Update documentation**: Use the new comprehensive guides
4. **Test thoroughly**: Validate that scoring works correctly with test scenarios

### Breaking Changes
- None - all changes are backward compatible

### Deprecations
- None in this release

---

## Contributing

When contributing to this project:

1. **Update this changelog** with your changes
2. **Follow semantic versioning** for version numbers
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Test thoroughly** with both high and low-risk scenarios

## Support

For issues related to specific versions:
- **v1.1.0+**: Use GitHub Issues with full error details
- **v1.0.0**: Upgrade to v1.1.0 to resolve scoring issues

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/) format.*
