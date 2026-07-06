"""
OSFI E-23 Model Risk Management Processor

Generates risk-level-based governance requirements and compliance
recommendations for OSFI Guideline E-23 Model Risk Management assessments.
Used by the risk-dimension-based scoring pipeline (see
risk_dimension_extraction.py for factor/dimension scoring).
"""

import json
import os
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class OSFIE23Processor:
    """Processes OSFI E-23 Model Risk Management assessments."""

    def __init__(self, data_path: str = "data/osfi_e23_framework.json"):
        """
        Initialize the OSFI E-23 processor.

        Args:
            data_path: Path to the E-23 framework data file
        """
        self.data_path = data_path
        self.framework_data = self._load_framework_data()

    def _load_framework_data(self) -> Dict[str, Any]:
        """Load OSFI E-23 framework data."""
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Successfully loaded OSFI E-23 framework data from {self.data_path}")
                return data
            else:
                # Create default framework data if file doesn't exist
                logger.info("Creating default OSFI E-23 framework data")
                return self._create_default_framework_data()
        except Exception as e:
            logger.error(f"Error loading OSFI E-23 framework data: {str(e)}")
            return self._create_default_framework_data()

    def _create_default_framework_data(self) -> Dict[str, Any]:
        """Create default OSFI E-23 framework data structure."""
        return {
            "framework_name": "OSFI Guideline E-23 Model Risk Management",
            "effective_date": "2027-05-01",
            "scope": "Federally regulated financial institutions",
            "principles": [
                {
                    "id": "1.1",
                    "title": "Organizational Enablement",
                    "description": "Effective reporting structures and proper resourcing should enable sound model governance"
                },
                {
                    "id": "1.2",
                    "title": "MRM Framework",
                    "description": "The MRM framework should align risk-taking activities to strategic objectives and risk appetite"
                },
                {
                    "id": "1.3",
                    "title": "Use of Models",
                    "description": "Models should be appropriate for their business purposes"
                },
                {
                    "id": "2.1",
                    "title": "Model Identification",
                    "description": "Institutions should identify and track all models in use or recently decommissioned"
                },
                {
                    "id": "2.2",
                    "title": "Model Risk Rating",
                    "description": "Institutions should establish a model risk rating approach that assesses key dimensions of model risk"
                },
                {
                    "id": "2.3",
                    "title": "Risk Management Intensity",
                    "description": "The scope, scale, and intensity of MRM should be commensurate with the risk introduced by the model"
                },
                {
                    "id": "3.1",
                    "title": "Policies, Procedures, and Controls",
                    "description": "MRM policies, procedures, and controls should be robust, flexible, and lead to effective requirements applied across the model lifecycle"
                }
            ],
            "risk_rating_levels": [
                {"level": "Low", "description": "Minimal governance requirements", "score_range": [0, 25]},
                {"level": "Medium", "description": "Standard governance requirements", "score_range": [26, 50]},
                {"level": "High", "description": "Enhanced governance requirements", "score_range": [51, 75]},
                {"level": "Critical", "description": "Maximum governance requirements", "score_range": [76, 100]}
            ],
            "lifecycle_components": [
                "Model Design",
                "Model Review",
                "Model Deployment",
                "Model Monitoring",
                "Model Decommission"
            ]
        }

    def _generate_governance_requirements(self, risk_level: str, risk_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate governance requirements based on risk level (Low/Medium/High/Critical)."""
        # Base requirements (Low risk - Minimal governance)
        base_requirements = {
            "organizational": [
                "Assign qualified model owner with appropriate expertise",
                "Establish clear roles and responsibilities for model stakeholders",
                "Ensure adequate resources for model risk management"
            ],
            "documentation": [
                "Maintain basic model documentation",
                "Document model rationale and business purpose",
                "Record model limitations and assumptions"
            ],
            "review_approval": [
                "Conduct independent model review",
                "Obtain appropriate approval before deployment",
                "Document review findings and recommendations"
            ],
            "monitoring": [
                "Implement ongoing model performance monitoring",
                "Establish performance thresholds and alerts",
                "Monitor for model drift and degradation"
            ]
        }

        # Medium risk: Standard governance requirements
        if risk_level in ["Medium", "High", "Critical"]:
            base_requirements["organizational"].extend([
                "Establish formal model risk management structure",
                "Define escalation procedures for model issues"
            ])

            base_requirements["documentation"].extend([
                "Maintain comprehensive model documentation",
                "Document validation testing results and outcomes"
            ])

            base_requirements["review_approval"].extend([
                "Implement formal change management process",
                "Conduct periodic independent reviews",
                "Establish model revalidation triggers"
            ])

            base_requirements["monitoring"].extend([
                "Establish regular performance reporting",
                "Implement deviation thresholds and escalation procedures",
                "Document monitoring results and actions taken"
            ])

        # High risk: Enhanced governance requirements
        if risk_level in ["High", "Critical"]:
            base_requirements["organizational"].extend([
                "Establish Model Risk Committee oversight",
                "Assign senior management accountability",
                "Engage multi-disciplinary review team"
            ])

            base_requirements["documentation"].extend([
                "Provide detailed explainability documentation",
                "Document bias testing and mitigation measures",
                "Maintain comprehensive audit trail with version control"
            ])

            base_requirements["review_approval"].extend([
                "Require senior committee approval",
                "Conduct comprehensive periodic reviews",
                "Implement rigorous independent validation"
            ])

            base_requirements["monitoring"].extend([
                "Implement continuous monitoring with automated alerts",
                "Conduct frequent performance assessments",
                "Maintain documented contingency and rollback procedures"
            ])

        # Critical risk: Maximum governance requirements
        if risk_level == "Critical":
            base_requirements["organizational"].extend([
                "Require board-level oversight and reporting",
                "Establish dedicated model risk function with direct reporting lines",
                "Include legal, compliance, and ethics experts in governance"
            ])

            base_requirements["documentation"].extend([
                "Provide executive-level documentation and reporting",
                "Maintain real-time audit trail with immutable records",
                "Document scenario analysis and stress testing results"
            ])

            base_requirements["review_approval"].extend([
                "Require board-level or equivalent approval",
                "Engage external independent validation",
                "Conduct pre-deployment certification process"
            ])

            base_requirements["monitoring"].extend([
                "Implement real-time monitoring with immediate escalation",
                "Establish 24/7 model surveillance capability",
                "Maintain live contingency procedures with rapid response capability"
            ])

        # AI/ML specific requirements
        if risk_analysis["qualitative_indicators"].get("ai_ml_usage"):
            base_requirements["ai_ml_specific"] = [
                "Implement explainability controls appropriate to model complexity",
                "Conduct bias testing and fairness assessments",
                "Monitor for autonomous re-parametrization",
                "Establish human oversight checkpoints",
                "Document training data provenance and quality"
            ]

        # Third-party specific requirements
        if risk_analysis["qualitative_indicators"].get("third_party"):
            base_requirements["third_party"] = [
                "Conduct vendor due diligence and ongoing oversight",
                "Establish service level agreements with performance metrics",
                "Maintain vendor risk assessment documentation",
                "Ensure data security and privacy compliance",
                "Develop vendor contingency and exit strategies"
            ]

        return base_requirements

    def _generate_compliance_recommendations(self, risk_level: str, risk_analysis: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations based on assessment."""
        recommendations = []

        # Base recommendations
        recommendations.extend([
            "Establish comprehensive Model Risk Management framework aligned with OSFI E-23",
            "Implement risk-based approach to model governance",
            "Ensure model inventory includes all models with non-negligible risk"
        ])

        # Risk level specific recommendations (TYPE of governance, not frequencies)
        if risk_level == "Critical":
            recommendations.extend([
                "🚨 CRITICAL RISK: Obtain board-level approval before deployment",
                "Implement maximum governance controls and oversight structure",
                "Conduct external validation and independent review",
                "Establish dedicated Model Risk Committee with executive reporting",
                "Implement continuous real-time monitoring with immediate escalation capabilities"
            ])
        elif risk_level == "High":
            recommendations.extend([
                "⚠️ HIGH RISK: Require senior management approval and oversight",
                "Implement enhanced governance and oversight controls",
                "Conduct comprehensive independent model reviews",
                "Establish robust monitoring with escalation procedures and contingency planning"
            ])
        elif risk_level == "Medium":
            recommendations.extend([
                "📋 MODERATE RISK: Implement standard governance procedures and formal review processes",
                "Conduct regular periodic model reviews with documented outcomes",
                "Establish structured monitoring, reporting, and issue escalation procedures"
            ])
        else:  # Low
            recommendations.extend([
                "✅ LOWER RISK: Apply proportionate governance controls appropriate to risk level",
                "Conduct periodic model reviews with basic documentation",
                "Implement standard monitoring procedures with defined thresholds"
            ])

        # Specific recommendations based on risk factors
        if risk_analysis["qualitative_indicators"].get("ai_ml_usage"):
            recommendations.append("🤖 AI/ML: Implement explainability controls and bias testing procedures")

        if risk_analysis["qualitative_indicators"].get("third_party"):
            recommendations.append("🏢 Third-party: Establish vendor oversight and contingency procedures")

        if risk_analysis["quantitative_indicators"].get("financial_impact"):
            recommendations.append("💰 Financial: Implement enhanced capital and liquidity impact assessments")

        if risk_analysis["qualitative_indicators"].get("customer_impact"):
            recommendations.append("👥 Customer Impact: Establish customer protection and recourse procedures")

        return recommendations
