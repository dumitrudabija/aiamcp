# AIA Assessment Scoring Fix Documentation

## Issue Description

The AIA assessment tool was returning scores of 0 for all assessments due to a format mismatch in how `selectedOption` values were being processed.

## Root Cause

The MCP tool interface sends responses with `selectedOption` as numeric indices (0, 1, 2, etc.), but the scoring system in `aia_processor.py` expects the actual choice `value` strings (like "item1-3", "item2-0", etc.) where the number after the dash represents the score.

### Before Fix
```python
# In server.py _assess_project method
converted_responses.append({
    "question_id": response.get("questionId", ""),
    "selected_values": [str(response.get("selectedOption", 0))]  # Wrong: converts index to string
})
```

This would convert `selectedOption: 1` to `selected_values: ["1"]`, but the scoring system was looking for choice values like `"item2-3"`.

### After Fix
```python
# In server.py _assess_project method
question = questions_by_name.get(question_id)
if question and question.get('choices'):
    if 0 <= selected_option < len(question['choices']):
        choice_value = question['choices'][selected_option]['value']  # Get actual choice value
        converted_responses.append({
            "question_id": question_id,
            "selected_values": [choice_value]  # Correct: uses actual choice value
        })
```

Now `selectedOption: 1` correctly maps to the actual choice value (e.g., `"item2-3"`), which the scoring system can properly evaluate.

## Solution Implementation

1. **Question Lookup**: Create a lookup dictionary of questions by name from `self.aia_processor.scorable_questions`

2. **Index to Value Mapping**: For each response, find the corresponding question and map the `selectedOption` index to the actual choice `value`

3. **Error Handling**: Added fallback logic for invalid indices or unknown questions

4. **Logging**: Added warning logs for debugging invalid responses

## Test Results

### High-Risk Scenario
- **Input**: 18 high-risk responses (selecting highest-scoring options)
- **Output**: 49 points → Impact Level IV (Very High Impact)
- **Individual Scores**: Each question correctly shows its score contribution

### Low-Risk Scenario  
- **Input**: 18 low-risk responses (selecting lowest-scoring options)
- **Output**: 5 points → Impact Level I (Little to no impact)
- **Individual Scores**: Each question correctly shows its score contribution

## Choice Value Format

AIA questions use choice values in the format `"item{n}-{score}"`:
- `"item1-0"` = First choice, 0 points
- `"item2-3"` = Second choice, 3 points  
- `"item3-1"` = Third choice, 1 point

The number after the dash is extracted by `aia_processor.py` using regex: `r'item\d+-(\d+)'`

## Impact

This fix resolves the critical scoring issue where all assessments returned 0 points regardless of responses. The AIA assessment tool now correctly:

- Maps user selections to proper choice values
- Calculates accurate risk scores
- Determines correct impact levels (I-IV)
- Provides meaningful assessment results

## Files Modified

- `server.py`: Updated `_assess_project()` method with proper selectedOption mapping
- `SCORING_FIX_DOCUMENTATION.md`: This documentation file

## Verification

The fix has been tested and verified with both high-risk and low-risk scenarios, confirming that:
- Scoring calculations are accurate
- Impact level determinations are correct
- Individual question scores are properly attributed
- The system handles edge cases gracefully
