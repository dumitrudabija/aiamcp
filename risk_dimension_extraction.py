"""
Risk Dimension Extraction Module

This module generates extraction prompts for Claude Desktop to extract
structured risk factor values from project descriptions, then validates
and processes the extracted values.

Architecture:
    User Description
        -> MCP generates extraction prompt (this module)
        -> Returns to Claude Desktop
        -> Claude extracts facts as JSON
        -> User confirms/adjusts
        -> MCP validates JSON (this module)
        -> MCP scores deterministically (osfi_e23_risk_dimensions.py)

Key Design Principles:
1. AI extracts facts, Python scores deterministically
2. NOT_STATED defaults to Medium risk with tracking
3. All extracted values are validated against schema
4. Audit trail maintains transparency
5. Prompt templates are configurable via config/extraction_prompts.yaml

Reference: OSFI Guideline E-23 – Model Risk Management
"""

from typing import Dict, List, Any, Tuple, Optional
from enum import Enum
import json
import logging
import os
import yaml
from pathlib import Path

from osfi_e23_risk_dimensions import (
    RISK_DIMENSIONS,
    DIMENSION_ORDER,
    FactorType,
    RiskLevel,
    get_dimension,
    get_dimension_factors,
    RISK_LEVEL_SCORES
)

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION LOADING
# =============================================================================

def _get_config_path() -> Path:
    """Get the path to the extraction prompts config file."""
    module_dir = Path(__file__).parent
    return module_dir / "config" / "extraction_prompts.yaml"


def _load_prompt_config() -> Dict[str, Any]:
    """
    Load prompt configuration from YAML file.

    Returns default values if config file is not found or has errors.
    """
    config_path = _get_config_path()

    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded extraction prompts config from {config_path}")
                return config
        else:
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return {}
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}, using defaults")
        return {}


# Load config at module initialization
_PROMPT_CONFIG = _load_prompt_config()


def reload_prompt_config() -> Dict[str, Any]:
    """
    Reload the prompt configuration from disk.

    Call this if you've updated the YAML file and want changes
    to take effect without restarting the server.

    Returns:
        The reloaded configuration dict
    """
    global _PROMPT_CONFIG
    _PROMPT_CONFIG = _load_prompt_config()
    return _PROMPT_CONFIG


def get_prompt_config() -> Dict[str, Any]:
    """Get the current prompt configuration."""
    return _PROMPT_CONFIG


# =============================================================================
# CONSTANTS
# =============================================================================

def _get_not_stated_constant() -> str:
    """Get the NOT_STATED constant from config or default."""
    not_stated_config = _PROMPT_CONFIG.get("not_stated_handling", {})
    return not_stated_config.get("constant", "NOT_STATED")

NOT_STATED = _get_not_stated_constant()
VALID_RISK_LEVELS = ["low", "medium", "high", "critical", NOT_STATED]


# =============================================================================
# DEFAULT PROMPT TEMPLATES (used when config not found or missing keys)
# =============================================================================

_DEFAULT_TEMPLATES = {
    "header": """## Risk Factor Extraction Task

Analyze the following project description and extract values for each risk factor.
For each factor, provide ONLY factual information explicitly stated or clearly implied.
If information is not available, use "{NOT_STATED}".""",

    "project_section": """### Project Description:
---
{project_description}
---""",

    "instructions": """### Extraction Instructions:

For each dimension below, extract the requested factor values based ONLY on
information in the project description. Do not infer or assume values.""",

    "output_format": """### Required Output Format:

Return a JSON object with this exact structure:
```json
{{
  "extraction_metadata": {{
    "confidence_notes": "Any notes about extraction confidence or ambiguity"
  }},
  "dimensions": {{
{json_template}
  }}
}}
```""",

    "important_notes": """IMPORTANT:
- Use exact factor IDs as shown above
- For quantitative factors: provide numeric values or "{NOT_STATED}"
- For qualitative factors: use one of the provided level keys (low/medium/high/critical) or "{NOT_STATED}"
- Include brief evidence quotes where possible""",

    "quantitative_factor": """    - **{factor_id}** ({factor_name}):
      Type: Quantitative ({unit})
      Ranges: {ranges}
      Extract: The numeric {unit} value, or "{NOT_STATED}" if not mentioned""",

    "qualitative_factor": """    - **{factor_id}** ({factor_name}):
      Type: Qualitative
      Options: {options}
      Extract: The matching level, or "{NOT_STATED}" if not determinable""",

    "dimension_section": """
### {dimension_name}
*Core Question: {core_question}*

Factors to extract:
{factor_questions}
"""
}


def _get_template(key: str) -> str:
    """
    Get a prompt template from config, with fallback to default.

    Args:
        key: The template key to retrieve

    Returns:
        The template string from config or default
    """
    # Check extraction_prompt section first
    extraction_config = _PROMPT_CONFIG.get("extraction_prompt", {})
    if key in extraction_config:
        return extraction_config[key]

    # Check factor_templates section
    factor_templates = _PROMPT_CONFIG.get("factor_templates", {})
    if key == "quantitative_factor" and "quantitative" in factor_templates:
        return factor_templates["quantitative"]
    if key == "qualitative_factor" and "qualitative" in factor_templates:
        return factor_templates["qualitative"]

    # Check dimension_template
    if key == "dimension_section" and "dimension_template" in _PROMPT_CONFIG:
        return _PROMPT_CONFIG["dimension_template"]

    # Fall back to default
    return _DEFAULT_TEMPLATES.get(key, "")


# =============================================================================
# EXTRACTION PROMPT GENERATION
# =============================================================================

def generate_extraction_prompt(project_description: str) -> str:
    """
    Generate a structured prompt for Claude Desktop to extract
    risk factor values from a project description.

    Templates are loaded from config/extraction_prompts.yaml if available,
    with fallback to built-in defaults.

    Args:
        project_description: The user's project description text

    Returns:
        A prompt string that instructs Claude to extract values
        for each risk factor in JSON format
    """
    # Build factor questions from dimension definitions
    factor_sections = []

    # Get templates
    quantitative_template = _get_template("quantitative_factor")
    qualitative_template = _get_template("qualitative_factor")
    dimension_template = _get_template("dimension_section")

    for dim_id in DIMENSION_ORDER:
        dim = get_dimension(dim_id)
        if not dim:
            continue

        dim_name = dim["name"]
        core_question = dim["core_question"]
        factors = dim.get("factors", [])

        factor_questions = []
        for factor in factors:
            factor_id = factor["id"]
            factor_name = factor["name"]
            factor_type = factor["type"]

            if factor_type == FactorType.QUANTITATIVE.value:
                # For quantitative: ask for numeric value with unit
                unit = factor.get("unit", "value")
                thresholds = factor.get("thresholds", {})
                ranges = _format_thresholds(thresholds)

                question = quantitative_template.format(
                    factor_id=factor_id,
                    factor_name=factor_name,
                    unit=unit,
                    ranges=ranges,
                    NOT_STATED=NOT_STATED
                )

            else:
                # For qualitative: provide the level options
                levels = factor.get("levels", {})
                options = _format_levels(levels)

                question = qualitative_template.format(
                    factor_id=factor_id,
                    factor_name=factor_name,
                    options=options,
                    NOT_STATED=NOT_STATED
                )

            factor_questions.append(question)

        section = dimension_template.format(
            dimension_name=dim_name,
            core_question=core_question,
            factor_questions=chr(10).join(factor_questions)
        )
        factor_sections.append(section)

    # Get main prompt templates
    header = _get_template("header").format(NOT_STATED=NOT_STATED)
    project_section = _get_template("project_section").format(
        project_description=project_description
    )
    instructions = _get_template("instructions")
    output_format = _get_template("output_format").format(
        json_template=_generate_json_template()
    )
    important_notes = _get_template("important_notes").format(NOT_STATED=NOT_STATED)

    # Assemble the full prompt
    prompt = f"""{header}

{project_section}

{instructions}

{"".join(factor_sections)}

{output_format}

{important_notes}
"""

    return prompt


def _format_thresholds(thresholds: Dict[str, Any]) -> str:
    """Format threshold values for display in prompt."""
    parts = []
    for level in ["low", "medium", "high", "critical"]:
        if level in thresholds:
            desc = thresholds[level].get("description", "")
            parts.append(f"{level}: {desc}")
    return " | ".join(parts)


def _format_levels(levels: Dict[str, str]) -> str:
    """Format qualitative level options for display in prompt."""
    parts = []
    for level in ["low", "medium", "high", "critical"]:
        if level in levels:
            parts.append(f"{level}=\"{levels[level]}\"")
    return " | ".join(parts)


def _generate_json_template() -> str:
    """Generate the JSON template structure for all dimensions."""
    lines = []

    for i, dim_id in enumerate(DIMENSION_ORDER):
        dim = get_dimension(dim_id)
        if not dim:
            continue

        factors = dim.get("factors", [])
        factor_lines = []

        for j, factor in enumerate(factors):
            factor_id = factor["id"]
            factor_type = factor["type"]

            if factor_type == FactorType.QUANTITATIVE.value:
                value_example = f'"<number or {NOT_STATED}>"'
            else:
                value_example = f'"<low|medium|high|critical|{NOT_STATED}>"'

            comma = "," if j < len(factors) - 1 else ""
            factor_lines.append(
                f'        "{factor_id}": {{"value": {value_example}, "evidence": "<quote or null>"}}{comma}'
            )

        comma = "," if i < len(DIMENSION_ORDER) - 1 else ""
        lines.append(f'    "{dim_id}": {{')
        lines.extend(factor_lines)
        lines.append(f'    }}{comma}')

    return "\n".join(lines)


# =============================================================================
# RESPONSE VALIDATION
# =============================================================================

def validate_extraction_response(response: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Validate the extracted JSON response against the dimension schema.

    Args:
        response: The JSON response from Claude's extraction

    Returns:
        Tuple of (validated_data, list_of_issues)
        - validated_data contains cleaned values with NOT_STATED defaults
        - issues lists any validation problems found
    """
    issues = []
    validated = {
        "dimensions": {},
        "not_stated_factors": [],  # Track which factors defaulted to Medium
        "extraction_metadata": response.get("extraction_metadata", {})
    }

    response_dimensions = response.get("dimensions", {})

    for dim_id in DIMENSION_ORDER:
        dim = get_dimension(dim_id)
        if not dim:
            continue

        validated["dimensions"][dim_id] = {
            "name": dim["name"],
            "factors": {}
        }

        dim_data = response_dimensions.get(dim_id, {})

        for factor in dim.get("factors", []):
            factor_id = factor["id"]
            factor_type = factor["type"]

            factor_data = dim_data.get(factor_id, {})

            # Extract and validate value
            raw_value = factor_data.get("value")
            evidence = factor_data.get("evidence")

            validated_value, is_not_stated, factor_issues = _validate_factor_value(
                factor_id, factor_type, raw_value, factor, dim_id
            )

            issues.extend(factor_issues)

            validated["dimensions"][dim_id]["factors"][factor_id] = {
                "name": factor["name"],
                "type": factor_type,
                "value": validated_value,
                "evidence": evidence,
                "is_not_stated": is_not_stated
            }

            if is_not_stated:
                validated["not_stated_factors"].append({
                    "dimension": dim_id,
                    "dimension_name": dim["name"],
                    "factor": factor_id,
                    "factor_name": factor["name"]
                })

    return validated, issues


def _validate_factor_value(
    factor_id: str,
    factor_type: str,
    raw_value: Any,
    factor_def: Dict[str, Any],
    dim_id: str
) -> Tuple[Any, bool, List[str]]:
    """
    Validate a single factor value.

    Returns:
        Tuple of (validated_value, is_not_stated, list_of_issues)
    """
    issues = []

    # Handle NOT_STATED or missing values
    if raw_value is None or raw_value == NOT_STATED or str(raw_value).upper() == NOT_STATED:
        return None, True, issues

    if factor_type == FactorType.QUANTITATIVE.value:
        # Validate numeric value
        try:
            if isinstance(raw_value, str):
                # Try to extract number from string
                cleaned = raw_value.replace(",", "").replace("$", "").replace("%", "")
                validated_value = float(cleaned)
            else:
                validated_value = float(raw_value)
            return validated_value, False, issues
        except (ValueError, TypeError):
            issues.append(
                f"Invalid quantitative value for {dim_id}.{factor_id}: '{raw_value}'"
            )
            return None, True, issues

    else:
        # Validate qualitative level
        if isinstance(raw_value, str):
            normalized = raw_value.lower().strip()
            if normalized in ["low", "medium", "high", "critical"]:
                return normalized, False, issues
            else:
                issues.append(
                    f"Invalid qualitative level for {dim_id}.{factor_id}: '{raw_value}'"
                )
                return None, True, issues
        else:
            issues.append(
                f"Expected string level for {dim_id}.{factor_id}, got: {type(raw_value)}"
            )
            return None, True, issues


# =============================================================================
# FACTOR SCORING (DETERMINISTIC)
# =============================================================================

def score_factor(
    factor_id: str,
    factor_type: str,
    value: Any,
    factor_def: Dict[str, Any],
    is_not_stated: bool
) -> Dict[str, Any]:
    """
    Score a single factor value deterministically.

    Args:
        factor_id: The factor identifier
        factor_type: "quantitative" or "qualitative"
        value: The extracted value (or None if NOT_STATED)
        factor_def: The factor definition from osfi_e23_risk_dimensions
        is_not_stated: Whether this value was NOT_STATED

    Returns:
        Dict with risk_level, numeric_score, and scoring_notes
    """
    result = {
        "factor_id": factor_id,
        "value": value,
        "is_not_stated": is_not_stated,
        "risk_level": "medium",  # Default
        "numeric_score": 2,  # Medium = 2
        "scoring_notes": ""
    }

    if is_not_stated:
        result["scoring_notes"] = "Defaulted to Medium - information not stated in description"
        return result

    if factor_type == FactorType.QUANTITATIVE.value:
        result = _score_quantitative(value, factor_def, result)
    else:
        result = _score_qualitative(value, factor_def, result)

    return result


def _score_quantitative(
    value: float,
    factor_def: Dict[str, Any],
    result: Dict[str, Any]
) -> Dict[str, Any]:
    """Score a quantitative factor based on thresholds."""
    thresholds = factor_def.get("thresholds", {})
    invert_scale = factor_def.get("invert_scale", False)

    # Determine risk level based on thresholds
    risk_level = "medium"  # Default

    for level in ["low", "medium", "high", "critical"]:
        if level not in thresholds:
            continue

        thresh = thresholds[level]
        min_val = thresh.get("min")
        max_val = thresh.get("max")

        in_range = True
        if min_val is not None and value < min_val:
            in_range = False
        if max_val is not None and value > max_val:
            in_range = False

        if in_range:
            risk_level = level
            break

    # Handle inverted scales (e.g., higher consistency = lower risk)
    if invert_scale:
        invert_map = {"low": "critical", "medium": "high", "high": "medium", "critical": "low"}
        risk_level = invert_map.get(risk_level, risk_level)

    result["risk_level"] = risk_level
    result["numeric_score"] = RISK_LEVEL_SCORES.get(risk_level, 2)
    result["scoring_notes"] = f"Value {value} maps to {risk_level} based on thresholds"

    return result


def _score_qualitative(
    value: str,
    factor_def: Dict[str, Any],
    result: Dict[str, Any]
) -> Dict[str, Any]:
    """Score a qualitative factor based on level mapping."""
    # Qualitative levels map directly to risk levels
    risk_level = value.lower() if isinstance(value, str) else "medium"

    if risk_level not in ["low", "medium", "high", "critical"]:
        risk_level = "medium"
        result["scoring_notes"] = f"Unknown level '{value}', defaulted to medium"
    else:
        result["scoring_notes"] = f"Direct mapping from qualitative level"

    result["risk_level"] = risk_level
    result["numeric_score"] = RISK_LEVEL_SCORES.get(risk_level, 2)

    return result


# =============================================================================
# DIMENSION SCORING
# =============================================================================

def score_dimension(
    dim_id: str,
    factor_scores: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate aggregate risk score for a dimension from its factor scores.

    Current implementation: Simple average of factor scores.
    Note: Weighting logic can be added here when specifications are provided.

    Args:
        dim_id: The dimension identifier
        factor_scores: List of scored factors for this dimension

    Returns:
        Dict with dimension risk_level, numeric_score, and breakdown
    """
    if not factor_scores:
        return {
            "dimension_id": dim_id,
            "risk_level": "not_assessed",
            "numeric_score": 0,
            "factor_count": 0,
            "not_stated_count": 0,
            "scoring_method": "none"
        }

    total_score = sum(f["numeric_score"] for f in factor_scores)
    not_stated_count = sum(1 for f in factor_scores if f["is_not_stated"])
    avg_score = total_score / len(factor_scores)

    # Map average to risk level
    if avg_score < 1.5:
        risk_level = "low"
    elif avg_score < 2.5:
        risk_level = "medium"
    elif avg_score < 3.5:
        risk_level = "high"
    else:
        risk_level = "critical"

    return {
        "dimension_id": dim_id,
        "risk_level": risk_level,
        "numeric_score": round(avg_score, 2),
        "factor_count": len(factor_scores),
        "not_stated_count": not_stated_count,
        "scoring_method": "simple_average",
        "scoring_note": "Weighting can be customized per institutional requirements"
    }


# =============================================================================
# OVERALL RISK CALCULATION
# =============================================================================

def calculate_overall_risk(
    dimension_scores: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate overall model risk from dimension scores.

    Current implementation: Simple average of dimension scores.
    Note: Weighting and amplification logic can be added per institutional specs.

    Args:
        dimension_scores: Dict of dimension_id -> dimension score data

    Returns:
        Dict with overall risk_level, numeric_score, and dimension breakdown
    """
    if not dimension_scores:
        return {
            "overall_risk_level": "not_assessed",
            "overall_numeric_score": 0,
            "dimensions_assessed": 0,
            "scoring_method": "none"
        }

    scores = [d["numeric_score"] for d in dimension_scores.values() if d["numeric_score"] > 0]

    if not scores:
        return {
            "overall_risk_level": "not_assessed",
            "overall_numeric_score": 0,
            "dimensions_assessed": 0,
            "scoring_method": "none"
        }

    avg_score = sum(scores) / len(scores)

    # Map average to risk level
    if avg_score < 1.5:
        risk_level = "low"
    elif avg_score < 2.5:
        risk_level = "medium"
    elif avg_score < 3.5:
        risk_level = "high"
    else:
        risk_level = "critical"

    # Count not_stated factors across all dimensions
    total_not_stated = sum(
        d.get("not_stated_count", 0)
        for d in dimension_scores.values()
    )

    return {
        "overall_risk_level": risk_level,
        "overall_numeric_score": round(avg_score, 2),
        "dimensions_assessed": len(scores),
        "total_not_stated_factors": total_not_stated,
        "scoring_method": "dimension_average",
        "scoring_note": "Weighting and amplification can be customized per institutional requirements"
    }


# =============================================================================
# FULL ASSESSMENT PIPELINE
# =============================================================================

def process_extraction_response(
    response: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process a complete extraction response through validation and scoring.

    This is the main entry point for processing Claude's extracted values.

    Args:
        response: The JSON response from Claude's extraction

    Returns:
        Complete assessment with:
        - validated_extraction: Cleaned extraction data
        - factor_scores: Individual factor scores
        - dimension_scores: Aggregate dimension scores
        - overall_assessment: Final risk rating
        - not_stated_summary: Factors that defaulted to Medium
        - validation_issues: Any issues found during validation
    """
    # Step 1: Validate extraction
    validated, issues = validate_extraction_response(response)

    # Step 2: Score each factor
    factor_scores = {}
    for dim_id in DIMENSION_ORDER:
        dim = get_dimension(dim_id)
        if not dim:
            continue

        factor_scores[dim_id] = []
        dim_factors = validated.get("dimensions", {}).get(dim_id, {}).get("factors", {})

        for factor in dim.get("factors", []):
            factor_id = factor["id"]
            factor_data = dim_factors.get(factor_id, {})

            score = score_factor(
                factor_id=factor_id,
                factor_type=factor["type"],
                value=factor_data.get("value"),
                factor_def=factor,
                is_not_stated=factor_data.get("is_not_stated", True)
            )
            score["evidence"] = factor_data.get("evidence")
            factor_scores[dim_id].append(score)

    # Step 3: Score each dimension
    dimension_scores = {}
    for dim_id, scores in factor_scores.items():
        dimension_scores[dim_id] = score_dimension(dim_id, scores)
        # Add dimension name
        dim = get_dimension(dim_id)
        if dim:
            dimension_scores[dim_id]["dimension_name"] = dim["name"]

    # Step 4: Calculate overall risk
    overall = calculate_overall_risk(dimension_scores)

    # Step 5: Compile results
    return {
        "validated_extraction": validated,
        "factor_scores": factor_scores,
        "dimension_scores": dimension_scores,
        "overall_assessment": overall,
        "not_stated_summary": {
            "count": len(validated.get("not_stated_factors", [])),
            "factors": validated.get("not_stated_factors", []),
            "note": "These factors were not found in the project description and defaulted to Medium risk"
        },
        "validation_issues": issues,
        "metadata": {
            "extraction_metadata": validated.get("extraction_metadata", {}),
            "scoring_methodology": "Deterministic threshold/level mapping with simple averaging",
            "customization_note": "Weights and aggregation methods can be tuned to institutional specifications"
        }
    }


# =============================================================================
# CONVENIENCE FUNCTIONS FOR MCP INTEGRATION
# =============================================================================

def get_extraction_prompt_for_description(project_description: str) -> Dict[str, Any]:
    """
    Generate extraction prompt ready for MCP tool response.

    Instructions are loaded from config/extraction_prompts.yaml if available.

    Args:
        project_description: The user's project description

    Returns:
        Dict structured for MCP tool response with prompt and instructions
    """
    prompt = generate_extraction_prompt(project_description)

    # Get instructions from config with defaults
    tool_instructions = _PROMPT_CONFIG.get("tool_response_instructions", {})

    return {
        "extraction_prompt": prompt,
        "instructions_for_claude": {
            "task": tool_instructions.get(
                "task",
                "Extract risk factor values from the project description"
            ),
            "output_format": tool_instructions.get(
                "output_format",
                "JSON as specified in the prompt"
            ),
            "handling_missing": tool_instructions.get(
                "handling_missing",
                f"Use '{NOT_STATED}' for any values not found"
            ).format(NOT_STATED=NOT_STATED),
            "confirmation_required": tool_instructions.get(
                "confirmation_required",
                "Present extracted values to user for confirmation before proceeding"
            )
        },
        "next_step": tool_instructions.get(
            "next_step",
            "After user confirms extraction, call assess_model_risk with the JSON response"
        )
    }


def format_not_stated_for_report(not_stated_summary: Dict[str, Any]) -> str:
    """
    Format NOT_STATED factors for inclusion in the report.

    Args:
        not_stated_summary: The not_stated_summary from process_extraction_response

    Returns:
        Formatted string for report inclusion
    """
    factors = not_stated_summary.get("factors", [])

    if not factors:
        return "All risk factors were successfully extracted from the project description."

    lines = [
        f"**{len(factors)} factors defaulted to Medium risk** (information not stated in description):",
        ""
    ]

    # Group by dimension
    by_dimension = {}
    for f in factors:
        dim_name = f.get("dimension_name", "Unknown")
        if dim_name not in by_dimension:
            by_dimension[dim_name] = []
        by_dimension[dim_name].append(f.get("factor_name", f.get("factor", "Unknown")))

    for dim_name, factor_names in by_dimension.items():
        lines.append(f"- **{dim_name}**: {', '.join(factor_names)}")

    lines.append("")
    lines.append("*These factors should be clarified in the project documentation for more accurate risk assessment.*")

    return "\n".join(lines)


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    # Quick test of extraction prompt generation
    test_description = """
    We are developing a credit scoring model that uses machine learning to assess
    loan applications. The model processes approximately 50,000 applications per year
    with potential exposure of $25 million. It uses a gradient boosting ensemble
    with 200 features trained on 2 million historical records. The model influences
    lending decisions but final approval requires human review.
    """

    print("=" * 60)
    print("Risk Dimension Extraction Module Test")
    print("=" * 60)

    # Generate prompt
    prompt = generate_extraction_prompt(test_description)
    print("\nGenerated Extraction Prompt (first 500 chars):")
    print("-" * 40)
    print(prompt[:500] + "...")

    # Test validation with mock response
    mock_response = {
        "extraction_metadata": {
            "confidence_notes": "Most values clearly stated"
        },
        "dimensions": {
            "misuse_unintended_harm": {
                "financial_exposure": {"value": 25000000, "evidence": "$25 million"},
                "decision_volume": {"value": 50000, "evidence": "50,000 applications"},
                "scope_expansion": {"value": "medium", "evidence": None},
                "reversibility": {"value": NOT_STATED, "evidence": None}
            }
        }
    }

    validated, issues = validate_extraction_response(mock_response)
    print("\n\nValidation Results:")
    print("-" * 40)
    print(f"Issues: {issues}")
    print(f"NOT_STATED factors: {len(validated.get('not_stated_factors', []))}")

    # Test full processing
    results = process_extraction_response(mock_response)
    print("\n\nFull Processing Results:")
    print("-" * 40)
    print(f"Overall Risk Level: {results['overall_assessment']['overall_risk_level']}")
    print(f"NOT_STATED count: {results['not_stated_summary']['count']}")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
