# Architecture Documentation

**Version**: 2.0.0
**Date**: 2025-11-16
**Architecture Type**: Modular, Service-Oriented, Delegation Pattern

---

## Table of Contents

1. [Overview](#overview)
2. [Design Philosophy](#design-philosophy)
3. [Module Architecture](#module-architecture)
4. [Module Dependencies](#module-dependencies)
5. [Data Flow](#data-flow)
6. [Design Patterns](#design-patterns)
7. [Module Responsibilities](#module-responsibilities)
8. [Extension Guide](#extension-guide)
9. [Architectural Decisions](#architectural-decisions)

---

## Overview

The AIA Assessment MCP Server v2.0.0 implements a **modular architecture** that separates concerns across 6 specialized modules, reducing the main server.py from 4,867 to 1,305 lines (73% reduction).

### Key Metrics

- **Total Codebase**: ~12,500 lines
- **Server.py (Orchestration)**: 1,305 lines (10.4%)
- **Specialized Modules**: 3,188 lines (25.5%)
- **Framework Processors**: 2,500+ lines (20%)
- **Support Libraries**: 5,500+ lines (44%)

### Architecture Goals

✅ **Maintainability**: Each module has a single, clear responsibility
✅ **Testability**: Isolated components enable comprehensive unit testing
✅ **Scalability**: New frameworks can be added as independent modules
✅ **Clarity**: Code organization matches conceptual domain model
✅ **Reusability**: Shared modules serve both AIA and OSFI frameworks

---

## Design Philosophy

### Separation of Concerns

The v2.0.0 architecture separates the system into four conceptual layers:

```
┌─────────────────────────────────────────┐
│   MCP Protocol Layer (server.py)        │  ← Orchestration & delegation
├─────────────────────────────────────────┤
│   Business Logic Layer (Modules)        │  ← Framework-specific intelligence
├─────────────────────────────────────────┤
│   Framework Processors (Processors)     │  ← Official regulatory logic
├─────────────────────────────────────────┤
│   Data Layer (JSON files, config)       │  ← Official government data
└─────────────────────────────────────────┘
```

### Delegation Pattern

Server.py **delegates** to specialized modules rather than containing logic directly:

```python
# OLD (v1.x) - Logic in server.py
def _intelligent_project_analysis(self, description):
    # 254 lines of analysis logic directly in server.py
    ...

# NEW (v2.0) - Delegation to specialized module
def _intelligent_project_analysis(self, description):
    """Delegates to AIAAnalyzer."""
    return self.aia_analyzer._intelligent_project_analysis(description)
```

### Dependency Injection

Modules receive dependencies through constructor injection:

```python
class AIAReportGenerator:
    def __init__(self, aia_data_extractor):
        self.aia_data_extractor = aia_data_extractor

class AIAAnalyzer:
    def __init__(self, aia_processor):
        self.aia_processor = aia_processor
```

---

## Module Architecture

### Core Server (Orchestration Layer)

#### server.py (1,305 lines)
**Responsibility**: MCP protocol handling, tool routing, session management

**Contains**:
- JSON-RPC over stdio handling
- MCP protocol negotiation
- Tool invocation routing
- Session state management
- Delegation to specialized modules

**Does NOT contain**:
- Framework-specific logic
- Document generation
- Data extraction
- Intelligence/analysis

**Key Initialization**:
```python
def __init__(self):
    # Framework processors
    self.aia_processor = AIAProcessor(...)
    self.osfi_e23_processor = OSFIE23Processor(...)

    # v2.0.0 Specialized modules
    self.framework_detector = FrameworkDetector()
    self.aia_data_extractor = AIADataExtractor(self.aia_processor)
    self.osfi_data_extractor = OSFIE23DataExtractor(self.osfi_e23_processor)
    self.aia_analyzer = AIAAnalyzer(self.aia_processor)
    self.aia_report_generator = AIAReportGenerator(self.aia_data_extractor)
    self.introduction_builder = IntroductionBuilder(self.framework_detector)

    # Workflow and validation
    self.workflow_engine = WorkflowEngine(...)
    self.description_validator = ProjectDescriptionValidator()
```

---

### AIA Modules

#### aia_analysis.py (1,027 lines)
**Responsibility**: AIA intelligence, question handling, automated analysis

**Key Classes**:
- `AIAAnalyzer`: Main analyzer class

**Key Methods**:
- `_intelligent_project_analysis()`: Keyword-based question answering
- `_functional_risk_analysis()`: Quick risk assessment
- `_get_questions()`: Question retrieval logic
- `_assess_project()`: Full AIA assessment
- Helper methods for scoring, categorization, and analysis

**Dependencies**:
- `aia_processor.py`: For official question data
- Uses keyword matching for intelligent analysis

**Used By**:
- `server.py`: Delegates all AIA analysis operations

---

#### aia_report_generator.py (277 lines)
**Responsibility**: Professional Word document generation for AIA compliance

**Key Classes**:
- `AIAReportGenerator`: Main generator class

**Key Methods**:
- `_export_assessment_report()`: Main export function
- `_generate_executive_summary()`: Summary creation
- `_get_assessment_disclaimer()`: Compliance disclaimers
- `_strip_markdown_formatting()`: Format cleaning

**Dependencies**:
- `aia_data_extractor`: For extracting data from assessments
- `python-docx`: For Word document generation

**Output**:
- Professional `.docx` files with:
  - Executive summary
  - Risk scores and impact levels
  - Key findings and recommendations
  - Official disclaimers

---

### OSFI E-23 Modules

#### osfi_e23_structure.py
**Responsibility**: Official OSFI E-23 Principles, Outcomes, and lifecycle definitions

**Contains**:
- All 12 OSFI Principles (1.1-3.6)
- 3 Outcomes
- 5 lifecycle stages (Design, Review, Deployment, Monitoring, Decommission)
- Appendix 1 model inventory fields

---

#### osfi_e23_report_generators.py
**Responsibility**: Stage-specific OSFI E-23 report generation

**Features**:
- Risk-adaptive content (tone varies by risk level)
- Lifecycle-focused (only shows relevant stage requirements)
- Streamlined format (4-6 pages instead of 40KB+)

---

### Shared Modules

#### utils/data_extractors.py (1,047 lines)
**Responsibility**: Unified data extraction for both frameworks

**Key Classes**:

1. **AIADataExtractor** (30 extraction methods)
   - `extract_score()`: AIA score extraction
   - `extract_impact_level()`: Impact level extraction
   - `extract_key_findings()`: Finding extraction
   - `extract_recommendations()`: Recommendation extraction
   - Many specialized extractors for different data types

2. **OSFIE23DataExtractor**
   - `extract_risk_level()`: Risk level extraction
   - `extract_governance_requirements()`: Governance extraction
   - `extract_lifecycle_stage()`: Stage detection
   - `extract_scoring_details()`: Risk calculation details

**Design Pattern**: Single Responsibility + Composition
- Each extractor handles one data type
- Both frameworks use consistent extraction patterns

---

#### utils/framework_detection.py (108 lines)
**Responsibility**: Smart context detection for framework routing

**Key Class**:
- `FrameworkDetector`: Keyword-based framework identification

**Detection Logic**:
```python
def detect(self, user_context: str, session_id: str) -> str:
    # OSFI keywords: "bank", "financial institution", "model risk"
    # AIA keywords: "government", "algorithmic impact", "automated decision"
    # Returns: "aia", "osfi_e23", or "both"
```

**Caching**: Session-aware detection caching for performance

---

#### config/tool_registry.py (365 lines)
**Responsibility**: Tool metadata and MCP protocol registration

**Contains**:
- Tool definitions (16 tools total)
- Tool descriptions and schemas
- MCP protocol compatibility
- Workflow step metadata

**Used By**:
- `server.py`: For tool registration and metadata

---

#### introduction_builder.py (364 lines)
**Responsibility**: Framework-specific workflow guidance

**Key Class**:
- `IntroductionBuilder`: Builds context-aware introductions

**Key Methods**:
- `_get_server_introduction()`: Main introduction builder
- `_build_aia_workflow_section()`: AIA-specific workflows
- `_build_osfi_workflow_section()`: OSFI-specific workflows
- `_build_both_workflows_section()`: Combined workflows
- `_detect_framework_context()`: Context detection

**Smart Features**:
- Detects user context (AIA, OSFI, or both)
- Shows only relevant workflow
- Reduces cognitive load

---

## Module Dependencies

### Dependency Graph

```
server.py
  ├─> aia_analyzer (aia_analysis.py)
  │     └─> aia_processor
  │
  ├─> aia_report_generator (aia_report_generator.py)
  │     └─> aia_data_extractor
  │           └─> aia_processor
  │
  ├─> introduction_builder (introduction_builder.py)
  │     └─> framework_detector
  │
  ├─> framework_detector (utils/framework_detection.py)
  │
  ├─> aia_data_extractor (utils/data_extractors.py)
  │     └─> aia_processor
  │
  ├─> osfi_data_extractor (utils/data_extractors.py)
  │     └─> osfi_e23_processor
  │
  ├─> workflow_engine
  │
  └─> description_validator
```

### Dependency Rules

✅ **Allowed**:
- Modules can depend on framework processors
- Modules can depend on other modules via constructor injection
- Server.py can depend on all modules

❌ **Not Allowed**:
- Circular dependencies between modules
- Modules directly accessing server.py
- Framework processors depending on modules (they're foundational)

---

## Data Flow

### AIA Assessment Flow

```
User Request
    ↓
server.py (MCP Handler)
    ↓
aia_analyzer._intelligent_project_analysis()
    ↓
aia_processor.get_design_phase_questions()
    ↓
aia_analyzer (performs keyword analysis)
    ↓
aia_data_extractor.extract_score()
    ↓
aia_report_generator._export_assessment_report()
    ↓
Word Document (.docx)
```

### OSFI E-23 Assessment Flow

```
User Request
    ↓
server.py (MCP Handler)
    ↓
osfi_e23_processor.assess_model_risk()
    ↓
osfi_data_extractor.extract_risk_level()
    ↓
osfi_e23_report_generators.generate_report()
    ↓
Word Document (.docx)
```

### Workflow Introduction Flow

```
User: "Run OSFI framework"
    ↓
server.py.get_server_introduction()
    ↓
framework_detector.detect(context)
    │
    ├─> "osfi_e23" detected
    │
    ↓
introduction_builder._build_osfi_workflow_section()
    ↓
Returns 6-step OSFI workflow to user
```

---

## Design Patterns

### 1. Delegation Pattern

**Intent**: Separate orchestration from implementation

**Example**:
```python
# server.py - Orchestrator
def _intelligent_project_analysis(self, description):
    return self.aia_analyzer._intelligent_project_analysis(description)

# aia_analysis.py - Implementation
def _intelligent_project_analysis(self, description):
    # 254 lines of actual logic here
```

**Benefits**:
- Single Responsibility Principle
- Easier testing
- Clear separation of concerns

---

### 2. Dependency Injection

**Intent**: Provide dependencies through constructors, not imports

**Example**:
```python
class AIAReportGenerator:
    def __init__(self, aia_data_extractor):
        self.aia_data_extractor = aia_data_extractor

# In server.py
self.aia_report_generator = AIAReportGenerator(self.aia_data_extractor)
```

**Benefits**:
- Testability (can inject mocks)
- Flexibility (can swap implementations)
- Clear dependencies

---

### 3. Strategy Pattern (Framework Detection)

**Intent**: Select algorithm at runtime based on context

**Example**:
```python
framework = self.framework_detector.detect(user_context)

if framework == 'aia':
    return self.introduction_builder._build_aia_workflow_section()
elif framework == 'osfi_e23':
    return self.introduction_builder._build_osfi_workflow_section()
else:
    return self.introduction_builder._build_both_workflows_section()
```

---

### 4. Builder Pattern (Introduction Builder)

**Intent**: Construct complex objects step by step

**Example**:
```python
base_response = {
    "assistant_directive": {...},
    "server_introduction": {...},
    "tool_categories": {...}
}

if framework_focus == 'aia':
    base_response["framework_workflow"] = self._build_aia_workflow_section()
```

---

## Module Responsibilities

### Responsibility Matrix

| Module | Primary Responsibility | Secondary Responsibilities |
|--------|----------------------|---------------------------|
| **server.py** | MCP protocol orchestration | Session management, tool routing |
| **aia_analysis.py** | AIA intelligence & analysis | Question answering, scoring |
| **aia_report_generator.py** | AIA document generation | Report formatting, export |
| **osfi_e23_structure.py** | OSFI data structures | Principle definitions |
| **osfi_e23_report_generators.py** | OSFI document generation | Risk-adaptive formatting |
| **utils/data_extractors.py** | Data extraction patterns | Result parsing |
| **utils/framework_detection.py** | Context detection | Framework routing |
| **config/tool_registry.py** | Tool metadata | MCP registration |
| **introduction_builder.py** | Workflow guidance | Framework selection |
| **aia_processor.py** | Official AIA framework | Question extraction |
| **osfi_e23_processor.py** | Official OSFI framework | Risk calculation |
| **workflow_engine.py** | Workflow orchestration | State management |
| **description_validator.py** | Quality gates | Validation logic |

---

## Extension Guide

### Adding a New Regulatory Framework

Example: Adding EU AI Act framework

#### Step 1: Create Framework Processor

```python
# eu_ai_act_processor.py
class EUAIActProcessor:
    def __init__(self):
        self.load_official_requirements()

    def assess_compliance(self, project_description):
        # Official EU AI Act logic
        pass
```

#### Step 2: Create Framework Module

```python
# eu_ai_act_analysis.py
class EUAIActAnalyzer:
    def __init__(self, eu_processor):
        self.eu_processor = eu_processor

    def analyze_system(self, description):
        # EU-specific analysis
        pass
```

#### Step 3: Create Report Generator

```python
# eu_ai_act_report_generator.py
class EUAIActReportGenerator:
    def __init__(self, eu_data_extractor):
        self.eu_data_extractor = eu_data_extractor

    def generate_report(self, assessment):
        # EU AI Act document generation
        pass
```

#### Step 4: Add Data Extractor

```python
# In utils/data_extractors.py
class EUAIActDataExtractor:
    def extract_risk_level(self, results):
        # Extract EU risk level (Unacceptable/High/Limited/Minimal)
        pass
```

#### Step 5: Update Framework Detection

```python
# In utils/framework_detection.py
EU_KEYWORDS = ["eu ai act", "european ai", "high-risk ai system"]

def detect(self, context):
    if any(kw in context.lower() for kw in EU_KEYWORDS):
        return "eu_ai_act"
```

#### Step 6: Update Introduction Builder

```python
# In introduction_builder.py
def _build_eu_workflow_section(self):
    return {
        "title": "🇪🇺 EU AI Act Compliance",
        "sequence": [...]
    }
```

#### Step 7: Wire in server.py

```python
# In server.py.__init__()
self.eu_processor = EUAIActProcessor()
self.eu_data_extractor = EUAIActDataExtractor(self.eu_processor)
self.eu_analyzer = EUAIActAnalyzer(self.eu_processor)
self.eu_report_generator = EUAIActReportGenerator(self.eu_data_extractor)
```

---

## Architectural Decisions

### Why Modular Architecture?

**Decision**: Extract specialized modules from monolithic server.py

**Rationale**:
- **Maintainability**: 4,867-line files are difficult to navigate
- **Testing**: Isolated modules enable unit testing
- **Team Development**: Multiple developers can work on different modules
- **Clarity**: Code organization matches domain model

**Alternatives Considered**:
1. Keep monolithic structure → Rejected (scalability issues)
2. Separate servers for each framework → Deferred (v2.0 addresses immediate concerns)
3. Microservices architecture → Rejected (over-engineering for current scale)

---

### Why Delegation Pattern?

**Decision**: server.py delegates to specialized modules

**Rationale**:
- Clear separation of orchestration vs. implementation
- server.py becomes thin routing layer
- Business logic isolated for testing

**Alternatives Considered**:
1. Direct imports in server.py → Rejected (tight coupling)
2. Event-driven architecture → Rejected (unnecessary complexity)

---

### Why Shared Data Extractors?

**Decision**: Single `data_extractors.py` for both frameworks

**Rationale**:
- Common patterns between AIA and OSFI extraction
- Reusable code reduces duplication
- Consistent extraction methodology

**Alternatives Considered**:
1. Framework-specific extractors → Considered but rejected (too much duplication)
2. Generic extractor with plugins → Rejected (over-engineering)

---

### Why Not Separate Servers?

**Decision**: Keep both frameworks in one server for v2.0

**Rationale**:
- Many systems need both frameworks (banks with automated decision systems)
- Shared infrastructure (workflow engine, validation, MCP protocol)
- v2.0 modular architecture addresses maintainability concerns

**Future Consideration**:
- May split into separate servers if:
  - Deployment flexibility required
  - Independent versioning needed
  - Frameworks evolve significantly differently

---

## Architecture Evolution

### v1.x (Monolithic)
```
server.py (4,867 lines)
  - All AIA logic
  - All OSFI logic
  - All reporting
  - All data extraction
  - MCP protocol
```

**Problems**:
- Difficult to navigate
- Hard to test
- Risky to modify
- Steep learning curve

---

### v2.0 (Modular)
```
server.py (1,305 lines - orchestration only)
  ├─> aia_analysis.py (1,027 lines)
  ├─> aia_report_generator.py (277 lines)
  ├─> utils/data_extractors.py (1,047 lines)
  ├─> introduction_builder.py (364 lines)
  ├─> utils/framework_detection.py (108 lines)
  └─> config/tool_registry.py (365 lines)
```

**Benefits**:
- ✅ 73% code reduction in server.py
- ✅ Clear module boundaries
- ✅ Easier testing
- ✅ Better maintainability
- ✅ Faster onboarding

---

## Summary

The v2.0.0 architecture successfully transforms a monolithic 4,867-line server into a professional, modular system with:

- **6 specialized modules** handling distinct responsibilities
- **Clean separation** between orchestration and implementation
- **Dependency injection** enabling testability
- **Clear extension points** for new frameworks
- **73% code reduction** in main orchestration file

This architecture balances simplicity (single server) with maintainability (modular design), providing a solid foundation for future growth while maintaining 100% backward compatibility.

---

**For implementation details, see:**
- `CLAUDE.md` - Developer guidelines
- `README.md` - Project overview
- `CHANGELOG.md` - Version history
- `ARCHITECTURE_ANALYSIS.md` - Architectural analysis and server separation considerations
