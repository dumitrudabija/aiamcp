"""
OSFI E-23 Model Risk Management Processor

Handles the core logic for processing OSFI Guideline E-23 Model Risk Management
assessments for federally regulated financial institutions in Canada.
"""

import json
import os
import re
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime

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
        self.risk_factors = self._initialize_risk_factors()
        self.lifecycle_components = self._initialize_lifecycle_components()
        
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
    
    def _initialize_risk_factors(self) -> Dict[str, List[str]]:
        """Initialize risk assessment factors based on OSFI E-23."""
        return {
            "quantitative_factors": [
                "Portfolio size and importance",
                "Financial impact potential",
                "Operational impact potential",
                "Customer base size affected",
                "Transaction volume processed",
                "Revenue dependency",
                "Capital allocation influence"
            ],
            "qualitative_factors": [
                "Business use and purpose criticality",
                "Model complexity level",
                "Level of autonomy",
                "Data input reliability",
                "Customer impact severity",
                "Regulatory risk exposure",
                "Reputational risk potential",
                "AI/ML technology usage",
                "Third-party dependencies",
                "Explainability requirements"
            ]
        }
    
    def _initialize_lifecycle_components(self) -> Dict[str, Dict[str, Any]]:
        """Initialize model lifecycle components with requirements."""
        return {
            "design": {
                "name": "Model Design",
                "requirements": [
                    "Clear organizational rationale",
                    "Data quality and accuracy standards",
                    "Appropriate development processes",
                    "Explainability considerations for AI/ML",
                    "Bias and ethical implications assessment"
                ],
                "deliverables": [
                    "Model rationale document",
                    "Data governance documentation",
                    "Development methodology documentation",
                    "Performance criteria definition"
                ]
            },
            "review": {
                "name": "Model Review",
                "requirements": [
                    "Independent assessment process",
                    "Conceptual soundness validation",
                    "Performance evaluation",
                    "Risk rating confirmation",
                    "Documentation review"
                ],
                "deliverables": [
                    "Model review report",
                    "Risk assessment documentation",
                    "Approval recommendation",
                    "Limitation and mitigation documentation"
                ]
            },
            "deployment": {
                "name": "Model Deployment",
                "requirements": [
                    "Quality and change control processes",
                    "Production environment testing",
                    "Stakeholder coordination",
                    "Risk assessment completion",
                    "Monitoring framework setup"
                ],
                "deliverables": [
                    "Deployment procedures documentation",
                    "Production testing results",
                    "Monitoring configuration",
                    "Exception handling procedures"
                ]
            },
            "monitoring": {
                "name": "Model Monitoring",
                "requirements": [
                    "Defined monitoring standards",
                    "Performance threshold setting",
                    "Drift detection for AI/ML models",
                    "Escalation procedures",
                    "Contingency planning"
                ],
                "deliverables": [
                    "Monitoring framework documentation",
                    "Performance dashboards",
                    "Alert and escalation procedures",
                    "Contingency plans"
                ]
            },
            "decommission": {
                "name": "Model Decommission",
                "requirements": [
                    "Formal retirement process",
                    "Stakeholder notification",
                    "Documentation retention",
                    "Downstream impact monitoring",
                    "Third-party model considerations"
                ],
                "deliverables": [
                    "Decommission plan",
                    "Stakeholder notifications",
                    "Archive documentation",
                    "Impact assessment report"
                ]
            }
        }
    
    def assess_model_risk(self, project_name: str, project_description: str) -> Dict[str, Any]:
        """
        Comprehensive model risk assessment based on OSFI E-23 framework.

        Includes detailed risk scoring breakdown and individual factor analysis
        (merged from former Step 4 - generate_risk_rating).

        Args:
            project_name: Name of the model/project
            project_description: Detailed description of the model

        Returns:
            Complete model risk assessment with detailed breakdown
        """
        logger.info(f"Assessing model risk for: {project_name}")

        # Analyze project description for risk indicators
        risk_analysis = self._analyze_risk_factors(project_description)

        # Calculate risk score
        risk_score = self._calculate_risk_score(risk_analysis)

        # Determine risk rating level
        risk_level, risk_description = self._determine_risk_level(risk_score)

        # Calculate detailed risk scores (merged from Step 4)
        quantitative_factors = risk_analysis["quantitative_indicators"]
        qualitative_factors = risk_analysis["qualitative_indicators"]
        risk_scores = self._calculate_detailed_risk_scores(quantitative_factors, qualitative_factors)

        # Generate risk factor analysis (merged from Step 4)
        risk_factor_analysis = self._analyze_individual_risk_factors(quantitative_factors, qualitative_factors)

        # Generate governance requirements
        governance_requirements = self._generate_governance_requirements(risk_level, risk_analysis)

        # Generate compliance recommendations
        recommendations = self._generate_compliance_recommendations(risk_level, risk_analysis)

        return {
            "project_name": project_name,
            "project_description": project_description,
            "assessment_date": datetime.now().isoformat(),
            "framework": "OSFI Guideline E-23 Model Risk Management",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_description": risk_description,
            "risk_analysis": risk_analysis,
            "risk_scores": risk_scores,  # NEW: Detailed scoring breakdown (from Step 4)
            "risk_factor_analysis": risk_factor_analysis,  # NEW: Individual factor analysis (from Step 4)
            "governance_requirements": governance_requirements,
            "recommendations": recommendations,
            "compliance_status": "Assessment Complete - Implementation Required",
            "compliance_warning": "⚠️ CRITICAL COMPLIANCE NOTICE: This assessment is based on automated analysis of project description. All results must be validated by qualified model risk professionals and approved by appropriate governance authorities before use for regulatory compliance. Risk assessments must be based on factual, verifiable project information - not AI interpretation. See OSFI_E23_COMPLIANCE_GUIDANCE.md for detailed requirements."
        }
    
    def _analyze_risk_factors(self, project_description: str) -> Dict[str, Any]:
        """Analyze project description for OSFI E-23 risk factors."""
        description_lower = project_description.lower()
        
        # Quantitative risk indicators
        quantitative_indicators = {
            'high_volume': any(term in description_lower for term in ['millions', 'thousands', 'large scale', 'high volume', 'enterprise-wide']),
            'financial_impact': any(term in description_lower for term in ['loan', 'credit', 'pricing', 'capital', 'risk management', 'trading', 'investment']),
            'customer_facing': any(term in description_lower for term in ['customer', 'client', 'retail', 'commercial', 'public']),
            'revenue_critical': any(term in description_lower for term in ['revenue', 'profit', 'income', 'business critical', 'core business']),
            'regulatory_impact': any(term in description_lower for term in ['regulatory', 'compliance', 'capital adequacy', 'stress testing', 'reporting'])
        }
        
        # Qualitative risk indicators  
        qualitative_indicators = {
            'ai_ml_usage': any(term in description_lower for term in ['ai', 'artificial intelligence', 'machine learning', 'neural network', 'deep learning']),
            'high_complexity': any(term in description_lower for term in ['complex', 'sophisticated', 'advanced', 'ensemble', 'multi-model']),
            'autonomous_decisions': any(term in description_lower for term in ['autonomous', 'automated decision', 'without human review', 'real-time decision']),
            'black_box': any(term in description_lower for term in ['black box', 'unexplainable', 'opaque', 'proprietary algorithm']),
            'third_party': any(term in description_lower for term in ['third party', 'vendor', 'external', 'outsourced', 'cloud-based']),
            'data_sensitive': any(term in description_lower for term in ['personal data', 'sensitive', 'confidential', 'private information']),
            'real_time': any(term in description_lower for term in ['real-time', 'real time', 'immediate', 'instant', 'live']),
            'customer_impact': any(term in description_lower for term in ['customer decision', 'client impact', 'individual outcome', 'personal finance'])
        }
        
        # Calculate factor scores
        quantitative_score = sum(1 for indicator in quantitative_indicators.values() if indicator) * 10
        qualitative_score = sum(1 for indicator in qualitative_indicators.values() if indicator) * 8
        
        return {
            "quantitative_indicators": quantitative_indicators,
            "qualitative_indicators": qualitative_indicators,
            "quantitative_score": quantitative_score,
            "qualitative_score": qualitative_score,
            "total_indicators": sum(1 for indicator in {**quantitative_indicators, **qualitative_indicators}.values() if indicator)
        }
    
    def _calculate_risk_score(self, risk_analysis: Dict[str, Any]) -> int:
        """Calculate overall risk score based on analysis."""
        base_score = risk_analysis["quantitative_score"] + risk_analysis["qualitative_score"]
        
        # Apply multipliers for critical combinations
        multiplier = 1.0
        
        quant_indicators = risk_analysis["quantitative_indicators"]
        qual_indicators = risk_analysis["qualitative_indicators"]
        
        # High-risk combinations
        if quant_indicators.get("financial_impact") and qual_indicators.get("ai_ml_usage"):
            multiplier += 0.3  # AI/ML in financial decisions
            
        if quant_indicators.get("customer_facing") and qual_indicators.get("autonomous_decisions"):
            multiplier += 0.2  # Autonomous customer-facing decisions
            
        if qual_indicators.get("black_box") and quant_indicators.get("regulatory_impact"):
            multiplier += 0.25  # Unexplainable models with regulatory impact
            
        if qual_indicators.get("third_party") and quant_indicators.get("revenue_critical"):
            multiplier += 0.15  # Third-party dependency in critical systems
        
        final_score = int(base_score * multiplier)
        return min(final_score, 100)  # Cap at 100
    
    def _determine_risk_level(self, risk_score: int) -> Tuple[str, str]:
        """Determine risk level based on score."""
        risk_levels = self.framework_data["risk_rating_levels"]
        
        for level_info in risk_levels:
            min_score, max_score = level_info["score_range"]
            if min_score <= risk_score <= max_score:
                return level_info["level"], level_info["description"]
        
        # Default to Critical if score exceeds ranges
        return "Critical", "Maximum governance requirements"
    
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
    
    def evaluate_lifecycle_compliance(self, project_name: str, project_description: str, 
                                    current_stage: str = "design") -> Dict[str, Any]:
        """
        Evaluate compliance with OSFI E-23 model lifecycle requirements.
        
        Args:
            project_name: Name of the model/project
            project_description: Detailed description
            current_stage: Current lifecycle stage
            
        Returns:
            Lifecycle compliance assessment
        """
        logger.info(f"Evaluating lifecycle compliance for: {project_name} at stage: {current_stage}")
        
        # Get lifecycle component requirements
        if current_stage not in self.lifecycle_components:
            current_stage = "design"  # Default to design stage
        
        stage_info = self.lifecycle_components[current_stage]
        
        # Analyze project for lifecycle compliance
        compliance_analysis = self._analyze_lifecycle_compliance(project_description, current_stage)

        # Generate next steps and recommendations
        next_steps = self._generate_lifecycle_next_steps(current_stage, compliance_analysis)

        # Get OSFI subcomponents for this stage
        from osfi_e23_structure import OSFI_LIFECYCLE_COMPONENTS, get_stage_principles
        stage_subcomponents = OSFI_LIFECYCLE_COMPONENTS.get(current_stage, {}).get("subcomponents", [])
        stage_principles = get_stage_principles(current_stage)

        # Create user-facing coverage explanation
        coverage_pct = compliance_analysis["compliance_percentage"]
        detected_count = compliance_analysis["compliance_score"]
        total_count = compliance_analysis["total_indicators"]

        coverage_explanation = (
            f"📊 **Coverage Assessment for {stage_info['name']} Stage**\n\n"
            f"This assessment evaluates coverage of the following OSFI E-23 elements:\n\n"
        )

        for i, subcomponent in enumerate(stage_subcomponents, 1):
            coverage_explanation += f"  {i}. {subcomponent}\n"

        coverage_explanation += (
            f"\n**Coverage Result**: {detected_count} of {total_count} elements detected ({coverage_pct}% coverage)\n\n"
            f"**OSFI Principles**: {', '.join(stage_principles)}"
        )

        return {
            "project_name": project_name,
            "project_description": project_description,
            "assessment_date": datetime.now().isoformat(),
            "current_stage": current_stage,
            "stage_name": stage_info["name"],
            "requirements": stage_info["requirements"],
            "deliverables": stage_info["deliverables"],
            "compliance_analysis": compliance_analysis,
            "coverage_explanation": coverage_explanation,
            "osfi_subcomponents": stage_subcomponents,
            "osfi_principles": stage_principles,
            "next_steps": next_steps,
            "all_lifecycle_stages": list(self.lifecycle_components.keys())
        }
    
    def _analyze_lifecycle_compliance(self, project_description: str, stage: str) -> Dict[str, Any]:
        """Analyze project description for lifecycle coverage indicators.

        Maps 1:1 to official OSFI E-23 lifecycle subcomponents.
        Each stage has exactly 3 indicators corresponding to 3 OSFI subcomponents.
        """
        description_lower = project_description.lower()

        # Coverage indicators mapped 1:1 to OSFI E-23 subcomponents
        compliance_indicators = {
            "design": {
                "model_rationale_covered": any(term in description_lower for term in ['purpose', 'objective', 'rationale', 'business case', 'business need', 'justification']),
                "model_data_covered": any(term in description_lower for term in ['data quality', 'data governance', 'data standards', 'data source', 'data lineage', 'data input', 'data ingest', 'demographic', 'transaction history', 'customer data', 'training data']),
                "model_development_covered": any(term in description_lower for term in ['methodology', 'approach', 'algorithm', 'technique', 'development', 'performance', 'accuracy', 'metrics', 'architecture', 'ensemble', 'neural network', 'xgboost', 'gradient boosting', 'scoring', 'prediction', 'random forest', 'regression'])
            },
            "review": {
                "independent_validation_covered": any(term in description_lower for term in ['independent', 'validation', 'review', 'assessment', 'third party', 'external review']),
                "conceptual_soundness_covered": any(term in description_lower for term in ['conceptual', 'soundness', 'methodology review', 'design review', 'assumptions', 'limitations']),
                "performance_evaluation_covered": any(term in description_lower for term in ['performance', 'testing', 'evaluation', 'validation testing', 'accuracy', 'benchmark'])
            },
            "deployment": {
                "production_implementation_covered": any(term in description_lower for term in ['production', 'deployment', 'implementation', 'go-live', 'rollout', 'launch']),
                "quality_control_covered": any(term in description_lower for term in ['quality control', 'quality assurance', 'testing', 'validation', 'qa', 'verification']),
                "change_management_covered": any(term in description_lower for term in ['change management', 'change control', 'version control', 'approval process', 'governance'])
            },
            "monitoring": {
                "performance_tracking_covered": any(term in description_lower for term in ['monitoring', 'tracking', 'performance', 'metrics', 'kpi', 'dashboard', 'observability']),
                "drift_detection_covered": any(term in description_lower for term in ['drift', 'data drift', 'model drift', 'degradation', 'distribution shift', 'stability']),
                "escalation_procedures_covered": any(term in description_lower for term in ['escalation', 'alert', 'notification', 'threshold', 'breach', 'contingency', 'remediation'])
            },
            "decommission": {
                "retirement_process_covered": any(term in description_lower for term in ['retirement', 'decommission', 'decommissioning', 'sunset', 'end of life', 'phase out']),
                "stakeholder_notification_covered": any(term in description_lower for term in ['notification', 'communication', 'stakeholder', 'inform', 'announce', 'alert users']),
                "documentation_retention_covered": any(term in description_lower for term in ['archive', 'retention', 'storage', 'documentation', 'records', 'historical data'])
            }
        }

        stage_indicators = compliance_indicators.get(stage, {})
        compliance_score = sum(1 for indicator in stage_indicators.values() if indicator)
        total_indicators = len(stage_indicators)
        compliance_percentage = (compliance_score / total_indicators * 100) if total_indicators > 0 else 0

        return {
            "stage_indicators": stage_indicators,
            "compliance_score": compliance_score,
            "total_indicators": total_indicators,
            "compliance_percentage": round(compliance_percentage, 1),
            "gaps_identified": [key for key, value in stage_indicators.items() if not value]
        }
    
    def _generate_lifecycle_next_steps(self, current_stage: str, compliance_analysis: Dict[str, Any]) -> List[str]:
        """Generate next steps based on lifecycle stage and compliance."""
        next_steps = []
        
        # Address gaps in current stage
        gaps = compliance_analysis.get("gaps_identified", [])
        if gaps:
            next_steps.append(f"Complete missing requirements for {current_stage} stage:")
            for gap in gaps:
                next_steps.append(f"  - Address {gap.replace('_', ' ')}")
        
        # Stage-specific next steps
        stage_next_steps = {
            "design": [
                "Complete model development and documentation",
                "Prepare for independent model review",
                "Finalize performance testing criteria"
            ],
            "review": [
                "Address review findings and recommendations",
                "Obtain formal model approval",
                "Prepare deployment procedures and testing plan"
            ],
            "deployment": [
                "Execute production deployment plan",
                "Validate model performance in production environment",
                "Activate monitoring and alerting systems"
            ],
            "monitoring": [
                "Maintain ongoing performance monitoring",
                "Review and update monitoring thresholds as needed",
                "Prepare for next scheduled model review"
            ],
            "decommission": [
                "Execute formal decommission procedures",
                "Complete documentation archival",
                "Monitor for any residual impacts"
            ]
        }
        
        next_steps.extend(stage_next_steps.get(current_stage, []))
        
        return next_steps
    
    def _calculate_detailed_risk_scores(self, quantitative_factors: Dict[str, bool],
                                      qualitative_factors: Dict[str, bool]) -> Dict[str, Any]:
        """
        Calculate detailed risk scores by category.

        IMPORTANT: Uses same calculation method as assess_model_risk to ensure consistency.
        Flat scoring: 10 points per quantitative factor, 8 per qualitative factor.
        """
        # Flat scoring (consistent with assess_model_risk)
        quant_score = sum(1 for indicator in quantitative_factors.values() if indicator) * 10
        qual_score = sum(1 for indicator in qualitative_factors.values() if indicator) * 8

        # Calculate overall score with risk amplification
        base_score = quant_score + qual_score

        # Risk amplification for dangerous combinations (same as assess_model_risk)
        amplification = 1.0
        if quantitative_factors.get('financial_impact') and qualitative_factors.get('ai_ml_usage'):
            amplification += 0.3  # AI/ML in financial decisions
        if quantitative_factors.get('customer_facing') and qualitative_factors.get('autonomous_decisions'):
            amplification += 0.2  # Autonomous customer-facing decisions
        if qualitative_factors.get('black_box') and quantitative_factors.get('regulatory_impact'):
            amplification += 0.25  # Unexplainable models with regulatory impact
        if qualitative_factors.get('third_party') and quantitative_factors.get('revenue_critical'):
            amplification += 0.15  # Third-party dependency in critical systems

        overall_score = min(int(base_score * amplification), 100)

        return {
            "quantitative_score": quant_score,
            "qualitative_score": qual_score,
            "base_score": base_score,
            "amplification_factor": amplification,
            "overall_score": overall_score,
            "calculation_note": "Uses same methodology as assess_model_risk for consistency"
        }
    
    def _analyze_individual_risk_factors(self, quantitative_factors: Dict[str, bool], 
                                       qualitative_factors: Dict[str, bool]) -> Dict[str, List[str]]:
        """Analyze individual risk factors and their implications."""
        analysis = {
            "high_risk_factors": [],
            "medium_risk_factors": [],
            "risk_interactions": []
        }
        
        # High risk factors
        high_risk_mapping = {
            'financial_impact': "Model directly impacts financial decisions and outcomes",
            'autonomous_decisions': "Model makes decisions without human oversight",
            'black_box': "Model lacks explainability and transparency",
            'regulatory_impact': "Model affects regulatory compliance and reporting"
        }
        
        for factor, description in high_risk_mapping.items():
            if (quantitative_factors.get(factor) or qualitative_factors.get(factor)):
                analysis["high_risk_factors"].append(f"{factor.replace('_', ' ').title()}: {description}")
        
        # Medium risk factors
        medium_risk_mapping = {
            'ai_ml_usage': "Model uses AI/ML techniques requiring specialized oversight",
            'high_complexity': "Model complexity increases validation and monitoring requirements",
            'third_party': "Third-party dependencies introduce additional oversight requirements",
            'customer_impact': "Model decisions directly affect customer outcomes",
            'data_sensitive': "Model processes sensitive data requiring enhanced controls"
        }
        
        for factor, description in medium_risk_mapping.items():
            if (quantitative_factors.get(factor) or qualitative_factors.get(factor)):
                analysis["medium_risk_factors"].append(f"{factor.replace('_', ' ').title()}: {description}")
        
        # Risk interactions
        if quantitative_factors.get('financial_impact') and qualitative_factors.get('ai_ml_usage'):
            analysis["risk_interactions"].append("High-risk combination: AI/ML in financial decision-making")
        
        if qualitative_factors.get('autonomous_decisions') and qualitative_factors.get('black_box'):
            analysis["risk_interactions"].append("High-risk combination: Autonomous decisions with limited explainability")
        
        if quantitative_factors.get('regulatory_impact') and qualitative_factors.get('third_party'):
            analysis["risk_interactions"].append("Medium-risk combination: Third-party models affecting regulatory compliance")
        
        return analysis
    
    def _determine_review_frequency(self, risk_level: str) -> str:
        """Determine review frequency based on risk level."""
        frequency_mapping = {
            "Low": "Annual",
            "Medium": "Semi-annual",
            "High": "Quarterly", 
            "Critical": "Monthly"
        }
        return frequency_mapping.get(risk_level, "Semi-annual")
    
    def _determine_approval_authority(self, risk_level: str) -> str:
        """Determine required approval authority based on risk level."""
        authority_mapping = {
            "Low": "Model Owner or Designated Manager",
            "Medium": "Senior Management or Risk Committee",
            "High": "Executive Committee or CRO",
            "Critical": "Board of Directors or CEO"
        }
        return authority_mapping.get(risk_level, "Senior Management")
    
    def _get_monitoring_frequency(self, risk_level: str) -> str:
        """Get monitoring frequency for risk level."""
        monitoring_mapping = {
            "Low": "Quarterly monitoring with annual deep-dive",
            "Medium": "Monthly monitoring with quarterly reviews",
            "High": "Weekly monitoring with monthly reviews",
            "Critical": "Daily monitoring with weekly reviews"
        }
        return monitoring_mapping.get(risk_level, "Monthly monitoring")
    
    def _get_documentation_requirements(self, risk_level: str) -> List[str]:
        """Get documentation requirements for risk level (Low/Medium/High/Critical)."""
        # Base documentation (Low risk)
        base_docs = [
            "Model rationale and business purpose",
            "Data sources and quality documentation",
            "Model methodology and assumptions",
            "Performance metrics and validation results"
        ]

        # Medium risk: Standard documentation
        if risk_level in ["Medium", "High", "Critical"]:
            base_docs.extend([
                "Model validation methodology and results",
                "Change management documentation",
                "Model limitations and assumptions documentation"
            ])

        # High risk: Enhanced documentation
        if risk_level in ["High", "Critical"]:
            base_docs.extend([
                "Detailed explainability documentation",
                "Bias testing and mitigation measures",
                "Comprehensive audit trail and change log",
                "Risk assessment and mitigation strategies",
                "Contingency and rollback procedures"
            ])

        # Critical risk: Maximum documentation
        if risk_level == "Critical":
            base_docs.extend([
                "Board presentation and approval documentation",
                "External validation reports",
                "Regulatory compliance attestations",
                "Continuous monitoring dashboards and alerts"
            ])

        return base_docs
    
    def create_compliance_framework(self, project_name: str, project_description: str,
                                  current_stage: str,
                                  risk_assessment: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create compliance framework for OSFI E-23 based on current lifecycle stage.

        Args:
            project_name: Name of the model/project
            project_description: Detailed description
            current_stage: Current lifecycle stage (from Step 3)
            risk_assessment: Optional existing risk assessment (from Step 2)

        Returns:
            Stage-specific compliance framework
        """
        logger.info(f"Creating compliance framework for: {project_name} at stage: {current_stage}")

        # Get or perform risk assessment
        if not risk_assessment:
            risk_assessment = self.assess_model_risk(project_name, project_description)

        risk_level = risk_assessment.get("risk_level", "Medium")

        # Generate stage-specific framework with OSFI element structure
        framework = {
            "project_name": project_name,
            "project_description": project_description,
            "framework_date": datetime.now().isoformat(),
            "current_stage": current_stage,
            "risk_assessment_summary": {
                "risk_level": risk_level,
                "risk_score": risk_assessment.get("risk_score", 0),
                "key_risk_factors": self._extract_key_risk_factors(risk_assessment)
            },
            "governance_structure": self._create_governance_structure(risk_level),
            "osfi_elements": self._create_osfi_element_structure(current_stage, risk_level),
            "monitoring_framework": self._create_monitoring_framework(risk_level),
            "documentation_requirements": self._get_documentation_requirements(risk_level)
        }

        return framework
    
    def _extract_key_risk_factors(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Extract key risk factors from assessment."""
        risk_factors = []
        
        risk_analysis = risk_assessment.get("risk_analysis", {})
        quant_indicators = risk_analysis.get("quantitative_indicators", {})
        qual_indicators = risk_analysis.get("qualitative_indicators", {})
        
        # Add present risk factors
        for factor, present in quant_indicators.items():
            if present:
                risk_factors.append(f"Quantitative: {factor.replace('_', ' ').title()}")
        
        for factor, present in qual_indicators.items():
            if present:
                risk_factors.append(f"Qualitative: {factor.replace('_', ' ').title()}")
        
        return risk_factors[:10]  # Limit to top 10
    
    def _create_governance_structure(self, risk_level: str) -> Dict[str, Any]:
        """
        Create governance structure based on risk level.

        Includes OSFI-mandated, OSFI-implied, and implementation-suggested roles.
        """
        base_structure = {
            "model_owner": {
                "role": "Designated business unit responsible for model",
                "osfi_required": True,
                "source": "OSFI Appendix 1 required field"
            },
            "model_developer": {
                "role": "Technical team or vendor developing the model",
                "osfi_required": True,
                "source": "OSFI Appendix 1 required field"
            },
            "model_reviewer": {
                "role": "Independent validation team",
                "osfi_required": False,
                "osfi_implied": True,
                "source": "OSFI Principle 3.4 requires independent assessment"
            },
            "model_approver": {
                "role": self._determine_approval_authority(risk_level),
                "osfi_required": False,
                "osfi_implied": True,
                "source": "Implied by lifecycle governance requirements"
            }
        }

        # Medium risk: Standard governance enhancements
        if risk_level in ["Medium", "High", "Critical"]:
            base_structure.update({
                "risk_manager": {
                    "role": "Risk management oversight for model deployment",
                    "osfi_required": False,
                    "osfi_implied": True,
                    "source": "OSFI Principle 2.3 implies risk-based governance"
                }
            })

        # High risk: Enhanced governance structure
        if risk_level in ["High", "Critical"]:
            base_structure.update({
                "model_risk_committee": {
                    "role": "Senior committee overseeing model risk",
                    "osfi_required": False,
                    "osfi_implied": False,
                    "source": "Implementation choice - risk-based governance practice"
                },
                "compliance_officer": {
                    "role": "Compliance function ensuring regulatory adherence",
                    "osfi_required": False,
                    "osfi_implied": False,
                    "source": "Implementation choice - risk-based governance practice"
                },
                "legal_ethics_advisor": {
                    "role": "Legal and ethics review for complex models",
                    "osfi_required": False,
                    "osfi_implied": False,
                    "source": "Implementation choice - risk-based governance practice"
                }
            })

        # Critical risk: Maximum governance structure
        if risk_level == "Critical":
            base_structure.update({
                "board_oversight": {
                    "role": "Board of Directors oversight for critical models",
                    "osfi_required": False,
                    "osfi_implied": False,
                    "source": "Implementation choice - industry practice for critical models"
                },
                "external_validator": {
                    "role": "Independent third-party validation",
                    "osfi_required": False,
                    "osfi_implied": False,
                    "source": "Implementation choice - industry practice for critical models"
                },
                "regulatory_liaison": {
                    "role": "Direct regulatory communication channel",
                    "osfi_required": False,
                    "osfi_implied": False,
                    "source": "Implementation choice - industry practice for critical models"
                }
            })

        return base_structure
    
    def _create_osfi_element_structure(self, current_stage: str, risk_level: str) -> List[Dict[str, Any]]:
        """
        Create OSFI element-based structure linking subcomponents to requirements and checklists.

        Organizes stage requirements, deliverables, and checklist items by the 3 official
        OSFI E-23 subcomponents for the current stage.
        """
        from osfi_e23_structure import OSFI_LIFECYCLE_COMPONENTS, get_stage_principles

        # Get stage info
        if current_stage not in self.lifecycle_components:
            current_stage = "design"

        stage_info = self.lifecycle_components[current_stage]
        osfi_components = OSFI_LIFECYCLE_COMPONENTS.get(current_stage, {})
        subcomponents = osfi_components.get("subcomponents", [])
        principles = osfi_components.get("principles", [])

        # Map requirements to OSFI elements (stage-specific)
        requirements_map = self._map_requirements_to_elements(current_stage, stage_info["requirements"], risk_level)

        # Map deliverables to OSFI elements (stage-specific)
        deliverables_map = self._map_deliverables_to_elements(current_stage, stage_info["deliverables"])

        # Map checklist items to OSFI elements (stage-specific, risk-aware)
        checklist_map = self._map_checklist_to_elements(current_stage, risk_level)

        # Build element structure
        elements = []
        for i, subcomponent in enumerate(subcomponents):
            element = {
                "element_name": subcomponent,
                "osfi_principle": principles[0] if len(principles) == 1 else principles[min(i, len(principles)-1)],
                "requirements": requirements_map.get(i, []),
                "deliverables": deliverables_map.get(i, []),
                "checklist_items": checklist_map.get(i, [])
            }
            elements.append(element)

        return elements

    def _map_requirements_to_elements(self, stage: str, requirements: List[str], risk_level: str) -> Dict[int, List[str]]:
        """Map requirements to OSFI element indices."""
        # Base mapping for each stage
        if stage == "design":
            mapping = {
                0: [requirements[0]] if len(requirements) > 0 else [],  # Model Rationale
                1: [requirements[1]] if len(requirements) > 1 else [],  # Model Data
                2: requirements[2:5] if len(requirements) > 2 else []   # Model Development
            }
            # Medium risk enhancements
            if risk_level in ["Medium", "High", "Critical"]:
                mapping[2].extend([
                    "Basic bias and fairness assessment",
                    "Model explainability documentation"
                ])
            # High risk enhancements
            if risk_level in ["High", "Critical"]:
                mapping[2].extend([
                    "Comprehensive bias and fairness assessment",
                    "Detailed explainability analysis",
                    "Regulatory compliance review"
                ])
            # Critical risk enhancements
            if risk_level == "Critical":
                mapping[2].extend([
                    "External expert review of methodology",
                    "Advanced stress testing and scenario analysis"
                ])
        elif stage == "review":
            mapping = {
                0: [requirements[0]] if len(requirements) > 0 else [],  # Independent Validation
                1: requirements[1:3] if len(requirements) > 1 else [],  # Conceptual Soundness
                2: requirements[3:] if len(requirements) > 3 else []    # Performance Evaluation
            }
            # Medium risk enhancements
            if risk_level in ["Medium", "High", "Critical"]:
                mapping[2].append("Standard stress testing procedures")
            # High risk enhancements
            if risk_level in ["High", "Critical"]:
                mapping[0].append("Regulatory pre-approval consultation")
                mapping[2].append("Comprehensive stress testing")
            # Critical risk enhancements
            if risk_level == "Critical":
                mapping[0].append("External independent validation")
                mapping[2].append("Advanced scenario analysis")
        elif stage == "deployment":
            mapping = {
                0: requirements[0:2] if len(requirements) > 0 else [],  # Production Implementation
                1: [requirements[2]] if len(requirements) > 2 else [],  # Quality Control
                2: requirements[3:] if len(requirements) > 3 else []    # Change Management
            }
        elif stage == "monitoring":
            mapping = {
                0: requirements[0:2] if len(requirements) > 0 else [],  # Performance Tracking
                1: [requirements[2]] if len(requirements) > 2 else [],  # Drift Detection
                2: requirements[3:] if len(requirements) > 3 else []    # Escalation Procedures
            }
            # Medium risk enhancements
            if risk_level in ["Medium", "High", "Critical"]:
                mapping[0].append("Regular performance reporting")
                mapping[2].append("Structured escalation procedures")
            # High risk enhancements
            if risk_level in ["High", "Critical"]:
                mapping[0].extend([
                    "Automated performance dashboards",
                    "Frequent governance reporting"
                ])
                mapping[2].append("Automated alert systems")
            # Critical risk enhancements
            if risk_level == "Critical":
                mapping[0].append("Real-time performance monitoring")
                mapping[2].append("Immediate escalation capability")
        elif stage == "decommission":
            mapping = {
                0: requirements[0:2] if len(requirements) > 0 else [],  # Retirement Process
                1: [requirements[2]] if len(requirements) > 2 else [],  # Stakeholder Notification
                2: requirements[3:] if len(requirements) > 3 else []    # Documentation Retention
            }
        else:
            mapping = {0: requirements, 1: [], 2: []}

        return mapping

    def _map_deliverables_to_elements(self, stage: str, deliverables: List[str]) -> Dict[int, List[str]]:
        """Map deliverables to OSFI element indices."""
        if stage == "design":
            return {
                0: [deliverables[0]] if len(deliverables) > 0 else [],  # Model Rationale
                1: [deliverables[1]] if len(deliverables) > 1 else [],  # Model Data
                2: deliverables[2:] if len(deliverables) > 2 else []    # Model Development
            }
        elif stage == "review":
            return {
                0: [deliverables[0]] if len(deliverables) > 0 else [],  # Independent Validation (report)
                1: [deliverables[1]] if len(deliverables) > 1 else [],  # Conceptual Soundness (risk assessment)
                2: deliverables[2:] if len(deliverables) > 2 else []    # Performance Evaluation
            }
        elif stage == "deployment":
            return {
                0: [deliverables[0], deliverables[1]] if len(deliverables) > 1 else [],  # Production Implementation
                1: [],  # Quality Control (covered in procedures)
                2: deliverables[2:] if len(deliverables) > 2 else []  # Change Management
            }
        elif stage == "monitoring":
            return {
                0: [deliverables[0], deliverables[1]] if len(deliverables) > 1 else [],  # Performance Tracking
                1: [],  # Drift Detection (covered in dashboards)
                2: deliverables[2:] if len(deliverables) > 2 else []  # Escalation
            }
        elif stage == "decommission":
            return {
                0: [deliverables[0]] if len(deliverables) > 0 else [],  # Retirement Process
                1: [deliverables[1]] if len(deliverables) > 1 else [],  # Stakeholder Notification
                2: deliverables[2:] if len(deliverables) > 2 else []    # Documentation Retention
            }
        else:
            return {0: deliverables, 1: [], 2: []}

    def _map_checklist_to_elements(self, stage: str, risk_level: str) -> Dict[int, List[Dict[str, Any]]]:
        """Map checklist items to OSFI element indices."""
        if stage == "design":
            mapping = {
                0: [  # Model Rationale
                    {"item": "Model inventory registration", "required": True},
                    {"item": "Risk rating assignment", "required": True}
                ],
                1: [],  # Model Data (no specific items currently)
                2: [  # Model Development
                    {"item": "Model documentation completion", "required": True}
                ]
            }
            # Medium risk enhancements
            if risk_level in ["Medium", "High", "Critical"]:
                mapping[2].append({"item": "Model validation testing", "required": True})
            # High risk enhancements
            if risk_level in ["High", "Critical"]:
                mapping[2].extend([
                    {"item": "Bias and fairness testing", "required": True},
                    {"item": "Explainability documentation", "required": True}
                ])
            # Critical risk enhancements
            if risk_level == "Critical":
                mapping[2].append({"item": "External methodology review", "required": True})
        elif stage == "review":
            mapping = {
                0: [  # Independent Validation
                    {"item": "Independent model review", "required": True}
                ],
                1: [],  # Conceptual Soundness (covered in review)
                2: [  # Performance Evaluation
                    {"item": "Formal model approval", "required": True}
                ]
            }
            # Medium risk enhancements
            if risk_level in ["Medium", "High", "Critical"]:
                mapping[0].append({"item": "Validation testing completed", "required": True})
            # High risk enhancements
            if risk_level in ["High", "Critical"]:
                mapping[2].append({"item": "Senior management approval", "required": True})
                mapping[0].append({"item": "Regulatory compliance verification", "required": True})
            # Critical risk enhancements
            if risk_level == "Critical":
                mapping[2].extend([
                    {"item": "Board-level approval", "required": True},
                    {"item": "External validation", "required": True},
                    {"item": "Regulatory pre-approval", "required": False}
                ])
        elif stage == "deployment":
            mapping = {
                0: [  # Production Implementation
                    {"item": "Production deployment testing", "required": True}
                ],
                1: [],  # Quality Control (covered in testing)
                2: [  # Change Management
                    {"item": "Monitoring system activation", "required": True}
                ]
            }
            # Medium risk enhancements
            if risk_level in ["Medium", "High", "Critical"]:
                mapping[2].append({"item": "Change control documentation", "required": True})
            # High risk enhancements
            if risk_level in ["High", "Critical"]:
                mapping[2].append({"item": "Enhanced monitoring setup", "required": True})
            # Critical risk enhancements
            if risk_level == "Critical":
                mapping[2].append({"item": "Real-time monitoring activation", "required": True})
        elif stage == "monitoring":
            # Note: These 3 elements are our implementation interpretation of OSFI Principle 3.6 (monitoring requirement)
            mapping = {
                0: [  # Performance Tracking
                    {"item": "Regular performance monitoring", "required": True}
                ],
                1: [  # Drift Detection
                    {"item": "Data drift monitoring setup", "required": True}
                ],
                2: [  # Escalation Procedures
                    {"item": "Model incident response procedures", "required": True}
                ]
            }
            # Medium risk enhancements
            if risk_level in ["Medium", "High", "Critical"]:
                mapping[0].append({"item": "Performance reporting procedures", "required": True})
                mapping[2].append({"item": "Defined escalation pathways", "required": True})
            # High risk enhancements
            if risk_level in ["High", "Critical"]:
                mapping[0].append({"item": "Automated performance dashboards", "required": True})
                mapping[1].append({"item": "Statistical drift detection tests", "required": True})
                mapping[2].append({"item": "Rapid escalation to senior management", "required": True})
            # Critical risk enhancements
            if risk_level == "Critical":
                mapping[0].append({"item": "Real-time monitoring dashboard", "required": True})
                mapping[2].append({"item": "Immediate executive notification", "required": True})
        elif stage == "decommission":
            # Note: These 3 elements are our implementation interpretation of OSFI Principle 3.6 (decommission requirement)
            mapping = {
                0: [  # Retirement Process
                    {"item": "Formal decommission approval", "required": True}
                ],
                1: [  # Stakeholder Notification
                    {"item": "Stakeholder decommission notification", "required": True}
                ],
                2: [  # Documentation Retention
                    {"item": "Model archive and documentation retention", "required": True}
                ]
            }
            # Medium risk enhancements
            if risk_level in ["Medium", "High", "Critical"]:
                mapping[2].append({"item": "Complete documentation archival", "required": True})
            # High risk enhancements
            if risk_level in ["High", "Critical"]:
                mapping[0].append({"item": "Risk assessment of decommission impacts", "required": True})
                mapping[2].append({"item": "Regulatory compliance documentation archival", "required": True})
            # Critical risk enhancements
            if risk_level == "Critical":
                mapping[0].append({"item": "Board notification of decommission", "required": True})
                mapping[2].append({"item": "Long-term archival with audit trail", "required": True})
        else:
            mapping = {0: [], 1: [], 2: []}

        return mapping

    def _create_monitoring_framework(self, risk_level: str) -> Dict[str, Any]:
        """Create monitoring framework based on risk level."""
        base_framework = {
            "monitoring_frequency": self._get_monitoring_frequency(risk_level),
            "key_metrics": [
                "Model performance accuracy",
                "Prediction stability",
                "Data quality indicators",
                "Usage patterns and volumes"
            ],
            "alert_thresholds": {
                "performance_degradation": "5% decline from baseline",
                "data_drift": "Significant distribution changes",
                "usage_anomalies": "Unexpected usage patterns"
            },
            "reporting_schedule": self._determine_review_frequency(risk_level)
        }
        
        if risk_level in ["High", "Critical"]:
            base_framework["key_metrics"].extend([
                "Bias and fairness metrics",
                "Explainability scores",
                "Regulatory compliance indicators",
                "Customer impact measures"
            ])
            
            base_framework["alert_thresholds"].update({
                "bias_detection": "Statistically significant bias indicators",
                "regulatory_breach": "Any regulatory threshold violation",
                "customer_complaints": "Unusual complaint patterns"
            })
        
        if risk_level == "Critical":
            base_framework.update({
                "real_time_monitoring": True,
                "automated_shutoff": "Automatic model deactivation on critical alerts",
                "escalation_procedures": "Immediate senior management notification"
            })
        
        return base_framework
    
