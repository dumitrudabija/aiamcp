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
        Assess model risk based on OSFI E-23 framework.
        
        Args:
            project_name: Name of the model/project
            project_description: Detailed description of the model
            
        Returns:
            Model risk assessment results
        """
        logger.info(f"Assessing model risk for: {project_name}")
        
        # Analyze project description for risk indicators
        risk_analysis = self._analyze_risk_factors(project_description)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(risk_analysis)
        
        # Determine risk rating level
        risk_level, risk_description = self._determine_risk_level(risk_score)
        
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
        """Generate governance requirements based on risk level."""
        base_requirements = {
            "organizational": [
                "Assign qualified model owner with appropriate expertise",
                "Establish clear roles and responsibilities for model stakeholders",
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
        
        # Enhanced requirements based on risk level
        if risk_level in ["High", "Critical"]:
            base_requirements["organizational"].extend([
                "Establish Model Risk Committee oversight",
                "Assign senior management accountability",
                "Engage multi-disciplinary review team including legal/ethics"
            ])
            
            base_requirements["documentation"].extend([
                "Provide detailed explainability documentation",
                "Document bias testing and mitigation measures",
                "Maintain comprehensive audit trail"
            ])
            
            base_requirements["review_approval"].extend([
                "Require board-level or senior committee approval",
                "Conduct quarterly comprehensive reviews",
                "Engage external validation for critical models"
            ])
            
            base_requirements["monitoring"].extend([
                "Implement real-time monitoring and alerting",
                "Conduct monthly performance assessments",
                "Maintain contingency and rollback procedures"
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
        
        # Risk level specific recommendations
        if risk_level == "Critical":
            recommendations.extend([
                "🚨 CRITICAL: Obtain board-level approval before deployment",
                "Implement maximum governance controls and oversight",
                "Conduct external validation and independent review",
                "Establish dedicated Model Risk Committee",
                "Implement continuous monitoring with real-time alerts"
            ])
        elif risk_level == "High":
            recommendations.extend([
                "⚠️ HIGH RISK: Require senior management approval",
                "Implement enhanced governance and oversight controls",
                "Conduct quarterly comprehensive model reviews",
                "Establish robust monitoring and contingency procedures"
            ])
        elif risk_level == "Medium":
            recommendations.extend([
                "📋 MODERATE RISK: Implement standard governance procedures",
                "Conduct semi-annual model reviews",
                "Establish regular monitoring and reporting"
            ])
        else:  # Low
            recommendations.extend([
                "✅ LOWER RISK: Apply proportionate governance controls",
                "Conduct annual model reviews",
                "Implement basic monitoring procedures"
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
        
        return {
            "project_name": project_name,
            "project_description": project_description,
            "assessment_date": datetime.now().isoformat(),
            "current_stage": current_stage,
            "stage_name": stage_info["name"],
            "requirements": stage_info["requirements"],
            "deliverables": stage_info["deliverables"],
            "compliance_analysis": compliance_analysis,
            "next_steps": next_steps,
            "all_lifecycle_stages": list(self.lifecycle_components.keys())
        }
    
    def _analyze_lifecycle_compliance(self, project_description: str, stage: str) -> Dict[str, Any]:
        """Analyze project description for lifecycle compliance indicators."""
        description_lower = project_description.lower()
        
        compliance_indicators = {
            "design": {
                "rationale_defined": any(term in description_lower for term in ['purpose', 'objective', 'rationale', 'business case']),
                "data_governance": any(term in description_lower for term in ['data quality', 'data governance', 'data standards']),
                "methodology_documented": any(term in description_lower for term in ['methodology', 'approach', 'algorithm', 'technique']),
                "performance_criteria": any(term in description_lower for term in ['performance', 'accuracy', 'metrics', 'criteria'])
            },
            "review": {
                "independent_review": any(term in description_lower for term in ['review', 'validation', 'assessment', 'evaluation']),
                "documentation_complete": any(term in description_lower for term in ['documented', 'documentation', 'recorded']),
                "testing_performed": any(term in description_lower for term in ['testing', 'validation', 'verification']),
                "approval_obtained": any(term in description_lower for term in ['approved', 'authorization', 'sign-off'])
            },
            "deployment": {
                "production_ready": any(term in description_lower for term in ['production', 'deployment', 'implementation']),
                "testing_completed": any(term in description_lower for term in ['tested', 'testing', 'validation']),
                "monitoring_setup": any(term in description_lower for term in ['monitoring', 'tracking', 'surveillance']),
                "procedures_documented": any(term in description_lower for term in ['procedures', 'process', 'workflow'])
            },
            "monitoring": {
                "monitoring_active": any(term in description_lower for term in ['monitoring', 'tracking', 'observing']),
                "thresholds_defined": any(term in description_lower for term in ['threshold', 'limit', 'boundary', 'alert']),
                "reporting_established": any(term in description_lower for term in ['reporting', 'dashboard', 'metrics']),
                "escalation_procedures": any(term in description_lower for term in ['escalation', 'alert', 'notification'])
            },
            "decommission": {
                "retirement_planned": any(term in description_lower for term in ['retirement', 'decommission', 'sunset']),
                "stakeholders_notified": any(term in description_lower for term in ['notification', 'communication', 'stakeholder']),
                "documentation_archived": any(term in description_lower for term in ['archive', 'retention', 'storage']),
                "impact_assessed": any(term in description_lower for term in ['impact', 'effect', 'consequence'])
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
    
    def generate_risk_rating(self, project_name: str, project_description: str, 
                           quantitative_factors: Optional[Dict[str, Any]] = None,
                           qualitative_factors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate detailed risk rating assessment.
        
        Args:
            project_name: Name of the model/project
            project_description: Detailed description
            quantitative_factors: Optional quantitative risk factors
            qualitative_factors: Optional qualitative risk factors
            
        Returns:
            Detailed risk rating assessment
        """
        logger.info(f"Generating risk rating for: {project_name}")
        
        # Use provided factors or analyze from description
        if not quantitative_factors or not qualitative_factors:
            risk_analysis = self._analyze_risk_factors(project_description)
            quantitative_factors = risk_analysis["quantitative_indicators"]
            qualitative_factors = risk_analysis["qualitative_indicators"]
        
        # Calculate detailed risk scores
        risk_scores = self._calculate_detailed_risk_scores(quantitative_factors, qualitative_factors)
        
        # Determine overall risk rating
        overall_score = risk_scores["overall_score"]
        risk_level, risk_description = self._determine_risk_level(overall_score)
        
        # Generate risk factor analysis
        risk_factor_analysis = self._analyze_individual_risk_factors(quantitative_factors, qualitative_factors)
        
        return {
            "project_name": project_name,
            "project_description": project_description,
            "assessment_date": datetime.now().isoformat(),
            "risk_rating": risk_level,
            "risk_description": risk_description,
            "overall_score": overall_score,
            "risk_scores": risk_scores,
            "risk_factor_analysis": risk_factor_analysis,
            "governance_intensity": self._determine_governance_intensity(risk_level),
            "review_frequency": self._determine_review_frequency(risk_level),
            "approval_authority": self._determine_approval_authority(risk_level)
        }
    
    def _calculate_detailed_risk_scores(self, quantitative_factors: Dict[str, bool], 
                                      qualitative_factors: Dict[str, bool]) -> Dict[str, Any]:
        """Calculate detailed risk scores by category."""
        # Quantitative scoring
        quant_weights = {
            'high_volume': 8,
            'financial_impact': 10,
            'customer_facing': 7,
            'revenue_critical': 9,
            'regulatory_impact': 8
        }
        
        quant_score = sum(quant_weights.get(factor, 5) for factor, present in quantitative_factors.items() if present)
        
        # Qualitative scoring
        qual_weights = {
            'ai_ml_usage': 8,
            'high_complexity': 7,
            'autonomous_decisions': 9,
            'black_box': 8,
            'third_party': 6,
            'data_sensitive': 7,
            'real_time': 6,
            'customer_impact': 8
        }
        
        qual_score = sum(qual_weights.get(factor, 5) for factor, present in qualitative_factors.items() if present)
        
        # Calculate overall score with risk amplification
        base_score = quant_score + qual_score
        
        # Risk amplification for dangerous combinations
        amplification = 1.0
        if quantitative_factors.get('financial_impact') and qualitative_factors.get('ai_ml_usage'):
            amplification += 0.3
        if qualitative_factors.get('autonomous_decisions') and qualitative_factors.get('black_box'):
            amplification += 0.25
        if quantitative_factors.get('regulatory_impact') and qualitative_factors.get('third_party'):
            amplification += 0.2
        
        overall_score = min(int(base_score * amplification), 100)
        
        return {
            "quantitative_score": quant_score,
            "qualitative_score": qual_score,
            "base_score": base_score,
            "amplification_factor": amplification,
            "overall_score": overall_score
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
    
    def _determine_governance_intensity(self, risk_level: str) -> Dict[str, str]:
        """Determine governance intensity based on risk level."""
        intensity_mapping = {
            "Low": "Minimal - Basic documentation and annual reviews",
            "Medium": "Standard - Regular monitoring and semi-annual reviews", 
            "High": "Enhanced - Comprehensive oversight and quarterly reviews",
            "Critical": "Maximum - Continuous monitoring and monthly reviews"
        }
        
        return {
            "level": risk_level,
            "description": intensity_mapping.get(risk_level, "Standard"),
            "monitoring_frequency": self._get_monitoring_frequency(risk_level),
            "documentation_requirements": self._get_documentation_requirements(risk_level)
        }
    
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
        """Get documentation requirements for risk level."""
        base_docs = [
            "Model rationale and business purpose",
            "Data sources and quality documentation",
            "Model methodology and assumptions",
            "Performance metrics and validation results"
        ]
        
        if risk_level in ["High", "Critical"]:
            base_docs.extend([
                "Detailed explainability documentation",
                "Bias testing and mitigation measures",
                "Comprehensive audit trail and change log",
                "Risk assessment and mitigation strategies",
                "Contingency and rollback procedures"
            ])
        
        if risk_level == "Critical":
            base_docs.extend([
                "Board presentation and approval documentation",
                "External validation reports",
                "Regulatory compliance attestations",
                "Continuous monitoring dashboards and alerts"
            ])
        
        return base_docs
    
    def create_compliance_framework(self, project_name: str, project_description: str,
                                  risk_assessment: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create comprehensive compliance framework for OSFI E-23.
        
        Args:
            project_name: Name of the model/project
            project_description: Detailed description
            risk_assessment: Optional existing risk assessment
            
        Returns:
            Comprehensive compliance framework
        """
        logger.info(f"Creating compliance framework for: {project_name}")
        
        # Get or perform risk assessment
        if not risk_assessment:
            risk_assessment = self.assess_model_risk(project_name, project_description)
        
        risk_level = risk_assessment.get("risk_level", "Medium")
        
        # Generate comprehensive framework
        framework = {
            "project_name": project_name,
            "project_description": project_description,
            "framework_date": datetime.now().isoformat(),
            "risk_assessment_summary": {
                "risk_level": risk_level,
                "risk_score": risk_assessment.get("risk_score", 0),
                "key_risk_factors": self._extract_key_risk_factors(risk_assessment)
            },
            "governance_structure": self._create_governance_structure(risk_level),
            "lifecycle_requirements": self._create_lifecycle_requirements(risk_level),
            "monitoring_framework": self._create_monitoring_framework(risk_level),
            "documentation_requirements": self._get_documentation_requirements(risk_level),
            "compliance_checklist": self._create_compliance_checklist(risk_level),
            "implementation_timeline": self._create_implementation_timeline(risk_level)
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
        """Create governance structure based on risk level."""
        base_structure = {
            "model_owner": "Designated business unit responsible for model",
            "model_developer": "Technical team or vendor developing the model",
            "model_reviewer": "Independent validation team",
            "model_approver": self._determine_approval_authority(risk_level)
        }
        
        if risk_level in ["High", "Critical"]:
            base_structure.update({
                "model_risk_committee": "Senior committee overseeing model risk",
                "compliance_officer": "Compliance function ensuring regulatory adherence",
                "legal_ethics_advisor": "Legal and ethics review for complex models"
            })
        
        if risk_level == "Critical":
            base_structure.update({
                "board_oversight": "Board of Directors oversight for critical models",
                "external_validator": "Independent third-party validation",
                "regulatory_liaison": "Direct regulatory communication channel"
            })
        
        return base_structure
    
    def _create_lifecycle_requirements(self, risk_level: str) -> Dict[str, Dict[str, Any]]:
        """Create lifecycle requirements based on risk level."""
        requirements = {}
        
        for stage, stage_info in self.lifecycle_components.items():
            stage_requirements = {
                "requirements": stage_info["requirements"].copy(),
                "deliverables": stage_info["deliverables"].copy(),
                "timeline": self._get_stage_timeline(stage, risk_level),
                "approval_required": stage in ["review", "deployment"] or risk_level in ["High", "Critical"]
            }
            
            # Enhanced requirements for higher risk levels
            if risk_level in ["High", "Critical"]:
                if stage == "design":
                    stage_requirements["requirements"].extend([
                        "Comprehensive bias and fairness assessment",
                        "Detailed explainability analysis",
                        "Regulatory compliance review"
                    ])
                elif stage == "review":
                    stage_requirements["requirements"].extend([
                        "External validation (Critical models)",
                        "Regulatory pre-approval consultation",
                        "Comprehensive stress testing"
                    ])
                elif stage == "monitoring":
                    stage_requirements["requirements"].extend([
                        "Real-time performance dashboards",
                        "Automated alert systems",
                        "Monthly governance reporting"
                    ])
            
            requirements[stage] = stage_requirements
        
        return requirements
    
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
    
    def _create_compliance_checklist(self, risk_level: str) -> List[Dict[str, Any]]:
        """Create compliance checklist based on risk level."""
        checklist = [
            {"item": "Model inventory registration", "required": True, "stage": "design"},
            {"item": "Risk rating assignment", "required": True, "stage": "design"},
            {"item": "Model documentation completion", "required": True, "stage": "design"},
            {"item": "Independent model review", "required": True, "stage": "review"},
            {"item": "Formal model approval", "required": True, "stage": "review"},
            {"item": "Production deployment testing", "required": True, "stage": "deployment"},
            {"item": "Monitoring system activation", "required": True, "stage": "deployment"},
            {"item": "Regular performance monitoring", "required": True, "stage": "monitoring"}
        ]
        
        if risk_level in ["High", "Critical"]:
            checklist.extend([
                {"item": "Bias and fairness testing", "required": True, "stage": "design"},
                {"item": "Explainability documentation", "required": True, "stage": "design"},
                {"item": "Senior management approval", "required": True, "stage": "review"},
                {"item": "Regulatory compliance verification", "required": True, "stage": "review"},
                {"item": "Enhanced monitoring setup", "required": True, "stage": "deployment"}
            ])
        
        if risk_level == "Critical":
            checklist.extend([
                {"item": "Board-level approval", "required": True, "stage": "review"},
                {"item": "External validation", "required": True, "stage": "review"},
                {"item": "Regulatory pre-approval", "required": False, "stage": "review"},
                {"item": "Real-time monitoring activation", "required": True, "stage": "deployment"}
            ])
        
        return checklist
    
    def _create_implementation_timeline(self, risk_level: str) -> Dict[str, str]:
        """Create implementation timeline based on risk level."""
        base_timeline = {
            "design_phase": "4-8 weeks",
            "review_phase": "2-4 weeks", 
            "deployment_phase": "2-3 weeks",
            "monitoring_setup": "1-2 weeks"
        }
        
        if risk_level in ["High", "Critical"]:
            base_timeline.update({
                "design_phase": "8-12 weeks",
                "review_phase": "4-6 weeks",
                "deployment_phase": "3-4 weeks",
                "monitoring_setup": "2-3 weeks"
            })
        
        if risk_level == "Critical":
            base_timeline.update({
                "design_phase": "12-16 weeks",
                "review_phase": "6-8 weeks",
                "external_validation": "4-6 weeks",
                "regulatory_consultation": "2-4 weeks",
                "deployment_phase": "4-6 weeks"
            })
        
        return base_timeline
    
    def _get_stage_timeline(self, stage: str, risk_level: str) -> str:
        """Get timeline for specific stage based on risk level."""
        timelines = {
            "Low": {
                "design": "2-4 weeks",
                "review": "1-2 weeks",
                "deployment": "1-2 weeks",
                "monitoring": "Ongoing",
                "decommission": "1-2 weeks"
            },
            "Medium": {
                "design": "4-6 weeks",
                "review": "2-3 weeks",
                "deployment": "2-3 weeks",
                "monitoring": "Ongoing",
                "decommission": "2-3 weeks"
            },
            "High": {
                "design": "6-10 weeks",
                "review": "3-5 weeks",
                "deployment": "3-4 weeks",
                "monitoring": "Ongoing",
                "decommission": "3-4 weeks"
            },
            "Critical": {
                "design": "10-16 weeks",
                "review": "6-8 weeks",
                "deployment": "4-6 weeks",
                "monitoring": "Ongoing",
                "decommission": "4-6 weeks"
            }
        }
        
        return timelines.get(risk_level, {}).get(stage, "2-4 weeks")
