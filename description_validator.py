"""
Project Description Validator

Validates project descriptions for adequacy before AIA and OSFI E-23 framework assessments.
Ensures descriptions contain sufficient information across key areas required by both frameworks.
"""

import re
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ProjectDescriptionValidator:
    """Validates project descriptions for framework assessment readiness."""

    def __init__(self):
        """Initialize the validator with content area definitions."""
        self.content_areas = {
            "system_technology": {
                "name": "System/Technology Description",
                "keywords": [
                    "system", "technology", "platform", "software", "algorithm",
                    "model", "AI", "artificial intelligence", "ML", "machine learning",
                    "automated", "application", "tool", "solution", "infrastructure"
                ],
                "min_words": 15,
                "description": "Technical description of the system, technology, or model being assessed"
            },
            "business_purpose": {
                "name": "Business Purpose/Application",
                "keywords": [
                    "purpose", "business", "objective", "goal", "use case",
                    "application", "decision", "process", "function", "service",
                    "mission", "requirement", "need", "benefit", "value"
                ],
                "min_words": 10,
                "description": "Clear business purpose, objectives, and intended use cases"
            },
            "data_sources": {
                "name": "Data Sources/Types",
                "keywords": [
                    "data", "information", "dataset", "source", "input",
                    "database", "records", "transaction", "file", "feed",
                    "collection", "storage", "repository", "archive", "stream"
                ],
                "min_words": 10,
                "description": "Description of data sources, types, and data handling processes"
            },
            "impact_scope": {
                "name": "Impact/Risk Scope",
                "keywords": [
                    "impact", "affect", "customer", "client", "risk",
                    "consequence", "stakeholder", "user", "financial", "outcome",
                    "result", "influence", "effect", "harm", "benefit", "exposure"
                ],
                "min_words": 8,
                "description": "Who or what is impacted by the system and potential risks"
            },
            "decision_process": {
                "name": "Decision-Making Process",
                "keywords": [
                    "decision", "determine", "recommend", "approve", "process",
                    "workflow", "automated", "manual", "rule", "logic",
                    "criteria", "evaluation", "assessment", "judgment", "choice"
                ],
                "min_words": 8,
                "description": "How decisions are made, level of automation, and human oversight"
            },
            "technical_architecture": {
                "name": "Technical Architecture/Methodology",
                "keywords": [
                    "architecture", "methodology", "approach", "framework",
                    "infrastructure", "deployment", "integration", "design",
                    "implementation", "structure", "component", "module", "interface"
                ],
                "min_words": 8,
                "description": "Technical approach, methodology, or architectural considerations"
            }
        }

        # Minimum requirements for validation
        self.min_total_words = 100
        self.min_areas_covered = 3  # 50% of 6 areas

    def validate_description(self, description: str) -> Dict[str, Any]:
        """
        Validate a project description for framework assessment readiness.

        Args:
            description: The project description to validate

        Returns:
            Dict containing validation results, coverage analysis, and recommendations
        """
        if not description or not isinstance(description, str):
            return {
                "is_valid": False,
                "total_words": 0,
                "areas_covered": 0,
                "areas_missing": list(self.content_areas.keys()),
                "coverage_details": {},
                "validation_message": "Project description is required and cannot be empty.",
                "recommendations": ["Please provide a detailed project description covering the key areas listed below."]
            }

        # Clean and analyze the description
        cleaned_description = self._clean_description(description)
        word_count = len(cleaned_description.split())

        # Analyze coverage for each content area
        coverage_details = self._analyze_coverage(cleaned_description)

        # Determine which areas are covered
        covered_areas = [area for area, details in coverage_details.items() if details["covered"]]
        missing_areas = [area for area, details in coverage_details.items() if not details["covered"]]

        # Validate against minimum requirements
        is_valid = (
            word_count >= self.min_total_words and
            len(covered_areas) >= self.min_areas_covered
        )

        # Generate validation message and recommendations
        validation_message, recommendations = self._generate_feedback(
            is_valid, word_count, covered_areas, missing_areas, coverage_details
        )

        # CRITICAL FIX: Framework readiness must be consistent with is_valid
        # All frameworks require overall validation to pass before proceeding
        # This prevents contradictory results where is_valid=False but framework flags are True
        return {
            "is_valid": is_valid,
            "total_words": word_count,
            "areas_covered": len(covered_areas),
            "areas_missing": missing_areas,
            "coverage_details": coverage_details,
            "validation_message": validation_message,
            "recommendations": recommendations,
            "framework_readiness": {
                "aia_framework": is_valid,  # Must pass overall validation
                "osfi_e23_framework": is_valid,  # Must pass overall validation
                "combined_readiness": is_valid
            }
        }

    def _clean_description(self, description: str) -> str:
        """Clean and normalize the description for analysis."""
        # Convert to lowercase for keyword matching
        cleaned = description.lower()

        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    def _analyze_coverage(self, description: str) -> Dict[str, Any]:
        """Analyze coverage of each content area in the description."""
        coverage_details = {}

        for area_key, area_config in self.content_areas.items():
            # Count keyword matches
            keyword_matches = []
            for keyword in area_config["keywords"]:
                if keyword.lower() in description:
                    keyword_matches.append(keyword)

            # Extract sentences containing keywords for word count
            sentences = description.split('.')
            relevant_sentences = []
            for sentence in sentences:
                if any(keyword.lower() in sentence for keyword in area_config["keywords"]):
                    relevant_sentences.append(sentence.strip())

            # Count words in relevant content
            relevant_text = ' '.join(relevant_sentences)
            word_count = len(relevant_text.split()) if relevant_text else 0

            # Determine if area is adequately covered
            has_keywords = len(keyword_matches) > 0
            meets_word_minimum = word_count >= area_config["min_words"]
            covered = has_keywords and meets_word_minimum

            coverage_details[area_key] = {
                "name": area_config["name"],
                "covered": covered,
                "keyword_matches": keyword_matches,
                "relevant_word_count": word_count,
                "min_words_required": area_config["min_words"],
                "description": area_config["description"]
            }

        return coverage_details

    def _generate_feedback(self, is_valid: bool, word_count: int, covered_areas: List[str],
                          missing_areas: List[str], coverage_details: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Generate validation message and recommendations."""

        if is_valid:
            message = (
                f"✅ Project description is adequate for framework assessment. "
                f"Covered {len(covered_areas)}/6 required areas ({word_count} words total)."
            )
            recommendations = [
                "Description meets minimum requirements for both AIA and OSFI E-23 frameworks.",
                "You may proceed with framework assessments.",
                f"Areas covered: {', '.join([coverage_details[area]['name'] for area in covered_areas])}"
            ]
        else:
            # Detailed failure message
            areas_needed = self.min_areas_covered - len(covered_areas)
            words_needed = max(0, self.min_total_words - word_count)

            message = (
                f"❌ Insufficient project description for framework assessment. "
                f"Covered {len(covered_areas)}/{self.min_areas_covered} required areas "
                f"({word_count}/{self.min_total_words} minimum words)."
            )

            recommendations = []

            if words_needed > 0:
                recommendations.append(f"• Add approximately {words_needed} more words to provide sufficient detail")

            if areas_needed > 0:
                recommendations.append(f"• Address {areas_needed} additional content area(s) from the list below")

            recommendations.append("\n📋 MISSING CONTENT AREAS:")
            for area in missing_areas:
                area_info = coverage_details[area]
                recommendations.append(
                    f"   ❌ {area_info['name']}: {area_info['description']} "
                    f"(minimum {area_info['min_words_required']} words)"
                )

            if covered_areas:
                recommendations.append(f"\n✅ COVERED AREAS: {', '.join([coverage_details[area]['name'] for area in covered_areas])}")

            recommendations.extend([
                "\n💡 FRAMEWORK REQUIREMENTS:",
                "• AIA Framework: Requires description of system purpose, impact scope, and decision processes",
                "• OSFI E-23 Framework: Requires model details, business application, and risk considerations",
                "• Combined Assessment: Needs comprehensive coverage across technical, business, and risk domains"
            ])

        return message, recommendations

    def get_description_template(self) -> str:
        """Provide a template for adequate project descriptions."""
        template = """
PROJECT DESCRIPTION TEMPLATE

To ensure your description meets framework requirements, please address these areas:

1. SYSTEM/TECHNOLOGY DESCRIPTION ({min_words}+ words)
   - What type of system, technology, or model is this?
   - What technologies, algorithms, or methodologies are used?

2. BUSINESS PURPOSE/APPLICATION ({business_min}+ words)
   - What business problem does this solve?
   - What are the primary objectives and use cases?

3. DATA SOURCES/TYPES ({data_min}+ words)
   - What data sources are used?
   - What types of information are processed?

4. IMPACT/RISK SCOPE ({impact_min}+ words)
   - Who is affected by this system?
   - What are the potential impacts or risks?

5. DECISION-MAKING PROCESS ({decision_min}+ words)
   - How are decisions made by the system?
   - What level of automation vs human oversight exists?

6. TECHNICAL ARCHITECTURE/METHODOLOGY ({tech_min}+ words)
   - What is the technical approach or architecture?
   - How is the system deployed and integrated?

MINIMUM REQUIREMENTS:
• Total description: {total_min}+ words
• Cover at least {min_areas}/6 areas above
• Include specific, factual details (avoid vague descriptions)
        """.format(
            min_words=self.content_areas["system_technology"]["min_words"],
            business_min=self.content_areas["business_purpose"]["min_words"],
            data_min=self.content_areas["data_sources"]["min_words"],
            impact_min=self.content_areas["impact_scope"]["min_words"],
            decision_min=self.content_areas["decision_process"]["min_words"],
            tech_min=self.content_areas["technical_architecture"]["min_words"],
            total_min=self.min_total_words,
            min_areas=self.min_areas_covered
        )

        return template.strip()