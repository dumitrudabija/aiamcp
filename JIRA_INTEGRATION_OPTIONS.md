# Jira Integration Options - Alternative Output Formats

**Question**: Instead of a Word document, how would I create a Jira ticket for checklist items?

**Answer**: You have 3 main options, depending on whether Jira exposes an MCP server.

---

## Option 1: If Jira Has Its Own MCP Server (Ideal)

### Architecture
```
┌─────────┐         ┌─────────────┐         ┌──────────────┐
│  USER   │ ←──────→│   CLAUDE    │ ←─MCP──→│  Your MCP    │
└─────────┘         └─────────────┘         │  (OSFI E-23) │
                           │                └──────────────┘
                           │                        ↓
                           │                 Returns assessment
                           │                   results JSON
                           │
                           │ MCP
                           ↓
                    ┌──────────────┐
                    │  Jira MCP    │
                    │  (Official)  │
                    └──────────────┘
                           ↓
                    Creates ticket
                    with checklist
```

### How It Works

**Step 1**: User triggers assessment
```
USER: "Assess my credit model for OSFI E-23 and create Jira tickets"
```

**Step 2**: Claude calls your MCP
```javascript
// Claude calls your MCP
use_mcp_tool("aia-assessment", "assess_model_risk", {
  projectName: "Credit Model",
  projectDescription: "..."
});

// Returns:
{
  risk_level: "High",
  risk_score: 68,
  compliance_checklist: [
    "Model validation documentation",
    "Independent model review",
    "Governance approval from CRO",
    ...
  ]
}
```

**Step 3**: Claude calls Jira MCP with results
```javascript
// Claude then calls Jira MCP
use_mcp_tool("jira", "create_issue", {
  project: "COMPLIANCE",
  issueType: "Task",
  summary: "OSFI E-23 Compliance - Credit Model (High Risk)",
  description: "Risk Score: 68/100\nRequires enhanced governance...",
  checklist: [
    {item: "Model validation documentation", done: false},
    {item: "Independent model review", done: false},
    {item: "Governance approval from CRO", done: false}
  ]
});
```

### Advantages
- ✅ Clean separation of concerns
- ✅ Jira maintains their own MCP server
- ✅ Claude orchestrates both tools
- ✅ No API key management in your code
- ✅ Jira updates don't break your code

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "aia-assessment": {
      "command": "/usr/bin/python3",
      "args": ["/path/to/server.py"]
    },
    "jira": {
      "command": "/path/to/jira-mcp-server",
      "args": ["--api-key", "YOUR_JIRA_API_KEY"]
    }
  }
}
```

**Check if Jira MCP exists**: https://github.com/modelcontextprotocol/servers

---

## Option 2: Direct Jira API Integration (If No Jira MCP)

### Architecture
```
┌─────────┐         ┌─────────────┐         ┌──────────────────┐
│  USER   │ ←──────→│   CLAUDE    │ ←─MCP──→│  Your MCP        │
└─────────┘         └─────────────┘         │  (Enhanced)      │
                                             └──────────────────┘
                                                      ↓
                                             Python calls Jira
                                             REST API directly
                                                      ↓
                                             ┌──────────────────┐
                                             │  Jira Cloud API  │
                                             │  (HTTPS REST)    │
                                             └──────────────────┘
```

### Implementation

**Step 1**: Add new MCP tool to your server

```python
# In config/tool_registry.py - add new tool metadata
{
    "name": "create_jira_compliance_ticket",
    "description": "🎫 Create Jira ticket with OSFI E-23 compliance checklist",
    "inputSchema": {
        "type": "object",
        "properties": {
            "project_name": {"type": "string"},
            "assessment_results": {"type": "object"},
            "jira_project_key": {"type": "string", "default": "COMPLIANCE"}
        },
        "required": ["project_name", "assessment_results"]
    }
}
```

**Step 2**: Create Jira integration module

```python
# jira_integration.py
import requests
import os
from typing import Dict, Any

class JiraIntegration:
    """Integrates OSFI E-23 assessments with Jira."""

    def __init__(self):
        self.jira_url = os.getenv("JIRA_URL", "https://yourcompany.atlassian.net")
        self.jira_email = os.getenv("JIRA_EMAIL")
        self.jira_api_token = os.getenv("JIRA_API_TOKEN")

    def create_compliance_ticket(
        self,
        project_key: str,
        project_name: str,
        assessment_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create Jira ticket from OSFI E-23 assessment.

        Args:
            project_key: Jira project key (e.g., "COMPLIANCE")
            project_name: Name of the model being assessed
            assessment_results: Results from assess_model_risk or export_e23_report

        Returns:
            Jira ticket details with ticket URL
        """

        # Extract data from assessment
        risk_level = assessment_results.get("risk_level", "Unknown")
        risk_score = assessment_results.get("risk_score", 0)
        checklist = assessment_results.get("compliance_checklist", [])

        # Build Jira ticket
        ticket_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": f"OSFI E-23 Compliance - {project_name} ({risk_level} Risk)",
                "description": self._build_description(assessment_results),
                "issuetype": {"name": "Task"},
                "priority": self._map_risk_to_priority(risk_level),
                "labels": ["osfi-e23", "compliance", f"risk-{risk_level.lower()}"],

                # Custom fields (adjust IDs to your Jira instance)
                "customfield_10001": risk_score,  # Risk Score
                "customfield_10002": risk_level,  # Risk Level
            }
        }

        # Create ticket
        response = requests.post(
            f"{self.jira_url}/rest/api/3/issue",
            auth=(self.jira_email, self.jira_api_token),
            headers={"Content-Type": "application/json"},
            json=ticket_data
        )

        if response.status_code == 201:
            ticket = response.json()
            ticket_key = ticket["key"]

            # Add checklist items as subtasks
            self._create_checklist_subtasks(ticket_key, checklist)

            return {
                "success": True,
                "ticket_key": ticket_key,
                "ticket_url": f"{self.jira_url}/browse/{ticket_key}",
                "message": f"Created Jira ticket {ticket_key} with {len(checklist)} checklist items"
            }
        else:
            return {
                "success": False,
                "error": response.text
            }

    def _build_description(self, assessment_results: Dict[str, Any]) -> str:
        """Build Jira ticket description from assessment results."""
        risk_level = assessment_results.get("risk_level", "Unknown")
        risk_score = assessment_results.get("risk_score", 0)

        description = f"""
h2. OSFI E-23 Model Risk Assessment

*Risk Level:* {risk_level}
*Risk Score:* {risk_score}/100

h3. Risk Factors Detected
{self._format_risk_factors(assessment_results)}

h3. Governance Requirements
{self._format_governance_requirements(assessment_results)}

h3. Compliance Checklist
See subtasks for detailed checklist items.

---
_Generated by OSFI E-23 Assessment MCP Server_
        """
        return description.strip()

    def _create_checklist_subtasks(self, parent_key: str, checklist: list):
        """Create Jira subtasks for each checklist item."""
        for item in checklist:
            subtask_data = {
                "fields": {
                    "project": {"key": parent_key.split("-")[0]},
                    "parent": {"key": parent_key},
                    "summary": item.get("requirement", item),
                    "issuetype": {"name": "Sub-task"},
                    "description": item.get("details", "")
                }
            }

            requests.post(
                f"{self.jira_url}/rest/api/3/issue",
                auth=(self.jira_email, self.jira_api_token),
                headers={"Content-Type": "application/json"},
                json=subtask_data
            )

    def _map_risk_to_priority(self, risk_level: str) -> Dict[str, str]:
        """Map OSFI risk level to Jira priority."""
        priority_map = {
            "Critical": {"name": "Highest"},
            "High": {"name": "High"},
            "Medium": {"name": "Medium"},
            "Low": {"name": "Low"}
        }
        return priority_map.get(risk_level, {"name": "Medium"})

    def _format_risk_factors(self, assessment_results: Dict[str, Any]) -> str:
        """Format risk factors as Jira markup."""
        factors = assessment_results.get("detected_factors", [])
        return "\n".join([f"* {factor}" for factor in factors])

    def _format_governance_requirements(self, assessment_results: Dict[str, Any]) -> str:
        """Format governance requirements as Jira markup."""
        governance = assessment_results.get("governance_requirements", {})
        return f"""
* *Approval Authority:* {governance.get('approval_authority', 'TBD')}
* *Monitoring Frequency:* {governance.get('monitoring_frequency', 'TBD')}
* *Review Requirements:* {governance.get('review_requirements', 'TBD')}
        """
```

**Step 3**: Add tool handler to server.py

```python
# In server.py
from jira_integration import JiraIntegration

class MCPServer:
    def __init__(self):
        # ... existing code ...
        self.jira = JiraIntegration()

    async def _create_jira_compliance_ticket(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Create Jira ticket from assessment results."""
        try:
            result = self.jira.create_compliance_ticket(
                project_key=arguments.get("jira_project_key", "COMPLIANCE"),
                project_name=arguments["project_name"],
                assessment_results=arguments["assessment_results"]
            )

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(e)})
            )]
```

**Step 4**: Configure environment variables

```bash
# .env file
JIRA_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_jira_api_token
```

**Step 5**: Install dependencies

```bash
pip install requests python-dotenv
```

### Usage Flow

```
USER: "Assess my credit model and create a Jira ticket"
  ↓
CLAUDE: Calls assess_model_risk
  ↓
PYTHON: Returns assessment results
  ↓
CLAUDE: Calls create_jira_compliance_ticket
  ↓
PYTHON:
  - Calls Jira REST API
  - Creates main ticket
  - Creates subtasks for checklist
  - Returns ticket URL
  ↓
CLAUDE: "✅ Created Jira ticket COMPLIANCE-123 with 12 checklist items"
```

### Advantages
- ✅ Full control over Jira integration
- ✅ Can customize ticket structure
- ✅ Works even if Jira doesn't have MCP
- ✅ Can add company-specific logic

### Disadvantages
- ❌ You manage API keys
- ❌ Jira API changes could break your code
- ❌ More code to maintain

---

## Option 3: Hybrid Approach (MCP + Direct API)

### When to Use
- Jira MCP exists but lacks features you need
- You want MCP benefits + custom functionality

### Implementation
```python
# Use Jira MCP for basic ticket creation
# Use direct API for advanced features (e.g., custom fields)

def create_ticket_hybrid(assessment_results):
    # 1. Use Jira MCP for ticket creation
    ticket = call_jira_mcp_create_ticket(basic_info)

    # 2. Enhance with direct API calls
    add_custom_fields_via_api(ticket.key, assessment_results)
    add_compliance_checklist_via_api(ticket.key, checklist)

    return ticket
```

---

## Comparison Matrix

| Feature | Option 1: Jira MCP | Option 2: Direct API | Option 3: Hybrid |
|---------|-------------------|---------------------|------------------|
| **Setup Complexity** | Low | Medium | Medium |
| **Maintenance** | Low (Jira maintains) | High (you maintain) | Medium |
| **Customization** | Limited | Full | High |
| **API Key Management** | Jira MCP handles | You handle | Both |
| **Reliability** | High | Medium | High |
| **Company-Specific Logic** | Limited | Full | Full |

---

## Recommended Approach

**Start with Option 1 (Jira MCP)** if it exists:
1. Check: https://github.com/modelcontextprotocol/servers
2. If Jira MCP exists → use it
3. If Jira MCP missing features → use Option 3 (Hybrid)
4. If no Jira MCP → use Option 2 (Direct API)

**Key Principle**: Your assessment logic **never changes**. Only the output format changes (Word vs Jira vs Slack vs Email).

---

## Example: Multi-Output Support

You could support **both Word documents AND Jira tickets**:

```python
# User chooses output format
USER: "Assess model and create both a report and a Jira ticket"

# Claude orchestrates
1. assess_model_risk()       → returns results
2. export_e23_report()        → creates Word doc
3. create_jira_ticket()       → creates Jira ticket

# Same assessment, multiple outputs!
```

This is the power of separating **assessment logic** (Python) from **output format** (pluggable).
