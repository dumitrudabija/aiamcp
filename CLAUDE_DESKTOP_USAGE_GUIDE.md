# Claude Desktop Usage Guide for AIA Assessment

## Problem Statement

Claude Desktop sometimes tries to interpret project descriptions and make its own risk assessments before using the actual MCP scoring tools, leading to inconsistent results where Claude's interpretation differs from the calculated score.

## Correct Workflow

### Step 1: Project Analysis (Optional)
```
Use: analyze_project_description
Purpose: Get initial understanding and categorization
Output: Framework overview and question categories
```

### Step 2: Question Retrieval
```
Use: get_questions
Purpose: Retrieve specific AIA questions that need answers
Parameters: 
  - category: "Impact", "System", "Algorithm", etc.
  - type: "risk" (for scoring questions)
Output: List of questions with their options and scoring
```

### Step 3: Collect Actual Responses
**CRITICAL**: This step requires human input - do NOT make assumptions!
- Present questions to stakeholders
- Collect actual selectedOption indices (0, 1, 2, etc.)
- Document the reasoning for each selection

### Step 4: Calculate Official Score
```
Use: assess_project
Purpose: Calculate the official AIA risk score
Parameters:
  - projectName: String
  - projectDescription: String  
  - responses: Array of {questionId, selectedOption}
Output: Official risk score and impact level
```

## What NOT to Do

❌ **Don't make assumptions about risk levels based on project descriptions**
❌ **Don't interpret or guess answers to AIA questions**
❌ **Don't provide preliminary risk assessments without actual responses**
❌ **Don't use assess_project without the responses array**

## Tool Descriptions Have Been Enhanced

The MCP server now includes explicit warnings in tool descriptions:

- **assess_project**: "FINAL STEP: Calculate official AIA risk score using actual question responses. CRITICAL: Only use this tool with actual user responses to specific AIA questions."

- **responses parameter**: "REQUIRED: Array of actual question responses with questionId and selectedOption. Without responses, this tool will only return questions to answer, not a risk assessment."

## Workflow Guidance in Responses

The MCP server now provides workflow guidance in its responses:

### When called without responses:
```json
{
  "workflow_guidance": {
    "message": "⚠️ IMPORTANT: This tool requires actual question responses to calculate a valid risk score.",
    "next_steps": [
      "1. Use 'analyze_project_description' to understand the project context",
      "2. Use 'get_questions' to retrieve specific AIA questions", 
      "3. Collect actual responses to questions from stakeholders",
      "4. Use 'assess_project' again with the responses array populated"
    ],
    "warning": "Do NOT make assumptions about risk levels based on project descriptions alone."
  }
}
```

### When called with responses:
```json
{
  "workflow_guidance": {
    "message": "✅ Assessment completed using X actual question responses.",
    "note": "This score is based on actual responses and is valid for AIA compliance purposes."
  }
}
```

## Example Correct Usage

```javascript
// Step 1: Analyze project (optional)
await use_mcp_tool("aia-assessment", "analyze_project_description", {
  "projectName": "AI Hiring System",
  "projectDescription": "Automated resume screening system"
});

// Step 2: Get questions
await use_mcp_tool("aia-assessment", "get_questions", {
  "type": "risk"
});

// Step 3: Collect actual responses from stakeholders
// (This requires human input - don't assume!)

// Step 4: Calculate official score
await use_mcp_tool("aia-assessment", "assess_project", {
  "projectName": "AI Hiring System", 
  "projectDescription": "Automated resume screening system",
  "responses": [
    {"questionId": "riskProfile1", "selectedOption": 1},
    {"questionId": "impact30", "selectedOption": 0},
    // ... more actual responses
  ]
});
```

## Key Reminders for Claude Desktop

1. **Only calculated scores are valid** - Don't make risk level interpretations
2. **Responses are required** - The assess_project tool needs actual question responses
3. **Follow the workflow** - Use tools in the correct order
4. **Don't assume** - Always collect actual stakeholder input for questions
5. **Trust the calculation** - The MCP server handles all scoring logic correctly

## Benefits of This Approach

- **Consistency**: Same scoring methodology every time
- **Compliance**: Follows Canada's official AIA framework
- **Accuracy**: Based on actual responses, not interpretations
- **Transparency**: Clear audit trail of questions and responses
- **Reliability**: Eliminates discrepancies between AI interpretation and calculated scores
