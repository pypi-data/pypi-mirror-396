# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the MLE Runtime project.

## Workflows

### 1. CI Workflow (`ci.yml`)

**Trigger:** Push or Pull Request to main/master/develop branches

**Purpose:** Continuous Integration testing

**Jobs:**
- **test**: Builds and tests on multiple platforms
  - Runs on: Ubuntu, Windows, macOS
  - Python versions: 3.8, 3.10, 3.11
  - Steps:
    1. Checkout code with submodules
    2. Set up Python and CMake
    3. Build C++ core library
    4. Run C++ tests with CTest
    5. Build Python package
    6. Run Python tests

- **lint**: Code quality checks
  - Runs on: Ubuntu
  - Checks:
    - Black formatting
    - Flake8 linting

### 2. Release Workflow (`release.yml`)

**Trigger:** 
- Push tags matching `v*` or `*.*.*` (e.g., v1.0.0, 1.0.0)
- Manual workflow dispatch

**Purpose:** Build and publish releases to PyPI

**Jobs:**
- **build_wheels**: Build platform-specific wheels
  - Runs on: Ubuntu, Windows, macOS
  - Python versions: 3.8, 3.9, 3.10, 3.11
  - Builds C++ core and Python wheels for each platform
  - Uploads wheel artifacts

- **build_sdist**: Build source distribution
  - Runs on: Ubuntu
  - Creates source tarball (.tar.gz)
  - Uploads sdist artifact

- **publish**: Publish to PyPI
  - Only runs on tag pushes
  - Downloads all wheel and sdist artifacts
  - Validates distributions with twine
  - Publishes to PyPI using API token

- **create_release**: Create GitHub Release
  - Only runs on tag pushes
  - Downloads all artifacts
  - Creates GitHub release with auto-generated notes
  - Attaches all wheels and sdist to release

## Setup Requirements

### Secrets

Configure these secrets in your GitHub repository settings:

1. **PYPI_API_TOKEN**: PyPI API token for publishing
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token
   - Add to GitHub: Settings → Secrets → Actions → New repository secret

### Branch Protection (Optional)

Recommended branch protection rules for `main`:
- Require pull request reviews
- Require status checks to pass (CI workflow)
- Require branches to be up to date

## Usage

### Running CI

CI runs automatically on:
- Every push to main/master/develop
- Every pull request to main/master/develop

### Creating a Release

1. Update version in:
   - `sdk/python/pyproject.toml`
   - `sdk/python/setup.py`

2. Commit and push changes:
   ```bash
   git add sdk/python/pyproject.toml sdk/python/setup.py
   git commit -m "Bump version to 1.0.5"
   git push
   ```

3. Create and push a tag:
   ```bash
   git tag v1.0.5
   git push origin v1.0.5
   ```

4. The release workflow will automatically:
   - Build wheels for all platforms and Python versions
   - Build source distribution
   - Publish to PyPI
   - Create GitHub release with artifacts

### Manual Release Trigger

You can also trigger the release workflow manually:
1. Go to Actions tab in GitHub
2. Select "Build and Publish Python Package"
3. Click "Run workflow"
4. Select branch and run

## Troubleshooting

### Build Failures

**C++ compilation errors:**
- Check CMake version (requires 3.15+)
- Ensure C++17 compiler is available
- Check cpp_core/CMakeLists.txt for dependencies

**Python build errors:**
- Verify pybind11 is installed
- Check numpy compatibility
- Ensure setup.py paths are correct

**Wheel build failures:**
- Check platform-specific compilation flags
- Verify all source files are included
- Check for missing dependencies

### PyPI Upload Failures

**Authentication errors:**
- Verify PYPI_API_TOKEN secret is set correctly
- Check token has upload permissions
- Try uploading to TestPyPI first

**Version conflicts:**
- Ensure version number is incremented
- Check if version already exists on PyPI
- Verify version format (semantic versioning)

**Distribution validation errors:**
- Run `twine check dist/*` locally
- Check README.md renders correctly
- Verify all required metadata is present

### Artifact Issues

**Missing artifacts:**
- Check if build jobs completed successfully
- Verify upload-artifact steps ran
- Check artifact retention period (7 days)

**Download failures:**
- Ensure merge-multiple is set correctly
- Check artifact names match between jobs
- Verify download-artifact version compatibility

## Platform-Specific Notes

### Windows
- Uses Visual Studio compiler
- CMake generates Visual Studio solution
- Requires `--config Release` for builds

### macOS
- Uses Clang compiler
- May require Xcode Command Line Tools
- Universal binaries not yet supported

### Linux
- Uses GCC compiler
- Builds on Ubuntu (glibc-based)
- Compatible with most Linux distributions

## Future Improvements

- [ ] Add cibuildwheel for easier multi-platform builds
- [ ] Add CUDA support in CI
- [ ] Add code coverage reporting
- [ ] Add security scanning (Dependabot, CodeQL)
- [ ] Add performance benchmarking
- [ ] Add documentation deployment
- [ ] Add Docker image builds
- [ ] Add TestPyPI deployment for testing
