# Refactoring Safety Plan
## Ensuring Zero Functionality Loss During Code Reorganization

**Created**: November 15, 2025
**Purpose**: Guarantee safe refactoring with multiple rollback points
**Approach**: Test-Driven Refactoring with continuous validation

---

## Safety Layers Implemented

### Layer 1: Version Control Safety ✅

**Git Tag Created**: `v1.16.0-pre-refactoring`
```bash
# Snapshot of working code before any changes
git tag -a v1.16.0-pre-refactoring -m "Snapshot before Phase 1 refactoring"
```

**Backup Branch Created**: `backup/pre-refactoring-2025-11-15`
```bash
# Complete backup of current state
git branch backup/pre-refactoring-2025-11-15
```

**Working Branch Created**: `refactor/phase1-split-server`
```bash
# All refactoring work happens here
git branch refactor/phase1-split-server
```

### Layer 2: File System Backup

**Location**: `backups/pre-refactoring-2025-11-15/`

**Created**: Complete copy of entire codebase
```bash
# Create timestamped backup
mkdir -p backups/pre-refactoring-2025-11-15
cp -r . backups/pre-refactoring-2025-11-15/
```

### Layer 3: Test Coverage Baseline

**Established**: Before any changes, run all tests and capture baseline
```bash
# Run all tests and capture output
pytest -v > test_baseline.txt 2>&1

# Install coverage measurement
pip install pytest-cov

# Generate coverage baseline
pytest --cov=. --cov-report=html --cov-report=term > coverage_baseline.txt 2>&1
```

### Layer 4: Functional Validation Script

**Created**: `validate_functionality.py` - Comprehensive smoke tests
- Tests all MCP tools work
- Validates AIA assessment flow
- Validates OSFI E-23 assessment flow
- Checks report generation
- Verifies workflow engine

---

## Rollback Procedures

### Quick Rollback (If issues found immediately)

```bash
# Discard all changes on working branch
git checkout main
git branch -D refactor/phase1-split-server

# You're back to the exact state before refactoring
```

### Rollback to Tagged Version

```bash
# Return to the tagged safe point
git checkout v1.16.0-pre-refactoring

# Create new branch from that point if needed
git checkout -b recovery-branch
```

### Rollback from Backup Branch

```bash
# Switch to backup branch
git checkout backup/pre-refactoring-2025-11-15

# Create new main from backup
git checkout -b main-recovered
```

### Nuclear Option: File System Restore

```bash
# If git is corrupted, restore from file backup
cd ..
rm -rf aia-assessment-mcp
cp -r aia-assessment-mcp-backup aia-assessment-mcp
cd aia-assessment-mcp
```

---

## Refactoring Workflow (Test-First Approach)

### Pre-Refactoring Checklist

Before making ANY code changes:

- [x] Git tag created: `v1.16.0-pre-refactoring`
- [x] Backup branch created: `backup/pre-refactoring-2025-11-15`
- [x] Working branch created: `refactor/phase1-split-server`
- [ ] File system backup created
- [ ] Test baseline captured
- [ ] Coverage baseline established
- [ ] Validation script created and passing
- [ ] All existing tests passing

### During Refactoring - After Each Change

After EVERY significant change (e.g., moving a function):

```bash
# 1. Run all tests
pytest -v

# 2. Run validation script
python validate_functionality.py

# 3. Check coverage hasn't decreased
pytest --cov=. --cov-report=term

# 4. If all pass, commit
git add .
git commit -m "refactor: Move X to Y - all tests passing"

# 5. If any fail, immediately revert
git reset --hard HEAD
```

### Validation Gates

Every change must pass these gates:

1. **Syntax Check**: `python -m py_compile <file>`
2. **Import Check**: `python -c "import server"`
3. **Unit Tests**: `pytest tests/unit/ -v`
4. **Functional Tests**: `pytest tests/functional/ -v`
5. **Integration Tests**: `pytest tests/integration/ -v`
6. **Validation Script**: `python validate_functionality.py`
7. **Coverage Check**: Coverage must not decrease

**Rule**: If ANY gate fails, STOP and rollback the last change.

---

## Test-Driven Refactoring Process

### Phase 1 Example: Extract Framework Detection

**Step 1: Establish Baseline** ✅ DONE
```bash
# All tests pass before we start
pytest -v
# Result: Should be all green
```

**Step 2: Write Tests for New Module** (BEFORE moving code)
```python
# tests/unit/test_framework_detection.py
def test_detect_osfi_keywords():
    detector = FrameworkDetector()
    result = detector.detect("OSFI credit model")
    assert result == "osfi_e23"

def test_detect_aia_keywords():
    detector = FrameworkDetector()
    result = detector.detect("AIA government system")
    assert result == "aia"
```

**Step 3: Create New Module** (Implementation)
```python
# utils/framework_detection.py
class FrameworkDetector:
    def detect(self, context: str) -> str:
        # Move code from server.py here
        pass
```

**Step 4: Update server.py** (Use new module)
```python
# server.py
from utils.framework_detection import FrameworkDetector

class MCPServer:
    def __init__(self):
        self.framework_detector = FrameworkDetector()

    def _detect_framework_context(self, context):
        # Delegate to new module
        return self.framework_detector.detect(context)
```

**Step 5: Run All Tests**
```bash
pytest -v
python validate_functionality.py
```

**Step 6: Commit if Green, Rollback if Red**
```bash
# If all green
git add .
git commit -m "refactor: Extract framework detection to utils/ - all tests passing"

# If any red
git reset --hard HEAD
# Fix the issue, repeat from step 4
```

---

## Validation Strategy

### Automated Validation Script

The `validate_functionality.py` script tests:

1. **Server Starts**: Can import and instantiate MCPServer
2. **Tool Registration**: All 13 tools are registered
3. **Introduction Tool**: Returns expected structure
4. **Framework Detection**: Detects OSFI, AIA, both correctly
5. **AIA Assessment**: Can process a sample assessment
6. **OSFI Assessment**: Can process a sample risk analysis
7. **Report Generation**: Can generate both report types
8. **Workflow Engine**: Can create and execute workflows

### Manual Validation Checklist

After completing each phase, manually verify:

- [ ] MCP server starts without errors
- [ ] Claude Desktop can connect to server
- [ ] Can run through AIA assessment end-to-end
- [ ] Can run through OSFI E-23 assessment end-to-end
- [ ] Can generate AIA report (.docx)
- [ ] Can generate OSFI E-23 report (.docx)
- [ ] Reports contain all expected sections
- [ ] No functionality appears missing

---

## Risk Mitigation Strategies

### Risk 1: Breaking Imports

**Mitigation**:
- Change one import at a time
- Run `python -c "import server"` after each change
- Keep backward-compatible imports during transition

**Example**:
```python
# Maintain backward compatibility during migration
try:
    from utils.framework_detection import FrameworkDetector
except ImportError:
    # Fallback to old location during transition
    FrameworkDetector = None
```

### Risk 2: Breaking Tests

**Mitigation**:
- Run tests after EVERY file change
- Keep test suite passing at all times
- Never commit if tests are red

### Risk 3: Losing Functionality

**Mitigation**:
- Validation script tests all major workflows
- Manual testing after each phase
- Incremental changes with frequent commits

### Risk 4: Git Merge Issues

**Mitigation**:
- Work in dedicated branch
- Commit frequently (every successful change)
- Don't merge to main until entire phase complete

### Risk 5: Configuration Issues

**Mitigation**:
- Don't change configuration files during refactoring
- Move code only, not behavior
- Validate configs load correctly after each change

---

## Emergency Procedures

### If Tests Start Failing Mid-Refactoring

```bash
# 1. STOP immediately
# 2. Check what changed
git diff

# 3. See recent commits
git log --oneline -5

# 4. Rollback to last known good state
git reset --hard HEAD~1  # Go back one commit

# 5. Re-run tests to confirm they pass
pytest -v

# 6. Identify the problem, fix it, try again
```

### If Server Won't Start

```bash
# 1. Check syntax errors
python -m py_compile server.py

# 2. Check imports
python -c "import server"

# 3. If errors, rollback
git reset --hard HEAD~1

# 4. Fix the issue in isolation, test, then reapply
```

### If Rollback Doesn't Work

```bash
# 1. Return to backup branch (100% safe)
git checkout backup/pre-refactoring-2025-11-15

# 2. Verify everything works
pytest -v
python validate_functionality.py

# 3. Create new working branch from backup
git checkout -b refactor/phase1-retry

# 4. Start refactoring again, more carefully
```

---

## Continuous Integration Approach

### After Each Module Extraction

1. **Extract** module from server.py
2. **Test** - run all tests
3. **Validate** - run validation script
4. **Commit** - if all green
5. **Repeat** - next module

### Commit Message Format

Use clear, descriptive commit messages:
```
refactor: Extract framework detection to utils/framework_detection.py

- Moved _detect_framework_context() to FrameworkDetector class
- Moved keyword lists to class constants
- All tests passing
- Coverage maintained at X%
```

### Checkpoints

Create git tags at major milestones:
```bash
# After each major extraction
git tag -a refactor-checkpoint-1 -m "Framework detection extracted"
git tag -a refactor-checkpoint-2 -m "Report generators extracted"
# etc.
```

---

## Success Criteria

Before considering refactoring complete:

### Technical Criteria
- [ ] All existing tests pass
- [ ] Test coverage >= baseline (or higher)
- [ ] No syntax errors
- [ ] No import errors
- [ ] Server starts successfully
- [ ] Validation script passes 100%

### Functional Criteria
- [ ] AIA assessment works end-to-end
- [ ] OSFI E-23 assessment works end-to-end
- [ ] Report generation works for both frameworks
- [ ] Workflow engine functions correctly
- [ ] Framework detection works as before

### Quality Criteria
- [ ] Code complexity reduced (measured)
- [ ] File sizes within targets (<800 lines)
- [ ] No code duplication introduced
- [ ] Type hints maintained/improved
- [ ] Documentation updated

---

## Phase 1 Detailed Plan

### Phase 1: Split server.py (3-5 days)

**Goal**: Reduce server.py from 4,867 lines to <800 lines

**Modules to Extract** (in this order):

1. **utils/framework_detection.py** (1 hour)
   - Extract `_detect_framework_context()`
   - Extract keyword lists
   - Test, validate, commit

2. **config/tool_registry.py** (2 hours)
   - Extract `_list_tools()` data
   - Create ToolRegistry class
   - Test, validate, commit

3. **utils/data_extractors.py** (2 hours)
   - Extract all `_extract_*()` functions
   - Create DataExtractor class
   - Test, validate, commit

4. **report_generators/aia_reporter.py** (4 hours)
   - Extract AIA report generation methods
   - Create AIAReporter class
   - Test, validate, commit

5. **report_generators/osfi_reporter.py** (4 hours)
   - Extract OSFI report generation methods
   - Create OSFIReporter class
   - Test, validate, commit

6. **services/aia_service.py** (3 hours)
   - Extract AIA orchestration logic
   - Create AIAService class
   - Test, validate, commit

7. **services/osfi_service.py** (3 hours)
   - Extract OSFI orchestration logic
   - Create OSFIService class
   - Test, validate, commit

**After Each Extraction**:
```bash
pytest -v
python validate_functionality.py
git commit -m "refactor: Extract X - all tests passing"
```

**End of Phase 1 Validation**:
```bash
# All tests pass
pytest -v --cov=. --cov-report=html

# Validation script passes
python validate_functionality.py

# Server.py is now <800 lines
wc -l server.py

# Create checkpoint tag
git tag -a phase1-complete -m "Phase 1 complete - server.py split successfully"
```

---

## Monitoring During Refactoring

### Metrics to Track

Create `refactoring_metrics.txt` and update after each commit:
```
Commit: <hash>
Date: <date>
server.py lines: <count>
Tests passing: <X/Y>
Coverage: <percentage>
Complexity: <score>
```

### Red Flags to Watch For

🚩 **STOP IMMEDIATELY IF**:
- Any test starts failing that was passing before
- Coverage drops by >5%
- Server won't start
- Import errors appear
- Validation script fails

---

## Final Safety Reminder

**GOLDEN RULE**:
> Never commit code with failing tests. Ever.

**If you're unsure**, rollback and try again.

**If tests fail**, don't try to "fix forward" - rollback to the last known good state, understand the problem, then reapply the change correctly.

**Every commit should be deployable** - this is continuous integration best practice.

---

## Rollback Quick Reference

```bash
# Undo last commit (keep changes in working directory)
git reset --soft HEAD~1

# Undo last commit (discard all changes)
git reset --hard HEAD~1

# Return to tagged version
git checkout v1.16.0-pre-refactoring

# Return to backup branch
git checkout backup/pre-refactoring-2025-11-15

# See what changed
git diff HEAD~1

# See recent commits
git log --oneline -10
```

---

**Document Status**: Ready for Phase 1 Execution
**Last Updated**: November 15, 2025
**Risk Level**: LOW (with these safety measures)
**Confidence**: HIGH (multiple rollback options available)
