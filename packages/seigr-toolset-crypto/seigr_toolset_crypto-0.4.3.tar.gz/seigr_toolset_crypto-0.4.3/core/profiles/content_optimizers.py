"""
Profile-Specific Optimizations System v0.3.1 - Phase 3

Specialized optimization strategies for different content types,
leveraging content characteristics for maximum efficiency.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from .profile_definitions import IntelligentSecurityProfile, IntelligentProfileParameters

class OptimizationStrategy(Enum):
    """Optimization strategy types"""
    COMPRESSION_FIRST = "compression_first"
    ENCRYPTION_FIRST = "encryption_first"  
    PARALLEL_PROCESSING = "parallel_processing"
    STREAMING_OPTIMIZED = "streaming_optimized"
    MEMORY_EFFICIENT = "memory_efficient"
    SPEED_OPTIMIZED = "speed_optimized"
    SIZE_OPTIMIZED = "size_optimized"
    HYBRID_APPROACH = "hybrid_approach"

@dataclass
class OptimizationConfig:
    """Configuration for profile-specific optimizations"""
    
    # Core strategy
    primary_strategy: OptimizationStrategy = OptimizationStrategy.HYBRID_APPROACH
    secondary_strategies: List[OptimizationStrategy] = None
    
    # Content-specific parameters
    content_type_hint: str = "unknown"
    estimated_compression_ratio: float = 0.5
    entropy_threshold: float = 7.0
    
    # Processing parameters
    chunk_size_kb: int = 64
    buffer_size_kb: int = 256
    parallel_chunk_count: int = 4
    
    # Optimization targets
    target_compression_ratio: float = 0.3
    target_speed_mbps: float = 50.0
    target_memory_mb: int = 128
    
    # Advanced features
    use_content_aware_chunking: bool = True
    enable_predictive_prefetch: bool = False
    adaptive_parameters: bool = True
    
    def __post_init__(self):
        if self.secondary_strategies is None:
            self.secondary_strategies = []

class ContentOptimizer(ABC):
    """Abstract base class for content-specific optimizers"""
    
    @abstractmethod
    def analyze_content(self, data: bytes) -> Dict[str, Any]:
        """Analyze content characteristics"""
        pass
    
    @abstractmethod
    def optimize_parameters(self, params: IntelligentProfileParameters, 
                          content_analysis: Dict[str, Any]) -> IntelligentProfileParameters:
        """Optimize parameters for this content type"""
        pass
    
    @abstractmethod
    def get_processing_strategy(self, content_analysis: Dict[str, Any]) -> OptimizationConfig:
        """Get optimal processing strategy"""
        pass
    
    @abstractmethod
    def estimate_performance(self, params: IntelligentProfileParameters,
                           content_size: int) -> Dict[str, float]:
        """Estimate performance metrics"""
        pass

class TextDocumentOptimizer(ContentOptimizer):
    """Optimizer for text documents (DOCUMENT_TEXT)"""
    
    # Text-specific patterns
    REPETITIVE_PATTERNS = [
        rb'\s+',           # Whitespace runs
        rb'(.)\1{3,}',     # Character repetition
        rb'(\w+\s+)\1{2,}', # Word repetition
    ]
    
    STRUCTURED_INDICATORS = [
        rb'<[^>]+>',       # XML/HTML tags
        rb'\{[^}]*\}',     # JSON objects
        rb'^\s*#',         # Comments/headers
        rb'^\s*\d+\.',     # Numbered lists
    ]
    
    def analyze_content(self, data: bytes) -> Dict[str, Any]:
        """Analyze text document characteristics"""
        
        analysis = {
            'content_type': 'text_document',
            'text_ratio': 0.0,
            'repetition_score': 0.0,
            'structure_score': 0.0,
            'compression_potential': 0.0,
            'chunking_strategy': 'line_aware',
            'optimization_hints': []
        }
        
        try:
            # Decode as text
            text = data.decode('utf-8', errors='ignore')
            analysis['text_ratio'] = len(text.encode('utf-8')) / len(data) if data else 0
            
            # Analyze repetition patterns
            repetition_count = 0
            for pattern in self.REPETITIVE_PATTERNS:
                import re
                matches = re.findall(pattern, data)
                repetition_count += len(matches)
            
            analysis['repetition_score'] = min(1.0, repetition_count / (len(data) / 1000))
            
            # Analyze structure
            structure_count = 0
            for pattern in self.STRUCTURED_INDICATORS:
                import re
                matches = re.findall(pattern, data)
                structure_count += len(matches)
            
            analysis['structure_score'] = min(1.0, structure_count / (len(data) / 500))
            
            # Estimate compression potential
            if analysis['repetition_score'] > 0.3:
                analysis['compression_potential'] = 0.8
                analysis['optimization_hints'].append('high_repetition_detected')
            elif analysis['structure_score'] > 0.2:
                analysis['compression_potential'] = 0.6
                analysis['optimization_hints'].append('structured_content_detected')
            else:
                analysis['compression_potential'] = 0.4
            
            # Determine chunking strategy
            if '\n' in text and len(text.split('\n')) > 10:
                analysis['chunking_strategy'] = 'line_aware'
            elif analysis['structure_score'] > 0.3:
                analysis['chunking_strategy'] = 'structure_aware'
            else:
                analysis['chunking_strategy'] = 'fixed_size'
            
        except Exception as e:
            analysis['error'] = str(e)
            analysis['compression_potential'] = 0.3  # Conservative estimate
        
        return analysis
    
    def optimize_parameters(self, params: IntelligentProfileParameters,
                          content_analysis: Dict[str, Any]) -> IntelligentProfileParameters:
        """Optimize parameters for text documents"""
        
        optimized = IntelligentProfileParameters(**asdict(params))
        
        # Compression optimization
        compression_potential = content_analysis.get('compression_potential', 0.4)
        if compression_potential > 0.6:
            optimized.compression_strategy = 'maximum'
        elif compression_potential < 0.3:
            optimized.compression_strategy = 'fast'
        
        # Chunk size optimization for text
        if content_analysis.get('chunking_strategy') == 'line_aware':
            optimized.chunk_size_preference = 'medium'  # Good balance for text
        elif content_analysis.get('structure_score', 0) > 0.5:
            optimized.chunk_size_preference = 'large'   # Preserve structure
        
        # Security adjustments for text
        if content_analysis.get('text_ratio', 0) > 0.9:  # Pure text
            optimized.content_sensitivity = 'medium'  # Usually safe
        
        # Memory optimization
        if content_analysis.get('repetition_score', 0) > 0.5:
            optimized.memory_usage_limit = 'moderate'  # Compression will help
        
        return optimized
    
    def get_processing_strategy(self, content_analysis: Dict[str, Any]) -> OptimizationConfig:
        """Get optimal processing strategy for text documents"""
        
        config = OptimizationConfig(
            content_type_hint='text_document',
            estimated_compression_ratio=content_analysis.get('compression_potential', 0.4)
        )
        
        # Strategy selection
        if content_analysis.get('compression_potential', 0) > 0.6:
            config.primary_strategy = OptimizationStrategy.COMPRESSION_FIRST
        elif content_analysis.get('text_ratio', 0) > 0.95:
            config.primary_strategy = OptimizationStrategy.SPEED_OPTIMIZED
        else:
            config.primary_strategy = OptimizationStrategy.HYBRID_APPROACH
        
        # Chunking configuration
        if content_analysis.get('chunking_strategy') == 'line_aware':
            config.use_content_aware_chunking = True
            config.chunk_size_kb = 32  # Smaller chunks for line boundaries
        
        return config
    
    def estimate_performance(self, params: IntelligentProfileParameters,
                           content_size: int) -> Dict[str, float]:
        """Estimate performance for text documents"""
        
        # Base estimates
        base_encryption_speed = 20.0  # MB/s
        base_compression_ratio = 0.4
        
        # Text-specific adjustments
        if params.compression_strategy == 'maximum':
            compression_ratio = 0.25
            speed_multiplier = 0.7
        elif params.compression_strategy == 'fast':
            compression_ratio = 0.5
            speed_multiplier = 1.3
        else:
            compression_ratio = base_compression_ratio
            speed_multiplier = 1.0
        
        # Size-based adjustments
        size_mb = content_size / (1024 * 1024)
        if size_mb > 100:
            speed_multiplier *= 0.9  # Larger files slightly slower
        
        return {
            'estimated_encryption_speed_mbps': base_encryption_speed * speed_multiplier,
            'estimated_compression_ratio': compression_ratio,
            'estimated_total_time_seconds': size_mb / (base_encryption_speed * speed_multiplier),
            'estimated_output_size_mb': size_mb * compression_ratio * 1.1,  # Include metadata
            'memory_usage_mb': min(128, max(32, size_mb * 0.2))
        }

class MediaOptimizer(ContentOptimizer):
    """Optimizer for media files (MEDIA_IMAGE, MEDIA_VIDEO, MEDIA_AUDIO)"""
    
    # Media file signatures and characteristics
    MEDIA_SIGNATURES = {
        b'\xff\xd8\xff': {'type': 'JPEG', 'compressible': False, 'chunk_friendly': True},
        b'\x89\x50\x4e\x47': {'type': 'PNG', 'compressible': False, 'chunk_friendly': True},
        b'\x47\x49\x46': {'type': 'GIF', 'compressible': False, 'chunk_friendly': False},
        b'\x52\x49\x46\x46': {'type': 'RIFF', 'compressible': False, 'chunk_friendly': True},
        b'\x00\x00\x00\x18\x66\x74\x79\x70': {'type': 'MP4', 'compressible': False, 'chunk_friendly': True},
        b'\x1a\x45\xdf\xa3': {'type': 'MKV', 'compressible': False, 'chunk_friendly': True},
    }
    
    def analyze_content(self, data: bytes) -> Dict[str, Any]:
        """Analyze media file characteristics"""
        
        analysis = {
            'content_type': 'media_file',
            'media_format': 'unknown',
            'is_compressed': True,  # Most media is pre-compressed
            'chunk_friendly': True,
            'has_metadata': False,
            'streaming_suitable': False,
            'optimization_hints': []
        }
        
        # Detect media format
        for signature, info in self.MEDIA_SIGNATURES.items():
            if data.startswith(signature):
                analysis['media_format'] = info['type']
                analysis['is_compressed'] = not info['compressible']
                analysis['chunk_friendly'] = info['chunk_friendly']
                break
        
        # Check for metadata sections (EXIF, ID3, etc.)
        if b'EXIF' in data[:1024] or b'ID3' in data[:1024]:
            analysis['has_metadata'] = True
            analysis['optimization_hints'].append('metadata_detected')
        
        # Streaming suitability
        if len(data) > 10 * 1024 * 1024:  # >10MB
            analysis['streaming_suitable'] = True
            analysis['optimization_hints'].append('streaming_recommended')
        
        # Compression analysis
        if analysis['is_compressed']:
            analysis['optimization_hints'].append('skip_compression')
        
        return analysis
    
    def optimize_parameters(self, params: IntelligentProfileParameters,
                          content_analysis: Dict[str, Any]) -> IntelligentProfileParameters:
        """Optimize parameters for media files"""
        
        optimized = IntelligentProfileParameters(**asdict(params))
        
        # Skip compression for pre-compressed media
        if content_analysis.get('is_compressed', True):
            optimized.compression_strategy = 'none'
        
        # Optimize for streaming if suitable
        if content_analysis.get('streaming_suitable', False):
            optimized.streaming_optimized = True
            optimized.chunk_size_preference = 'large'
        
        # Memory optimization for large media files
        optimized.memory_usage_limit = 'moderate'
        
        # Security optimization (media usually lower sensitivity)
        if optimized.content_sensitivity == 'medium':
            optimized.content_sensitivity = 'low'  # Media usually less sensitive
        
        # Chunk-friendly optimization
        if content_analysis.get('chunk_friendly', True):
            optimized.parallel_processing = True
        
        return optimized
    
    def get_processing_strategy(self, content_analysis: Dict[str, Any]) -> OptimizationConfig:
        """Get optimal processing strategy for media files"""
        
        config = OptimizationConfig(
            content_type_hint='media_file',
            estimated_compression_ratio=0.95  # Minimal compression expected
        )
        
        # Strategy selection based on file characteristics
        if content_analysis.get('streaming_suitable', False):
            config.primary_strategy = OptimizationStrategy.STREAMING_OPTIMIZED
            config.secondary_strategies = [OptimizationStrategy.PARALLEL_PROCESSING]
        elif content_analysis.get('chunk_friendly', True):
            config.primary_strategy = OptimizationStrategy.PARALLEL_PROCESSING
        else:
            config.primary_strategy = OptimizationStrategy.SPEED_OPTIMIZED
        
        # Disable compression for pre-compressed media
        if content_analysis.get('is_compressed', True):
            config.target_compression_ratio = 0.95
        
        # Large chunk sizes for media
        config.chunk_size_kb = 256
        config.buffer_size_kb = 512
        
        return config
    
    def estimate_performance(self, params: IntelligentProfileParameters,
                           content_size: int) -> Dict[str, float]:
        """Estimate performance for media files"""
        
        # Media files typically encrypt faster (no compression overhead)
        base_encryption_speed = 80.0  # MB/s
        
        # Streaming optimization boost
        if params.streaming_optimized:
            speed_multiplier = 1.5
        else:
            speed_multiplier = 1.0
        
        size_mb = content_size / (1024 * 1024)
        
        return {
            'estimated_encryption_speed_mbps': base_encryption_speed * speed_multiplier,
            'estimated_compression_ratio': 0.95,  # Minimal compression
            'estimated_total_time_seconds': size_mb / (base_encryption_speed * speed_multiplier),
            'estimated_output_size_mb': size_mb * 1.05,  # Small metadata overhead
            'memory_usage_mb': min(256, max(64, size_mb * 0.1))  # Lower memory for media
        }

class CredentialsOptimizer(ContentOptimizer):
    """Optimizer for credential files (CREDENTIALS_*)"""
    
    # Credential patterns and formats (simple string matching)
    CREDENTIAL_PATTERNS = [
        b'-----BEGIN',
        b'PRIVATE KEY',
        b'password',
        b'api_key',
        b'secret',
        b'token',
        b'database_password',
    ]
    
    def analyze_content(self, data: bytes) -> Dict[str, Any]:
        """Analyze credential file characteristics"""
        
        analysis = {
            'content_type': 'credentials',
            'credential_count': 0,
            'has_private_keys': False,
            'structured_format': False,
            'sensitivity_level': 'high',
            'optimization_hints': []
        }
        
        # Count credential patterns using simple string matching
        credential_count = 0
        data_lower = data.lower()
        
        for pattern in self.CREDENTIAL_PATTERNS:
            if pattern.lower() in data_lower:
                credential_count += 1
            
            if b'private key' in pattern.lower():
                analysis['has_private_keys'] = True
        
        analysis['credential_count'] = credential_count
        
        # Check for structured formats
        try:
            text = data.decode('utf-8', errors='ignore')
            if any(indicator in text for indicator in ['{', '[', '<', 'BEGIN']):
                analysis['structured_format'] = True
        except (UnicodeDecodeError, AttributeError):
            # Non-text data or decoding error - skip structured format check
            pass
        
        # Determine sensitivity level
        if analysis['has_private_keys'] or credential_count > 5:
            analysis['sensitivity_level'] = 'maximum'
        elif credential_count > 0:
            analysis['sensitivity_level'] = 'high'
        
        # Optimization hints
        if analysis['credential_count'] > 0:
            analysis['optimization_hints'].append('maximum_security_required')
        if analysis['structured_format']:
            analysis['optimization_hints'].append('preserve_structure')
        
        return analysis
    
    def optimize_parameters(self, params: IntelligentProfileParameters,
                          content_analysis: Dict[str, Any]) -> IntelligentProfileParameters:
        """Optimize parameters for credential files"""
        
        optimized = IntelligentProfileParameters(**asdict(params))
        
        # Maximum security for credentials
        optimized.lattice_size = max(optimized.lattice_size, 256)
        optimized.depth = max(optimized.depth, 8)
        optimized.phe_path_count = max(optimized.phe_path_count, 15)
        
        # Enable all security features
        optimized.forward_secrecy = True
        optimized.plausible_deniability = True
        optimized.content_sensitivity = 'maximum'
        
        # Optimize for security over speed
        optimized.optimize_for = 'security'
        
        # Enhanced metadata protection
        optimized.metadata_strategy = 'comprehensive'
        optimized.checksum_strategy = 'paranoid'
        
        # Disable streaming for small credential files
        optimized.streaming_optimized = False
        
        return optimized
    
    def get_processing_strategy(self, content_analysis: Dict[str, Any]) -> OptimizationConfig:
        """Get optimal processing strategy for credentials"""
        
        config = OptimizationConfig(
            content_type_hint='credentials',
            estimated_compression_ratio=0.6  # Text-based, some compression possible
        )
        
        # Security-first strategy
        config.primary_strategy = OptimizationStrategy.ENCRYPTION_FIRST
        config.secondary_strategies = [OptimizationStrategy.SIZE_OPTIMIZED]
        
        # Conservative chunk sizes for credentials
        config.chunk_size_kb = 16
        config.buffer_size_kb = 64
        
        # Enable advanced features
        config.adaptive_parameters = True
        
        return config
    
    def estimate_performance(self, params: IntelligentProfileParameters,
                           content_size: int) -> Dict[str, float]:
        """Estimate performance for credential files"""
        
        # Credential files prioritize security over speed
        base_encryption_speed = 10.0  # MB/s (slower due to security)
        
        size_mb = content_size / (1024 * 1024)
        
        # Most credential files are small
        if size_mb < 1:
            speed_multiplier = 0.8  # Extra security overhead
        else:
            speed_multiplier = 1.0
        
        return {
            'estimated_encryption_speed_mbps': base_encryption_speed * speed_multiplier,
            'estimated_compression_ratio': 0.6,
            'estimated_total_time_seconds': max(1.0, size_mb / (base_encryption_speed * speed_multiplier)),
            'estimated_output_size_mb': max(0.1, size_mb * 0.7),  # Some compression + metadata
            'memory_usage_mb': min(64, max(16, size_mb * 0.5))
        }

class SourceCodeOptimizer(ContentOptimizer):
    """Optimizer for source code files (SOURCE_CODE)"""
    
    # Programming language indicators
    LANGUAGE_PATTERNS = {
        'python': [rb'def\s+\w+', rb'import\s+\w+', rb'class\s+\w+'],
        'javascript': [rb'function\s+\w+', rb'const\s+\w+\s*=', rb'let\s+\w+'],
        'java': [rb'public\s+class', rb'private\s+\w+', rb'import\s+\w+'],
        'cpp': [rb'#include\s*<', rb'class\s+\w+', rb'namespace\s+\w+'],
        'html': [rb'<html', rb'<body', rb'<div'],
        'css': [rb'\w+\s*{', rb'@media', rb'#\w+'],
        'json': [rb'{\s*"', rb'"\s*:\s*"', rb']\s*}'],
        'xml': [rb'<?xml', rb'<\w+[^>]*>', rb'</\w+>'],
    }
    
    def analyze_content(self, data: bytes) -> Dict[str, Any]:
        """Analyze source code characteristics"""
        
        analysis = {
            'content_type': 'source_code',
            'detected_language': 'unknown',
            'comment_ratio': 0.0,
            'whitespace_ratio': 0.0,
            'repetition_potential': 0.0,
            'minification_potential': 0.0,
            'optimization_hints': []
        }
        
        import re
        
        # Detect programming language
        language_scores = {}
        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, data))
                score += matches
            language_scores[lang] = score
        
        if language_scores:
            analysis['detected_language'] = max(language_scores, key=language_scores.get)
        
        try:
            text = data.decode('utf-8', errors='ignore')
            
            # Analyze comment ratio
            comment_chars = 0
            for line in text.split('\n'):
                stripped = line.strip()
                if stripped.startswith(('#', '//', '/*', '<!--')):
                    comment_chars += len(line)
            
            analysis['comment_ratio'] = comment_chars / len(text) if text else 0
            
            # Analyze whitespace
            whitespace_chars = sum(1 for c in text if c.isspace())
            analysis['whitespace_ratio'] = whitespace_chars / len(text) if text else 0
            
            # Estimate minification potential
            if analysis['detected_language'] in ['javascript', 'css', 'html']:
                analysis['minification_potential'] = analysis['whitespace_ratio'] + analysis['comment_ratio']
                if analysis['minification_potential'] > 0.3:
                    analysis['optimization_hints'].append('high_minification_potential')
            
            # Repetition analysis for compression
            if analysis['comment_ratio'] > 0.2 or analysis['whitespace_ratio'] > 0.3:
                analysis['repetition_potential'] = 0.7
                analysis['optimization_hints'].append('high_compression_potential')
            else:
                analysis['repetition_potential'] = 0.4
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def optimize_parameters(self, params: IntelligentProfileParameters,
                          content_analysis: Dict[str, Any]) -> IntelligentProfileParameters:
        """Optimize parameters for source code"""
        
        optimized = IntelligentProfileParameters(**asdict(params))
        
        # Compression optimization
        repetition_potential = content_analysis.get('repetition_potential', 0.4)
        if repetition_potential > 0.6:
            optimized.compression_strategy = 'maximum'
        else:
            optimized.compression_strategy = 'adaptive'
        
        # Security level for source code (usually medium)
        if optimized.content_sensitivity == 'high':
            optimized.content_sensitivity = 'medium'  # Source code typically medium sensitivity
        
        # Chunk size optimization
        optimized.chunk_size_preference = 'medium'  # Good for code structure
        
        # Enable streaming for large repositories
        if content_analysis.get('size_mb', 0) > 5:
            optimized.streaming_optimized = True
        
        return optimized
    
    def get_processing_strategy(self, content_analysis: Dict[str, Any]) -> OptimizationConfig:
        """Get optimal processing strategy for source code"""
        
        config = OptimizationConfig(
            content_type_hint='source_code',
            estimated_compression_ratio=content_analysis.get('repetition_potential', 0.4)
        )
        
        # Strategy based on compression potential
        if content_analysis.get('repetition_potential', 0) > 0.6:
            config.primary_strategy = OptimizationStrategy.COMPRESSION_FIRST
        else:
            config.primary_strategy = OptimizationStrategy.HYBRID_APPROACH
        
        # Language-specific optimizations
        language = content_analysis.get('detected_language', 'unknown')
        if language in ['javascript', 'css', 'html']:
            config.target_compression_ratio = 0.3  # High compression potential
        elif language in ['python', 'java']:
            config.target_compression_ratio = 0.5  # Moderate compression
        
        return config
    
    def estimate_performance(self, params: IntelligentProfileParameters,
                           content_size: int) -> Dict[str, float]:
        """Estimate performance for source code"""
        
        base_encryption_speed = 30.0  # MB/s
        
        # Compression strategy impact
        if params.compression_strategy == 'maximum':
            compression_ratio = 0.35
            speed_multiplier = 0.8
        elif params.compression_strategy == 'adaptive':
            compression_ratio = 0.5
            speed_multiplier = 1.0
        else:
            compression_ratio = 0.7
            speed_multiplier = 1.2
        
        size_mb = content_size / (1024 * 1024)
        
        return {
            'estimated_encryption_speed_mbps': base_encryption_speed * speed_multiplier,
            'estimated_compression_ratio': compression_ratio,
            'estimated_total_time_seconds': size_mb / (base_encryption_speed * speed_multiplier),
            'estimated_output_size_mb': size_mb * compression_ratio * 1.1,
            'memory_usage_mb': min(128, max(32, size_mb * 0.3))
        }

class ProfileOptimizationManager:
    """Main manager for profile-specific optimizations"""
    
    def __init__(self):
        self.optimizers = {
            IntelligentSecurityProfile.DOCUMENT_TEXT: TextDocumentOptimizer(),
            IntelligentSecurityProfile.DOCUMENT_OFFICE: TextDocumentOptimizer(),  # Similar to text
            IntelligentSecurityProfile.DOCUMENT_PDF: TextDocumentOptimizer(),     # Document-like
            IntelligentSecurityProfile.MEDIA_IMAGE: MediaOptimizer(),
            IntelligentSecurityProfile.MEDIA_VIDEO: MediaOptimizer(),
            IntelligentSecurityProfile.MEDIA_AUDIO: MediaOptimizer(),
            IntelligentSecurityProfile.CREDENTIALS_KEYS: CredentialsOptimizer(),
            IntelligentSecurityProfile.CREDENTIALS_PASSWORDS: CredentialsOptimizer(),
            IntelligentSecurityProfile.CREDENTIALS_TOKENS: CredentialsOptimizer(),
            IntelligentSecurityProfile.SOURCE_CODE: SourceCodeOptimizer(),
            # Add more as needed...
        }
    
    def get_profile_optimizer(self, profile: IntelligentSecurityProfile) -> Optional[ContentOptimizer]:
        """Get optimizer for specific profile"""
        return self.optimizers.get(profile)
    
    def optimize_for_profile(self, profile: IntelligentSecurityProfile,
                           data: bytes,
                           base_params: IntelligentProfileParameters) -> Dict[str, Any]:
        """Complete optimization for specific profile"""
        
        optimizer = self.get_profile_optimizer(profile)
        if not optimizer:
            # Fallback to generic optimization
            return {
                'optimized_parameters': asdict(base_params),
                'processing_strategy': OptimizationConfig(),
                'performance_estimate': self._generic_performance_estimate(base_params, len(data)),
                'content_analysis': {'content_type': 'generic', 'optimizer': 'none'},
                'optimization_applied': False
            }
        
        # Perform content analysis
        content_analysis = optimizer.analyze_content(data)
        
        # Optimize parameters
        optimized_params = optimizer.optimize_parameters(base_params, content_analysis)
        
        # Get processing strategy
        processing_strategy = optimizer.get_processing_strategy(content_analysis)
        
        # Estimate performance
        performance_estimate = optimizer.estimate_performance(optimized_params, len(data))
        
        return {
            'optimized_parameters': asdict(optimized_params),
            'processing_strategy': asdict(processing_strategy),
            'performance_estimate': performance_estimate,
            'content_analysis': content_analysis,
            'optimization_applied': True,
            'optimizer_type': optimizer.__class__.__name__
        }
    
    def _generic_performance_estimate(self, params: IntelligentProfileParameters, 
                                    content_size: int) -> Dict[str, float]:
        """Generic performance estimation fallback"""
        
        size_mb = content_size / (1024 * 1024)
        base_speed = 25.0  # MB/s
        
        return {
            'estimated_encryption_speed_mbps': base_speed,
            'estimated_compression_ratio': 0.5,
            'estimated_total_time_seconds': size_mb / base_speed,
            'estimated_output_size_mb': size_mb * 0.6,
            'memory_usage_mb': min(128, max(32, size_mb * 0.2))
        }
    
    def get_optimization_recommendations(self, profile: IntelligentSecurityProfile,
                                       data: bytes) -> List[str]:
        """Get optimization recommendations for profile and content"""
        
        optimizer = self.get_profile_optimizer(profile)
        if not optimizer:
            return ['Consider using a more specific profile for better optimization']
        
        content_analysis = optimizer.analyze_content(data)
        recommendations = []
        
        # Generic recommendations based on content analysis
        if 'optimization_hints' in content_analysis:
            for hint in content_analysis['optimization_hints']:
                if hint == 'high_compression_potential':
                    recommendations.append('Enable maximum compression for better size reduction')
                elif hint == 'streaming_recommended':
                    recommendations.append('Enable streaming optimization for large files')
                elif hint == 'maximum_security_required':
                    recommendations.append('Use maximum security settings for sensitive content')
        
        # Size-based recommendations
        size_mb = len(data) / (1024 * 1024)
        if size_mb > 100:
            recommendations.append('Consider streaming encryption for large files')
        elif size_mb < 0.1:
            recommendations.append('Minimize metadata overhead for small files')
        
        return recommendations

# Convenience functions
def optimize_for_content(profile: IntelligentSecurityProfile, data: bytes,
                        base_params: IntelligentProfileParameters) -> Dict[str, Any]:
    """Optimize parameters for specific content and profile"""
    
    manager = ProfileOptimizationManager()
    return manager.optimize_for_profile(profile, data, base_params)

def get_content_optimizer(profile: IntelligentSecurityProfile) -> Optional[ContentOptimizer]:
    """Get content optimizer for profile"""
    
    manager = ProfileOptimizationManager()
    return manager.get_profile_optimizer(profile)

def analyze_content_characteristics(data: bytes, 
                                  profile_hint: Optional[IntelligentSecurityProfile] = None) -> Dict[str, Any]:
    """Analyze content characteristics with optional profile hint"""
    
    manager = ProfileOptimizationManager()
    
    if profile_hint and profile_hint in manager.optimizers:
        optimizer = manager.optimizers[profile_hint]
        return optimizer.analyze_content(data)
    else:
        # Try to detect best profile first
        from .profile_definitions import ContentAnalyzer
        content_analysis = ContentAnalyzer.analyze_content(data)
        recommended_profile = content_analysis.get('recommended_profile')
        
        if recommended_profile and recommended_profile in manager.optimizers:
            optimizer = manager.optimizers[recommended_profile]
            return optimizer.analyze_content(data)
        else:
            # Generic analysis
            return {
                'content_type': 'generic',
                'optimization_hints': ['use_specific_profile_for_better_optimization'],
                'estimated_compression_ratio': 0.5
            }