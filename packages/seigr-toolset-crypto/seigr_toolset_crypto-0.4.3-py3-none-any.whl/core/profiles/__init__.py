"""
Core Profiles Module

Provides security profiles system for STC v0.4.0.
Offers automated, pattern-based profile selection for various use cases.
"""

from .security_profiles import (
    SecurityProfile,
    ProfileParameters,
    SecurityProfileManager,
    get_profile_for_file,
    get_optimized_parameters,
    recommend_profile_interactive
)

from .profile_definitions import (
    AdvancedProfileManager,
    ContentAnalyzer
)

__all__ = [
    'SecurityProfile',
    'ProfileParameters', 
    'SecurityProfileManager',
    'get_profile_for_file',
    'get_optimized_parameters',
    'recommend_profile_interactive',
    'AdvancedProfileManager',
    'ContentAnalyzer'
]