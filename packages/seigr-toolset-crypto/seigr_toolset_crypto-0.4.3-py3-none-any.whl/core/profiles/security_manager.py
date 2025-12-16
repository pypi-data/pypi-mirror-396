"""
Phase 3 Integration Layer v0.3.1

Unified interface integrating Enhanced Security Profiles, Context-Aware Security,
and Profile-Specific Optimizations into a cohesive Phase 3 system.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import time
from datetime import datetime

# Intelligent Security System imports
from .profile_definitions import (
    IntelligentSecurityProfile, IntelligentProfileParameters, 
    ContentAnalyzer, AdvancedProfileManager
)
from .adaptive_security import (
    SecurityContext, OperationalContext, EnvironmentRisk,
    AdaptiveSecurityManager
)
from .content_optimizers import (
    ProfileOptimizationManager
)

# Legacy imports for compatibility
from .security_profiles import SecurityProfile, SecurityProfileManager

class SecurityMode(Enum):
    """Phase 3 operation modes"""
    LEGACY_COMPATIBLE = "legacy_compatible"      # Phase 2 compatibility mode
    ENHANCED_PROFILES = "enhanced_profiles"      # Enhanced profiles only
    CONTEXT_AWARE = "context_aware"              # Context-aware security
    FULL_INTELLIGENCE = "full_intelligence"      # All Phase 3 features
    CUSTOM_PIPELINE = "custom_pipeline"          # User-defined pipeline

@dataclass
class SecurityConfiguration:
    """Complete Phase 3 system configuration"""
    
    # Operation mode
    mode: SecurityMode = SecurityMode.FULL_INTELLIGENCE
    
    # Feature enablement
    enable_enhanced_profiles: bool = True
    enable_intelligent_profiles: bool = True
    enable_adaptive_security: bool = True
    enable_context_awareness: bool = True
    enable_profile_optimizations: bool = True
    enable_intelligent_adaptation: bool = True
    enable_threat_assessment: bool = True
    
    # Intelligence settings
    intelligence_level: str = "standard"  # "basic", "standard", "advanced"
    learning_enabled: bool = True
    adaptive_parameters: bool = True
    
    # Performance settings
    performance_priority: str = "balanced"  # "security", "balanced", "speed"
    memory_budget_mb: int = 256
    processing_timeout_seconds: int = 300
    
    # Compatibility settings
    legacy_fallback: bool = True
    strict_compatibility: bool = False
    
    # Debug and monitoring
    enable_detailed_logging: bool = False
    collect_performance_metrics: bool = True

class UnifiedSecurityManager:
    """Unified Phase 3 Security Management System"""
    
    def __init__(self, config: Optional[SecurityConfiguration] = None):
        self.config = config or SecurityConfiguration()
        
        # Initialize subsystems
        self.content_analyzer = ContentAnalyzer()
        self.intelligent_profile_manager = AdvancedProfileManager()
        self.adaptive_manager = AdaptiveSecurityManager()
        self.optimization_manager = ProfileOptimizationManager()
        
        # Legacy compatibility
        self.legacy_manager = SecurityProfileManager()
        
        # Performance tracking
        self.operation_history: List[Dict[str, Any]] = []
        
    def analyze_and_recommend(self, data: bytes, filename: str = "",
                            operation_context: Optional[str] = None,
                            environment_risk: Optional[str] = None,
                            user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Complete Phase 3 analysis and recommendation pipeline"""
        
        start_time = time.time()
        
        try:
            # Phase 1: Content Analysis
            content_analysis_start = time.time()
            content_analysis = self.content_analyzer.analyze_content(data, filename)
            content_analysis_time = time.time() - content_analysis_start
            
            # Phase 2: Enhanced Profile Recommendation
            profile_analysis_start = time.time()
            if self.config.enable_enhanced_profiles:
                profile_analysis = self.intelligent_profile_manager.analyze_and_recommend(
                    data, filename, len(data)
                )
                recommended_profile = IntelligentSecurityProfile(profile_analysis['recommended_profile'])
            else:
                # Fallback to legacy profiles
                legacy_profile = self.legacy_manager.detect_profile_from_content(data, filename)
                profile_analysis = {
                    'recommended_profile': legacy_profile.value,
                    'confidence': 0.6,
                    'parameters': asdict(self.legacy_manager.get_profile_parameters(legacy_profile))
                }
                recommended_profile = self._map_legacy_to_enhanced(legacy_profile)
            profile_analysis_time = time.time() - profile_analysis_start
            
            # Phase 3: Context-Aware Security Analysis
            context_analysis_start = time.time()
            if self.config.enable_context_awareness:
                # Create security context
                op_context = OperationalContext(operation_context) if operation_context else OperationalContext.STORAGE
                env_risk = EnvironmentRisk(environment_risk) if environment_risk else EnvironmentRisk.STANDARD
                
                security_context = self.adaptive_manager.analyze_security_context(
                    data, filename, op_context, env_risk, user_preferences
                )
                
                # Get adaptive parameters
                context_analysis = self.adaptive_manager.get_adaptive_security_parameters(security_context)
            else:
                security_context = None
                context_analysis = {'security_parameters': profile_analysis['parameters']}
            context_analysis_time = time.time() - context_analysis_start
            
            # Phase 4: Profile-Specific Optimizations
            optimization_start = time.time()
            if self.config.enable_profile_optimizations:
                base_params = IntelligentProfileParameters(**context_analysis['security_parameters'])
                optimization_result = self.optimization_manager.optimize_for_profile(
                    recommended_profile, data, base_params
                )
                final_parameters = optimization_result['optimized_parameters']
                processing_strategy = optimization_result['processing_strategy']
            else:
                final_parameters = context_analysis['security_parameters']
                processing_strategy = {'primary_strategy': 'hybrid_approach'}
            optimization_time = time.time() - optimization_start
            
            # Phase 5: Final Integration and Validation
            integration_start = time.time()
            
            # Validate parameters
            validation_result = self._validate_final_parameters(final_parameters, data, filename)
            
            # Generate comprehensive recommendations
            recommendations = self._generate_comprehensive_recommendations(
                content_analysis, profile_analysis, context_analysis, 
                optimization_result if self.config.enable_profile_optimizations else {},
                security_context
            )
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(
                content_analysis, profile_analysis, context_analysis
            )
            
            integration_time = time.time() - integration_start
            total_time = time.time() - start_time
            
            # Build comprehensive result
            result = {
                # Core results
                'recommended_profile': recommended_profile.value,
                'final_parameters': final_parameters,
                'processing_strategy': processing_strategy,
                
                # Analysis results
                'content_analysis': content_analysis,
                'profile_analysis': profile_analysis,
                'context_analysis': context_analysis if self.config.enable_context_awareness else {},
                'adaptive_analysis': context_analysis if self.config.enable_context_awareness else {},
                'optimization_analysis': optimization_result if self.config.enable_profile_optimizations else {},
                
                # Recommendations and guidance
                'recommendations': recommendations,
                'confidence_scores': confidence_scores,
                'validation_result': validation_result,
                
                # System information
                'phase3_config': asdict(self.config),
                'features_used': self._get_features_used(),
                
                # Performance metrics
                'performance_metrics': {
                    'total_analysis_time_ms': total_time * 1000,
                    'content_analysis_time_ms': content_analysis_time * 1000,
                    'profile_analysis_time_ms': profile_analysis_time * 1000,
                    'context_analysis_time_ms': context_analysis_time * 1000,
                    'optimization_time_ms': optimization_time * 1000,
                    'integration_time_ms': integration_time * 1000,
                    'data_size_bytes': len(data),
                    'analysis_speed_mbps': (len(data) / (1024 * 1024)) / max(total_time, 0.001)
                },
                
                # Metadata
                'timestamp': datetime.now().isoformat(),
                'version': '0.3.1',
                'analysis_id': self._generate_analysis_id()
            }
            
            # Record operation
            self._record_operation(result)
            
            return result
            
        except Exception as e:
            # Fallback to legacy system
            return self._handle_analysis_error(e, data, filename)
    
    def get_quick_recommendation(self, data: bytes, filename: str = "") -> Dict[str, Any]:
        """Quick recommendation using minimal Phase 3 features"""
        
        # Fast content analysis
        content_analysis = self.content_analyzer.analyze_content(data[:4096], filename)  # Sample only
        
        # Get enhanced profile
        recommended_profile = content_analysis['recommended_profile']
        
        # Get base parameters
        if recommended_profile in self.intelligent_profile_manager.INTELLIGENT_PROFILE_CONFIGS:
            base_params = self.intelligent_profile_manager.INTELLIGENT_PROFILE_CONFIGS[recommended_profile]
        else:
            legacy_profile = self._map_enhanced_to_legacy(recommended_profile)
            base_params = self.legacy_manager.get_profile_parameters(legacy_profile)
        
        return {
            'recommended_profile': recommended_profile.value,
            'parameters': asdict(base_params),
            'confidence': content_analysis['confidence'],
            'mode': 'quick_analysis',
            'analysis_time_ms': 0  # Minimal time for quick analysis
        }
    
    def get_legacy_compatible_recommendation(self, data: bytes, filename: str = "") -> Dict[str, Any]:
        """Legacy-compatible recommendation (Phase 2 compatibility)"""
        
        # Use legacy profile detection
        legacy_profile = self.legacy_manager.detect_profile_from_content(data, filename)
        legacy_params = self.legacy_manager.get_profile_parameters(legacy_profile)
        
        # Apply intelligent security enhancements if enabled
        if self.config.enable_enhanced_profiles:
            intelligent_profile = self._map_legacy_to_intelligent(legacy_profile)
            content_analysis = self.content_analyzer.analyze_content(data[:1024], filename)
            
            # Apply intelligent optimizations
            if intelligent_profile in self.intelligent_profile_manager.INTELLIGENT_PROFILE_CONFIGS:
                intelligent_params = self.intelligent_profile_manager._apply_intelligent_optimizations(
                    legacy_params, content_analysis, len(data)
                )
                final_params = asdict(intelligent_params)
            else:
                final_params = asdict(legacy_params)
        else:
            final_params = asdict(legacy_params)
        
        return {
            'recommended_profile': legacy_profile.value,
            'parameters': final_params,
            'confidence': 0.8,
            'mode': 'legacy_compatible',
            'enhanced_features_applied': self.config.enable_enhanced_profiles,
            'intelligent_features_applied': self.config.enable_intelligent_profiles
        }
    
    def _validate_final_parameters(self, parameters: Dict[str, Any], 
                                 data: bytes, filename: str) -> Dict[str, Any]:
        """Validate final parameters make sense"""
        
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        # Basic parameter validation
        if parameters.get('lattice_size', 0) < 32:
            validation['warnings'].append('Lattice size below recommended minimum')
        
        if parameters.get('depth', 0) < 3:
            validation['warnings'].append('Depth below recommended minimum')
        
        # Content-specific validation
        content_size = len(data)
        if content_size > 100 * 1024 * 1024 and not parameters.get('streaming_optimized', False):
            validation['suggestions'].append('Consider enabling streaming optimization for large files')
        
        if parameters.get('content_sensitivity') == 'maximum' and parameters.get('optimize_for') == 'speed':
            validation['warnings'].append('Maximum security and speed optimization may be conflicting')
        
        # Context validation
        if parameters.get('forward_secrecy', False) and content_size < 1024:
            validation['suggestions'].append('Forward secrecy may be overkill for small files')
        
        return validation
    
    def _generate_comprehensive_recommendations(self, content_analysis: Dict[str, Any],
                                              profile_analysis: Dict[str, Any],
                                              context_analysis: Dict[str, Any],
                                              optimization_analysis: Dict[str, Any],
                                              security_context: Optional[SecurityContext]) -> Dict[str, Any]:
        """Generate comprehensive recommendations"""
        
        recommendations = {
            'security_recommendations': [],
            'performance_recommendations': [], 
            'operational_recommendations': [],
            'configuration_suggestions': [],
            'alternative_profiles': []
        }
        
        # Security recommendations
        content_sensitivity = content_analysis.get('content_sensitivity', 'medium')
        if content_sensitivity in ['high', 'maximum']:
            recommendations['security_recommendations'].extend([
                'Enable maximum security features for sensitive content',
                'Consider additional authentication layers',
                'Enable forward secrecy for long-term protection'
            ])
        
        # Performance recommendations
        if len(optimization_analysis) > 0:
            perf_estimate = optimization_analysis.get('performance_estimate', {})
            if perf_estimate.get('estimated_total_time_seconds', 0) > 60:
                recommendations['performance_recommendations'].append(
                    'Consider streaming optimization to reduce processing time'
                )
        
        # Context-aware recommendations
        if security_context:
            if security_context.operation_type == OperationalContext.SHARING:
                recommendations['operational_recommendations'].append(
                    'Enable comprehensive metadata for file verification during sharing'
                )
            
            if security_context.environment_risk in [EnvironmentRisk.HOSTILE, EnvironmentRisk.ELEVATED]:
                recommendations['security_recommendations'].append(
                    'Enable hostile environment protections'
                )
        
        # Alternative profiles
        alternatives = profile_analysis.get('alternative_profiles', [])
        if alternatives:
            recommendations['alternative_profiles'] = alternatives[:3]  # Top 3
        
        return recommendations
    
    def _calculate_confidence_scores(self, content_analysis: Dict[str, Any],
                                   profile_analysis: Dict[str, Any],
                                   context_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for different aspects"""
        
        scores = {
            'overall_confidence': 0.7,
            'content_analysis_confidence': content_analysis.get('confidence', 0.7),
            'profile_recommendation_confidence': profile_analysis.get('confidence', 0.7), 
            'parameter_optimization_confidence': 0.8
        }
        
        # Context analysis confidence
        if self.config.enable_context_awareness and context_analysis:
            threat_assessment = context_analysis.get('threat_assessment', {})
            scores['threat_assessment_confidence'] = threat_assessment.get('confidence', 0.7)
        
        # Calculate overall confidence
        confidence_values = [v for v in scores.values() if isinstance(v, float)]
        scores['overall_confidence'] = sum(confidence_values) / len(confidence_values)
        
        return scores
    
    def _get_features_used(self) -> List[str]:
        """Get list of Phase 3 features used"""
        
        features = []
        
        if self.config.enable_enhanced_profiles:
            features.append('enhanced_security_profiles')
        
        if self.config.enable_intelligent_profiles:
            features.append('intelligent_security_profiles')
        
        if self.config.enable_context_awareness:
            features.append('context_aware_security')
        
        if self.config.enable_profile_optimizations:
            features.append('profile_specific_optimizations')
        
        if self.config.enable_intelligent_adaptation:
            features.append('intelligent_parameter_adaptation')
        
        if self.config.enable_threat_assessment:
            features.append('threat_assessment')
        
        if self.config.enable_adaptive_security:
            features.append('adaptive_security')
        
        if self.config.learning_enabled:
            features.append('machine_learning')
        
        return features
    
    def _generate_analysis_id(self) -> str:
        """Generate unique analysis ID using Seigr methods"""
        
        unique_data = f"{datetime.now().isoformat()}_{time.time()}"
        return self._seigr_simple_hash(unique_data)[:12]
    
    def _seigr_simple_hash(self, data: str) -> str:
        """Simple hash implementation following Seigr standards"""
        
        # Simple but effective hash using polynomial rolling hash
        hash_value = 0
        prime = 31
        
        for char in data:
            hash_value = (hash_value * prime + ord(char)) % (2**32)
        
        # Convert to hex string
        return format(hash_value, '08x')
    
    def _record_operation(self, result: Dict[str, Any]) -> None:
        """Record operation for learning and monitoring"""
        
        if not self.config.collect_performance_metrics:
            return
        
        operation_record = {
            'timestamp': result['timestamp'],
            'analysis_id': result['analysis_id'],
            'data_size_bytes': result['performance_metrics']['data_size_bytes'],
            'total_time_ms': result['performance_metrics']['total_analysis_time_ms'],
            'recommended_profile': result['recommended_profile'],
            'confidence': result['confidence_scores']['overall_confidence'],
            'features_used': result['features_used']
        }
        
        self.operation_history.append(operation_record)
        
        # Keep history manageable
        if len(self.operation_history) > 1000:
            self.operation_history = self.operation_history[-500:]
    
    def _handle_analysis_error(self, error: Exception, data: bytes, filename: str) -> Dict[str, Any]:
        """Handle analysis errors with fallback"""
        
        if self.config.legacy_fallback:
            try:
                # Fallback to legacy system
                legacy_profile = self.legacy_manager.detect_profile_from_file(filename) if filename else SecurityProfile.DOCUMENT
                legacy_params = self.legacy_manager.get_profile_parameters(legacy_profile)
                
                return {
                    'recommended_profile': legacy_profile.value,
                    'parameters': asdict(legacy_params),
                    'confidence': 0.3,
                    'mode': 'error_fallback',
                    'error': str(error),
                    'fallback_used': True
                }
            except Exception as e:  # nosec B110 - Fallback creation error handled by ultimate fallback
                # Failed to create fallback recommendation - will use ultimate fallback
                pass
        
        # Ultimate fallback
        return {
            'recommended_profile': SecurityProfile.DOCUMENT.value,
            'parameters': asdict(SecurityProfileManager.PROFILE_CONFIGS[SecurityProfile.DOCUMENT]),
            'confidence': 0.1,
            'mode': 'ultimate_fallback',
            'error': str(error),
            'warning': 'Analysis failed, using minimal security settings'
        }
    
    def _map_legacy_to_intelligent(self, legacy_profile: SecurityProfile) -> IntelligentSecurityProfile:
        """Map legacy profile to enhanced profile"""
        
        mapping = {
            SecurityProfile.DOCUMENT: IntelligentSecurityProfile.DOCUMENT_OFFICE,
            SecurityProfile.MEDIA: IntelligentSecurityProfile.MEDIA_IMAGE,
            SecurityProfile.CREDENTIALS: IntelligentSecurityProfile.CREDENTIALS_PASSWORDS,
            SecurityProfile.BACKUP: IntelligentSecurityProfile.BACKUP_PERSONAL,
            SecurityProfile.CUSTOM: IntelligentSecurityProfile.CUSTOM
        }
        
        return mapping.get(legacy_profile, IntelligentSecurityProfile.DOCUMENT_OFFICE)
    
    def _map_intelligent_to_legacy(self, intelligent_profile: IntelligentSecurityProfile) -> SecurityProfile:
        """Map enhanced profile to legacy profile"""
        
        mapping = {
            IntelligentSecurityProfile.DOCUMENT_TEXT: SecurityProfile.DOCUMENT,
            IntelligentSecurityProfile.DOCUMENT_OFFICE: SecurityProfile.DOCUMENT,
            IntelligentSecurityProfile.DOCUMENT_PDF: SecurityProfile.DOCUMENT,
            IntelligentSecurityProfile.DOCUMENT_STRUCTURED: SecurityProfile.DOCUMENT,
            IntelligentSecurityProfile.MEDIA_IMAGE: SecurityProfile.MEDIA,
            IntelligentSecurityProfile.MEDIA_VIDEO: SecurityProfile.MEDIA,
            IntelligentSecurityProfile.MEDIA_AUDIO: SecurityProfile.MEDIA,
            IntelligentSecurityProfile.MEDIA_ARCHIVE: SecurityProfile.MEDIA,
            IntelligentSecurityProfile.CREDENTIALS_KEYS: SecurityProfile.CREDENTIALS,
            IntelligentSecurityProfile.CREDENTIALS_PASSWORDS: SecurityProfile.CREDENTIALS,
            IntelligentSecurityProfile.CREDENTIALS_TOKENS: SecurityProfile.CREDENTIALS,
            IntelligentSecurityProfile.CREDENTIALS_WALLETS: SecurityProfile.CREDENTIALS,
            IntelligentSecurityProfile.BACKUP_PERSONAL: SecurityProfile.BACKUP,
            IntelligentSecurityProfile.BACKUP_SYSTEM: SecurityProfile.BACKUP,
            IntelligentSecurityProfile.BACKUP_ARCHIVE: SecurityProfile.BACKUP,
            IntelligentSecurityProfile.BACKUP_COMPRESSED: SecurityProfile.BACKUP,
            IntelligentSecurityProfile.SOURCE_CODE: SecurityProfile.DOCUMENT,
            IntelligentSecurityProfile.DATABASE: SecurityProfile.CREDENTIALS,
            IntelligentSecurityProfile.CONFIGURATION: SecurityProfile.CREDENTIALS,
            IntelligentSecurityProfile.TEMPORARY: SecurityProfile.BACKUP,
            IntelligentSecurityProfile.CUSTOM: SecurityProfile.CUSTOM
        }
        
        return mapping.get(intelligent_profile, SecurityProfile.DOCUMENT)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get Phase 3 system status and statistics"""
        
        recent_operations = self.operation_history[-10:] if self.operation_history else []
        
        return {
            'version': '0.3.1',
            'configuration': asdict(self.config),
            'features_available': self._get_features_used(),
            'operation_statistics': {
                'total_operations': len(self.operation_history),
                'recent_operations': len(recent_operations),
                'average_confidence': sum(op.get('confidence', 0) for op in recent_operations) / max(len(recent_operations), 1),
                'average_analysis_time_ms': sum(op.get('total_time_ms', 0) for op in recent_operations) / max(len(recent_operations), 1)
            },
            'subsystem_status': {
                'content_analyzer': 'active',
                'intelligent_profile_manager': 'active' if self.config.enable_enhanced_profiles else 'disabled',
                'adaptive_manager': 'active' if self.config.enable_context_awareness else 'disabled',
                'optimization_manager': 'active' if self.config.enable_profile_optimizations else 'disabled',
                'legacy_compatibility': 'active' if self.config.legacy_fallback else 'disabled'
            }
        }

# Convenience functions for Phase 3
def analyze_with_intelligence(data: bytes, filename: str = "",
                       operation_context: Optional[str] = None,
                       environment_risk: Optional[str] = None,
                       user_preferences: Optional[Dict[str, Any]] = None,
                       config: Optional[SecurityConfiguration] = None) -> Dict[str, Any]:
    """Complete Phase 3 analysis with all features"""
    
    manager = UnifiedSecurityManager(config)
    return manager.analyze_and_recommend(
        data, filename, operation_context, environment_risk, user_preferences
    )

def quick_security_recommendation(data: bytes, filename: str = "") -> Dict[str, Any]:
    """Quick Phase 3 recommendation for fast analysis"""
    
    config = SecurityConfiguration(
        mode=SecurityMode.ENHANCED_PROFILES,
        intelligence_level="basic"
    )
    
    manager = UnifiedSecurityManager(config)
    return manager.get_quick_recommendation(data, filename)

def legacy_compatible_analysis(data: bytes, filename: str = "") -> Dict[str, Any]:
    """Legacy-compatible analysis (Phase 2 compatibility mode)"""
    
    config = SecurityConfiguration(
        mode=SecurityMode.LEGACY_COMPATIBLE,
        enable_context_awareness=False,
        enable_profile_optimizations=False
    )
    
    manager = UnifiedSecurityManager(config)
    return manager.get_legacy_compatible_recommendation(data, filename)

def create_security_config(mode: str = "full_intelligence",
                        intelligence_level: str = "standard",
                        performance_priority: str = "balanced") -> SecurityConfiguration:
    """Create Phase 3 configuration with common settings"""
    
    mode_enum = SecurityMode(mode) if mode in [e.value for e in SecurityMode] else SecurityMode.FULL_INTELLIGENCE
    
    return SecurityConfiguration(
        mode=mode_enum,
        intelligence_level=intelligence_level,
        performance_priority=performance_priority
    )