"""
Data Extractors Module

Provides specialized data extraction utilities for AIA and OSFI E-23 assessments.
Extracted from server.py to reduce complexity and improve code organization.

This module contains helper methods for extracting, formatting, and processing
assessment data for report generation.
"""

from typing import Dict, Any, List
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor
import logging

logger = logging.getLogger(__name__)


class AIADataExtractor:
    """
    Data extractor for AIA (Algorithmic Impact Assessment) reports.

    Handles extraction of scores, impact levels, findings, and recommendations
    from AIA assessment results.
    """

    def __init__(self, aia_processor):
        """
        Initialize AIA data extractor.

        Args:
            aia_processor: AIAProcessor instance for accessing AIA-specific logic
        """
        self.aia_processor = aia_processor

    def extract_score(self, assessment_results: Dict[str, Any]) -> int:
        """Extract score from assessment results."""
        # Try different possible score field names
        if 'functional_risk_score' in assessment_results:
            return assessment_results['functional_risk_score']
        elif 'partialAssessment' in assessment_results:
            return assessment_results['partialAssessment'].get('currentScore', 0)
        elif 'currentScore' in assessment_results:
            return assessment_results['currentScore']
        elif 'rawImpactScore' in assessment_results:
            return assessment_results['rawImpactScore']
        else:
            return 0

    def extract_impact_level(self, assessment_results: Dict[str, Any]) -> str:
        """Extract impact level from assessment results."""
        # Try different possible impact level field names
        if 'likely_impact_level' in assessment_results:
            return assessment_results['likely_impact_level']
        elif 'partialAssessment' in assessment_results:
            return assessment_results['partialAssessment'].get('impactLevel', 'Level I')
        elif 'impactLevel' in assessment_results:
            return assessment_results['impactLevel']
        else:
            score = self.extract_score(assessment_results)
            level, _, _ = self.aia_processor.determine_impact_level(score)
            return f"Level {self._get_impact_level_roman(level)}"

    def _get_impact_level_roman(self, level: int) -> str:
        """Convert numeric impact level to Roman numeral."""
        roman_map = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
        return roman_map.get(level, 'I')

    def extract_key_findings(self, assessment_results: Dict[str, Any], project_description: str) -> List[str]:
        """Extract key findings from assessment results."""
        findings = []
        description_lower = project_description.lower()

        # Add findings based on system characteristics
        if any(term in description_lower for term in ['ai', 'machine learning', 'algorithm']):
            findings.append("System uses AI/ML algorithms requiring interpretability considerations")

        if any(term in description_lower for term in ['personal', 'sensitive', 'private', 'pii']):
            findings.append("System processes personal information requiring privacy safeguards")

        if any(term in description_lower for term in ['automated', 'without human review']):
            findings.append("Automated decision-making requires human oversight mechanisms")

        if any(term in description_lower for term in ['financial', 'economic', 'loan', 'credit']):
            findings.append("Financial decisions have significant economic impact on individuals")

        if any(term in description_lower for term in ['thousands', 'daily', 'real-time', 'high volume']):
            findings.append("High-volume processing requires robust monitoring systems")

        # Add findings from assessment results
        if 'planning_guidance' in assessment_results:
            guidance = assessment_results['planning_guidance']
            if isinstance(guidance, list) and len(guidance) > 0:
                findings.append("Specific compliance planning requirements identified")

        if 'critical_gaps' in assessment_results:
            gaps = assessment_results['critical_gaps']
            if isinstance(gaps, list) and len(gaps) > 0:
                findings.append("Critical information gaps require stakeholder input")

        # Default findings if none found
        if not findings:
            findings = [
                "System requires compliance with AIA framework requirements",
                "Risk mitigation measures should be implemented",
                "Regular monitoring and documentation needed"
            ]

        return findings[:6]  # Limit to 6 key findings

    def extract_recommendations(self, assessment_results: Dict[str, Any], score: int, impact_level: str) -> List[str]:
        """Extract recommendations from assessment results."""
        recommendations = []

        # Add recommendations from assessment results
        if 'planning_guidance' in assessment_results:
            guidance = assessment_results['planning_guidance']
            if isinstance(guidance, list):
                recommendations.extend(guidance[:4])  # Take first 4 guidance items

        # Add score-based recommendations
        if score >= 56:
            recommendations.extend([
                "Establish qualified oversight committee with external validation",
                "Implement comprehensive bias testing and mitigation procedures",
                "Conduct extensive stakeholder consultation process"
            ])
        elif score >= 31:
            recommendations.extend([
                "Implement enhanced oversight and monitoring procedures",
                "Establish regular bias testing and performance reviews",
                "Plan stakeholder engagement and consultation processes"
            ])
        else:
            recommendations.extend([
                "Implement standard monitoring and documentation procedures",
                "Establish clear decision-making audit trails",
                "Plan regular system performance reviews"
            ])

        # Remove duplicates and limit
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)

        return unique_recommendations[:8]  # Limit to 8 recommendations

    def extract_true_risk_factors(self, risk_analysis: Dict[str, Any]) -> List[str]:
        """Extract only TRUE risk factors from assessment."""
        factors = []

        # Quantitative indicators
        quant = risk_analysis.get("quantitative_indicators", {})
        if quant.get("financial_impact"):
            factors.append("Financial Impact: Model influences material financial decisions or exposures")
        if quant.get("large_transaction_volume"):
            factors.append("Large Transaction Volume: Model processes significant number of transactions")
        if quant.get("customer_impact"):
            factors.append("Customer Impact: Model directly affects customer outcomes or decisions")

        # Qualitative indicators
        qual = risk_analysis.get("qualitative_indicators", {})
        if qual.get("complex_methodology"):
            factors.append("Complex Methodology: Advanced analytical or computational techniques employed")
        if qual.get("ai_ml_usage"):
            factors.append("AI/ML Usage: Model utilizes artificial intelligence or machine learning algorithms")
        if qual.get("data_quality_concerns"):
            factors.append("Data Quality Sensitivity: Model performance significantly dependent on data quality")
        if qual.get("regulatory_sensitivity"):
            factors.append("Regulatory Sensitivity: Model outputs subject to regulatory scrutiny or reporting")

        return factors

    def get_assessment_disclaimer(self, assessment_results: Dict[str, Any]) -> str:
        """Get appropriate disclaimer based on assessment type."""
        if 'disclaimer' in assessment_results:
            return assessment_results['disclaimer']
        elif 'functional_risk_score' in assessment_results:
            return "⚠️ Early Indicator - Not Official Assessment. Based on functional characteristics only. Final assessment requires complete stakeholder input and official AIA process completion."
        else:
            return "This assessment is based on available project information and automated analysis. Final AIA compliance requires complete stakeholder input and official government review process."


class OSFIE23DataExtractor:
    """
    Data extractor for OSFI E-23 (Model Risk Management) reports.

    Handles extraction of risk levels, scores, governance requirements,
    and compliance checklists from OSFI E-23 assessment results.
    """

    def __init__(self, osfi_e23_processor):
        """
        Initialize OSFI E-23 data extractor.

        Args:
            osfi_e23_processor: OSFIE23Processor instance for accessing E-23-specific logic
        """
        self.osfi_e23_processor = osfi_e23_processor

    def extract_risk_level(self, assessment_results: Dict[str, Any]) -> str:
        """Extract risk level from E-23 assessment results."""
        return assessment_results.get("risk_level",
               assessment_results.get("risk_rating", "Medium"))

    def extract_risk_score(self, assessment_results: Dict[str, Any]) -> int:
        """Extract risk score from E-23 assessment results."""
        return assessment_results.get("risk_score",
               assessment_results.get("overall_score", 0))

    def extract_risk_analysis(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract risk analysis points from E-23 assessment results."""
        analysis_points = []

        # Extract from risk_analysis if available
        risk_analysis = assessment_results.get("risk_analysis", {})

        # Quantitative indicators
        quant_indicators = risk_analysis.get("quantitative_indicators", {})
        for indicator, present in quant_indicators.items():
            if present:
                indicator_text = indicator.replace('_', ' ').title()
                analysis_points.append(f"Quantitative Risk Factor: {indicator_text} identified")

        # Qualitative indicators
        qual_indicators = risk_analysis.get("qualitative_indicators", {})
        for indicator, present in qual_indicators.items():
            if present:
                indicator_text = indicator.replace('_', ' ').title()
                analysis_points.append(f"Qualitative Risk Factor: {indicator_text} identified")

        # Risk factor analysis if available
        if 'risk_factor_analysis' in assessment_results:
            factor_analysis = assessment_results['risk_factor_analysis']

            high_risk_factors = factor_analysis.get('high_risk_factors', [])
            for factor in high_risk_factors[:3]:  # Limit to top 3
                analysis_points.append(f"High Risk: {factor}")

            risk_interactions = factor_analysis.get('risk_interactions', [])
            for interaction in risk_interactions[:2]:  # Limit to top 2
                analysis_points.append(f"Risk Interaction: {interaction}")

        # Default analysis if none found
        if not analysis_points:
            analysis_points = [
                "Model risk assessment completed using OSFI E-23 methodology",
                "Risk factors evaluated across quantitative and qualitative dimensions",
                "Governance requirements determined based on risk profile"
            ]

        return analysis_points[:8]  # Limit to 8 analysis points

    def extract_governance_requirements(self, assessment_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract governance requirements from E-23 assessment results."""
        # Try to get governance requirements from assessment results
        governance_reqs = assessment_results.get("governance_requirements", {})

        if governance_reqs:
            return governance_reqs

        # Generate default governance requirements based on risk level
        risk_level = self.extract_risk_level(assessment_results)

        base_requirements = {
            "organizational": [
                "Assign qualified model owner with appropriate expertise",
                "Establish clear roles and responsibilities",
                "Ensure adequate resources for model risk management"
            ],
            "documentation": [
                "Maintain comprehensive model documentation",
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

        # Enhanced requirements for higher risk levels
        if risk_level in ["High", "Critical"]:
            base_requirements["organizational"].extend([
                "Establish Model Risk Committee oversight",
                "Assign senior management accountability"
            ])

            base_requirements["review_approval"].extend([
                "Require senior management approval",
                "Conduct quarterly comprehensive reviews"
            ])

            base_requirements["monitoring"].extend([
                "Implement real-time monitoring and alerting",
                "Maintain contingency and rollback procedures"
            ])

        return base_requirements

    def extract_recommendations(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract recommendations from E-23 assessment results."""
        recommendations = assessment_results.get("recommendations", [])

        if recommendations:
            return recommendations[:8]  # Limit to 8 recommendations

        # Generate default recommendations based on risk level
        risk_level = self.extract_risk_level(assessment_results)

        default_recommendations = [
            "Establish comprehensive Model Risk Management framework aligned with OSFI E-23",
            "Implement risk-based approach to model governance",
            "Ensure model inventory includes all models with non-negligible risk"
        ]

        if risk_level == "Critical":
            default_recommendations.extend([
                "🚨 CRITICAL: Obtain board-level approval before deployment",
                "Implement maximum governance controls and oversight",
                "Conduct external validation and independent review"
            ])
        elif risk_level == "High":
            default_recommendations.extend([
                "⚠️ HIGH RISK: Require senior management approval",
                "Implement enhanced governance and oversight controls",
                "Conduct quarterly comprehensive model reviews"
            ])
        elif risk_level == "Medium":
            default_recommendations.extend([
                "📋 MODERATE RISK: Implement standard governance procedures",
                "Conduct semi-annual model reviews"
            ])
        else:
            default_recommendations.extend([
                "✅ LOWER RISK: Apply proportionate governance controls",
                "Conduct annual model reviews"
            ])

        return default_recommendations

    def extract_lifecycle_info(self, assessment_results: Dict[str, Any]) -> str:
        """Extract lifecycle compliance information from E-23 assessment results."""
        if 'compliance_checklist' in assessment_results:
            checklist = assessment_results['compliance_checklist']
            completed_items = len([item for item in checklist if item.get('completed', False)])
            total_items = len(checklist)
            return f"Compliance checklist: {completed_items}/{total_items} items completed. Review lifecycle requirements and ensure all mandatory items are addressed before model deployment."

        if 'current_stage' in assessment_results:
            current_stage = assessment_results['current_stage']
            return f"Model is currently in {current_stage} stage. Ensure all stage-specific requirements are met before proceeding to the next lifecycle phase."

        return "Model lifecycle compliance should be evaluated across all five stages: Design, Review, Deployment, Monitoring, and Decommission. Ensure appropriate governance controls are applied at each stage."

    def extract_business_rationale(self, assessment_results: Dict[str, Any], project_description: str) -> str:
        """Extract business rationale for E-23 model."""
        description_lower = project_description.lower()

        # Generate business rationale based on project characteristics
        if any(term in description_lower for term in ['risk management', 'credit risk', 'market risk']):
            return "This model supports risk management objectives by providing quantitative risk assessments to inform business decisions and regulatory compliance requirements."
        elif any(term in description_lower for term in ['fraud', 'detection', 'prevention']):
            return "This model enhances fraud detection capabilities to protect the institution and customers from financial losses while maintaining operational efficiency."
        elif any(term in description_lower for term in ['pricing', 'loan', 'credit']):
            return "This model supports pricing and credit decision-making to optimize risk-adjusted returns while ensuring fair and consistent treatment of customers."
        elif any(term in description_lower for term in ['regulatory', 'compliance', 'reporting']):
            return "This model supports regulatory compliance and reporting requirements while improving operational efficiency and decision-making accuracy."
        else:
            return "This model supports business objectives by automating decision-making processes, improving operational efficiency, and enhancing risk management capabilities."

    def extract_key_risk_factors(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract key risk factors from assessment results."""
        risk_factors = []

        # From assessment results if available
        if 'quantitative_factors' in assessment_results:
            quant_factors = assessment_results['quantitative_factors']
            if isinstance(quant_factors, dict):
                for factor, value in quant_factors.items():
                    if value:  # If factor is present/true
                        risk_factors.append(f"Quantitative factor: {factor.replace('_', ' ').title()}")

        # From qualitative factors
        if 'qualitative_factors' in assessment_results:
            qual_factors = assessment_results['qualitative_factors']
            if isinstance(qual_factors, dict):
                for factor, value in qual_factors.items():
                    if value:  # If factor is present/true
                        risk_factors.append(f"Qualitative factor: {factor.replace('_', ' ').title()}")

        # Default risk factors if none found
        if not risk_factors:
            risk_factors = [
                "Model complexity and interpretability requirements",
                "Data quality and governance considerations",
                "Business impact and operational criticality",
                "Regulatory compliance and oversight requirements"
            ]

        return risk_factors[:8]  # Limit to top 8

    def extract_immediate_actions(self, assessment_results: Dict[str, Any], risk_level: str) -> List[str]:
        """Extract immediate actions based on risk level."""
        actions = [
            "Complete model definition and scope documentation",
            "Assign clear model ownership and accountability",
            "Document current model development status and gaps"
        ]

        if risk_level in ["High", "Critical"]:
            actions.extend([
                "Establish independent validation team immediately",
                "Implement enhanced monitoring and controls",
                "Schedule executive briefing on model risk"
            ])
        elif risk_level == "Medium":
            actions.extend([
                "Plan validation team structure and resources",
                "Design monitoring framework requirements",
                "Schedule stakeholder alignment meetings"
            ])

        return actions

    def extract_short_term_goals(self, assessment_results: Dict[str, Any], risk_level: str) -> List[str]:
        """Extract short-term goals (3-6 months)."""
        goals = [
            "Complete comprehensive model validation",
            "Implement monitoring and alerting framework",
            "Establish ongoing governance processes"
        ]

        if risk_level in ["High", "Critical"]:
            goals.extend([
                "Conduct independent third-party validation",
                "Implement advanced model testing scenarios",
                "Establish board-level reporting framework"
            ])

        return goals

    def extract_long_term_objectives(self, assessment_results: Dict[str, Any], risk_level: str) -> List[str]:
        """Extract long-term objectives (6+ months)."""
        objectives = [
            "Achieve full OSFI E-23 compliance certification",
            "Integrate model into enterprise risk framework",
            "Establish continuous improvement processes"
        ]

        if risk_level in ["High", "Critical"]:
            objectives.extend([
                "Implement advanced model risk analytics",
                "Establish challenger model framework",
                "Achieve automated compliance monitoring"
            ])

        return objectives

    def extract_scoring_details(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ACTUAL scoring breakdown from assessment results using real OSFI E-23 calculation logic."""
        scoring_details = {
            "quantitative_breakdown": {},
            "qualitative_breakdown": {},
            "amplification_applied": False,
            "amplification_details": {},
            "calculation_method": "actual"
        }

        # Try to get actual risk analysis data first
        risk_analysis = assessment_results.get('risk_analysis', {})

        if risk_analysis:
            # Extract ACTUAL quantitative indicators and scores
            quant_indicators = risk_analysis.get('quantitative_indicators', {})

            for indicator, present in quant_indicators.items():
                if present:
                    scoring_details["quantitative_breakdown"][indicator] = {
                        "score": 10,  # Each quantitative indicator = 10 points
                        "reason": self._get_osfi_quantitative_reason(indicator),
                        "present": True
                    }

            # Extract ACTUAL qualitative indicators and scores
            qual_indicators = risk_analysis.get('qualitative_indicators', {})

            for indicator, present in qual_indicators.items():
                if present:
                    scoring_details["qualitative_breakdown"][indicator] = {
                        "score": 8,  # Each qualitative indicator = 8 points
                        "reason": self._get_osfi_qualitative_reason(indicator),
                        "present": True
                    }

            # Calculate actual multipliers applied
            quant_score = risk_analysis.get('quantitative_score', 0)
            qual_score = risk_analysis.get('qualitative_score', 0)
            base_score = quant_score + qual_score
            final_score = self.extract_risk_score(assessment_results)

            if base_score > 0:
                actual_multiplier = final_score / base_score
                if actual_multiplier > 1.05:  # More than 5% increase indicates amplification
                    scoring_details["amplification_applied"] = True
                    scoring_details["amplification_details"] = {
                        "factor": round(actual_multiplier, 2),
                        "base_score": base_score,
                        "final_score": final_score,
                        "reason": self._determine_amplification_reason(quant_indicators, qual_indicators),
                        "triggering_factors": self._get_actual_amplification_triggers(quant_indicators, qual_indicators)
                    }
        else:
            # Fallback to inference if no risk_analysis available
            scoring_details = self._infer_scoring_details_from_assessment(assessment_results)
            scoring_details["calculation_method"] = "inferred"

        return scoring_details

    def _get_osfi_quantitative_reason(self, indicator: str) -> str:
        """Get official OSFI E-23 reasons for quantitative indicators."""
        reasons = {
            "high_volume": "High transaction/decision volume amplifies potential model impact",
            "financial_impact": "Direct financial decisions create significant loss potential",
            "customer_facing": "Customer-impacting decisions require enhanced oversight",
            "revenue_critical": "Revenue-critical functions present business continuity risks",
            "regulatory_impact": "Regulatory exposure requires compliance-grade governance"
        }
        return reasons.get(indicator, f"{indicator.replace('_', ' ').title()} contributes to operational risk")

    def _get_osfi_qualitative_reason(self, indicator: str) -> str:
        """Get official OSFI E-23 reasons for qualitative indicators."""
        reasons = {
            "ai_ml_usage": "AI/ML models present interpretability and bias validation challenges",
            "high_complexity": "Complex models are difficult to validate and monitor effectively",
            "autonomous_decisions": "Autonomous systems reduce human oversight and intervention ability",
            "black_box": "Black-box models limit explainability and audit capability",
            "third_party": "Third-party dependencies introduce external risk vectors",
            "data_sensitive": "Sensitive data processing requires enhanced privacy controls",
            "real_time": "Real-time processing limits validation and intervention windows",
            "customer_impact": "Direct customer impact requires fairness and bias controls"
        }
        return reasons.get(indicator, f"{indicator.replace('_', ' ').title()} contributes to model risk profile")

    def _determine_amplification_reason(self, quant_indicators: dict, qual_indicators: dict) -> str:
        """Determine why amplification was applied based on actual indicator combinations."""
        reasons = []

        if quant_indicators.get("financial_impact") and qual_indicators.get("ai_ml_usage"):
            reasons.append("AI/ML usage in financial decision-making (+30%)")
        if quant_indicators.get("customer_facing") and qual_indicators.get("autonomous_decisions"):
            reasons.append("Autonomous customer-facing decisions (+20%)")
        if qual_indicators.get("black_box") and quant_indicators.get("regulatory_impact"):
            reasons.append("Black-box models with regulatory impact (+25%)")
        if qual_indicators.get("third_party") and quant_indicators.get("revenue_critical"):
            reasons.append("Third-party dependencies in critical systems (+15%)")

        return "; ".join(reasons) if reasons else "High-risk factor combination detected"

    def _get_actual_amplification_triggers(self, quant_indicators: dict, qual_indicators: dict) -> list:
        """Get actual amplification triggers that were applied."""
        triggers = []

        if quant_indicators.get("financial_impact") and qual_indicators.get("ai_ml_usage"):
            triggers.append("Financial Impact + AI/ML Usage")
        if quant_indicators.get("customer_facing") and qual_indicators.get("autonomous_decisions"):
            triggers.append("Customer Facing + Autonomous Decisions")
        if qual_indicators.get("black_box") and quant_indicators.get("regulatory_impact"):
            triggers.append("Black Box + Regulatory Impact")
        if qual_indicators.get("third_party") and quant_indicators.get("revenue_critical"):
            triggers.append("Third Party + Revenue Critical")

        return triggers

    def _infer_scoring_details_from_assessment(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Infer scoring details when detailed breakdown is not available."""
        risk_score = self.extract_risk_score(assessment_results)
        risk_level = self.extract_risk_level(assessment_results)

        # Create plausible scoring breakdown based on risk level and score
        scoring_details = {
            "quantitative_breakdown": {},
            "qualitative_breakdown": {},
            "amplification_applied": False,
            "amplification_details": {}
        }

        # Infer likely quantitative factors based on risk level
        quant_base_score = min(risk_score * 0.6, 45)  # ~60% from quantitative
        scoring_details["quantitative_breakdown"] = {
            "financial_impact": {
                "score": int(quant_base_score * 0.4),
                "reason": "Significant financial decisions affected by model outputs",
                "present": True
            },
            "operational_criticality": {
                "score": int(quant_base_score * 0.35),
                "reason": "Model is critical to core business operations",
                "present": True
            },
            "portfolio_size": {
                "score": int(quant_base_score * 0.25),
                "reason": "Large portfolio size increases potential impact of model errors",
                "present": True
            }
        }

        # Infer likely qualitative factors based on risk level
        qual_base_score = risk_score - quant_base_score
        scoring_details["qualitative_breakdown"] = {
            "ai_ml_usage": {
                "score": int(qual_base_score * 0.5),
                "reason": "AI/ML models present inherent interpretability and bias risks",
                "present": True
            },
            "model_complexity": {
                "score": int(qual_base_score * 0.3),
                "reason": "Complex models are harder to validate and control",
                "present": True
            },
            "explainability": {
                "score": int(qual_base_score * 0.2),
                "reason": "Limited explainability reduces oversight effectiveness",
                "present": True
            }
        }

        # Add amplification for High/Critical risk levels
        if risk_level in ["High", "Critical"]:
            scoring_details["amplification_applied"] = True
            scoring_details["amplification_details"] = {
                "factor": 1.2 if risk_level == "High" else 1.4,
                "reason": f"High-risk factor combinations typical of {risk_level} risk models",
                "triggering_factors": ["AI/ML + Financial Impact", "High Complexity + Large Portfolio"]
            }

        return scoring_details

    def extract_quantitative_factors(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract quantitative risk factors from assessment results."""
        factors = []
        risk_analysis = assessment_results.get("risk_analysis", {})
        quant_indicators = risk_analysis.get("quantitative_indicators", {})

        factor_descriptions = {
            'high_volume': "High transaction volume requiring robust processing capabilities",
            'financial_impact': "Significant financial impact on institution and customers",
            'customer_facing': "Direct customer impact requiring enhanced controls",
            'revenue_critical': "Revenue-critical application with business continuity implications",
            'regulatory_impact': "Regulatory compliance and reporting dependencies"
        }

        for factor, present in quant_indicators.items():
            if present and factor in factor_descriptions:
                factors.append(factor_descriptions[factor])

        if not factors:
            factors = [
                "Standard operational impact assessment completed",
                "Financial materiality evaluated based on model usage",
                "Customer impact scope determined"
            ]

        return factors

    def extract_qualitative_factors(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract qualitative risk factors from assessment results."""
        factors = []
        risk_analysis = assessment_results.get("risk_analysis", {})
        qual_indicators = risk_analysis.get("qualitative_indicators", {})

        factor_descriptions = {
            'ai_ml_usage': "AI/ML technology requiring specialized validation and monitoring",
            'high_complexity': "High model complexity increasing validation requirements",
            'autonomous_decisions': "Autonomous decision-making with limited human oversight",
            'black_box': "Limited model explainability and transparency",
            'third_party': "Third-party model dependencies requiring vendor oversight",
            'data_sensitive': "Sensitive data processing requiring enhanced controls",
            'real_time': "Real-time processing with immediate decision impact",
            'customer_impact': "Direct customer decision impact requiring fairness controls"
        }

        for factor, present in qual_indicators.items():
            if present and factor in factor_descriptions:
                factors.append(factor_descriptions[factor])

        if not factors:
            factors = [
                "Standard model complexity assessment completed",
                "Technology risk evaluation performed",
                "Operational risk factors identified"
            ]

        return factors

    def extract_risk_interactions(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract risk interactions and amplification factors."""
        interactions = []

        if 'risk_factor_analysis' in assessment_results:
            factor_analysis = assessment_results['risk_factor_analysis']
            risk_interactions = factor_analysis.get('risk_interactions', [])
            interactions.extend(risk_interactions)

        if not interactions:
            interactions = [
                "Risk factor interactions evaluated for amplification effects",
                "Combined risk scenarios assessed for governance implications",
                "Risk mitigation strategies aligned with interaction patterns"
            ]

        return interactions

    def extract_organizational_structure(self, assessment_results: Dict[str, Any]) -> Dict[str, str]:
        """Extract organizational structure from assessment results."""
        if 'governance_structure' in assessment_results:
            return assessment_results['governance_structure']

        # Generate default organizational structure
        risk_level = self.extract_risk_level(assessment_results)

        base_structure = {
            "model_owner": "Business unit responsible for model outcomes and business rationale",
            "model_developer": "Technical team or vendor responsible for model development and maintenance",
            "model_reviewer": "Independent validation team responsible for model review and testing",
            "model_approver": f"Approval authority as per risk level: {self.osfi_e23_processor._determine_approval_authority(risk_level)}"
        }

        if risk_level in ["High", "Critical"]:
            base_structure.update({
                "model_risk_committee": "Senior committee providing oversight and governance for model risk",
                "compliance_officer": "Compliance function ensuring adherence to regulatory requirements"
            })

        if risk_level == "Critical":
            base_structure.update({
                "board_oversight": "Board of Directors providing oversight for critical models",
                "external_validator": "Independent third-party validation for critical model components"
            })

        return base_structure

    def extract_policies_procedures(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract policies and procedures requirements."""
        policies = [
            "Model Risk Management Policy defining roles, responsibilities, and governance framework",
            "Model Development Standards specifying technical and documentation requirements",
            "Model Review and Validation Procedures for independent assessment processes",
            "Model Approval Procedures defining authority levels and approval criteria",
            "Model Monitoring and Performance Management Procedures",
            "Model Change Management Procedures for updates and modifications",
            "Model Decommission Procedures for retirement and replacement processes"
        ]

        risk_level = self.extract_risk_level(assessment_results)

        if risk_level in ["High", "Critical"]:
            policies.extend([
                "Enhanced Documentation Standards for complex and high-risk models",
                "Bias Testing and Fairness Assessment Procedures for AI/ML models",
                "Third-party Model Oversight Procedures for vendor-developed models"
            ])

        return policies

    def extract_design_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model design requirements."""
        requirements = [
            "Clear organizational rationale and business case documentation",
            "Comprehensive data quality and governance standards",
            "Appropriate model development methodology and documentation",
            "Performance criteria and success metrics definition",
            "Model limitations and assumptions documentation"
        ]

        risk_level = self.extract_risk_level(assessment_results)

        if risk_level in ["High", "Critical"]:
            requirements.extend([
                "Detailed explainability and interpretability analysis",
                "Comprehensive bias and fairness assessment",
                "Regulatory compliance and impact analysis"
            ])

        return requirements

    def extract_review_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model review and validation requirements."""
        requirements = [
            "Independent conceptual soundness review",
            "Comprehensive performance evaluation and testing",
            "Risk rating confirmation and documentation",
            "Model documentation completeness review",
            "Limitation and mitigation strategy assessment"
        ]

        risk_level = self.extract_risk_level(assessment_results)

        if risk_level in ["High", "Critical"]:
            requirements.extend([
                "Enhanced validation testing including stress scenarios",
                "External validation for critical model components",
                "Regulatory pre-approval consultation where applicable"
            ])

        return requirements

    def extract_deployment_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model deployment requirements."""
        requirements = [
            "Quality assurance and change control processes",
            "Production environment testing and validation",
            "Stakeholder coordination and communication",
            "Risk assessment completion and sign-off",
            "Monitoring framework setup and configuration"
        ]

        risk_level = self.extract_risk_level(assessment_results)

        if risk_level in ["High", "Critical"]:
            requirements.extend([
                "Enhanced production testing with parallel run validation",
                "Real-time monitoring and alerting system activation",
                "Contingency and rollback procedure implementation"
            ])

        return requirements

    def extract_monitoring_framework(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract monitoring framework details."""
        risk_level = self.extract_risk_level(assessment_results)

        frequency_mapping = {
            "Low": "Quarterly monitoring with annual comprehensive review",
            "Medium": "Monthly monitoring with quarterly comprehensive review",
            "High": "Weekly monitoring with monthly comprehensive review",
            "Critical": "Daily monitoring with weekly comprehensive review"
        }

        base_kpis = [
            "Model performance accuracy and stability metrics",
            "Prediction quality and consistency indicators",
            "Data quality and completeness measures",
            "Usage patterns and volume statistics"
        ]

        if risk_level in ["High", "Critical"]:
            base_kpis.extend([
                "Bias and fairness metrics for protected characteristics",
                "Explainability and transparency measures",
                "Regulatory compliance indicators",
                "Customer impact and complaint metrics"
            ])

        return {
            "frequency": frequency_mapping.get(risk_level, "Monthly monitoring"),
            "kpis": base_kpis
        }

    def extract_decommission_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model decommission requirements."""
        return [
            "Formal model retirement process and timeline",
            "Stakeholder notification and communication plan",
            "Documentation retention and archival procedures",
            "Downstream system impact assessment and mitigation",
            "Third-party model considerations and vendor coordination",
            "Data retention and disposal procedures",
            "Replacement model transition planning"
        ]

    def extract_documentation_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract documentation requirements."""
        risk_level = self.extract_risk_level(assessment_results)

        base_docs = [
            "Model rationale and business purpose documentation",
            "Data sources, quality standards, and governance documentation",
            "Model methodology, assumptions, and limitations documentation",
            "Performance metrics, validation results, and testing documentation",
            "Risk assessment and mitigation strategy documentation"
        ]

        if risk_level in ["High", "Critical"]:
            base_docs.extend([
                "Detailed explainability and interpretability documentation",
                "Comprehensive bias testing and mitigation measures documentation",
                "Audit trail and change management documentation",
                "Contingency planning and rollback procedures documentation"
            ])

        if risk_level == "Critical":
            base_docs.extend([
                "Board presentation and approval documentation",
                "External validation and independent review reports",
                "Regulatory compliance attestations and correspondence",
                "Continuous monitoring dashboards and alert configurations"
            ])

        return base_docs

    def extract_compliance_checklist(self, assessment_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract compliance checklist from assessment results."""
        if 'compliance_checklist' in assessment_results:
            return assessment_results['compliance_checklist']

        # Generate default compliance checklist
        risk_level = self.extract_risk_level(assessment_results)

        base_checklist = [
            {"item": "Model inventory registration", "required": True, "stage": "design", "completed": False},
            {"item": "Risk rating assignment", "required": True, "stage": "design", "completed": False},
            {"item": "Model documentation completion", "required": True, "stage": "design", "completed": False},
            {"item": "Independent model review", "required": True, "stage": "review", "completed": False},
            {"item": "Formal model approval", "required": True, "stage": "review", "completed": False},
            {"item": "Production deployment testing", "required": True, "stage": "deployment", "completed": False},
            {"item": "Monitoring system activation", "required": True, "stage": "deployment", "completed": False},
            {"item": "Regular performance monitoring", "required": True, "stage": "monitoring", "completed": False}
        ]

        if risk_level in ["High", "Critical"]:
            base_checklist.extend([
                {"item": "Bias and fairness testing", "required": True, "stage": "design", "completed": False},
                {"item": "Explainability documentation", "required": True, "stage": "design", "completed": False},
                {"item": "Senior management approval", "required": True, "stage": "review", "completed": False},
                {"item": "Enhanced monitoring setup", "required": True, "stage": "deployment", "completed": False}
            ])

        if risk_level == "Critical":
            base_checklist.extend([
                {"item": "Board-level approval", "required": True, "stage": "review", "completed": False},
                {"item": "External validation", "required": True, "stage": "review", "completed": False},
                {"item": "Real-time monitoring activation", "required": True, "stage": "deployment", "completed": False}
            ])

        return base_checklist

    def extract_implementation_timeline(self, assessment_results: Dict[str, Any]) -> Dict[str, str]:
        """Extract implementation timeline from assessment results."""
        if 'implementation_timeline' in assessment_results:
            return assessment_results['implementation_timeline']

        # Generate default timeline based on risk level
        risk_level = self.extract_risk_level(assessment_results)

        timeline_mapping = {
            "Low": {
                "design_phase": "4-6 weeks",
                "review_phase": "2-3 weeks",
                "deployment_phase": "2-3 weeks",
                "monitoring_setup": "1-2 weeks"
            },
            "Medium": {
                "design_phase": "6-8 weeks",
                "review_phase": "3-4 weeks",
                "deployment_phase": "3-4 weeks",
                "monitoring_setup": "2-3 weeks"
            },
            "High": {
                "design_phase": "8-12 weeks",
                "review_phase": "4-6 weeks",
                "deployment_phase": "4-5 weeks",
                "monitoring_setup": "3-4 weeks"
            },
            "Critical": {
                "design_phase": "12-16 weeks",
                "review_phase": "6-8 weeks",
                "external_validation": "4-6 weeks",
                "deployment_phase": "5-7 weeks",
                "monitoring_setup": "4-5 weeks"
            }
        }

        return timeline_mapping.get(risk_level, timeline_mapping["Medium"])

    def get_assessment_disclaimer(self, assessment_results: Dict[str, Any]) -> str:
        """Get appropriate disclaimer for E-23 assessment."""
        return "This OSFI E-23 model risk assessment is based on available project information and automated analysis. Final compliance with OSFI Guideline E-23 requires comprehensive stakeholder input, independent validation, and appropriate governance oversight. This assessment should be reviewed and validated by qualified model risk management professionals before making final risk management decisions."
