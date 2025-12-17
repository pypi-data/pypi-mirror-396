# Release Guide for rs_audio_stats Python Package

This guide explains how to release new versions of the Python package with pre-built wheels for all platforms.

## Prerequisites

1. **Set up PyPI API Token**
   - Go to your GitHub repository settings
   - Navigate to: Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token (starts with `pypi-`)

## Release Process

### Automatic Release (Recommended)

1. **Update version numbers**:
   ```bash
   # Update version in these files:
   # - lib_python/pyproject.toml
   # - lib_python/Cargo.toml
   # - lib_python/rs_audio_stats/__init__.py
   ```

2. **Commit and tag**:
   ```bash
   git add .
   git commit -m "Release v1.1.1"
   git tag v1.1.1
   git push origin main --tags
   ```

3. **GitHub Actions will automatically**:
   - Build wheels for all platforms:
     - Windows (x86_64)
     - macOS (x86_64, arm64, universal2)
     - Linux (x86_64, aarch64)
   - Upload to PyPI

### Manual Workflow Trigger

1. Go to Actions tab in GitHub
2. Select "Build Python Wheels" workflow
3. Click "Run workflow"
4. Select branch and run

## Supported Platforms

The workflow builds wheels for:

- **Windows**: x86_64
- **macOS**: x86_64, arm64 (Apple Silicon), universal2
- **Linux**: x86_64, aarch64 (ARM64)

All wheels use abi3 (stable ABI) for Python 3.10+, meaning one wheel works for all Python versions ≥ 3.10.

## Local Testing

To test the wheel locally before release:

```bash
cd lib_python
maturin build --release
pip install target/wheels/*.whl
python -c "import rs_audio_stats; print(rs_audio_stats.__version__)"
```

## Verification

After release, verify installation:

```bash
pip install rs-audio-stats
python -c "import rs_audio_stats; info, results = rs_audio_stats.analyze_audio_all('test.wav')"
```

## Troubleshooting

1. **Build fails**: Check Rust toolchain is installed
2. **Upload fails**: Verify PYPI_API_TOKEN is set correctly
3. **Import fails**: Ensure correct Python version (≥3.10)

## Notes

- Users DO NOT need Rust installed
- All dependencies are bundled in the wheel
- Cross-platform wheels ensure wide compatibility