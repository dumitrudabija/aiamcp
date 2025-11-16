"""
Framework Detection Module

Provides smart detection of which regulatory framework (AIA or OSFI E-23)
is relevant based on user context and session state.

This module was extracted from server.py as part of Phase 1 refactoring
to reduce complexity and improve code organization.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class FrameworkDetector:
    """
    Detects which regulatory framework to emphasize based on context.

    Supports:
    - AIA (Algorithmic Impact Assessment) for government systems
    - OSFI E-23 (Model Risk Management) for financial institutions
    - Combined mode when both frameworks apply
    """

    # OSFI E-23 indicators (financial institutions)
    OSFI_KEYWORDS = [
        'osfi', 'e-23', 'e23', 'guideline e-23',
        'bank', 'financial institution', 'credit union', 'insurance',
        'model risk', 'basel', 'regulatory capital',
        'credit risk model', 'credit scoring', 'lending model',
        'financial model', 'risk rating', 'model governance'
    ]

    # AIA indicators (government/public sector)
    AIA_KEYWORDS = [
        'aia', 'algorithmic impact', 'impact assessment',
        'government', 'federal', 'public service', 'public sector',
        'automated decision', 'treasury board', 'canada.ca',
        'government service', 'benefits', 'eligibility',
        'administrative decision'
    ]

    # Combined indicators (need both frameworks)
    COMBINED_KEYWORDS = [
        'both frameworks', 'aia and osfi', 'osfi and aia',
        'government and bank', 'combined assessment',
        'both assessments'
    ]

    def __init__(self, workflow_engine=None):
        """
        Initialize framework detector.

        Args:
            workflow_engine: Optional WorkflowEngine instance for session-based detection
        """
        self.workflow_engine = workflow_engine

    def detect(self, user_context: str = "", session_id: Optional[str] = None) -> str:
        """
        Detect which framework to emphasize based on user context and session state.

        Args:
            user_context: User's statement or project context
            session_id: Optional session ID to check for existing workflow type

        Returns:
            'aia' | 'osfi_e23' | 'both'
        """
        # First, check if there's an existing session with a defined assessment type
        if session_id and self.workflow_engine and hasattr(self.workflow_engine, 'sessions'):
            if session_id in self.workflow_engine.sessions:
                session = self.workflow_engine.sessions[session_id]
                assessment_type = session.get('assessment_type', '')

                if 'aia' in assessment_type.lower():
                    logger.info(f"Framework detection: 'aia' (from session {session_id})")
                    return 'aia'
                elif 'osfi' in assessment_type.lower():
                    logger.info(f"Framework detection: 'osfi_e23' (from session {session_id})")
                    return 'osfi_e23'

        # If no session or no clear type, use keyword detection
        if user_context:
            context_lower = user_context.lower()

            # Check for combined first (most specific)
            if any(kw in context_lower for kw in self.COMBINED_KEYWORDS):
                logger.info("Framework detection: 'both' (explicit combined request)")
                return 'both'

            # Count keyword matches for each framework
            osfi_matches = sum(1 for kw in self.OSFI_KEYWORDS if kw in context_lower)
            aia_matches = sum(1 for kw in self.AIA_KEYWORDS if kw in context_lower)

            # If one framework has significantly more matches, choose it
            if osfi_matches > aia_matches and osfi_matches >= 1:
                logger.info(f"Framework detection: 'osfi_e23' ({osfi_matches} keyword matches)")
                return 'osfi_e23'
            elif aia_matches > osfi_matches and aia_matches >= 1:
                logger.info(f"Framework detection: 'aia' ({aia_matches} keyword matches)")
                return 'aia'

        # Default: show both if context is unclear
        logger.info("Framework detection: 'both' (default - unclear context)")
        return 'both'
