"""
AIA Analysis Module

Provides intelligent analysis capabilities for Canada's Algorithmic Impact Assessment (AIA).
Extracted from server.py to reduce complexity and improve code organization.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AIAAnalyzer:
    """Intelligent analyzer for AIA assessments."""

    def __init__(self, aia_processor):
        """Initialize with AIAProcessor instance."""
        self.aia_processor = aia_processor

    def _get_design_phase_questions(self) -> List[Dict[str, Any]]:
        """Get questions visible in Design phase."""
        return self.aia_processor.get_design_phase_questions()

    def _analyze_project_description(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project description analysis requests with intelligent automatic scoring."""
        # WORKFLOW ENFORCEMENT: Check if introduction has been shown
        intro_check = self._check_introduction_requirement()
        if intro_check:
            return intro_check

        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")

        logger.info(f"Analyzing project description: {project_name}")
        
        # Get Design phase questions for all calculations
        design_phase_questions = self._get_design_phase_questions()
        design_phase_max_score = sum(q['max_score'] for q in design_phase_questions)
        
        # Perform intelligent analysis of the project description
        auto_responses = self._intelligent_project_analysis(project_description)
        
        # Calculate preliminary score based on automatic analysis
        preliminary_score = self.aia_processor.calculate_score(auto_responses)
        impact_level, level_name, level_description = self.aia_processor.determine_impact_level(preliminary_score)
        
        # Get questions that still need manual input (Design phase only)
        answered_question_ids = {r['question_id'] for r in auto_responses}
        questions_by_name = {q['name']: q for q in design_phase_questions}
        
        manual_questions = []
        for question in design_phase_questions:
            if question['name'] not in answered_question_ids:
                manual_questions.append(question)
        
        # Get auto-answered questions with reasoning
        auto_answered_questions = []
        for response in auto_responses:
            question_id = response['question_id']
            if question_id in questions_by_name:
                question = questions_by_name[question_id]
                selected_value = response['selected_values'][0]
                
                # Find the selected choice
                selected_choice = None
                for choice in question['choices']:
                    if choice['value'] == selected_value:
                        selected_choice = choice
                        break
                
                if selected_choice:
                    auto_answered_questions.append({
                        'question_id': question_id,
                        'question_title': question['title'],
                        'selected_answer': selected_choice['text'],
                        'score_contribution': selected_choice['score'],
                        'reasoning': response.get('reasoning', 'Automatically determined from project description')
                    })
        
        # Format auto-answered questions for the expected response format
        auto_answered_formatted = []
        for response in auto_responses:
            question_id = response['question_id']
            if question_id in questions_by_name:
                question = questions_by_name[question_id]
                selected_value = response['selected_values'][0]
                
                # Find the selected choice and its index
                selected_choice = None
                selected_option = 0
                for i, choice in enumerate(question['choices']):
                    if choice['value'] == selected_value:
                        selected_choice = choice
                        selected_option = i
                        break
                
                if selected_choice:
                    auto_answered_formatted.append({
                        'questionId': question_id,
                        'question': question['title'],
                        'selectedOption': selected_option,
                        'selectedText': selected_choice['text'],
                        'confidence': 'high' if response.get('confidence', 0.6) > 0.7 else 'medium',
                        'reasoning': response.get('reasoning', 'Automatically determined from project description')
                    })
        
        # Format manual input questions
        needs_manual_input = []
        for question in manual_questions[:18]:  # Limit to 18 questions
            needs_manual_input.append({
                'questionId': question['name'],
                'question': question['title'],
                'category': self._get_question_category(question['name']),
                'type': 'risk' if question.get('max_score', 0) > 0 else 'mitigation',
                'options': [{'text': choice['text'], 'score': choice['score']} for choice in question['choices']],
                'reasoning': 'Could not be determined from project description - requires manual input'
            })
        
        # Calculate percentages using Design phase questions
        completion_percentage = round((len(auto_responses) / len(design_phase_questions)) * 100)
        score_percentage = round((preliminary_score / design_phase_max_score) * 100, 2)
        
        return {
            "projectName": project_name,
            "projectDescription": project_description,
            "autoAnswered": auto_answered_formatted,
            "needsManualInput": needs_manual_input,
            "partialAssessment": {
                "rawImpactScore": preliminary_score,
                "mitigationScore": 0,  # Will be calculated when mitigation questions are answered
                "currentScore": preliminary_score,
                "impactLevel": self._get_impact_level_roman(impact_level),
                "impactLevelDescription": level_description,
                "scorePercentage": score_percentage,
                "completionPercentage": completion_percentage
            }
        }
    

    def _intelligent_project_analysis(self, project_description: str) -> List[Dict[str, Any]]:
        """Perform intelligent analysis of project description to automatically answer questions."""
        auto_responses = []
        description_lower = project_description.lower()
        
        # Enhanced risk indicators with more comprehensive pattern matching
        risk_indicators = {
            'high_volume': any(term in description_lower for term in ['thousands', 'millions', 'large scale', 'mass', 'bulk', 'daily', 'hourly', 'real-time', 'continuous']),
            'personal_data': any(term in description_lower for term in ['personal', 'private', 'confidential', 'sensitive', 'pii', 'credit', 'income', 'employment history', 'financial information']),
            'financial': any(term in description_lower for term in ['financial', 'money', 'payment', 'economic', 'benefit', 'tax', 'loan', 'credit', 'bank', 'mortgage', 'insurance']),
            'health': any(term in description_lower for term in ['health', 'medical', 'healthcare', 'patient', 'treatment', 'diagnosis', 'clinical']),
            'employment': any(term in description_lower for term in ['employment', 'hiring', 'job', 'recruitment', 'hr', 'resume', 'candidate']),
            'law_enforcement': any(term in description_lower for term in ['police', 'criminal', 'law enforcement', 'investigation', 'security', 'surveillance']),
            'ai_ml': any(term in description_lower for term in ['ai', 'artificial intelligence', 'machine learning', 'neural', 'deep learning', 'algorithm', 'model', 'trained']),
            'automated_decision': any(term in description_lower for term in ['automated', 'automatic', 'decision', 'approve', 'deny', 'reject', 'classify', 'determine', 'final decision', 'without human review']),
            'third_party': any(term in description_lower for term in ['third party', 'third-party', 'vendor', 'contractor', 'external', 'bureau', 'service']),
            'public_facing': any(term in description_lower for term in ['public', 'citizen', 'client', 'customer', 'user', 'applicant', 'individual']),
            'government': any(term in description_lower for term in ['government', 'federal', 'department', 'ministry', 'agency', 'public sector']),
            'full_automation': any(term in description_lower for term in ['without human review', 'automatically approve', 'automatically deny', 'final decision', 'no human intervention']),
            'real_time': any(term in description_lower for term in ['real-time', 'real time', 'immediate', 'instant', 'live']),
            'high_impact_decisions': any(term in description_lower for term in ['approve', 'deny', 'reject', 'grant', 'refuse', 'determine eligibility'])
        }
        
        # Filter questions to only include those visible in Design phase
        # Based on survey-enfr.json analysis: Design phase users see questions that are either:
        # 1. Always visible (no visibleIf condition), OR
        # 2. Have visibleIf condition "{projectDetailsPhase} = \"item1\"" (Design phase)
        design_phase_questions = self._get_design_phase_questions()
        
        # Get questions by name for lookup
        questions_by_name = {q['name']: q for q in design_phase_questions}
        
        # Automatically answer questions based on comprehensive project analysis
        for question in design_phase_questions:
            question_name = question['name']
            question_title = question['title'].lower()
            
            # Skip if no choices available
            if not question.get('choices'):
                continue
            
            selected_choice_index = None
            reasoning = ""
            
            # AUTOMATION TYPE QUESTIONS - Critical for scoring
            if 'type of automation' in question_title or 'automation you are planning' in question_title:
                if risk_indicators['full_automation'] or risk_indicators['automated_decision']:
                    # Full automation - highest risk
                    selected_choice_index = len(question['choices']) - 1  # Last option (full automation)
                    reasoning = "Project description indicates full automation without human review"
                else:
                    selected_choice_index = 0  # Partial automation
                    reasoning = "Partial automation with human oversight indicated"
            
            # IMPACT QUESTIONS - Critical for high scores
            elif 'impact' in question_title and ('economic' in question_title or 'rights' in question_title or 'freedoms' in question_title):
                if risk_indicators['financial'] and risk_indicators['high_impact_decisions']:
                    # Financial decisions with high impact
                    selected_choice_index = len(question['choices']) - 1  # Very high impact
                    reasoning = "Financial decision system with significant economic impact on individuals"
                elif risk_indicators['personal_data'] and risk_indicators['automated_decision']:
                    selected_choice_index = max(2, len(question['choices']) - 2)  # High impact
                    reasoning = "Automated decisions using personal data have high impact potential"
                elif risk_indicators['public_facing']:
                    selected_choice_index = 1  # Moderate impact
                    reasoning = "Public-facing system has moderate impact potential"
                else:
                    selected_choice_index = 0  # Low impact
                    reasoning = "Limited impact indicators in project description"
            
            # REVERSIBILITY QUESTIONS
            elif 'reversible' in question_title:
                if risk_indicators['financial'] and risk_indicators['automated_decision']:
                    selected_choice_index = len(question['choices']) - 2  # Difficult to reverse
                    reasoning = "Financial decisions are typically difficult to reverse"
                elif risk_indicators['high_impact_decisions']:
                    selected_choice_index = 1  # Likely reversible
                    reasoning = "High-impact decisions usually have reversal processes"
                else:
                    selected_choice_index = 0  # Reversible
                    reasoning = "Standard decisions are typically reversible"
            
            # VOLUME AND FREQUENCY QUESTIONS
            elif 'frequency' in question_title or 'volume' in question_title or 'how many' in question_title:
                if risk_indicators['high_volume']:
                    selected_choice_index = len(question['choices']) - 1  # Highest volume option
                    reasoning = "Project description indicates high-volume processing"
                else:
                    selected_choice_index = 0  # Lower volume
                    reasoning = "Standard volume processing indicated"
            
            # SECTOR-SPECIFIC QUESTIONS
            elif any(sector in question_title for sector in ['health', 'economic', 'employment', 'law enforcement', 'licensing', 'social assistance']):
                if risk_indicators['health'] and 'health' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Health-related system identified"
                elif risk_indicators['financial'] and ('economic' in question_title or 'financial' in question_title):
                    selected_choice_index = 0  # Yes
                    reasoning = "Financial/economic system identified"
                elif risk_indicators['employment'] and 'employment' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Employment-related system identified"
                elif risk_indicators['law_enforcement'] and 'law enforcement' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Law enforcement system identified"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Sector not clearly indicated in description"
            
            # ALGORITHM COMPLEXITY AND INTERPRETABILITY
            elif 'algorithm' in question_title and ('interpret' in question_title or 'explain' in question_title or 'secret' in question_title):
                if risk_indicators['ai_ml']:
                    selected_choice_index = 0  # Yes - difficult to interpret
                    reasoning = "AI/ML systems are typically less interpretable"
                else:
                    selected_choice_index = 1  # No - interpretable
                    reasoning = "Rule-based system likely more interpretable"
            
            elif 'continue to learn' in question_title or 'evolve' in question_title:
                if risk_indicators['ai_ml']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Machine learning systems continue to evolve"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Static rule-based system"
            
            # SYSTEM DEVELOPMENT QUESTIONS
            elif 'developed' in question_title or 'who developed' in question_title:
                if risk_indicators['third_party']:
                    # Find third-party option
                    for i, choice in enumerate(question['choices']):
                        if 'third party' in choice['text'].lower() or 'non-government' in choice['text'].lower():
                            selected_choice_index = i
                            break
                    if selected_choice_index is None:
                        selected_choice_index = len(question['choices']) - 1
                    reasoning = "Third-party development indicated in description"
                else:
                    selected_choice_index = 0  # Internal development
                    reasoning = "Internal development assumed"
            
            # DATA AND PRIVACY QUESTIONS
            elif 'personal information' in question_title:
                if risk_indicators['personal_data']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Personal information usage clearly indicated"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "No personal information usage indicated"
            
            elif 'security classification' in question_title:
                if risk_indicators['financial'] or risk_indicators['personal_data']:
                    # Find Protected A or higher
                    for i, choice in enumerate(question['choices']):
                        if 'protected a' in choice['text'].lower():
                            selected_choice_index = i
                            break
                    if selected_choice_index is None:
                        selected_choice_index = 1  # Default to Protected A level
                    reasoning = "Financial/personal data typically requires Protected A classification"
                else:
                    selected_choice_index = 0  # None
                    reasoning = "No sensitive data classification required"
            
            # RISK PROFILE QUESTIONS
            elif 'public scrutiny' in question_title:
                if risk_indicators['financial'] or risk_indicators['public_facing']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Financial/public-facing systems often subject to scrutiny"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Limited public scrutiny expected"
            
            elif 'fraud' in question_title or 'exploitation' in question_title:
                if risk_indicators['financial'] or risk_indicators['personal_data']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Financial/personal data systems are fraud targets"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Limited fraud risk"
            
            # TECHNICAL SYSTEM QUESTIONS
            elif 'accountability' in question_title or 'assigned' in question_title:
                selected_choice_index = 0  # Yes - assume proper governance
                reasoning = "Standard governance practices assumed"
            
            elif 'alternative' in question_title and 'non-automated' in question_title:
                if risk_indicators['full_automation']:
                    selected_choice_index = 1  # No alternative
                    reasoning = "Full automation may lack manual alternatives"
                else:
                    selected_choice_index = 0  # Yes - alternative available
                    reasoning = "Manual alternatives typically available"
            
            elif 'protected characteristics' in question_title:
                if risk_indicators['ai_ml'] and (risk_indicators['employment'] or risk_indicators['financial']):
                    selected_choice_index = 0  # Yes - may consider protected characteristics
                    reasoning = "AI systems in sensitive domains may inadvertently use protected characteristics"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "System designed to avoid protected characteristics"
            
            # MITIGATION AND GOVERNANCE QUESTIONS
            elif 'recourse' in question_title or 'challenge' in question_title:
                if risk_indicators['high_impact_decisions']:
                    selected_choice_index = 0  # Yes
                    reasoning = "High-impact systems typically have recourse processes"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Limited recourse process"
            
            elif 'monitoring' in question_title and 'performance' in question_title:
                if risk_indicators['ai_ml'] or risk_indicators['automated_decision']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Automated systems require performance monitoring"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Limited monitoring for simple systems"
            
            elif 'reasons' in question_title or 'explainable' in question_title:
                if risk_indicators['ai_ml']:
                    selected_choice_index = 1  # No - AI systems often lack explainability
                    reasoning = "AI/ML systems typically lack detailed explainability"
                else:
                    selected_choice_index = 0  # Yes
                    reasoning = "Rule-based systems can provide explanations"
            
            # DEFAULT HANDLING - More nuanced defaults
            if selected_choice_index is None:
                # For yes/no questions, be more risk-aware
                if len(question['choices']) == 2:
                    # If it's a risk question (higher score for "yes"), default to moderate risk
                    if question['choices'][0]['score'] > question['choices'][1]['score']:
                        selected_choice_index = 1  # Lower risk option
                    else:
                        selected_choice_index = 0  # Standard option
                    reasoning = "Conservative default response"
                else:
                    # For multi-choice, default to second option (moderate)
                    selected_choice_index = min(1, len(question['choices']) - 1)
                    reasoning = "Moderate default response based on limited information"
            
            # Ensure index is valid
            selected_choice_index = max(0, min(selected_choice_index, len(question['choices']) - 1))
            selected_choice = question['choices'][selected_choice_index]
            
            auto_responses.append({
                'question_id': question_name,
                'selected_values': [selected_choice['value']],
                'reasoning': reasoning,
                'confidence': 0.8 if "clearly indicated" in reasoning or "identified" in reasoning else 0.6
            })
        
        return auto_responses

    def _generate_analysis_recommendations(self, impact_level: int, score: int) -> List[str]:
        """Generate recommendations based on preliminary analysis."""
        recommendations = []
        
        if impact_level >= 3:
            recommendations.extend([
                "⚠️  HIGH RISK SYSTEM DETECTED - Requires qualified oversight",
                "Implement comprehensive governance framework immediately",
                "Conduct thorough bias testing and mitigation",
                "Establish robust monitoring and audit trails",
                "Plan for external validation and independent oversight"
            ])
        elif impact_level == 2:
            recommendations.extend([
                "Moderate risk system - Enhanced oversight required",
                "Implement bias detection and mitigation measures",
                "Establish clear audit trails and monitoring",
                "Plan regular stakeholder consultations"
            ])
        else:
            recommendations.extend([
                "Lower risk system - Standard procedures apply",
                "Implement basic monitoring and documentation",
                "Establish clear decision-making processes"
            ])
        
        # Add specific recommendations based on score
        if score > 40:
            recommendations.append("Consider if this system truly needs to be fully automated")
        if score > 25:
            recommendations.append("Implement human oversight for high-impact decisions")
        
        return recommendations

    def _functional_preview(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle functional preview requests - early risk assessment focused on technical characteristics."""
        # WORKFLOW ENFORCEMENT: Check if introduction has been shown
        intro_check = self._check_introduction_requirement()
        if intro_check:
            return intro_check

        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")

        logger.info(f"Functional preview for project: {project_name}")

        # Validate project description adequacy for framework assessment
        validation_result = self.description_validator.validate_description(project_description)
        if not validation_result["is_valid"]:
            return {
                "assessment": {
                    "status": "validation_failed",
                    "message": "❌ Insufficient project description for AIA functional preview",
                    "validation_details": validation_result,
                    "required_action": "Use 'validate_project_description' tool to check requirements and improve description"
                },
                "framework_readiness": validation_result["framework_readiness"],
                "recommendations": [
                    "Project description does not meet minimum requirements for AIA functional preview",
                    "Please provide more detailed information covering the missing areas",
                    "Use the 'validate_project_description' tool to check specific requirements",
                    "Re-run functional preview after improving the description"
                ]
            }

        # Perform functional analysis focusing on technical characteristics
        functional_responses = self._functional_risk_analysis(project_description)
        
        # Calculate functional risk score
        functional_score = self.aia_processor.calculate_score(functional_responses)
        
        # Analyze gaps and categorize by priority
        gap_analysis = self._analyze_gaps(functional_responses, project_description)
        
        # Generate planning intelligence
        planning_guidance = self._generate_planning_guidance(functional_score, project_description)
        
        # Calculate score sensitivity analysis
        score_sensitivity = self._calculate_score_sensitivity(functional_score, gap_analysis)
        
        # Determine likely impact level range
        base_impact_level, _, _ = self.aia_processor.determine_impact_level(functional_score)
        likely_range = self._estimate_impact_level_range(functional_score, gap_analysis)
        
        return {
            "mcp_official_data": {
                "data_source": "🔧 MCP SERVER (Official): Canada.ca AIA framework calculations",
                "functional_risk_score": functional_score,
                "score_range": f"{likely_range['min_score']}-{likely_range['max_score']}",
                "likely_impact_level": f"Level {self._get_impact_level_roman(base_impact_level)}",
                "scoring_methodology": "Official AIA framework formula using government-verified question weights",
                "compliance_note": "Score calculated using official Treasury Board Directive methodology"
            },
            "ai_generated_analysis": {
                "data_source": "🧠 CLAUDE ANALYSIS (AI-Generated): Interpretations and recommendations",
                "project_name": project_name,
                "project_description": project_description,
                "confidence": "High - based on functional characteristics",
                "critical_gaps": gap_analysis['critical'],
                "important_gaps": gap_analysis['important'],
                "administrative_gaps": gap_analysis['administrative'],
                "planning_guidance": planning_guidance,
                "score_sensitivity": score_sensitivity,
                "ai_interpretation_note": "Gap analysis and recommendations generated by AI based on official scores"
            },
            "compliance_warnings": {
                "disclaimer": "⚠️ Early Indicator - Not Official Assessment. Based on functional characteristics only. Final assessment requires complete stakeholder input.",
                "professional_validation": "⚠️ Results require validation by qualified professionals",
                "regulatory_compliance": "⚠️ Official scores come from MCP server - AI provides interpretation only"
            }
        }
    

    def _functional_risk_analysis(self, project_description: str) -> List[Dict[str, Any]]:
        """Analyze project for functional risk characteristics, focusing ONLY on clearly detectable technical aspects."""
        auto_responses = []
        description_lower = project_description.lower()
        
        # Enhanced functional risk indicators
        risk_indicators = {
            'high_volume': any(term in description_lower for term in ['thousands', 'millions', 'large scale', 'mass', 'bulk', 'daily', 'hourly', 'real-time', 'continuous']),
            'personal_data': any(term in description_lower for term in ['personal', 'private', 'confidential', 'sensitive', 'pii', 'credit', 'income', 'employment history', 'financial information']),
            'financial': any(term in description_lower for term in ['financial', 'money', 'payment', 'economic', 'benefit', 'tax', 'loan', 'credit', 'bank', 'mortgage', 'insurance']),
            'health': any(term in description_lower for term in ['health', 'medical', 'healthcare', 'patient', 'treatment', 'diagnosis', 'clinical']),
            'employment': any(term in description_lower for term in ['employment', 'hiring', 'job', 'recruitment', 'hr', 'resume', 'candidate']),
            'law_enforcement': any(term in description_lower for term in ['police', 'criminal', 'law enforcement', 'investigation', 'security', 'surveillance']),
            'ai_ml': any(term in description_lower for term in ['ai', 'artificial intelligence', 'machine learning', 'neural', 'deep learning', 'algorithm', 'model', 'trained']),
            'automated_decision': any(term in description_lower for term in ['automated', 'automatic', 'decision', 'approve', 'deny', 'reject', 'classify', 'determine', 'final decision', 'without human review']),
            'third_party': any(term in description_lower for term in ['third party', 'third-party', 'vendor', 'contractor', 'external', 'bureau', 'service']),
            'public_facing': any(term in description_lower for term in ['public', 'citizen', 'client', 'customer', 'user', 'applicant', 'individual']),
            'full_automation': any(term in description_lower for term in ['without human review', 'automatically approve', 'automatically deny', 'final decision', 'no human intervention']),
            'real_time': any(term in description_lower for term in ['real-time', 'real time', 'immediate', 'instant', 'live']),
            'high_impact_decisions': any(term in description_lower for term in ['approve', 'deny', 'reject', 'grant', 'refuse', 'determine eligibility']),
            'simple_classification': any(term in description_lower for term in ['categorize', 'classify', 'sort', 'organize']) and not any(term in description_lower for term in ['approve', 'deny', 'reject', 'decision']),
            'human_review': any(term in description_lower for term in ['reviewed by', 'human staff', 'manual review', 'human oversight', 'staff review'])
        }
        
        # Get all questions for analysis
        questions_by_name = {q['name']: q for q in self.aia_processor.scorable_questions}
        
        # ONLY answer questions where we have clear functional evidence - be very selective
        for question in self.aia_processor.scorable_questions:
            question_name = question['name']
            question_title = question['title'].lower()
            
            # Skip if no choices available
            if not question.get('choices'):
                continue
            
            selected_choice_index = None
            reasoning = ""
            
            # ONLY ANSWER QUESTIONS WITH CLEAR FUNCTIONAL EVIDENCE
            
            # Automation Type - Only if clearly stated
            if 'type of automation' in question_title or 'automation you are planning' in question_title:
                if risk_indicators['full_automation']:
                    selected_choice_index = len(question['choices']) - 1  # Full automation
                    reasoning = "Full automation clearly stated - no human review mentioned"
                elif risk_indicators['human_review']:
                    selected_choice_index = 0  # Partial automation
                    reasoning = "Human review explicitly mentioned"
                elif risk_indicators['automated_decision'] and not risk_indicators['human_review']:
                    selected_choice_index = max(1, len(question['choices']) - 2)  # Mostly automated
                    reasoning = "Automated decisions mentioned without explicit human review"
                # Skip if unclear
            
            # Economic Impact - Only for clearly financial systems
            elif 'economic interests' in question_title and 'impact' in question_title:
                if risk_indicators['financial'] and risk_indicators['high_impact_decisions']:
                    selected_choice_index = len(question['choices']) - 1  # Very high impact
                    reasoning = "Financial decisions with clear economic consequences"
                elif risk_indicators['financial']:
                    selected_choice_index = max(1, len(question['choices']) - 2)  # High impact
                    reasoning = "Financial system with economic impact"
                # Skip if not clearly financial
            
            # Rights/Freedoms Impact - Only for high-impact systems
            elif 'rights or freedoms' in question_title and 'impact' in question_title:
                if risk_indicators['financial'] and risk_indicators['automated_decision']:
                    selected_choice_index = len(question['choices']) - 1  # Very high impact
                    reasoning = "Automated financial decisions impact individual rights"
                elif risk_indicators['employment'] or risk_indicators['health']:
                    selected_choice_index = max(1, len(question['choices']) - 2)  # High impact
                    reasoning = "Employment/health system impacts individual rights"
                # Skip if impact unclear
            
            # Personal Information - Only if explicitly mentioned
            elif 'personal information' in question_title:
                if risk_indicators['personal_data']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Personal information usage explicitly mentioned"
                elif risk_indicators['simple_classification'] and not risk_indicators['personal_data']:
                    selected_choice_index = 1  # No
                    reasoning = "Simple classification without personal data"
                # Skip if unclear
            
            # Algorithm Interpretability - Only for AI/ML systems
            elif 'difficult to interpret' in question_title or 'explain' in question_title:
                if risk_indicators['ai_ml']:
                    selected_choice_index = 0  # Yes - difficult to interpret
                    reasoning = "AI/ML system mentioned - typically less interpretable"
                elif risk_indicators['simple_classification']:
                    selected_choice_index = 1  # No - interpretable
                    reasoning = "Simple classification system - likely interpretable"
                # Skip if system type unclear
            
            # Learning Algorithm - Only for AI/ML systems
            elif 'continue to learn' in question_title or 'evolve' in question_title:
                if risk_indicators['ai_ml']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Machine learning system mentioned"
                elif risk_indicators['simple_classification']:
                    selected_choice_index = 1  # No
                    reasoning = "Simple rule-based classification system"
                # Skip if unclear
            
            # Volume/Frequency - Only if clearly stated
            elif 'frequency' in question_title or 'volume' in question_title or 'how many' in question_title:
                if risk_indicators['high_volume']:
                    selected_choice_index = len(question['choices']) - 1  # High volume
                    reasoning = "High volume processing explicitly mentioned"
                # Skip if volume not mentioned
            
            # Sector-specific - Only if clearly in that sector
            elif any(sector in question_title for sector in ['health', 'economic', 'employment', 'law enforcement']):
                if risk_indicators['health'] and 'health' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Healthcare system clearly identified"
                elif risk_indicators['financial'] and ('economic' in question_title or 'financial' in question_title):
                    selected_choice_index = 0  # Yes
                    reasoning = "Financial system clearly identified"
                elif risk_indicators['employment'] and 'employment' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Employment system clearly identified"
                elif risk_indicators['law_enforcement'] and 'law enforcement' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Law enforcement system clearly identified"
                # Skip if sector unclear
            
            # Third-party development - Only if explicitly mentioned
            elif 'developed' in question_title or 'who developed' in question_title:
                if risk_indicators['third_party']:
                    # Find third-party option
                    for i, choice in enumerate(question['choices']):
                        if 'third party' in choice['text'].lower() or 'non-government' in choice['text'].lower():
                            selected_choice_index = i
                            break
                    if selected_choice_index is not None:
                        reasoning = "Third-party development explicitly mentioned"
                # Skip if development source unclear
            
            # Real-time processing - Only if explicitly mentioned
            elif 'real-time' in question_title or 'immediate' in question_title:
                if risk_indicators['real_time']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Real-time processing explicitly mentioned"
                # Skip if timing unclear
            
            # Skip all other questions - don't make assumptions
            
            # Only add response if we found clear evidence
            if selected_choice_index is not None:
                # Ensure index is valid
                selected_choice_index = max(0, min(selected_choice_index, len(question['choices']) - 1))
                selected_choice = question['choices'][selected_choice_index]
                
                auto_responses.append({
                    'question_id': question_name,
                    'selected_values': [selected_choice['value']],
                    'reasoning': reasoning,
                    'confidence': 0.9,  # High confidence since we only answer with clear evidence
                    'is_functional': True
                })
        
        return auto_responses
    

    def _analyze_gaps(self, functional_responses: List[Dict[str, Any]], project_description: str) -> Dict[str, List[str]]:
        """Analyze gaps and categorize by impact priority."""
        answered_questions = {r['question_id'] for r in functional_responses}
        questions_by_name = {q['name']: q for q in self.aia_processor.scorable_questions}
        
        critical_gaps = []
        important_gaps = []
        administrative_gaps = []
        
        # Define critical questions that would significantly change the score
        critical_question_patterns = [
            'policy or legal authority',
            'bias testing',
            'stakeholder consultation',
            'impact assessment',
            'protected characteristics'
        ]
        
        # Define important questions that affect compliance planning
        important_question_patterns = [
            'oversight',
            'appeal',
            'monitoring',
            'audit',
            'training'
        ]
        
        for question in self.aia_processor.scorable_questions:
            if question['name'] not in answered_questions:
                question_title = question['title'].lower()
                
                # Categorize based on question content and potential impact
                if any(pattern in question_title for pattern in critical_question_patterns):
                    critical_gaps.append(question['title'])
                elif any(pattern in question_title for pattern in important_question_patterns):
                    important_gaps.append(question['title'])
                elif question.get('max_score', 0) > 2:  # High-scoring questions are important
                    important_gaps.append(question['title'])
                else:
                    administrative_gaps.append(question['title'])
        
        return {
            'critical': critical_gaps[:5],  # Limit to top 5
            'important': important_gaps[:7],  # Limit to top 7
            'administrative': administrative_gaps[:5]  # Limit to top 5
        }
    

    def _generate_planning_guidance(self, functional_score: int, project_description: str) -> List[str]:
        """Generate actionable planning guidance based on functional risk score."""
        guidance = []
        description_lower = project_description.lower()
        
        # Risk indicators for guidance
        is_financial = any(term in description_lower for term in ['financial', 'loan', 'credit', 'bank'])
        is_ai_ml = any(term in description_lower for term in ['ai', 'machine learning', 'neural'])
        is_high_volume = any(term in description_lower for term in ['thousands', 'daily', 'real-time'])
        is_automated = any(term in description_lower for term in ['automated', 'without human review'])
        
        # Score-based guidance
        if functional_score >= 40:
            guidance.extend([
                "🚨 HIGH RISK: Budget for comprehensive governance framework",
                "Plan for qualified oversight committee and external validation",
                "Expect quarterly bias assessments and continuous monitoring requirements",
                "Allocate resources for extensive stakeholder consultation process"
            ])
        elif functional_score >= 25:
            guidance.extend([
                "⚠️ MODERATE-HIGH RISK: Plan for enhanced oversight procedures",
                "Budget for regular bias testing and mitigation measures",
                "Expect monthly monitoring and reporting requirements",
                "Plan stakeholder engagement and consultation processes"
            ])
        elif functional_score >= 15:
            guidance.extend([
                "📋 MODERATE RISK: Implement standard oversight procedures",
                "Plan for basic bias detection and monitoring systems",
                "Expect quarterly reviews and documentation requirements"
            ])
        else:
            guidance.extend([
                "✅ LOWER RISK: Standard operational procedures apply",
                "Implement basic monitoring and documentation systems"
            ])
        
        # Specific guidance based on system characteristics
        if is_financial:
            guidance.append("💰 Financial systems: Plan for enhanced audit trails and appeals processes")
        
        if is_ai_ml:
            guidance.append("🤖 AI/ML systems: Budget for explainability tools and bias testing infrastructure")
        
        if is_high_volume:
            guidance.append("📊 High-volume systems: Plan for automated monitoring and alerting systems")
        
        if is_automated:
            guidance.append("⚙️ Automated decisions: Implement human oversight checkpoints and exception handling")
        
        return guidance
    


    # Question and Score Helper Methods

    def _get_question_category(self, question_name: str) -> str:
        """Get the display category for a question."""
        # Map internal categories to display categories
        for category, questions in self.aia_processor.question_categories.items():
            if question_name in questions:
                if category == 'technical':
                    return 'System'  # Most technical questions are system-related
                elif category == 'impact_risk':
                    return 'Impact'
                elif category == 'manual':
                    return 'Project'
        return 'System'  # Default
    

    def _get_impact_level_roman(self, impact_level: int) -> str:
        """Convert impact level number to Roman numeral."""
        roman_map = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
        return roman_map.get(impact_level, 'I')
    

    def _get_design_phase_questions(self) -> List[Dict[str, Any]]:
        """Filter questions to only include those visible in Design phase.
        
        Based on survey-enfr.json analysis, Design phase users see questions that are either:
        1. Always visible (no visibleIf condition), OR
        2. Have visibleIf condition "{projectDetailsPhase} = \"item1\"" (Design phase)
        
        This excludes questions that are only visible in Implementation phase.
        """
        # Load the survey data to check visibility conditions
        try:
            with open('data/survey-enfr.json', 'r', encoding='utf-8') as f:
                survey_data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load survey data for phase filtering: {e}")
            # Fallback to all questions if we can't load the survey data
            return self.aia_processor.scorable_questions
        
        # Find pages that are Implementation-only (have visibleIf with item2)
        implementation_only_pages = set()
        
        # Check each page for visibility conditions
        for page in survey_data.get('pages', []):
            page_name = page.get('name', '')
            page_visible_if = page.get('visibleIf', '')
            
            # Check if this page is only visible in Implementation phase
            if '{projectDetailsPhase} = "item2"' in page_visible_if:
                implementation_only_pages.add(page_name)
                logger.info(f"Found Implementation-only page: {page_name}")
        
        # Extract all question names, excluding those from Implementation-only pages
        design_phase_question_names = set()
        

    def _get_questions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests for questions by category or type."""
        category = arguments.get("category")
        question_type = arguments.get("type")
        
        logger.info(f"Retrieving questions - category: {category}, type: {question_type}")
        
        # Get Design phase questions only (not all 162 questions)
        all_questions = self._get_design_phase_questions()
        
        # Filter by category if specified
        if category:
            # Map category names to our internal categories
            category_map = {
                "Project": "manual",
                "System": "technical", 
                "Algorithm": "technical",
                "Decision": "impact_risk",
                "Impact": "impact_risk",
                "Data": "technical",
                "Consultations": "manual",
                "De-risking": "manual"
            }
            
            internal_category = category_map.get(category, "manual")
            category_questions = self.aia_processor.question_categories.get(internal_category, [])
            
            # Get full question details
            questions_by_name = {q['name']: q for q in all_questions}
            filtered_questions = []
            
            for question_name in category_questions:
                if question_name in questions_by_name:
                    filtered_questions.append(questions_by_name[question_name])
            
            all_questions = filtered_questions
        
        # Filter by type if specified (risk vs mitigation)
        if question_type:
            if question_type == "risk":
                # Return questions that contribute to risk scoring
                all_questions = [q for q in all_questions if q.get('max_score', 0) > 0]
            elif question_type == "mitigation":
                # Return questions about mitigation measures
                all_questions = [q for q in all_questions if 'mitigation' in q.get('title', '').lower() or 'measure' in q.get('title', '').lower()]
        
        return {
            "questions": all_questions[:20],  # Limit to first 20 questions
            "total_available": len(all_questions),
            "filters_applied": {
                "category": category,
                "type": question_type
            },
            "framework_info": {
                "name": "Canada's Algorithmic Impact Assessment (Design Phase)",
                "total_questions": len(self._get_design_phase_questions()),
                "max_possible_score": sum(q['max_score'] for q in self._get_design_phase_questions())
            }
        }
    

    def _get_questions_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle questions summary requests."""
        logger.info("Retrieving questions summary")
        
        # Use Design phase questions for summary calculation
        design_phase_questions = self._get_design_phase_questions()
        
        # Calculate summary based on Design phase questions only
        total_questions = len(design_phase_questions)
        max_possible_score = sum(q['max_score'] for q in design_phase_questions)
        
        # Count questions by type
        risk_questions = len([q for q in design_phase_questions if q.get('max_score', 0) > 0])
        mitigation_questions = total_questions - risk_questions
        
        summary = {
            "total_questions": total_questions,
            "risk_questions": risk_questions,
            "mitigation_questions": mitigation_questions,
            "max_possible_score": max_possible_score,
            "framework": "Canada's Algorithmic Impact Assessment (Design Phase)"
        }
        
        return {
            "success": True,
            "summary": summary
        }
    

    def _get_questions_by_category(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests for questions by category."""
        category = arguments.get("category", "")
        limit = arguments.get("limit")
        
        logger.info(f"Retrieving {category} questions")
        
        # Get questions from the specified category
        category_questions = self.aia_processor.question_categories.get(category, [])
        
        if limit:
            category_questions = category_questions[:limit]
        
        # Get full question details (Design phase only)
        design_phase_questions = self._get_design_phase_questions()
        questions_by_name = {q['name']: q for q in design_phase_questions}
        detailed_questions = []
        
        for question_name in category_questions:
            if question_name in questions_by_name:
                detailed_questions.append(questions_by_name[question_name])
        
        return {
            "success": True,
            "category": category,
            "total_in_category": len(self.aia_processor.question_categories.get(category, [])),
            "returned_count": len(detailed_questions),
            "questions": detailed_questions
        }
    

    def _calculate_assessment_score(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle score calculation requests."""
        responses = arguments.get("responses", [])
        
        logger.info(f"Calculating score for {len(responses)} responses")
        
        # Use the existing AIAProcessor logic
        total_score = self.aia_processor.calculate_score(responses)
        level, level_name, level_description = self.aia_processor.determine_impact_level(total_score)
        
        # Use Design phase questions for max score calculation
        design_phase_questions = self._get_design_phase_questions()
        max_possible_score = sum(q['max_score'] for q in design_phase_questions)
        
        return {
            "success": True,
            "calculation": {
                "total_score": total_score,
                "responses_processed": len(responses),
                "max_possible_score": max_possible_score,
                "impact_level": level,
                "level_name": level_name,
                "level_description": level_description
            }
        }


    def _calculate_score_sensitivity(self, base_score: int, gap_analysis: Dict[str, List[str]]) -> Dict[str, str]:
        """Calculate how the score might change based on critical gaps."""
        sensitivity = {}
        
        # Estimate impact of critical gaps
        if gap_analysis['critical']:
            if any('policy' in gap.lower() or 'authority' in gap.lower() for gap in gap_analysis['critical']):
                new_score = base_score + 3
                new_level = self.aia_processor.determine_impact_level(new_score)[0]
                sensitivity['if_policy_authority_needed'] = f"+3 points → likely Level {self._get_impact_level_roman(new_level)}"
            
            if any('bias' in gap.lower() for gap in gap_analysis['critical']):
                sensitivity['if_no_bias_testing'] = "+2-5 points depending on system complexity"
            
            if any('consultation' in gap.lower() for gap in gap_analysis['critical']):
                sensitivity['if_limited_consultation'] = "+1-3 points depending on stakeholder impact"
        
        # Overall range estimate
        min_additional = 0
        max_additional = len(gap_analysis['critical']) * 2 + len(gap_analysis['important']) * 1
        
        if max_additional > 0:
            min_score = base_score + min_additional
            max_score = base_score + max_additional
            sensitivity['overall_range'] = f"Final score likely {min_score}-{max_score} points after complete assessment"
        
        return sensitivity
    

    def _estimate_impact_level_range(self, base_score: int, gap_analysis: Dict[str, List[str]]) -> Dict[str, int]:
        """Estimate the likely range of final impact levels."""
        # Conservative estimate: assume some critical gaps will add points
        min_additional = 0
        max_additional = len(gap_analysis['critical']) * 2 + len(gap_analysis['important']) * 1
        
        min_score = base_score + min_additional
        max_score = min(base_score + max_additional, 100)  # Cap at reasonable maximum
        
        return {
            'min_score': min_score,
            'max_score': max_score
        }

    # AIA Data Extraction Methods (delegate to AIADataExtractor)


