# Developer Guide

**Version**: 2.0.0
**Last Updated**: November 16, 2025
**For**: Contributors and developers extending the AIA Assessment MCP Server

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Codebase Navigation](#codebase-navigation)
4. [Common Development Tasks](#common-development-tasks)
5. [Testing Guide](#testing-guide)
6. [Adding a New Framework](#adding-a-new-framework)
7. [Debugging Guide](#debugging-guide)
8. [Best Practices](#best-practices)
9. [Code Review Checklist](#code-review-checklist)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Python 3.9+
- pip or pip3
- Git
- Text editor or IDE (VS Code recommended)
- Claude Desktop (for MCP testing)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/dumitrudabija/aiamcp.git
cd aiamcp

# Install dependencies
pip3 install -r requirements.txt

# Validate installation
python3 validate_mcp.py

# Run comprehensive tests
python3 validate_functionality.py
```

Expected output: `8/8 validations passed`

---

## Development Environment Setup

### Recommended IDE Configuration

#### VS Code
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

### Git Configuration

```bash
# Set up pre-commit validation hook (optional)
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
python3 validate_functionality.py
if [ $? -ne 0 ]; then
    echo "❌ Validation failed - commit aborted"
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=1
python3 server.py
```

---

## Codebase Navigation

### v2.0.0 Module Map

```
Core Entry Point:
└─ server.py (1,305 lines)
   ├─ MCP protocol handling
   ├─ Tool routing
   └─ Delegation to modules

Framework-Specific Logic:
├─ AIA Modules/
│  ├─ aia_analysis.py (1,027 lines)
│  │  └─ Intelligent analysis, question handling
│  └─ aia_report_generator.py (277 lines)
│     └─ Word document generation
│
└─ OSFI E-23 Modules/
   ├─ osfi_e23_structure.py
   │  └─ Official Principles & lifecycle
   └─ osfi_e23_report_generators.py
      └─ Stage-specific reports

Shared Infrastructure:
├─ utils/
│  ├─ data_extractors.py (1,047 lines)
│  │  └─ AIADataExtractor, OSFIE23DataExtractor
│  └─ framework_detection.py (108 lines)
│     └─ FrameworkDetector
│
├─ config/
│  └─ tool_registry.py (365 lines)
│     └─ Tool metadata
│
└─ introduction_builder.py (364 lines)
   └─ Workflow guidance

Foundation:
├─ aia_processor.py
│  └─ Official AIA 104 questions
├─ osfi_e23_processor.py
│  └─ OSFI E-23 risk methodology
├─ workflow_engine.py
│  └─ Workflow state management
└─ description_validator.py
   └─ Quality gates
```

### File Modification Cheat Sheet

| Modification Type | Primary Files | Test Files |
|-------------------|---------------|------------|
| AIA analysis logic | `aia_analysis.py` | `validate_functionality.py` |
| AIA reports | `aia_report_generator.py` | Manual .docx review |
| OSFI reports | `osfi_e23_report_generators.py` | Manual .docx review |
| Data extraction | `utils/data_extractors.py` | `validate_functionality.py` |
| Framework detection | `utils/framework_detection.py` | `test_framework_detection.py` |
| Workflow guidance | `introduction_builder.py` | Manual testing |
| New tool | `config/tool_registry.py`, `server.py` | `validate_mcp.py` |

**⚠️ DO NOT MODIFY**:
- `data/survey-enfr.json` - Official government data
- `config.json` scoring thresholds without verification

---

## Common Development Tasks

### Task 1: Add a New AIA Analysis Feature

**Goal**: Add keyword detection for a new domain (e.g., healthcare AI)

**Steps**:

1. **Edit aia_analysis.py**:
```python
# Add to _intelligent_project_analysis method
healthcare_keywords = ["medical", "patient", "diagnosis", "healthcare"]
if any(kw in description_lower for kw in healthcare_keywords):
    # Add healthcare-specific question answering logic
    pass
```

2. **Test**:
```bash
python3 validate_functionality.py
# Should show 8/8 passing
```

3. **Manual test** with sample healthcare AI description

---

### Task 2: Modify Report Format

**Goal**: Add a new section to AIA reports

**Steps**:

1. **Edit aia_report_generator.py**:
```python
def _export_assessment_report(self, arguments):
    # ... existing code ...

    # Add new section
    doc.add_heading('Risk Mitigation Strategies', level=1)
    strategies = self._generate_mitigation_strategies(assessment_results)
    for strategy in strategies:
        doc.add_paragraph(strategy, style='List Bullet')
```

2. **Add helper method**:
```python
def _generate_mitigation_strategies(self, assessment_results):
    """Generate risk mitigation strategies."""
    # Implementation
    return strategies
```

3. **Test**:
```bash
# Generate a test report
# Review .docx output manually
```

---

### Task 3: Add Data Extraction Method

**Goal**: Extract a new field from assessment results

**Steps**:

1. **Edit utils/data_extractors.py**:
```python
class AIADataExtractor:
    def extract_compliance_status(self, assessment_results: Dict[str, Any]) -> str:
        """Extract compliance status from assessment."""
        score = self.extract_score(assessment_results)
        if score >= 56:
            return "Enhanced Compliance Required"
        elif score >= 31:
            return "Standard Compliance Required"
        else:
            return "Basic Compliance Required"
```

2. **Use in report generator**:
```python
# In aia_report_generator.py
compliance_status = self.aia_data_extractor.extract_compliance_status(assessment_results)
doc.add_paragraph(f'Compliance Status: {compliance_status}')
```

3. **Test**:
```bash
python3 validate_functionality.py
```

---

### Task 4: Add New Framework Detection Keywords

**Goal**: Improve detection for specific use cases

**Steps**:

1. **Edit utils/framework_detection.py**:
```python
OSFI_KEYWORDS = [
    # Existing keywords...
    "basel iii",  # New
    "capital requirements",  # New
    "stress testing"  # New
]
```

2. **Test with sample descriptions** containing new keywords

---

## Testing Guide

### Automated Testing

#### 1. Comprehensive Validation Suite
```bash
python3 validate_functionality.py
```

**What it tests**:
- ✅ Module imports
- ✅ Server initialization
- ✅ Framework detection
- ✅ Tool registration (16 tools)
- ✅ AIA processor (104 questions)
- ✅ OSFI processor
- ✅ Workflow engine
- ✅ Description validator

**Expected**: `8/8 validations passed`

#### 2. MCP Server Validation
```bash
python3 validate_mcp.py
```

**What it tests**:
- Python installation
- Dependencies
- MCP protocol compatibility
- Server startup

#### 3. Specific Component Tests
```bash
# AIA design phase filtering
python3 test_design_phase_filtering.py

# Functional preview
python3 test_functional_preview.py

# Framework detection
python3 test_framework_detection.py
```

### Manual Testing

#### Test AIA Assessment
```bash
# Start server in debug mode
export DEBUG=1
python3 server.py
```

Then in Claude Desktop:
1. Request: "Assess this AI system: [description]"
2. Verify workflow introduction appears
3. Complete assessment
4. Export report
5. Review .docx file

#### Test OSFI E-23 Assessment
1. Request: "Run OSFI E-23 assessment for [model description]"
2. Verify 5-step workflow presented
3. Complete assessment
4. Check risk rating calculation (integrated into step 2)
5. Export and review report

### Test Data

**Sample AIA Project Description**:
```
Automated loan approval system using machine learning to assess creditworthiness.
System processes personal financial data including income, employment history, and
credit scores to make lending decisions. Used by a federally regulated bank for
consumer loans under $50,000. System makes automated decisions that can be
appealed by applicants.
```

**Sample OSFI Model Description**:
```
Credit risk scoring model in Design stage. Uses gradient boosting machine learning
algorithm to predict probability of default for commercial loans. Model processes
financial statements, credit bureau data, and industry risk factors. Outputs risk
scores used in lending decisions for loans $100K-$5M. High materiality due to
portfolio size of $500M.
```

---

## Adding a New Framework

See `ARCHITECTURE.md` Extension Guide for detailed steps. Quick summary:

### 1. Create Framework Processor
```python
# eu_ai_act_processor.py
class EUAIActProcessor:
    def __init__(self):
        self.requirements = self._load_requirements()

    def assess_compliance(self, description):
        # Official EU AI Act logic
        pass
```

### 2. Create Analyzer Module
```python
# eu_ai_act_analysis.py
class EUAIActAnalyzer:
    def __init__(self, eu_processor):
        self.eu_processor = eu_processor
```

### 3. Create Report Generator
```python
# eu_ai_act_report_generator.py
class EUAIActReportGenerator:
    def generate_report(self, assessment):
        # Generate Word document
        pass
```

### 4. Add to server.py
```python
def __init__(self):
    # ... existing initialization ...
    self.eu_processor = EUAIActProcessor()
    self.eu_analyzer = EUAIActAnalyzer(self.eu_processor)
    self.eu_report_generator = EUAIActReportGenerator(...)
```

### 5. Update Framework Detection
```python
# utils/framework_detection.py
EU_KEYWORDS = ["eu ai act", "european", "high-risk ai"]
```

### 6. Add Tool Definitions
```python
# config/tool_registry.py
{
    "name": "assess_eu_compliance",
    "description": "Assess compliance with EU AI Act",
    ...
}
```

---

## Debugging Guide

### Common Issues & Solutions

#### Issue: "Module not found" error

**Cause**: Import path issue or missing `__init__.py`

**Solution**:
```bash
# Ensure __init__.py files exist
touch utils/__init__.py
touch config/__init__.py

# Check Python path
python3 -c "import sys; print(sys.path)"
```

---

#### Issue: Validation tests failing

**Cause**: Code changes broke existing functionality

**Solution**:
```bash
# Run with debug output
python3 validate_functionality.py 2>&1 | grep "FAIL"

# Check specific module
python3 -c "from aia_analysis import AIAAnalyzer; print('OK')"
```

---

#### Issue: MCP tools not appearing in Claude Desktop

**Cause**: Tool registration issue or Claude Desktop config

**Solution**:
```bash
# Validate MCP server
python3 validate_mcp.py

# Check tool registry
python3 -c "from config.tool_registry import get_all_tools; print(len(get_all_tools()))"
# Should print: 16

# Restart Claude Desktop completely
```

---

#### Issue: Assessment scores seem incorrect

**Cause**: Scoring logic error or missing questions

**Solution**:
```bash
# Verify question count
python3 -c "from aia_processor import AIAProcessor; p = AIAProcessor(); print(len(p.scorable_questions))"
# Should print: 104

# Test scoring logic
python3 test_design_phase_filtering.py
```

---

### Debugging Tools

#### Python Debugger (pdb)
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Run server
python3 server.py
```

#### Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

#### Interactive Testing
```python
# Test components in Python REPL
python3

>>> from aia_analysis import AIAAnalyzer
>>> from aia_processor import AIAProcessor
>>> processor = AIAProcessor()
>>> analyzer = AIAAnalyzer(processor)
>>> result = analyzer._intelligent_project_analysis("test description")
>>> print(result)
```

---

## Best Practices

### Code Organization

✅ **DO**:
- Keep methods under 50 lines when possible
- Use descriptive variable names
- Add docstrings to all public methods
- Group related methods together
- Use type hints

❌ **DON'T**:
- Mix framework logic in shared modules
- Add business logic to server.py
- Modify official data files
- Skip validation tests

### Example - Good Method Structure
```python
def extract_score(self, assessment_results: Dict[str, Any]) -> int:
    """
    Extract AIA score from assessment results.

    Args:
        assessment_results: Assessment data containing score information

    Returns:
        int: AIA score (0-224)

    Raises:
        KeyError: If required score field is missing
    """
    if "score" in assessment_results:
        return assessment_results["score"]
    elif "functional_risk_score" in assessment_results:
        return assessment_results["functional_risk_score"]
    else:
        return 0
```

### Commit Messages

Format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

Example:
```
feat(aia): Add healthcare keyword detection

- Added healthcare-specific keywords to analysis
- Improved question answering for medical AI systems
- Updated tests to cover new functionality

Closes #123
```

### Testing Requirements

Before committing:
1. ✅ Run `python3 validate_functionality.py` → Must show 8/8
2. ✅ Run `python3 -m py_compile <modified-file>.py` → No syntax errors
3. ✅ Manual test affected functionality
4. ✅ Update documentation if adding features

---

## Code Review Checklist

### For Reviewers

**Functionality**:
- [ ] Code solves the stated problem
- [ ] No regression in existing features
- [ ] validate_functionality.py passes (8/8)
- [ ] Edge cases handled

**Code Quality**:
- [ ] Follows existing patterns
- [ ] No code duplication
- [ ] Clear variable/method names
- [ ] Appropriate comments
- [ ] Type hints used

**Testing**:
- [ ] Adequate test coverage
- [ ] Manual testing performed
- [ ] Test data is realistic

**Documentation**:
- [ ] Docstrings added/updated
- [ ] README updated if needed
- [ ] CHANGELOG updated
- [ ] Architecture docs updated if structure changed

**Compliance** (Critical for this project):
- [ ] No modification to official data files
- [ ] Scoring logic verified against official frameworks
- [ ] Professional validation warnings maintained
- [ ] Regulatory terminology correct

---

## Troubleshooting

### Performance Issues

**Symptom**: Slow response times

**Check**:
```python
import time

start = time.time()
# ... your code ...
end = time.time()
print(f"Execution time: {end - start}s")
```

**Common causes**:
- Unnecessary file I/O
- Large data processing
- Inefficient loops

---

### Memory Issues

**Symptom**: High memory usage

**Check**:
```python
import sys
print(f"Object size: {sys.getsizeof(obj)} bytes")
```

**Common causes**:
- Large dictionaries in memory
- Unclosed file handles
- Circular references

---

### Import Errors

**Symptom**: `ModuleNotFoundError`

**Solutions**:
```bash
# Check working directory
pwd

# Verify file exists
ls -la <module_name>.py

# Check for __init__.py
ls -la utils/__init__.py
ls -la config/__init__.py

# Verify Python path includes current directory
python3 -c "import sys; print('.' in sys.path)"
```

---

## Additional Resources

### Documentation
- `README.md` - Project overview and quick start
- `ARCHITECTURE.md` - Architecture deep dive
- `CLAUDE.md` - Claude Code developer guidelines
- `CHANGELOG.md` - Version history
- `docs/` - Additional guides and technical docs

### External Resources
- [MCP Documentation](https://modelcontextprotocol.io)
- [Canada AIA Framework](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/algorithmic-impact-assessment.html)
- [OSFI E-23 Guideline](https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/model-risk-management-guideline-e-23)

### Community
- GitHub Issues: Report bugs or request features
- Pull Requests: Contribute code improvements

---

## Quick Reference

### Essential Commands
```bash
# Validate installation
python3 validate_mcp.py

# Run all tests
python3 validate_functionality.py

# Start server (debug mode)
export DEBUG=1 && python3 server.py

# Check syntax
python3 -m py_compile server.py

# Count lines of code
find . -name "*.py" -not -path "./tests/*" -not -path "./.pytest_cache/*" | xargs wc -l
```

### Module Import Quick Reference
```python
# Framework processors
from aia_processor import AIAProcessor
from osfi_e23_processor import OSFIE23Processor

# Analyzers
from aia_analysis import AIAAnalyzer

# Report generators
from aia_report_generator import AIAReportGenerator
from osfi_e23_report_generators import OSFIE23ReportGenerator

# Data extractors
from utils.data_extractors import AIADataExtractor, OSFIE23DataExtractor

# Framework detection
from utils.framework_detection import FrameworkDetector

# Workflow
from workflow_engine import WorkflowEngine

# Validation
from description_validator import ProjectDescriptionValidator
```

---

**Happy coding! If you have questions, see `ARCHITECTURE.md` for design details or create a GitHub issue.**
