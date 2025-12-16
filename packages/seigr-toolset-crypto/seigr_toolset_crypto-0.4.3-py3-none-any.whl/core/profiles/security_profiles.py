"""
Security Profiles System

Replaces manual parameter tuning with use-case based security profiles.
Users choose their use case, system optimizes parameters automatically.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import mimetypes
import os

class SecurityProfile(Enum):
    """Predefined security profiles for different use cases"""
    DOCUMENT = "document"         # Office files, PDFs, text documents
    MEDIA = "media"              # Photos, videos, audio files
    CREDENTIALS = "credentials"   # Passwords, keys, certificates, secrets
    BACKUP = "backup"            # Archive files, backups, bulk data
    CUSTOM = "custom"            # User-defined parameters

@dataclass
class ProfileParameters:
    """Complete parameter set for a security profile"""
    
    # Core encryption parameters
    lattice_size: int = 128
    depth: int = 6
    morph_interval: int = 100
    
    # PHE parameters
    phe_path_count: int = 7
    phe_difficulty_base: int = 1
    adaptive_difficulty: bool = True
    
    # Decoy parameters
    use_decoys: bool = True
    decoy_count_base: int = 3
    variable_decoy_sizes: bool = True
    randomize_decoy_count: bool = True
    
    # Adaptive features
    adaptive_morphing: bool = True
    adaptive_decoy_sizing: bool = True
    timing_randomization: bool = False
    
    # Performance preferences
    optimize_for: str = "balanced"  # "speed", "balanced", "security"
    memory_usage_limit: str = "moderate"  # "low", "moderate", "high"
    
    # Metadata preferences
    metadata_compression: bool = True
    minimize_metadata: bool = False

class SecurityProfileManager:
    """Manages security profiles and parameter optimization"""
    
    # Predefined profile configurations
    PROFILE_CONFIGS = {
        SecurityProfile.DOCUMENT: ProfileParameters(
            lattice_size=128,
            depth=6,
            morph_interval=100,
            phe_path_count=7,
            phe_difficulty_base=1,
            adaptive_difficulty=True,
            use_decoys=True,
            decoy_count_base=3,
            variable_decoy_sizes=True,
            randomize_decoy_count=True,
            adaptive_morphing=True,
            adaptive_decoy_sizing=True,
            timing_randomization=False,
            optimize_for="balanced",
            memory_usage_limit="moderate",
            metadata_compression=True,
            minimize_metadata=False
        ),
        
        SecurityProfile.MEDIA: ProfileParameters(
            lattice_size=96,              # Smaller for speed
            depth=5,                      # Reduced depth
            morph_interval=150,           # Less frequent morphing
            phe_path_count=5,             # Fewer paths
            phe_difficulty_base=1,
            adaptive_difficulty=False,    # Disabled for consistent performance
            use_decoys=True,
            decoy_count_base=2,           # Fewer decoys
            variable_decoy_sizes=True,
            randomize_decoy_count=False,  # Consistent performance
            adaptive_morphing=False,      # Disabled for speed
            adaptive_decoy_sizing=True,
            timing_randomization=False,
            optimize_for="speed",
            memory_usage_limit="high",    # Can use more memory for speed
            metadata_compression=True,
            minimize_metadata=True        # Critical for large media files
        ),
        
        SecurityProfile.CREDENTIALS: ProfileParameters(
            lattice_size=256,             # Maximum security
            depth=8,                      # Maximum depth
            morph_interval=50,            # Frequent morphing
            phe_path_count=15,            # Maximum paths
            phe_difficulty_base=2,        # Higher base difficulty
            adaptive_difficulty=True,
            use_decoys=True,
            decoy_count_base=7,           # Maximum decoys
            variable_decoy_sizes=True,
            randomize_decoy_count=True,
            adaptive_morphing=True,
            adaptive_decoy_sizing=False,  # Always use full security
            timing_randomization=True,    # Extra protection
            optimize_for="security",
            memory_usage_limit="high",
            metadata_compression=True,
            minimize_metadata=False
        ),
        
        SecurityProfile.BACKUP: ProfileParameters(
            lattice_size=64,              # Minimum for speed
            depth=4,                      # Minimum depth
            morph_interval=200,           # Infrequent morphing
            phe_path_count=3,             # Minimum paths
            phe_difficulty_base=1,
            adaptive_difficulty=False,
            use_decoys=False,             # Disabled for maximum speed
            decoy_count_base=1,
            variable_decoy_sizes=False,
            randomize_decoy_count=False,
            adaptive_morphing=False,
            adaptive_decoy_sizing=True,
            timing_randomization=False,
            optimize_for="speed",
            memory_usage_limit="low",
            metadata_compression=True,
            minimize_metadata=True
        )
    }
    
    # File type mappings for auto-detection
    FILE_TYPE_MAPPINGS = {
        # Document types
        'document': [
            '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt',
            '.xls', '.xlsx', '.ods', '.ppt', '.pptx', '.odp',
            '.md', '.tex', '.csv', '.xml', '.html'
        ],
        
        # Media types
        'media': [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'
        ],
        
        # Credential types
        'credentials': [
            '.key', '.pem', '.crt', '.p12', '.pfx', '.jks',
            '.kdb', '.kdbx', '.wallet', '.keystore'
        ],
        
        # Backup/Archive types
        'backup': [
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
            '.xz', '.iso', '.img', '.dmg', '.backup', '.bak'
        ]
    }
    
    @classmethod
    def detect_profile_from_file(cls, filepath: str) -> SecurityProfile:
        """Auto-detect security profile based on file characteristics"""
        
        # Get file extension
        _, ext = os.path.splitext(filepath.lower())
        
        # Check explicit mappings first
        for profile_name, extensions in cls.FILE_TYPE_MAPPINGS.items():
            if ext in extensions:
                return SecurityProfile(profile_name)
        
        # Use MIME type as fallback
        mimetype, _ = mimetypes.guess_type(filepath)
        if mimetype:
            if mimetype.startswith('text/'):
                return SecurityProfile.DOCUMENT
            elif mimetype.startswith('image/') or mimetype.startswith('video/') or mimetype.startswith('audio/'):
                return SecurityProfile.MEDIA
            elif mimetype.startswith('application/'):
                # Archive types
                if any(archive in mimetype for archive in ['zip', 'tar', 'gzip', 'compress']):
                    return SecurityProfile.BACKUP
                else:
                    return SecurityProfile.DOCUMENT
        
        # Default fallback
        return SecurityProfile.DOCUMENT
    
    @classmethod
    def detect_profile_from_content(cls, data: bytes, filename: str = "") -> SecurityProfile:
        """Detect profile from file content and name"""
        
        # First try filename-based detection
        if filename:
            profile = cls.detect_profile_from_file(filename)
            if profile != SecurityProfile.DOCUMENT:  # If we got a specific match
                return profile
        
        # Content-based heuristics
        if len(data) < 1024:
            return SecurityProfile.CREDENTIALS  # Small files likely sensitive
        
        # Check for common file signatures
        if data.startswith(b'%PDF'):
            return SecurityProfile.DOCUMENT
        elif data.startswith((b'\x89PNG', b'\xff\xd8\xff', b'GIF8')):
            return SecurityProfile.MEDIA
        elif data.startswith((b'PK\x03\x04', b'Rar!', b'7z\xbc\xaf')):
            return SecurityProfile.BACKUP
        elif data.startswith((b'-----BEGIN', b'-----END')):
            return SecurityProfile.CREDENTIALS
        
        # Default to document profile
        return SecurityProfile.DOCUMENT
    
    @classmethod
    def get_profile_parameters(cls, profile: SecurityProfile, 
                             file_size: Optional[int] = None,
                             custom_overrides: Optional[Dict[str, Any]] = None) -> ProfileParameters:
        """Get optimized parameters for a security profile"""
        
        if profile == SecurityProfile.CUSTOM and custom_overrides:
            # Start with document profile as base
            base_params = cls.PROFILE_CONFIGS[SecurityProfile.DOCUMENT]
            params = ProfileParameters(**asdict(base_params))
            
            # Apply custom overrides
            for key, value in custom_overrides.items():
                if hasattr(params, key):
                    setattr(params, key, value)
            
            return params
        
        # Get base parameters for profile
        base_params = cls.PROFILE_CONFIGS.get(profile, cls.PROFILE_CONFIGS[SecurityProfile.DOCUMENT])
        params = ProfileParameters(**asdict(base_params))
        
        # Apply file size optimizations
        if file_size is not None:
            params = cls._optimize_for_file_size(params, file_size)
        
        return params
    
    @classmethod
    def _optimize_for_file_size(cls, params: ProfileParameters, file_size: int) -> ProfileParameters:
        """Optimize parameters based on file size"""
        
        # Size categories
        if file_size < 10 * 1024:  # <10KB
            # Very small files - minimal overhead
            if params.optimize_for != "security":
                params.decoy_count_base = max(1, params.decoy_count_base - 1)
                params.minimize_metadata = True
        
        elif file_size < 1024 * 1024:  # <1MB
            # Small files - balance efficiency
            if params.optimize_for == "speed":
                params.decoy_count_base = max(1, params.decoy_count_base - 1)
            params.adaptive_decoy_sizing = True
        
        elif file_size < 100 * 1024 * 1024:  # <100MB
            # Medium files - standard parameters work well
            pass
        
        else:  # >=100MB
            # Large files - optimize for streaming and memory
            if params.optimize_for != "security":
                params.lattice_size = min(params.lattice_size, 128)  # Cap lattice size
                params.depth = min(params.depth, 6)  # Cap depth
            
            params.minimize_metadata = True
            params.adaptive_decoy_sizing = True
        
        return params
    
    @classmethod
    def recommend_profile(cls, filepath: str = "", file_size: int = 0, 
                         content_sample: bytes = b"") -> Dict[str, Any]:
        """Provide profile recommendation with explanation"""
        
        # Auto-detect profile
        if content_sample and filepath:
            detected_profile = cls.detect_profile_from_content(content_sample, filepath)
        elif filepath:
            detected_profile = cls.detect_profile_from_file(filepath)
        else:
            detected_profile = SecurityProfile.DOCUMENT
        
        # Get profile parameters
        params = cls.get_profile_parameters(detected_profile, file_size)
        
        # Generate explanation
        explanation = cls._generate_recommendation_explanation(
            detected_profile, file_size, filepath
        )
        
        # Calculate expected performance
        performance = cls._estimate_performance(params, file_size)
        
        return {
            'recommended_profile': detected_profile.value,
            'parameters': asdict(params),
            'explanation': explanation,
            'estimated_performance': performance,
            'alternatives': cls._suggest_alternatives(detected_profile, file_size)
        }
    
    @classmethod
    def _generate_recommendation_explanation(cls, profile: SecurityProfile, 
                                           file_size: int, filepath: str) -> str:
        """Generate human-readable explanation for profile choice"""
        
        explanations = {
            SecurityProfile.DOCUMENT: (
                "Recommended for office documents, PDFs, and text files. "
                "Provides balanced security and performance with good metadata efficiency."
            ),
            SecurityProfile.MEDIA: (
                "Optimized for photos, videos, and audio files. "
                "Prioritizes speed and minimal metadata overhead for large media files."
            ),
            SecurityProfile.CREDENTIALS: (
                "Maximum security for passwords, keys, and sensitive data. "
                "Uses strongest encryption with extra protection features enabled."
            ),
            SecurityProfile.BACKUP: (
                "Fast processing for archives and backup files. "
                "Optimized for speed with minimal security overhead."
            )
        }
        
        base_explanation = explanations.get(profile, explanations[SecurityProfile.DOCUMENT])
        
        # Add file size context
        if file_size > 0:
            if file_size < 10 * 1024:
                size_context = " Optimized for very small files with minimal metadata overhead."
            elif file_size < 1024 * 1024:
                size_context = " Good balance of security and efficiency for small files."
            elif file_size < 100 * 1024 * 1024:
                size_context = " Standard parameters work well for medium-sized files."
            else:
                size_context = " Optimized for large files with streaming support and memory efficiency."
            
            base_explanation += size_context
        
        return base_explanation
    
    @classmethod
    def _estimate_performance(cls, params: ProfileParameters, file_size: int) -> Dict[str, float]:
        """Estimate performance characteristics"""
        
        # Base performance factors
        lattice_factor = (params.lattice_size / 128) ** 2
        depth_factor = params.depth / 6
        decoy_factor = params.decoy_count_base / 3
        
        # Estimate encryption time (seconds)
        base_time = 1.0  # Base time for 128x128x6 with 3 decoys
        encryption_time = base_time * lattice_factor * depth_factor * decoy_factor
        
        # File size impact
        if file_size > 0:
            size_factor = max(1.0, file_size / (1024 * 1024))  # Scale by MB
            encryption_time *= (1.0 + size_factor * 0.1)  # 10% increase per MB
        
        # Decryption time (typically faster)
        decryption_time = encryption_time * 0.7
        
        # Memory usage (MB)
        base_memory = 50  # Base memory usage
        memory_usage = base_memory * lattice_factor * depth_factor
        
        # Metadata size estimation
        if file_size > 0:
            try:
                from ..metadata.layered_format import MetadataFactory
                profile_enum = SecurityProfile(params.optimize_for) if params.optimize_for in ['document', 'media', 'credentials', 'backup'] else SecurityProfile.DOCUMENT
                metadata_size = MetadataFactory.estimate_metadata_size(file_size, profile_enum)
            except ImportError:
                # Fallback estimation if metadata module not available
                metadata_size = cls._estimate_metadata_size_fallback(file_size, params)
        else:
            metadata_size = 25000  # Default estimate
        
        return {
            'encryption_time_seconds': round(encryption_time, 2),
            'decryption_time_seconds': round(decryption_time, 2),
            'memory_usage_mb': round(memory_usage, 1),
            'metadata_size_kb': round(metadata_size / 1024, 1),
            'relative_speed': cls._calculate_relative_speed(params),
            'security_level': cls._calculate_security_level(params)
        }
    
    @classmethod
    def _calculate_relative_speed(cls, params: ProfileParameters) -> str:
        """Calculate relative speed rating"""
        
        # Speed factors (lower = faster)
        speed_score = 0
        speed_score += params.lattice_size / 32  # Lattice size impact
        speed_score += params.depth * 0.5  # Depth impact
        speed_score += params.decoy_count_base * 0.3  # Decoy impact
        speed_score += params.phe_path_count * 0.1  # PHE impact
        
        if speed_score < 5:
            return "Very Fast"
        elif speed_score < 8:
            return "Fast"
        elif speed_score < 12:
            return "Moderate"
        elif speed_score < 16:
            return "Slow"
        else:
            return "Very Slow"
    
    @classmethod
    def _calculate_security_level(cls, params: ProfileParameters) -> str:
        """Calculate security level rating"""
        
        # Security factors (higher = more secure)
        security_score = 0
        security_score += params.lattice_size / 32  # Lattice size
        security_score += params.depth * 0.8  # Depth
        security_score += params.decoy_count_base * 0.5  # Decoys
        security_score += params.phe_path_count * 0.2  # PHE paths
        
        # Adaptive features bonus
        if params.adaptive_difficulty:
            security_score += 1
        if params.adaptive_morphing:
            security_score += 1
        if params.timing_randomization:
            security_score += 1
        
        if security_score < 6:
            return "Basic"
        elif security_score < 10:
            return "Good"
        elif security_score < 15:
            return "High"
        elif security_score < 20:
            return "Very High"
        else:
            return "Maximum"
    
    @classmethod
    def _suggest_alternatives(cls, current_profile: SecurityProfile, 
                            file_size: int) -> List[Dict[str, str]]:
        """Suggest alternative profiles"""
        
        alternatives = []
        
        # Always suggest custom profile
        alternatives.append({
            'profile': SecurityProfile.CUSTOM.value,
            'reason': 'Full control over all parameters'
        })
        
        # Suggest based on current profile
        if current_profile == SecurityProfile.DOCUMENT:
            if file_size > 100 * 1024 * 1024:  # Large file
                alternatives.append({
                    'profile': SecurityProfile.MEDIA.value,
                    'reason': 'Better performance for large files'
                })
            alternatives.append({
                'profile': SecurityProfile.CREDENTIALS.value,
                'reason': 'Maximum security if data is sensitive'
            })
        
        elif current_profile == SecurityProfile.MEDIA:
            alternatives.append({
                'profile': SecurityProfile.DOCUMENT.value,
                'reason': 'Better security if file contains sensitive content'
            })
            if file_size > 1024 * 1024 * 1024:  # Very large
                alternatives.append({
                    'profile': SecurityProfile.BACKUP.value,
                    'reason': 'Fastest processing for very large files'
                })
        
        elif current_profile == SecurityProfile.CREDENTIALS:
            if file_size > 10 * 1024 * 1024:  # Large sensitive file
                alternatives.append({
                    'profile': SecurityProfile.DOCUMENT.value,
                    'reason': 'Better balance of security and performance for larger files'
                })
        
        elif current_profile == SecurityProfile.BACKUP:
            alternatives.append({
                'profile': SecurityProfile.DOCUMENT.value,
                'reason': 'Better security with modest performance cost'
            })
        
        return alternatives
    
    @classmethod
    def _estimate_metadata_size_fallback(cls, file_size: int, params: ProfileParameters) -> int:
        """Fallback metadata size estimation when MetadataFactory not available"""
        
        # Base metadata sizes (bytes)
        core_size = 8192  # 8KB core metadata
        
        # Security layer estimation
        if file_size < 1024 * 1024:  # <1MB - Algorithmic decoys
            security_size = 200  # Minimal storage
        elif file_size < 100 * 1024 * 1024:  # <100MB - Differential decoys
            security_size = min(5000, file_size // 1000)  # ~0.1% of file size, max 5KB
        else:  # >=100MB - Selective decoys
            security_size = min(20000, file_size // 10000)  # ~0.01% of file size, max 20KB
        
        # Extension layer
        extension_size = 1024  # 1KB for future extensions
        
        # Apply profile adjustments
        if params.optimize_for == "speed":
            security_size = int(security_size * 0.7)  # Reduce for speed
        elif params.optimize_for == "security":
            security_size = int(security_size * 1.5)  # Increase for security
        
        return core_size + security_size + extension_size

# Convenience functions for common operations
def get_profile_for_file(filepath: str) -> SecurityProfile:
    """Get recommended profile for a file"""
    return SecurityProfileManager.detect_profile_from_file(filepath)

def get_optimized_parameters(profile: SecurityProfile, file_size: int = 0) -> Dict[str, Any]:
    """Get optimized parameters for profile and file size"""
    params = SecurityProfileManager.get_profile_parameters(profile, file_size)
    return asdict(params)

def recommend_profile_interactive(filepath: str = "", file_size: int = 0) -> Dict[str, Any]:
    """Interactive profile recommendation"""
    return SecurityProfileManager.recommend_profile(filepath, file_size)