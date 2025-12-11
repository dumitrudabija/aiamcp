# Jira MCP Integration Pattern - Maintaining Data Integrity

**Problem**: How to use Jira's official MCP while ensuring Claude doesn't hallucinate/modify checklist items?

**Solution**: Python creates exact Jira ticket specifications → Claude passes them verbatim to Jira MCP

---

## Architecture Pattern

```
┌────────────────────────────────────────────────────────────────┐
│ STEP 1: Python Generates Exact Ticket Specifications          │
└────────────────────────────────────────────────────────────────┘

USER: "Assess my model and create Jira tickets for the checklist"
  ↓
CLAUDE: Calls your MCP "assess_and_prepare_jira_tickets"
  ↓
PYTHON (Your MCP):
  1. Runs OSFI E-23 assessment (deterministic)
  2. Generates compliance checklist (deterministic)
  3. Creates EXACT Jira ticket specifications (one per checklist item)
  4. Returns structured ticket specs to Claude

┌────────────────────────────────────────────────────────────────┐
│ STEP 2: Claude Passes Specs Verbatim to Jira MCP              │
└────────────────────────────────────────────────────────────────┘

CLAUDE: Receives ticket specifications from Python
  ↓
FOR EACH ticket spec:
  CLAUDE: Calls Jira MCP with exact spec (no modification)
  JIRA MCP: Creates ticket
  ↓
RESULT: 12 Jira tickets created, one per checklist item
```

---

## Implementation

### Step 1: Add Tool to Your MCP

```python
# config/tool_registry.py - Add new tool
{
    "name": "prepare_jira_tickets_from_assessment",
    "description": """
    🎫 STEP 1 OF 2: Prepare Jira ticket specifications from OSFI E-23 assessment.

    This tool generates EXACT Jira ticket specifications that Claude will pass
    to the Jira MCP. Python creates the ticket data - Claude just delivers it.

    Returns: Array of Jira ticket specifications (one per checklist item)

    NEXT STEP: Claude will call Jira MCP for each returned specification.
    """,
    "inputSchema": {
        "type": "object",
        "properties": {
            "assessment_results": {
                "type": "object",
                "description": "Results from assess_model_risk or full OSFI E-23 workflow"
            },
            "jira_project_key": {
                "type": "string",
                "description": "Jira project key (e.g., 'COMPLIANCE')",
                "default": "COMPLIANCE"
            },
            "parent_ticket_summary": {
                "type": "string",
                "description": "Optional parent ticket summary. If provided, checklist items become subtasks."
            }
        },
        "required": ["assessment_results", "jira_project_key"]
    }
}
```

### Step 2: Implement Ticket Preparation Logic

```python
# jira_ticket_builder.py
from typing import Dict, Any, List
import json

class JiraTicketBuilder:
    """
    Builds exact Jira ticket specifications from OSFI E-23 assessments.

    These specifications are designed to be passed directly to Jira MCP
    without modification by the LLM.
    """

    def prepare_compliance_tickets(
        self,
        assessment_results: Dict[str, Any],
        jira_project_key: str,
        create_parent_ticket: bool = True
    ) -> Dict[str, Any]:
        """
        Generate exact Jira ticket specifications from assessment.

        Returns structured data that Claude passes verbatim to Jira MCP.
        """

        # Extract assessment data (Python deterministic)
        project_name = assessment_results.get('project_name', 'Unnamed Model')
        risk_level = assessment_results.get('risk_level', 'Unknown')
        risk_score = assessment_results.get('risk_score', 0)
        checklist = assessment_results.get('compliance_checklist', [])

        # Build ticket specifications
        ticket_specs = []

        # Parent ticket (overview)
        if create_parent_ticket:
            parent_spec = self._build_parent_ticket_spec(
                project_key=jira_project_key,
                project_name=project_name,
                risk_level=risk_level,
                risk_score=risk_score,
                assessment_results=assessment_results
            )
            ticket_specs.append(parent_spec)

        # Child tickets (one per checklist item)
        for idx, checklist_item in enumerate(checklist, start=1):
            child_spec = self._build_checklist_item_spec(
                project_key=jira_project_key,
                project_name=project_name,
                risk_level=risk_level,
                checklist_item=checklist_item,
                item_number=idx,
                total_items=len(checklist),
                parent_exists=create_parent_ticket
            )
            ticket_specs.append(child_spec)

        # Return structured specifications
        return {
            "success": True,
            "ticket_specifications": ticket_specs,
            "total_tickets_to_create": len(ticket_specs),
            "parent_ticket_included": create_parent_ticket,
            "checklist_items_count": len(checklist),
            "data_integrity": "All ticket data generated by Python - pass verbatim to Jira MCP",
            "assistant_instructions": {
                "action": "Call Jira MCP 'create_issue' for each ticket in ticket_specifications",
                "important": "Pass each ticket specification EXACTLY as provided - do not modify fields",
                "verification": f"Expected {len(ticket_specs)} Jira tickets to be created"
            }
        }

    def _build_parent_ticket_spec(
        self,
        project_key: str,
        project_name: str,
        risk_level: str,
        risk_score: int,
        assessment_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build parent ticket specification (overview)."""

        return {
            "ticket_type": "parent",
            "jira_spec": {
                "fields": {
                    "project": {"key": project_key},
                    "summary": f"OSFI E-23 Compliance - {project_name} ({risk_level} Risk)",
                    "description": self._build_parent_description(assessment_results),
                    "issuetype": {"name": "Epic"},  # Or "Task" depending on your Jira
                    "priority": self._map_risk_to_priority(risk_level),
                    "labels": [
                        "osfi-e23",
                        "model-risk-management",
                        f"risk-{risk_level.lower()}",
                        f"score-{risk_score}"
                    ],
                    # Add custom fields if needed
                    # "customfield_10050": risk_score,  # Risk Score custom field
                    # "customfield_10051": risk_level,  # Risk Level custom field
                }
            },
            "metadata": {
                "source": "OSFI_E23_Python_Assessment",
                "project_name": project_name,
                "risk_level": risk_level,
                "risk_score": risk_score
            }
        }

    def _build_checklist_item_spec(
        self,
        project_key: str,
        project_name: str,
        risk_level: str,
        checklist_item: Dict[str, Any],
        item_number: int,
        total_items: int,
        parent_exists: bool
    ) -> Dict[str, Any]:
        """Build individual checklist item ticket specification."""

        # Extract checklist item data (from Python assessment)
        if isinstance(checklist_item, dict):
            requirement = checklist_item.get('requirement', str(checklist_item))
            osfi_principle = checklist_item.get('osfi_principle', '')
            deliverables = checklist_item.get('deliverables', [])
            priority = checklist_item.get('priority', 'Medium')
        else:
            # Simple string checklist item
            requirement = str(checklist_item)
            osfi_principle = ''
            deliverables = []
            priority = 'Medium'

        # Build ticket specification
        spec = {
            "ticket_type": "subtask" if parent_exists else "task",
            "item_number": item_number,
            "total_items": total_items,
            "jira_spec": {
                "fields": {
                    "project": {"key": project_key},
                    "summary": f"[{item_number}/{total_items}] {requirement}",
                    "description": self._build_checklist_item_description(
                        requirement=requirement,
                        osfi_principle=osfi_principle,
                        deliverables=deliverables,
                        project_name=project_name,
                        risk_level=risk_level
                    ),
                    "issuetype": {"name": "Sub-task" if parent_exists else "Task"},
                    "priority": {"name": priority},
                    "labels": [
                        "osfi-e23-checklist",
                        f"risk-{risk_level.lower()}",
                        f"principle-{osfi_principle.replace('.', '-')}" if osfi_principle else "general"
                    ]
                }
            },
            "metadata": {
                "source": "OSFI_E23_Compliance_Checklist",
                "checklist_item": requirement,
                "osfi_principle": osfi_principle,
                "deliverable_count": len(deliverables)
            }
        }

        # Add parent link if this is a subtask
        if parent_exists:
            spec["jira_spec"]["fields"]["parent"] = {
                "note": "Set to parent ticket key after parent is created"
            }

        return spec

    def _build_parent_description(self, assessment_results: Dict[str, Any]) -> str:
        """Build Jira description for parent ticket."""

        risk_level = assessment_results.get('risk_level', 'Unknown')
        risk_score = assessment_results.get('risk_score', 0)
        detected_factors = assessment_results.get('detected_factors', [])
        governance = assessment_results.get('governance_requirements', {})

        description = f"""
h2. OSFI E-23 Model Risk Assessment Summary

*Risk Level:* {risk_level}
*Risk Score:* {risk_score}/100

h3. Risk Factors Detected
{self._format_factors_jira(detected_factors)}

h3. Governance Requirements
* *Approval Authority:* {governance.get('approval_authority', 'TBD')}
* *Monitoring Frequency:* {governance.get('monitoring_frequency', 'TBD')}
* *Documentation Level:* {governance.get('documentation_level', 'TBD')}

h3. Compliance Actions
See linked subtasks for detailed compliance checklist items.

---
_Generated by OSFI E-23 Assessment MCP Server_
_All data is deterministic - generated by Python regulatory logic_
        """
        return description.strip()

    def _build_checklist_item_description(
        self,
        requirement: str,
        osfi_principle: str,
        deliverables: List[str],
        project_name: str,
        risk_level: str
    ) -> str:
        """Build Jira description for checklist item ticket."""

        description_parts = [
            f"h3. Compliance Requirement",
            f"{requirement}",
            "",
        ]

        if osfi_principle:
            description_parts.extend([
                f"h4. OSFI E-23 Reference",
                f"*Principle:* {osfi_principle}",
                ""
            ])

        if deliverables:
            description_parts.extend([
                f"h4. Required Deliverables",
                *[f"* {deliverable}" for deliverable in deliverables],
                ""
            ])

        description_parts.extend([
            f"h4. Context",
            f"* *Model:* {project_name}",
            f"* *Risk Level:* {risk_level}",
            "",
            "---",
            "_Generated by OSFI E-23 Assessment MCP Server_"
        ])

        return "\n".join(description_parts)

    def _map_risk_to_priority(self, risk_level: str) -> Dict[str, str]:
        """Map OSFI risk level to Jira priority."""
        priority_map = {
            "Critical": {"name": "Highest"},
            "High": {"name": "High"},
            "Medium": {"name": "Medium"},
            "Low": {"name": "Low"}
        }
        return priority_map.get(risk_level, {"name": "Medium"})

    def _format_factors_jira(self, factors: List[str]) -> str:
        """Format risk factors as Jira bullet list."""
        if not factors:
            return "* None detected"
        return "\n".join([f"* {factor}" for factor in factors])
```

### Step 3: Add Tool Handler to server.py

```python
# In server.py
from jira_ticket_builder import JiraTicketBuilder

class MCPServer:
    def __init__(self):
        # ... existing code ...
        self.jira_builder = JiraTicketBuilder()

    async def _prepare_jira_tickets_from_assessment(
        self,
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """
        Prepare exact Jira ticket specifications from assessment.

        Python generates all ticket data - Claude just passes to Jira MCP.
        """
        try:
            result = self.jira_builder.prepare_compliance_tickets(
                assessment_results=arguments['assessment_results'],
                jira_project_key=arguments.get('jira_project_key', 'COMPLIANCE'),
                create_parent_ticket=arguments.get('create_parent_ticket', True)
            )

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        except Exception as e:
            logger.error(f"Error preparing Jira tickets: {str(e)}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e)
                }, indent=2)
            )]
```

---

## Usage Flow

### Conversational Workflow

```
USER: "Assess my credit risk model for OSFI E-23"
  ↓
CLAUDE: Calls assess_model_risk
  ↓
PYTHON: Returns assessment with compliance checklist (12 items)
  ↓
CLAUDE: "Assessment complete. Risk Level: High (68/100).
         You have 12 compliance requirements."
  ↓
USER: "Great, now create Jira tickets for those requirements"
  ↓
CLAUDE: Calls prepare_jira_tickets_from_assessment
  ↓
PYTHON: Returns exact specifications for 13 tickets:
  - 1 parent ticket (Epic)
  - 12 child tickets (one per checklist item)
  ↓
CLAUDE: Receives ticket specifications
  ↓
CLAUDE: FOR EACH ticket spec in ticket_specifications:
  Calls Jira MCP: create_issue(spec.jira_spec)
  ↓
JIRA MCP: Creates ticket
  ↓
CLAUDE: "✅ Created 13 Jira tickets:
         - Parent: COMPLIANCE-456 (Epic)
         - Subtasks: COMPLIANCE-457 through COMPLIANCE-468
         All checklist items now tracked in Jira."
```

### Example: What Claude Receives from Python

```json
{
  "success": true,
  "ticket_specifications": [
    {
      "ticket_type": "parent",
      "jira_spec": {
        "fields": {
          "project": {"key": "COMPLIANCE"},
          "summary": "OSFI E-23 Compliance - Credit Risk Model (High Risk)",
          "description": "h2. OSFI E-23 Model Risk Assessment Summary\n...",
          "issuetype": {"name": "Epic"},
          "priority": {"name": "High"},
          "labels": ["osfi-e23", "model-risk-management", "risk-high", "score-68"]
        }
      }
    },
    {
      "ticket_type": "subtask",
      "item_number": 1,
      "jira_spec": {
        "fields": {
          "project": {"key": "COMPLIANCE"},
          "summary": "[1/12] Model validation documentation per OSFI Principle 3.2",
          "description": "h3. Compliance Requirement\nModel validation...",
          "issuetype": {"name": "Sub-task"},
          "priority": {"name": "High"},
          "labels": ["osfi-e23-checklist", "risk-high", "principle-3-2"]
        }
      }
    },
    {
      "ticket_type": "subtask",
      "item_number": 2,
      "jira_spec": {
        "fields": {
          "project": {"key": "COMPLIANCE"},
          "summary": "[2/12] Independent model review by qualified personnel",
          "description": "h3. Compliance Requirement\nIndependent review...",
          "issuetype": {"name": "Sub-task"},
          "priority": {"name": "High"}
        }
      }
    }
    // ... 10 more checklist items ...
  ],
  "total_tickets_to_create": 13,
  "assistant_instructions": {
    "action": "Call Jira MCP 'create_issue' for each ticket in ticket_specifications",
    "important": "Pass each ticket specification EXACTLY as provided - do not modify fields"
  }
}
```

### Example: What Claude Passes to Jira MCP (Verbatim)

```javascript
// Claude calls Jira MCP with EXACT spec from Python
use_mcp_tool("jira", "create_issue", {
  "fields": {
    "project": {"key": "COMPLIANCE"},
    "summary": "[1/12] Model validation documentation per OSFI Principle 3.2",
    "description": "h3. Compliance Requirement\nModel validation...",
    "issuetype": {"name": "Sub-task"},
    "priority": {"name": "High"},
    "labels": ["osfi-e23-checklist", "risk-high", "principle-3-2"]
  }
});

// ✅ No modification by Claude
// ✅ Exact Python data → Jira
// ✅ Data integrity maintained
```

---

## Data Integrity Guarantees

### What Python Controls (100%)
- ✅ Checklist item text
- ✅ Ticket summaries
- ✅ Ticket descriptions
- ✅ OSFI principle references
- ✅ Priority levels
- ✅ Labels and categorization
- ✅ Number of tickets created

### What Claude Controls
- ❌ None of the ticket content
- ✅ Only: Calling Jira MCP with exact specs
- ✅ Only: Tracking success/failure of each ticket creation

### Why This Works
1. **Structured Data**: Python returns exact Jira API format
2. **Clear Instructions**: "Pass EXACTLY as provided - do not modify"
3. **Verification**: Count of tickets created = count of specs
4. **Audit Trail**: Each ticket has "source" metadata showing Python origin

---

## Advantages of This Approach

✅ **Uses Official Jira MCP** - No custom API integration needed
✅ **Conversational** - User says "create Jira tickets"
✅ **Data Integrity** - Python defines all content
✅ **One Ticket Per Item** - Clean Jira structure
✅ **Maintainable** - Jira MCP handles Jira API changes
✅ **Auditable** - Clear data flow from Python → Jira
✅ **Flexible** - Can adjust ticket structure in Python code

---

## Configuration

### Claude Desktop Config

```json
{
  "mcpServers": {
    "aia-assessment": {
      "command": "/usr/bin/python3",
      "args": ["/path/to/server.py"]
    },
    "jira": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-jira",
        "--api-token", "YOUR_JIRA_API_TOKEN",
        "--email", "your-email@company.com",
        "--base-url", "https://yourcompany.atlassian.net"
      ]
    }
  }
}
```

---

## Alternative: Python Calls Jira API Directly

If you prefer Python to handle everything (no LLM orchestration):

```python
@tool("export_e23_to_jira_direct")
def export_e23_to_jira_direct(assessment_results, jira_project_key):
    """
    Python creates assessment AND Jira tickets in one atomic operation.

    No LLM involved in ticket creation - 100% Python → Jira.
    """

    # Prepare ticket specs (same as above)
    ticket_specs = jira_builder.prepare_compliance_tickets(...)

    # Python calls Jira API directly (no Claude intermediary)
    jira_client = JiraAPIClient()
    created_tickets = []

    for spec in ticket_specs['ticket_specifications']:
        ticket = jira_client.create_issue(spec['jira_spec'])
        created_tickets.append(ticket)

    return {
        "success": True,
        "tickets_created": len(created_tickets),
        "ticket_keys": [t['key'] for t in created_tickets],
        "parent_ticket": created_tickets[0]['key'],
        "data_integrity": "100% - Python created all tickets directly via Jira API"
    }
```

**Tradeoff**: Less conversational ("create tickets" becomes one tool call), but maximum data integrity.

---

## Recommendation

**Use the MCP orchestration approach** because:
1. Clean separation: Your MCP = assessment logic, Jira MCP = Jira integration
2. Conversational: User can say "now create Jira tickets"
3. Maintainable: Jira MCP team handles API changes
4. Data integrity: Python controls all content through structured specs

The key insight: **Python doesn't create tickets directly, it creates EXACT SPECIFICATIONS that Claude delivers to Jira MCP.**

This maintains data integrity while using the official Jira MCP.
