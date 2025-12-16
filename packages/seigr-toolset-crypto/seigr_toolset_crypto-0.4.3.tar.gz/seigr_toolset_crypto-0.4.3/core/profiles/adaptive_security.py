"""
Adaptive Security System v0.3.1

Dynamic security adaptation based on content analysis, threat assessment,
and operational context. Provides intelligent security level adjustment.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .profile_definitions import (
    ContentAnalyzer, AdvancedProfileManager
)

class ThreatLevel(Enum):
    """Threat assessment levels"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    EXTREME = "extreme"

class OperationalContext(Enum):
    """Operational context types"""
    DEVELOPMENT = "development"        # Development/testing environment
    STAGING = "staging"               # Staging environment
    PRODUCTION = "production"         # Production environment
    BACKUP = "backup"                # Backup operation
    ARCHIVE = "archive"              # Long-term archival
    SHARING = "sharing"              # File sharing/transfer
    STORAGE = "storage"              # Long-term storage
    PROCESSING = "processing"        # Data processing/analysis

class EnvironmentRisk(Enum):
    """Environment risk assessment"""
    SECURE = "secure"                # Secure, controlled environment
    TRUSTED = "trusted"              # Trusted environment
    STANDARD = "standard"            # Standard security environment
    ELEVATED = "elevated"            # Elevated risk environment
    HOSTILE = "hostile"              # Potentially hostile environment
    UNKNOWN = "unknown"              # Unknown risk level

@dataclass
class SecurityContext:
    """Complete security context information"""
    
    # Content context
    content_sensitivity: str = "medium"
    content_type: str = "unknown"
    content_size: int = 0
    content_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Threat context
    threat_level: ThreatLevel = ThreatLevel.MODERATE
    threat_indicators: List[str] = field(default_factory=list)
    threat_assessment: Dict[str, Any] = field(default_factory=dict)
    
    # Operational context
    operation_type: OperationalContext = OperationalContext.STORAGE
    environment_risk: EnvironmentRisk = EnvironmentRisk.STANDARD
    time_sensitivity: str = "standard"  # "immediate", "standard", "batch"
    
    # User context
    user_preference: str = "balanced"   # "security", "balanced", "performance"
    compliance_requirements: List[str] = field(default_factory=list)
    
    # System context
    system_resources: str = "normal"    # "limited", "normal", "abundant"
    network_conditions: str = "stable"  # "unstable", "stable", "high_bandwidth"
    
    # Temporal context
    timestamp: datetime = field(default_factory=datetime.now)
    expiry_duration: Optional[timedelta] = None
    
    # Historical context
    previous_operations: List[Dict[str, Any]] = field(default_factory=list)
    learning_enabled: bool = True

class ThreatAssessment:
    """Comprehensive threat assessment system"""
    
    # Known threat indicators
    HIGH_RISK_PATTERNS = [
        # Network indicators
        r'(?i)(malware|virus|trojan|backdoor)',
        r'(?i)(phishing|social.engineering)',
        r'(?i)(data.breach|credential.dump)',
        
        # Content indicators
        r'(?i)(ransomware|encrypt.*demand)',
        r'(?i)(suspicious.*activity|anomal)',
        r'(?i)(unauthorized.*access)',
        
        # System indicators
        r'(?i)(privilege.*escalation)',
        r'(?i)(buffer.*overflow|injection)',
        r'(?i)(rootkit|keylogger)',
    ]
    
    MEDIUM_RISK_PATTERNS = [
        # Network activity
        r'(?i)(unusual.*traffic|spike)',
        r'(?i)(failed.*login|authentication)',
        r'(?i)(scan|probe|reconnaissance)',
        
        # File activity
        r'(?i)(suspicious.*file|unknown.*source)',
        r'(?i)(modified.*system|altered)',
        r'(?i)(unexpected.*behavior)',
    ]
    
    # Risk scoring weights
    RISK_WEIGHTS = {
        'content_sensitivity': 0.3,
        'environment_risk': 0.25,
        'threat_indicators': 0.2,
        'operational_context': 0.15,
        'temporal_factors': 0.1
    }
    
    @classmethod
    def assess_threats(cls, context: SecurityContext, 
                      additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive threat assessment"""
        
        assessment = {
            'overall_threat_level': ThreatLevel.MODERATE,
            'threat_score': 0.5,
            'risk_factors': [],
            'mitigation_recommendations': [],
            'confidence': 0.7,
            'assessment_details': {}
        }
        
        # Content-based threat assessment
        content_threats = cls._assess_content_threats(context)
        assessment['assessment_details']['content_threats'] = content_threats
        
        # Environment-based assessment
        env_threats = cls._assess_environment_threats(context)
        assessment['assessment_details']['environment_threats'] = env_threats
        
        # Operational context assessment
        op_threats = cls._assess_operational_threats(context)
        assessment['assessment_details']['operational_threats'] = op_threats
        
        # Temporal assessment
        temporal_threats = cls._assess_temporal_threats(context)
        assessment['assessment_details']['temporal_threats'] = temporal_threats
        
        # Historical pattern analysis
        if context.learning_enabled and context.previous_operations:
            historical_threats = cls._assess_historical_patterns(context)
            assessment['assessment_details']['historical_threats'] = historical_threats
        
        # Calculate overall threat score
        threat_score = cls._calculate_threat_score(assessment['assessment_details'])
        assessment['threat_score'] = threat_score
        assessment['overall_threat_level'] = cls._score_to_threat_level(threat_score)
        
        # Generate mitigation recommendations
        assessment['mitigation_recommendations'] = cls._generate_mitigation_recommendations(
            assessment['overall_threat_level'], assessment['assessment_details']
        )
        
        # Extract risk factors
        assessment['risk_factors'] = cls._extract_risk_factors(assessment['assessment_details'])
        
        return assessment
    
    @classmethod
    def _assess_content_threats(cls, context: SecurityContext) -> Dict[str, Any]:
        """Assess threats based on content analysis"""
        
        threats = {
            'sensitivity_risk': 0.0,
            'content_indicators': [],
            'encryption_status': 'unknown',
            'integrity_concerns': []
        }
        
        # Sensitivity-based risk
        sensitivity = context.content_sensitivity
        if sensitivity == 'maximum':
            threats['sensitivity_risk'] = 0.9
        elif sensitivity == 'high':
            threats['sensitivity_risk'] = 0.7
        elif sensitivity == 'medium':
            threats['sensitivity_risk'] = 0.4
        else:
            threats['sensitivity_risk'] = 0.2
        
        # Content analysis indicators
        if context.content_analysis:
            analysis = context.content_analysis
            
            # Check for existing encryption
            if analysis.get('encryption_detected', False):
                threats['encryption_status'] = 'already_encrypted'
                threats['content_indicators'].append('pre_encrypted_content')
            
            # Check for suspicious patterns
            if 'analysis_details' in analysis:
                details = analysis['analysis_details']
                if details.get('filename_indicators', {}).get('security_indicators'):
                    threats['content_indicators'].extend(
                        details['filename_indicators']['security_indicators']
                    )
        
        return threats
    
    @classmethod
    def _assess_environment_threats(cls, context: SecurityContext) -> Dict[str, Any]:
        """Assess environment-based threats"""
        
        threats = {
            'environment_risk_score': 0.0,
            'risk_factors': [],
            'network_concerns': [],
            'system_concerns': []
        }
        
        # Environment risk mapping
        risk_mapping = {
            EnvironmentRisk.SECURE: 0.1,
            EnvironmentRisk.TRUSTED: 0.2,
            EnvironmentRisk.STANDARD: 0.4,
            EnvironmentRisk.ELEVATED: 0.7,
            EnvironmentRisk.HOSTILE: 0.9,
            EnvironmentRisk.UNKNOWN: 0.6
        }
        
        threats['environment_risk_score'] = risk_mapping.get(context.environment_risk, 0.5)
        
        # Environment-specific concerns
        if context.environment_risk in [EnvironmentRisk.HOSTILE, EnvironmentRisk.ELEVATED]:
            threats['risk_factors'].extend([
                'high_risk_environment',
                'enhanced_security_required'
            ])
        
        if context.environment_risk == EnvironmentRisk.UNKNOWN:
            threats['risk_factors'].append('unknown_environment_risk')
        
        # Network condition concerns
        if context.network_conditions == 'unstable':
            threats['network_concerns'].append('network_reliability_issues')
        
        # System resource concerns
        if context.system_resources == 'limited':
            threats['system_concerns'].append('resource_constraints_may_affect_security')
        
        return threats
    
    @classmethod
    def _assess_operational_threats(cls, context: SecurityContext) -> Dict[str, Any]:
        """Assess operational context threats"""
        
        threats = {
            'operation_risk_score': 0.0,
            'context_factors': [],
            'compliance_gaps': [],
            'operational_recommendations': []
        }
        
        # Operation type risk mapping
        operation_risks = {
            OperationalContext.DEVELOPMENT: 0.2,
            OperationalContext.STAGING: 0.3,
            OperationalContext.PRODUCTION: 0.6,
            OperationalContext.BACKUP: 0.4,
            OperationalContext.ARCHIVE: 0.3,
            OperationalContext.SHARING: 0.8,
            OperationalContext.STORAGE: 0.4,
            OperationalContext.PROCESSING: 0.5
        }
        
        threats['operation_risk_score'] = operation_risks.get(context.operation_type, 0.5)
        
        # Context-specific factors
        if context.operation_type == OperationalContext.SHARING:
            threats['context_factors'].extend([
                'data_in_transit',
                'external_exposure_risk',
                'recipient_validation_required'
            ])
        elif context.operation_type == OperationalContext.PRODUCTION:
            threats['context_factors'].extend([
                'production_environment',
                'availability_requirements',
                'compliance_critical'
            ])
        
        # Time sensitivity impact
        if context.time_sensitivity == 'immediate':
            threats['context_factors'].append('time_pressure_may_reduce_security_validation')
        
        # Compliance assessment
        if context.compliance_requirements:
            # Check if current settings meet compliance requirements
            # This would integrate with actual compliance checking logic
            for requirement in context.compliance_requirements:
                if requirement not in ['basic_encryption', 'standard_security']:
                    threats['compliance_gaps'].append(f'compliance_requirement_{requirement}')
        
        return threats
    
    @classmethod
    def _assess_temporal_threats(cls, context: SecurityContext) -> Dict[str, Any]:
        """Assess time-based threat factors"""
        
        threats = {
            'temporal_risk_score': 0.0,
            'time_factors': [],
            'urgency_impact': 0.0,
            'expiry_considerations': []
        }
        
        # Time sensitivity impact
        time_risks = {
            'immediate': 0.3,  # Rush may compromise security
            'standard': 0.0,   # Normal time allowance
            'batch': -0.1      # Extra time for security validation
        }
        
        threats['urgency_impact'] = time_risks.get(context.time_sensitivity, 0.0)
        
        # Expiry duration considerations
        if context.expiry_duration:
            days = context.expiry_duration.days
            if days < 1:
                threats['expiry_considerations'].append('very_short_term_protection')
                threats['temporal_risk_score'] += 0.1
            elif days < 30:
                threats['expiry_considerations'].append('short_term_protection')
            elif days > 365:
                threats['expiry_considerations'].append('long_term_protection_considerations')
                threats['temporal_risk_score'] += 0.2
        
        # Current time context (business hours, weekends, etc.)
        current_hour = context.timestamp.hour
        is_weekend = context.timestamp.weekday() >= 5
        
        if current_hour < 6 or current_hour > 22:  # Off hours
            threats['time_factors'].append('off_hours_operation')
        if is_weekend:
            threats['time_factors'].append('weekend_operation')
        
        return threats
    
    @classmethod
    def _assess_historical_patterns(cls, context: SecurityContext) -> Dict[str, Any]:
        """Assess threats based on historical patterns"""
        
        threats = {
            'pattern_risk_score': 0.0,
            'suspicious_patterns': [],
            'normal_patterns': [],
            'anomaly_indicators': []
        }
        
        if not context.previous_operations:
            return threats
        
        # Analyze operation frequency
        recent_ops = [op for op in context.previous_operations 
                     if 'timestamp' in op and 
                     datetime.fromisoformat(op['timestamp']) > datetime.now() - timedelta(hours=24)]
        
        if len(recent_ops) > 100:  # Unusually high activity
            threats['suspicious_patterns'].append('high_frequency_operations')
            threats['pattern_risk_score'] += 0.3
        
        # Analyze file type patterns
        recent_types = [op.get('content_type', 'unknown') for op in recent_ops]
        unique_types = set(recent_types)
        
        if 'credentials' in recent_types and len(unique_types) > 5:
            threats['suspicious_patterns'].append('mixed_sensitive_content_types')
            threats['pattern_risk_score'] += 0.2
        
        # Check for escalating security patterns
        security_levels = [op.get('security_level', 'medium') for op in recent_ops[-10:]]
        if security_levels and security_levels[-3:] == ['high', 'high', 'high']:
            threats['anomaly_indicators'].append('escalating_security_requirements')
        
        return threats
    
    @classmethod
    def _calculate_threat_score(cls, assessment_details: Dict[str, Any]) -> float:
        """Calculate overall threat score from assessment details"""
        
        score = 0.0
        
        # Content threats
        if 'content_threats' in assessment_details:
            content = assessment_details['content_threats']
            score += content.get('sensitivity_risk', 0.0) * cls.RISK_WEIGHTS['content_sensitivity']
        
        # Environment threats
        if 'environment_threats' in assessment_details:
            env = assessment_details['environment_threats']
            score += env.get('environment_risk_score', 0.0) * cls.RISK_WEIGHTS['environment_risk']
        
        # Operational threats
        if 'operational_threats' in assessment_details:
            op = assessment_details['operational_threats']
            score += op.get('operation_risk_score', 0.0) * cls.RISK_WEIGHTS['operational_context']
        
        # Temporal threats
        if 'temporal_threats' in assessment_details:
            temporal = assessment_details['temporal_threats']
            base_temporal = temporal.get('temporal_risk_score', 0.0)
            urgency = temporal.get('urgency_impact', 0.0)
            score += (base_temporal + urgency) * cls.RISK_WEIGHTS['temporal_factors']
        
        # Historical patterns
        if 'historical_threats' in assessment_details:
            historical = assessment_details['historical_threats']
            score += historical.get('pattern_risk_score', 0.0) * cls.RISK_WEIGHTS['threat_indicators']
        
        # Normalize score to 0-1 range
        return max(0.0, min(1.0, score))
    
    @classmethod
    def _score_to_threat_level(cls, score: float) -> ThreatLevel:
        """Convert threat score to threat level"""
        
        if score < 0.1:
            return ThreatLevel.MINIMAL
        elif score < 0.3:
            return ThreatLevel.LOW
        elif score < 0.5:
            return ThreatLevel.MODERATE
        elif score < 0.7:
            return ThreatLevel.HIGH
        elif score < 0.9:
            return ThreatLevel.CRITICAL
        else:
            return ThreatLevel.EXTREME
    
    @classmethod
    def _generate_mitigation_recommendations(cls, threat_level: ThreatLevel, 
                                           assessment_details: Dict[str, Any]) -> List[str]:
        """Generate threat mitigation recommendations"""
        
        recommendations = []
        
        # Level-based recommendations
        if threat_level in [ThreatLevel.CRITICAL, ThreatLevel.EXTREME]:
            recommendations.extend([
                'enable_maximum_security_profile',
                'enable_forward_secrecy',
                'use_maximum_encryption_parameters',
                'enable_additional_authentication_layers'
            ])
        elif threat_level == ThreatLevel.HIGH:
            recommendations.extend([
                'use_high_security_profile',
                'enable_enhanced_metadata_protection',
                'consider_additional_validation'
            ])
        elif threat_level == ThreatLevel.MODERATE:
            recommendations.extend([
                'use_balanced_security_profile',
                'enable_standard_protections'
            ])
        
        # Specific threat-based recommendations
        for category, details in assessment_details.items():
            if category == 'content_threats':
                if 'pre_encrypted_content' in details.get('content_indicators', []):
                    recommendations.append('verify_double_encryption_necessity')
            elif category == 'environment_threats':
                if details.get('environment_risk_score', 0) > 0.6:
                    recommendations.append('enable_hostile_environment_protections')
            elif category == 'operational_threats':
                if 'data_in_transit' in details.get('context_factors', []):
                    recommendations.append('enable_transit_specific_protections')
        
        return list(set(recommendations))  # Remove duplicates
    
    @classmethod
    def _extract_risk_factors(cls, assessment_details: Dict[str, Any]) -> List[str]:
        """Extract risk factors from assessment details"""
        
        risk_factors = []
        
        for category, details in assessment_details.items():
            if isinstance(details, dict):
                # Extract various risk factor lists
                for key, value in details.items():
                    if key.endswith('_factors') or key.endswith('_indicators') or key.endswith('_concerns'):
                        if isinstance(value, list):
                            risk_factors.extend(value)
        
        return list(set(risk_factors))  # Remove duplicates

class AdaptiveSecurityManager:
    """Main adaptive security management system"""
    
    def __init__(self):
        self.learning_history: List[Dict[str, Any]] = []
        self.threat_assessor = ThreatAssessment()
        self.profile_manager = AdvancedProfileManager()
    
    def analyze_security_context(self, data: bytes, filename: str = "",
                               operational_context: Optional[OperationalContext] = None,
                               environment_risk: Optional[EnvironmentRisk] = None,
                               user_preferences: Optional[Dict[str, Any]] = None) -> SecurityContext:
        """Analyze complete security context"""
        
        # Get content analysis
        content_analysis = ContentAnalyzer.analyze_content(data, filename)
        
        # Build security context
        context = SecurityContext(
            content_sensitivity=content_analysis['content_sensitivity'],
            content_type=content_analysis['file_type'],
            content_size=len(data),
            content_analysis=content_analysis,
            operation_type=operational_context or OperationalContext.STORAGE,
            environment_risk=environment_risk or EnvironmentRisk.STANDARD
        )
        
        # Apply user preferences
        if user_preferences:
            context.user_preference = user_preferences.get('security_preference', 'balanced')
            context.compliance_requirements = user_preferences.get('compliance_requirements', [])
            context.time_sensitivity = user_preferences.get('time_sensitivity', 'standard')
        
        # Add historical context
        if self.learning_history:
            context.previous_operations = self.learning_history[-50:]  # Last 50 operations
        
        return context
    
    def get_adaptive_security_parameters(self, security_context: SecurityContext) -> Dict[str, Any]:
        """Get adaptively optimized security parameters"""
        
        # Perform threat assessment
        threat_assessment = self.threat_assessor.assess_threats(security_context)
        
        # Get base profile recommendation
        profile_analysis = self.profile_manager.analyze_and_recommend(
            b"",  # Empty data since we already have analysis
            security_context.content_analysis.get('filename', ''),
            security_context.content_size
        )
        
        # Apply context-aware adaptations
        adapted_params = self._adapt_parameters_to_context(
            profile_analysis['parameters'],
            security_context,
            threat_assessment
        )
        
        # Record operation for learning
        self._record_security_decision(security_context, threat_assessment, adapted_params)
        
        return {
            'security_parameters': adapted_params,
            'threat_assessment': threat_assessment,
            'profile_analysis': profile_analysis,
            'adaptations_applied': self._get_adaptation_summary(adapted_params, profile_analysis['parameters']),
            'security_context': security_context,
            'confidence': min(
                profile_analysis.get('confidence', 0.7),
                threat_assessment.get('confidence', 0.7)
            )
        }
    
    def _adapt_parameters_to_context(self, base_params: Dict[str, Any],
                                   context: SecurityContext,
                                   threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt security parameters based on context and threat assessment"""
        
        adapted_params = base_params.copy()
        threat_level = threat_assessment['overall_threat_level']
        
        # Threat level adaptations
        if threat_level in [ThreatLevel.CRITICAL, ThreatLevel.EXTREME]:
            adapted_params['lattice_size'] = max(adapted_params.get('lattice_size', 128), 256)
            adapted_params['depth'] = max(adapted_params.get('depth', 6), 8)
            adapted_params['phe_path_count'] = max(adapted_params.get('phe_path_count', 8), 15)
            adapted_params['forward_secrecy'] = True
            adapted_params['plausible_deniability'] = True
            adapted_params['content_sensitivity'] = 'maximum'
        
        elif threat_level == ThreatLevel.HIGH:
            adapted_params['lattice_size'] = max(adapted_params.get('lattice_size', 128), 192)
            adapted_params['depth'] = max(adapted_params.get('depth', 6), 7)
            adapted_params['content_sensitivity'] = 'high'
        
        elif threat_level in [ThreatLevel.MINIMAL, ThreatLevel.LOW] and context.user_preference == 'performance':
            adapted_params['lattice_size'] = min(adapted_params.get('lattice_size', 128), 96)
            adapted_params['depth'] = min(adapted_params.get('depth', 6), 5)
            adapted_params['optimize_for'] = 'speed'
        
        # Environment-specific adaptations
        if context.environment_risk in [EnvironmentRisk.HOSTILE, EnvironmentRisk.ELEVATED]:
            adapted_params['use_decoys'] = True
            adapted_params['decoy_count_base'] = max(adapted_params.get('decoy_count_base', 3), 5)
            adapted_params['steganography_hints'] = True
        
        # Operational context adaptations
        if context.operation_type == OperationalContext.SHARING:
            adapted_params['metadata_strategy'] = 'comprehensive'  # Full verification data
            adapted_params['checksum_strategy'] = 'paranoid'
        elif context.operation_type == OperationalContext.BACKUP:
            adapted_params['compression_strategy'] = 'maximum'
            adapted_params['streaming_optimized'] = True
        elif context.operation_type == OperationalContext.DEVELOPMENT:
            adapted_params['intelligence_level'] = 'basic'  # Faster for development
        
        # User preference adaptations
        if context.user_preference == 'security':
            adapted_params['optimize_for'] = 'security'
            adapted_params['auto_adjust_security'] = True
        elif context.user_preference == 'performance':
            adapted_params['optimize_for'] = 'speed'
            adapted_params['compression_strategy'] = 'fast'
        
        # System resource adaptations
        if context.system_resources == 'limited':
            adapted_params['memory_usage_limit'] = 'low'
            adapted_params['streaming_optimized'] = True
            adapted_params['chunk_size_preference'] = 'small'
        elif context.system_resources == 'abundant':
            adapted_params['memory_usage_limit'] = 'high'
            adapted_params['chunk_size_preference'] = 'large'
        
        # Time sensitivity adaptations
        if context.time_sensitivity == 'immediate':
            adapted_params['optimize_for'] = 'speed'
            adapted_params['intelligence_level'] = 'basic'
        elif context.time_sensitivity == 'batch':
            adapted_params['intelligence_level'] = 'advanced'
            adapted_params['compression_strategy'] = 'maximum'
        
        # Compliance adaptations
        for requirement in context.compliance_requirements:
            if requirement == 'GDPR':
                adapted_params['forward_secrecy'] = True
                adapted_params['plausible_deniability'] = True
            elif requirement == 'HIPAA':
                adapted_params['lattice_size'] = max(adapted_params.get('lattice_size', 128), 192)
                adapted_params['content_sensitivity'] = 'high'
            elif requirement == 'SOX':
                adapted_params['metadata_strategy'] = 'comprehensive'
                adapted_params['checksum_strategy'] = 'paranoid'
        
        return adapted_params
    
    def _record_security_decision(self, context: SecurityContext,
                                threat_assessment: Dict[str, Any],
                                final_params: Dict[str, Any]) -> None:
        """Record security decision for learning"""
        
        if not context.learning_enabled:
            return
        
        record = {
            'timestamp': context.timestamp.isoformat(),
            'content_type': context.content_type,
            'content_size': context.content_size,
            'content_sensitivity': context.content_sensitivity,
            'threat_level': threat_assessment['overall_threat_level'].value,
            'threat_score': threat_assessment['threat_score'],
            'operation_type': context.operation_type.value,
            'environment_risk': context.environment_risk.value,
            'user_preference': context.user_preference,
            'security_level': final_params.get('optimize_for', 'balanced'),
            'final_lattice_size': final_params.get('lattice_size', 128),
            'adaptations_count': len(self._get_adaptation_summary(final_params, {}))
        }
        
        self.learning_history.append(record)
        
        # Keep history manageable
        if len(self.learning_history) > 1000:
            self.learning_history = self.learning_history[-500:]
    
    def _get_adaptation_summary(self, adapted_params: Dict[str, Any],
                              base_params: Dict[str, Any]) -> List[str]:
        """Get summary of adaptations applied"""
        
        adaptations = []
        
        for key, value in adapted_params.items():
            base_value = base_params.get(key)
            if base_value is not None and base_value != value:
                adaptations.append(f"{key}: {base_value} → {value}")
        
        return adaptations
    
    def get_security_recommendations(self, security_context: SecurityContext) -> Dict[str, Any]:
        """Get comprehensive security recommendations"""
        
        threat_assessment = self.threat_assessor.assess_threats(security_context)
        
        recommendations = {
            'immediate_actions': [],
            'configuration_changes': [],
            'operational_improvements': [],
            'long_term_considerations': [],
            'compliance_notes': []
        }
        
        # Immediate security actions
        if threat_assessment['overall_threat_level'] in [ThreatLevel.CRITICAL, ThreatLevel.EXTREME]:
            recommendations['immediate_actions'].extend([
                'Switch to maximum security profile immediately',
                'Enable all available security features',
                'Consider additional authentication layers'
            ])
        
        # Configuration recommendations
        risk_factors = threat_assessment.get('risk_factors', [])
        if 'high_risk_environment' in risk_factors:
            recommendations['configuration_changes'].append('Enable hostile environment protections')
        if 'data_in_transit' in risk_factors:
            recommendations['configuration_changes'].append('Enable transit-specific security measures')
        
        # Operational improvements
        if security_context.time_sensitivity == 'immediate':
            recommendations['operational_improvements'].append(
                'Consider pre-configured security templates for urgent operations'
            )
        
        # Long-term considerations
        if len(security_context.previous_operations) > 50:
            recommendations['long_term_considerations'].append(
                'Historical pattern analysis suggests reviewing security policies'
            )
        
        # Compliance notes
        for requirement in security_context.compliance_requirements:
            recommendations['compliance_notes'].append(
                f'Ensure {requirement} compliance requirements are met'
            )
        
        return recommendations

# Convenience functions
def create_security_context(data: bytes, filename: str = "",
                          operation: str = "storage",
                          environment: str = "standard",
                          user_prefs: Optional[Dict[str, Any]] = None) -> SecurityContext:
    """Create security context with intelligent defaults"""
    
    manager = AdaptiveSecurityManager()
    
    # Map string parameters to enums
    op_context = OperationalContext(operation) if operation in [e.value for e in OperationalContext] else OperationalContext.STORAGE
    env_risk = EnvironmentRisk(environment) if environment in [e.value for e in EnvironmentRisk] else EnvironmentRisk.STANDARD
    
    return manager.analyze_security_context(data, filename, op_context, env_risk, user_prefs)

def get_intelligent_security_parameters(data: bytes, filename: str = "",
                                      operation: str = "storage",
                                      environment: str = "standard",
                                      user_prefs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get intelligently adapted security parameters"""
    
    manager = AdaptiveSecurityManager()
    context = create_security_context(data, filename, operation, environment, user_prefs)
    
    return manager.get_adaptive_security_parameters(context)

def assess_security_threats(context: SecurityContext) -> Dict[str, Any]:
    """Assess security threats for given context"""
    
    return ThreatAssessment.assess_threats(context)