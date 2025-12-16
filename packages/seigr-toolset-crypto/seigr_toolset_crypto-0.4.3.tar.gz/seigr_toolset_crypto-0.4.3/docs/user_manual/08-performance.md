# Performance Guide

Understanding and optimizing STC performance.

## Quick Summary

| Use Case | Speed | Memory | Best For |
|----------|-------|--------|----------|
| Small files | ~0.5-2s | 7MB | Documents |
| Large files | 50-100 MB/s | 7MB | Backups |
| Streaming | 132.9 FPS | 7MB | P2P, video |

## By Profile

| Profile | Time (10MB) | Security |
|---------|------------|----------|
| Fast | ~0.3s | Basic |
| Document | ~0.8s | Balanced |
| Credentials | ~2.0s | High |
| Financial | ~3.5s | Maximum |

## Optimization Tips

### 1. Choose Right Profile

```python
# Auto-detect for best performance
profile = get_profile_for_file("photo.jpg")
stc.encrypt_file("photo.jpg", "out.enc", profile=profile)
```

### 2. Reuse Context

```python
# Fast: Reuse context (2-3x faster)
ctx = STCContext('app-seed')
for file in files:
    ctx.encrypt_file(file, f"{file}.enc", password="pass")
```

### 3. Adjust Difficulty

| Mode | Speed | Use For |
|------|-------|---------|
| fast | 1x | Temp files |
| balanced | 2x | Most files |
| paranoid | 5x | Credentials |

## Next Steps

- [Troubleshooting](05-troubleshooting.md)
- [API Reference](07-api-reference.md)
