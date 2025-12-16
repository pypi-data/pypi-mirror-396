"""
Intelligent Security Profiles System v0.3.1

Advanced security profiles with intelligent auto-detection, 
adaptive security, and content-specific optimizations.
Uses only Seigr-standard implementations.
"""

from enum import Enum
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import os
from pathlib import Path

from .security_profiles import SecurityProfile, ProfileParameters, SecurityProfileManager

class IntelligentSecurityProfile(Enum):
    """Intelligent security profiles with granular classification"""
    
    # Document categories
    DOCUMENT_TEXT = "document_text"
    DOCUMENT_OFFICE = "document_office"
    DOCUMENT_PDF = "document_pdf"
    DOCUMENT_STRUCTURED = "document_structured"
    
    # Media categories  
    MEDIA_IMAGE = "media_image"
    MEDIA_VIDEO = "media_video"
    MEDIA_AUDIO = "media_audio"
    MEDIA_ARCHIVE = "media_archive"
    
    # Credential categories
    CREDENTIALS_KEYS = "credentials_keys"
    CREDENTIALS_PASSWORDS = "credentials_passwords"
    CREDENTIALS_TOKENS = "credentials_tokens"
    CREDENTIALS_WALLETS = "credentials_wallets"
    
    # Backup categories
    BACKUP_PERSONAL = "backup_personal"
    BACKUP_SYSTEM = "backup_system"
    BACKUP_ARCHIVE = "backup_archive"
    BACKUP_COMPRESSED = "backup_compressed"
    
    # Special categories
    SOURCE_CODE = "source_code"
    DATABASE = "database"
    CONFIGURATION = "configuration"
    TEMPORARY = "temporary"
    
    # Legacy compatibility
    DOCUMENT = "document"
    MEDIA = "media"
    CREDENTIALS = "credentials"
    BACKUP = "backup"
    CUSTOM = "custom"

@dataclass
class IntelligentProfileParameters(ProfileParameters):
    """Intelligent parameters with advanced security features"""
    
    # Content-aware settings
    content_sensitivity: str = "medium"
    auto_adjust_security: bool = True
    
    # Performance optimizations
    streaming_optimized: bool = False
    chunk_size_preference: str = "auto"
    compression_strategy: str = "adaptive"
    
    # Advanced security features
    steganography_hints: bool = False
    plausible_deniability: bool = True
    forward_secrecy: bool = False
    
    # Metadata optimization
    metadata_strategy: str = "balanced"
    checksum_strategy: str = "adaptive"
    
    # Intelligence features
    intelligence_level: str = "standard"
    auto_profile_switching: bool = False

class ContentAnalyzer:
    """Analyzes file content to determine optimal security settings using Seigr methods"""
    
    # Security sensitivity keywords
    HIGH_SENSITIVITY_KEYWORDS = [
        'password', 'secret', 'private', 'key', 'token', 'credential', 
        'social security', 'credit card', 'bank account', 'passport',
        'api key', 'oauth', 'jwt', 'bearer', 'session'
    ]
    
    MEDIUM_SENSITIVITY_KEYWORDS = [
        'confidential', 'proprietary', 'internal', 'employee', 
        'customer', 'client', 'contract', 'agreement'
    ]
    
    # File type binary signatures
    BINARY_SIGNATURES = {
        b'\x50\x4b\x03\x04': 'zip_office',
        b'\x25\x50\x44\x46': 'pdf',
        b'\x89\x50\x4e\x47': 'png',
        b'\xff\xd8\xff': 'jpeg',
        b'\x52\x49\x46\x46': 'media_container',
        b'\x1f\x8b\x08': 'gzip',
        b'\x42\x5a\x68': 'bzip2',
    }
    
    @classmethod
    def analyze_content(cls, data: bytes, filename: str = "") -> Dict[str, Any]:
        """Comprehensive content analysis for optimal profile selection"""
        
        analysis = {
            'file_type': 'unknown',
            'content_sensitivity': 'medium',
            'is_binary': False,
            'size_category': cls._categorize_size(len(data)),
            'recommended_profile': None,
            'confidence': 0.0,
        }
        
        # Basic file type detection
        file_type = cls._detect_file_type(data, filename)
        analysis['file_type'] = file_type
        analysis['is_binary'] = cls._is_binary_content(data)
        
        # Content sensitivity analysis
        sensitivity = cls._analyze_sensitivity(data)
        analysis['content_sensitivity'] = sensitivity
        
        # Profile recommendation
        profile, confidence = cls._recommend_intelligent_profile(analysis, filename)
        analysis['recommended_profile'] = profile
        analysis['confidence'] = confidence
        
        return analysis
    
    @classmethod
    def _detect_file_type(cls, data: bytes, filename: str) -> str:
        """Detect file type from content and filename"""
        
        # Check binary signatures first
        for signature, file_type in cls.BINARY_SIGNATURES.items():
            if data.startswith(signature):
                return file_type
        
        # Check filename extension
        if filename:
            ext = Path(filename).suffix.lower()
            
            if ext in ['.txt', '.md', '.rst', '.log']:
                return 'text'
            elif ext in ['.py', '.js', '.html', '.css', '.xml']:
                return 'source_code'
            elif ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                return 'office_document'
            elif ext in ['.pdf']:
                return 'pdf'
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                return 'image'
            elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
                return 'video'
            elif ext in ['.mp3', '.wav', '.flac', '.aac']:
                return 'audio'
            elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
                return 'archive'
            elif ext in ['.key', '.pem', '.p12', '.pfx']:
                return 'cryptographic_key'
            elif ext in ['.db', '.sqlite', '.mdb']:
                return 'database'
        
        # Content-based detection for text files
        try:
            text_content = data[:1024].decode('utf-8', errors='ignore').lower()
            
            if text_content.strip().startswith(('<?xml', '<html', '<!doctype')):
                return 'markup'
            elif text_content.strip().startswith(('{', '[')):
                return 'structured_data'
            elif '-----begin' in text_content and '-----end' in text_content:
                return 'pem_format'
            elif any(keyword in text_content for keyword in ['function', 'class', 'import', 'def', 'var', 'const']):
                return 'source_code'
            else:
                return 'text'
                
        except UnicodeDecodeError:
            return 'binary'
    
    @classmethod
    def _analyze_sensitivity(cls, data: bytes) -> str:
        """Analyze content sensitivity level using Seigr pattern matching"""
        
        try:
            text_content = data.decode('utf-8', errors='ignore').lower()
            
            high_count = sum(1 for keyword in cls.HIGH_SENSITIVITY_KEYWORDS if keyword in text_content)
            
            if high_count >= 2:
                return 'maximum'
            elif high_count >= 1:
                return 'high'
            
            medium_count = sum(1 for keyword in cls.MEDIUM_SENSITIVITY_KEYWORDS if keyword in text_content)
            
            if medium_count >= 3:
                return 'high'
            elif medium_count >= 1:
                return 'medium'
            
            return 'low'
            
        except UnicodeDecodeError:
            return 'medium'
    
    @classmethod
    def _categorize_size(cls, size: int) -> str:
        """Categorize file size for optimization"""
        
        if size < 10 * 1024:
            return 'tiny'
        elif size < 1024 * 1024:
            return 'small'
        elif size < 10 * 1024 * 1024:
            return 'medium'
        elif size < 100 * 1024 * 1024:
            return 'large'
        elif size < 1024 * 1024 * 1024:
            return 'very_large'
        else:
            return 'huge'
    
    @classmethod
    def _is_binary_content(cls, data: bytes) -> bool:
        """Determine if content is binary using Seigr analysis"""
        
        if len(data) == 0:
            return False
        
        sample = data[:1024]
        
        if b'\x00' in sample:
            return True
        
        printable_count = 0
        for byte in sample:
            if 32 <= byte <= 126 or byte in [9, 10, 13]:
                printable_count += 1
        
        printable_ratio = printable_count / len(sample)
        return printable_ratio < 0.75
    
    @classmethod
    def _recommend_intelligent_profile(cls, analysis: Dict[str, Any], filename: str) -> Tuple[IntelligentSecurityProfile, float]:
        """Recommend intelligent profile based on analysis"""
        
        file_type = analysis['file_type']
        sensitivity = analysis['content_sensitivity']
        size_category = analysis['size_category']
        
        # Initialize with defaults - will be overwritten in all branches
        profile = IntelligentSecurityProfile.DOCUMENT_OFFICE
        confidence = 0.5
        
        # Prioritize file type detection over sensitivity for media files
        if file_type in ['jpeg', 'png', 'image']:
            profile = IntelligentSecurityProfile.MEDIA_IMAGE
            confidence = 0.9
        elif file_type == 'video':
            profile = IntelligentSecurityProfile.MEDIA_VIDEO
            confidence = 0.9
        elif file_type == 'audio':
            profile = IntelligentSecurityProfile.MEDIA_AUDIO
            confidence = 0.9
        elif file_type == 'source_code':
            profile = IntelligentSecurityProfile.SOURCE_CODE
            confidence = 0.9
        elif file_type == 'cryptographic_key' or sensitivity == 'maximum':
            profile = IntelligentSecurityProfile.CREDENTIALS_KEYS
            confidence = 0.95
        elif file_type == 'pem_format' or 'key' in filename.lower():
            profile = IntelligentSecurityProfile.CREDENTIALS_KEYS
            confidence = 0.9
        elif sensitivity == 'high':
            profile = IntelligentSecurityProfile.CREDENTIALS_PASSWORDS
            confidence = 0.8
        elif file_type == 'pdf':
            profile = IntelligentSecurityProfile.DOCUMENT_PDF
            confidence = 0.9
        elif file_type == 'office_document':
            profile = IntelligentSecurityProfile.DOCUMENT_OFFICE
            confidence = 0.9
        elif file_type in ['text', 'markup']:
            profile = IntelligentSecurityProfile.DOCUMENT_TEXT
            confidence = 0.8
        elif file_type == 'archive':
            if size_category in ['large', 'very_large', 'huge']:
                profile = IntelligentSecurityProfile.BACKUP_COMPRESSED
            else:
                profile = IntelligentSecurityProfile.BACKUP_PERSONAL
            confidence = 0.8
        elif file_type == 'database':
            profile = IntelligentSecurityProfile.DATABASE
            confidence = 0.85
        elif sensitivity in ['high', 'maximum']:
            # Handle high sensitivity files not caught by specific types
            profile = IntelligentSecurityProfile.CREDENTIALS_PASSWORDS
            confidence = 0.6
        # else: use defaults (profile=DOCUMENT_OFFICE, confidence=0.5)
        
        return profile, confidence

class AdvancedProfileManager(SecurityProfileManager):
    """Advanced security profile manager with pattern-based content analysis"""
    
    INTELLIGENT_PROFILE_CONFIGS = {
        IntelligentSecurityProfile.DOCUMENT_TEXT: IntelligentProfileParameters(
            lattice_size=96, depth=5, morph_interval=120,
            phe_path_count=5, phe_difficulty_base=1,
            use_decoys=True, decoy_count_base=2,
            optimize_for="balanced", memory_usage_limit="moderate",
            content_sensitivity="low", streaming_optimized=False,
            compression_strategy="adaptive", metadata_strategy="minimal",
            intelligence_level="standard"
        ),
        
        IntelligentSecurityProfile.CREDENTIALS_KEYS: IntelligentProfileParameters(
            lattice_size=256, depth=8, morph_interval=25,
            phe_path_count=15, phe_difficulty_base=3,
            use_decoys=True, decoy_count_base=7,
            optimize_for="security", memory_usage_limit="high",
            content_sensitivity="maximum", streaming_optimized=False,
            compression_strategy="maximum", metadata_strategy="comprehensive",
            forward_secrecy=True, plausible_deniability=True,
            intelligence_level="advanced"
        ),
        
        IntelligentSecurityProfile.SOURCE_CODE: IntelligentProfileParameters(
            lattice_size=128, depth=6, morph_interval=60,
            phe_path_count=8, phe_difficulty_base=2,
            use_decoys=True, decoy_count_base=3,
            optimize_for="balanced", memory_usage_limit="moderate",
            content_sensitivity="medium", streaming_optimized=True,
            compression_strategy="balanced", metadata_strategy="balanced",
            intelligence_level="standard"
        ),
    }
    
    @classmethod
    def analyze_and_recommend(cls, data: bytes, filename: str = "", 
                            file_size: Optional[int] = None) -> Dict[str, Any]:
        """Complete analysis and recommendation pipeline using Seigr standards"""
        
        if file_size is None:
            file_size = len(data)
        
        content_analysis = ContentAnalyzer.analyze_content(data, filename)
        recommended_profile = content_analysis['recommended_profile']
        confidence = content_analysis['confidence']
        
        if recommended_profile in cls.INTELLIGENT_PROFILE_CONFIGS:
            base_params = cls.INTELLIGENT_PROFILE_CONFIGS[recommended_profile]
        else:
            legacy_profile = cls._map_to_legacy_profile(recommended_profile)
            base_params = cls.PROFILE_CONFIGS.get(legacy_profile, 
                                                cls.PROFILE_CONFIGS[SecurityProfile.DOCUMENT])
        
        result = {
            'recommended_profile': recommended_profile.value,
            'confidence': confidence,
            'parameters': asdict(base_params),
            'content_analysis': content_analysis,
            'performance_estimate': cls._estimate_performance(base_params, file_size),
            'optimizations_applied': [],
            'alternative_profiles': [],
            'security_assessment': cls._assess_security_level(base_params, content_analysis),
        }
        
        return result
    
    @classmethod
    def _map_to_legacy_profile(cls, intelligent_profile: IntelligentSecurityProfile) -> SecurityProfile:
        """Map intelligent profiles to legacy profiles for compatibility"""
        
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
        }
        
        return mapping.get(intelligent_profile, SecurityProfile.DOCUMENT)
    
    @classmethod
    def _apply_intelligent_optimizations(cls, base_params: ProfileParameters,
                                       content_analysis: Dict[str, Any],
                                       file_size: int) -> IntelligentProfileParameters:
        """Apply intelligent optimizations based on content analysis using Seigr methods"""
        
        # Convert base_params to IntelligentProfileParameters regardless of input type
        intelligent_params = IntelligentProfileParameters(**asdict(base_params))
        
        sensitivity = content_analysis['content_sensitivity']
        if sensitivity == 'maximum':
            intelligent_params.lattice_size = max(intelligent_params.lattice_size, 256)
            intelligent_params.depth = max(intelligent_params.depth, 8)
            intelligent_params.forward_secrecy = True
        elif sensitivity == 'low' and intelligent_params.optimize_for != 'security':
            intelligent_params.lattice_size = min(intelligent_params.lattice_size, 96)
            intelligent_params.depth = min(intelligent_params.depth, 5)
        
        size_category = content_analysis['size_category']
        if size_category in ['large', 'very_large', 'huge']:
            intelligent_params.streaming_optimized = True
            if hasattr(intelligent_params, 'minimize_metadata'):
                intelligent_params.minimize_metadata = True
            if size_category == 'huge':
                intelligent_params.chunk_size_preference = 'large'
        elif size_category == 'tiny':
            intelligent_params.metadata_strategy = 'minimal'
            intelligent_params.decoy_count_base = max(1, intelligent_params.decoy_count_base - 1)
        
        return intelligent_params
    
    @classmethod
    def _estimate_performance(cls, params: ProfileParameters, file_size: int) -> Dict[str, Any]:
        """Estimate performance metrics"""
        
        # Simple performance estimation based on parameters
        base_time = 0.1  # Base encryption time in seconds
        
        # Factor in lattice size
        lattice_factor = params.lattice_size / 128.0
        
        # Factor in depth
        depth_factor = params.depth / 6.0
        
        # Factor in file size
        size_factor = max(1.0, file_size / (1024 * 1024))  # MB factor
        
        encryption_time = base_time * lattice_factor * depth_factor * size_factor
        
        return {
            'encryption_time_seconds': round(encryption_time, 3),
            'decryption_time_seconds': round(encryption_time * 0.8, 3),
            'memory_usage_mb': round(params.lattice_size / 10.0, 1),
            'security_level': 'High' if params.lattice_size >= 256 else 'Medium'
        }
    
    @classmethod
    def _assess_security_level(cls, params: ProfileParameters, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall security level"""
        
        # Calculate security score
        security_score = 0
        
        # Lattice size contribution
        if params.lattice_size >= 256:
            security_score += 40
        elif params.lattice_size >= 128:
            security_score += 30
        else:
            security_score += 20
        
        # Depth contribution
        if params.depth >= 8:
            security_score += 30
        elif params.depth >= 6:
            security_score += 20
        else:
            security_score += 10
        
        # Other factors
        if params.use_decoys:
            security_score += 15
        if hasattr(params, 'forward_secrecy') and params.forward_secrecy:
            security_score += 15
        
        # Content sensitivity adjustment
        sensitivity = content_analysis.get('content_sensitivity', 'medium')
        if sensitivity == 'maximum':
            security_score = min(100, security_score + 10)
        elif sensitivity == 'low':
            security_score = max(30, security_score - 10)
        
        level = 'Maximum' if security_score >= 90 else 'High' if security_score >= 70 else 'Medium' if security_score >= 50 else 'Basic'
        
        return {
            'overall_level': level,
            'security_score': security_score,
            'content_sensitivity': sensitivity,
            'recommendations': []
        }

# Convenience functions
def analyze_file_content(filepath: str) -> Dict[str, Any]:
    """Analyze file content and recommend optimal profile using Seigr methods"""
    
    try:
        with open(filepath, 'rb') as f:
            sample_size = min(64 * 1024, os.path.getsize(filepath))
            data = f.read(sample_size)
            
        return AdvancedProfileManager.analyze_and_recommend(data, filepath, os.path.getsize(filepath))
    
    except Exception as e:
        legacy_profile = SecurityProfileManager.detect_profile_from_file(filepath)
        return {
            'recommended_profile': legacy_profile.value,
            'confidence': 0.3,
            'error': str(e),
            'fallback_used': True
        }

def get_intelligent_profile(data: bytes, filename: str = "") -> IntelligentSecurityProfile:
    """Get intelligent profile recommendation using Seigr analysis"""
    
    analysis = ContentAnalyzer.analyze_content(data, filename)
    return analysis['recommended_profile']

def get_intelligent_parameters(profile: IntelligentSecurityProfile, 
                             content_analysis: Optional[Dict[str, Any]] = None,
                             file_size: int = 0) -> Dict[str, Any]:
    """Get intelligent parameters for profile using Seigr standards"""
    
    if profile in AdvancedProfileManager.INTELLIGENT_PROFILE_CONFIGS:
        base_params = AdvancedProfileManager.INTELLIGENT_PROFILE_CONFIGS[profile]
    else:
        legacy_profile = AdvancedProfileManager._map_to_legacy_profile(profile)
        base_params = SecurityProfileManager.PROFILE_CONFIGS[legacy_profile]
    
    if content_analysis:
        optimized_params = AdvancedProfileManager._apply_intelligent_optimizations(
            base_params, content_analysis, file_size
        )
        return asdict(optimized_params)
    else:
        return asdict(base_params)
