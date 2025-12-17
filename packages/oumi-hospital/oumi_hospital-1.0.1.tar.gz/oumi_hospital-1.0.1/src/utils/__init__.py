"""
🏥 Oumi Hospital Utilities

Wrapper functions and utilities for Oumi API integration.
"""

from .oumi_integration import (
    OumiInferenceWrapper,
    OumiEvaluationWrapper,
    OumiSynthesisWrapper,
    OumiTrainingWrapper,
    DiagnosisResult,
    SkillPreservationResult,
    create_conversation_from_prompt,
    extract_response_from_conversation,
    calculate_failure_rate,
    classify_severity
)

from .console import (
    HospitalConsole,
    hospital_console,
    HOSPITAL_THEME,
    HOSPITAL_SPINNERS,
    print_header,
    print_agent_banner,
    print_success,
    print_warning,
    print_error,
    print_info
)

from .logging_config import (
    setup_hospital_logging,
    get_hospital_logger,
    log_agent_action,
    log_oumi_api_call,
    log_performance_metric,
    get_default_logger,
    AgentLogContext
)

__all__ = [
    # Oumi Integration
    "OumiInferenceWrapper",
    "OumiEvaluationWrapper", 
    "OumiSynthesisWrapper",
    "OumiTrainingWrapper",
    "DiagnosisResult",
    "SkillPreservationResult",
    "create_conversation_from_prompt",
    "extract_response_from_conversation",
    "calculate_failure_rate",
    "classify_severity",
    
    # Console
    "HospitalConsole",
    "hospital_console",
    "HOSPITAL_THEME", 
    "HOSPITAL_SPINNERS",
    "print_header",
    "print_agent_banner",
    "print_success",
    "print_warning",
    "print_error",
    "print_info",
    
    # Logging
    "setup_hospital_logging",
    "get_hospital_logger",
    "log_agent_action", 
    "log_oumi_api_call",
    "log_performance_metric",
    "get_default_logger",
    "AgentLogContext"
]