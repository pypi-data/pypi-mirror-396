# portfolio-mcp Development Scratchpad

## Current Status: Live Testing Complete - Ready for Publish

**Last Updated:** December 14, 2024

---

## 🔧 CREATE-MCP-APP Blueprint

This section documents ALL transformations needed to create a new MCP server from `fastmcp-template`. This will serve as the specification for a `create-mcp-app` CLI tool.

### Input Parameters (for create-mcp-app)

```yaml
project_name: "portfolio-mcp"           # kebab-case
package_name: "portfolio_mcp"           # snake_case (derived)
description: "Portfolio analysis MCP server powered by mcp-refcache"
author_name: "l4b4r4b4b4"
author_email: "lucas.cansino@mail.de"
github_owner: "l4b4r4b4b4"
python_version: "3.12"
include_langfuse: false                 # Optional tracing
include_docker: true                    # Docker support
```

### Step-by-Step Transformations

#### 1. Clone Template
```bash
git clone https://github.com/l4b4r4b4b4/fastmcp-template.git $PROJECT_NAME
cd $PROJECT_NAME
rm -rf .git
git init
```

#### 2. Update pyproject.toml
**File:** `pyproject.toml`

| Field | Template Value | New Value |
|-------|---------------|-----------|
| `name` | `"fastmcp-template"` | `"portfolio-mcp"` |
| `description` | Template description | User-provided |
| `authors` | Template author | User-provided |
| `project.scripts` | `fastmcp-template = "app.__main__:app"` | `portfolio-mcp = "app.__main__:app"` |

**Add dependencies as needed:**
```toml
dependencies = [
    "fastmcp>=2.14.0",
    "mcp-refcache>=0.1.0",
    # ... project-specific deps
]
```

#### 3. Update app/__init__.py
**File:** `app/__init__.py`

```python
# Change:
__app_name__ = "fastmcp-template"
# To:
__app_name__ = "portfolio-mcp"
```

#### 4. Update app/__main__.py
**File:** `app/__main__.py`

| Change | From | To |
|--------|------|-----|
| App name | `"fastmcp-template"` | `"portfolio-mcp"` |
| App description | Template description | User-provided |
| Help text | Template references | Project-specific |

#### 5. Update app/config.py
**File:** `app/config.py`

| Change | From | To |
|--------|------|-----|
| `env_prefix` | `"FASTMCP_"` | `"PORTFOLIO_MCP_"` (or project-specific) |
| Class name | `Settings` | Keep or rename |
| Remove unused | Langfuse settings if not needed | Delete |

#### 6. Update app/server.py
**File:** `app/server.py`

| Change | From | To |
|--------|------|-----|
| Server name | `"fastmcp-template"` | `"portfolio-mcp"` |
| Cache name | `"fastmcp-template"` | `"portfolio-mcp"` |
| Tool imports | Template tools | Project tools |

#### 7. Remove Unused Template Files
**Delete if not needed:**
```bash
rm -f app/tracing.py              # If no Langfuse
rm -rf app/prompts/               # If no prompts
rm -f app/tools/demo.py           # Template demo
rm -f app/tools/cache.py          # If using server.py cache
rm -f app/tools/context.py        # Template context
rm -f app/tools/secrets.py        # Template secrets
rm -f app/tools/health.py         # If not needed
```

#### 8. Update app/tools/__init__.py
**File:** `app/tools/__init__.py`

Update `__all__` to export only project-specific tools:
```python
__all__ = [
    "register_analysis_tools",
    "register_data_tools",
    "register_optimization_tools",
    "register_portfolio_tools",
]
```

#### 9. Update .zed/settings.json
**File:** `.zed/settings.json`

```json
{
  "context_servers": {
    "portfolio-mcp-dev": {
      "command": "uv",
      "args": ["run", "portfolio-mcp", "stdio"]
    }
  }
}
```

#### 10. Update Docker Files

**docker-compose.yml:**
- Service name: `fastmcp-template` → `portfolio-mcp`
- Image name: `ghcr.io/.../fastmcp-template` → `ghcr.io/.../portfolio-mcp`

**docker/Dockerfile:**
- Comments and labels
- Base image reference

**docker/Dockerfile.base:**
- Comments and labels
- Image source URL

#### 11. Update GitHub Workflows

**Files:** `.github/workflows/*.yml`

| File | Changes |
|------|---------|
| `ci.yml` | Update header comment |
| `cd.yml` | Update `IMAGE_NAME` env var |
| `release.yml` | Update `BASE_IMAGE_NAME` and `APP_IMAGE_NAME` |
| `publish.yml` | Update PyPI project URL and usage examples |

#### 12. Update Documentation

**README.md:**
- Project name and description
- Installation commands (`uvx portfolio-mcp`)
- Usage examples
- Feature list

**TOOLS.md:**
- List all available tools with descriptions

**CHANGELOG.md:**
- Initialize with v0.0.1

#### 13. Update Tests

**tests/conftest.py:**
- Update fixtures for project tools

**tests/test_server.py:**
- Update server name assertions

#### 14. Lock Dependencies
```bash
uv lock
uv sync --all-groups
```

#### 15. Run Verification
```bash
uv run ruff check . --fix
uv run ruff format .
uv run pytest --cov
uv run portfolio-mcp --help
```

#### 16. Build Artifacts
```bash
# PyPI package
uv build

# Docker images
docker build -f docker/Dockerfile.base -t portfolio-mcp-base:latest .
docker build -f docker/Dockerfile -t portfolio-mcp:latest .
```

### File Transformation Summary

| File | Action | Key Changes |
|------|--------|-------------|
| `pyproject.toml` | MODIFY | name, description, scripts |
| `app/__init__.py` | MODIFY | `__app_name__` |
| `app/__main__.py` | MODIFY | app name, description |
| `app/config.py` | MODIFY | env_prefix, remove unused |
| `app/server.py` | MODIFY | server name, cache name, imports |
| `app/tools/__init__.py` | MODIFY | exports |
| `app/tracing.py` | DELETE | if no Langfuse |
| `app/prompts/` | DELETE | if no prompts |
| `app/tools/demo.py` | DELETE | template demo |
| `app/tools/cache.py` | DELETE | if using server.py |
| `app/tools/context.py` | DELETE | template only |
| `app/tools/secrets.py` | DELETE | template only |
| `app/tools/health.py` | DELETE | if not needed |
| `.zed/settings.json` | MODIFY | server name |
| `docker-compose.yml` | MODIFY | service/image names |
| `docker/Dockerfile` | MODIFY | comments, base image |
| `docker/Dockerfile.base` | MODIFY | comments, labels |
| `.github/workflows/*.yml` | MODIFY | image names, URLs |
| `README.md` | MODIFY | all content |
| `TOOLS.md` | MODIFY | tool list |
| `CHANGELOG.md` | MODIFY | version history |
| `tests/*.py` | MODIFY | imports, fixtures |

### GitHub Workflow: Feature Branch → PR → Merge → Release

1. **Create feature branch:**
   ```bash
   git checkout -b feature/initial-port
   ```

2. **Commit changes:**
   ```bash
   git add .
   git commit -m "feat: port portfolio-mcp from fastmcp-template"
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/initial-port
   # Create PR via GitHub UI or CLI
   ```

4. **CI runs automatically:**
   - Lint & Format (ruff)
   - Tests (pytest, coverage)
   - Security (bandit, pip-audit)

5. **Merge to main:**
   - Squash merge recommended
   - CI runs again on main

6. **Release triggers:**
   - `release.yml` builds Docker images → GHCR
   - Tag with `v0.0.1` to trigger:
     - `publish.yml` → PyPI
     - `release.yml` → versioned Docker tags

### PyPI Trusted Publisher Setup

Before first release, configure on PyPI:
1. Go to https://pypi.org/manage/project/portfolio-mcp/settings/publishing/
2. Add trusted publisher:
   - Owner: `l4b4r4b4b4`
   - Repository: `portfolio-mcp`
   - Workflow: `publish.yml`
   - Environment: `pypi`

### Post-Publish Verification

```bash
# Test PyPI install
uvx portfolio-mcp --help
uvx portfolio-mcp stdio  # In another terminal, test with MCP client

# Test Docker
docker run --rm ghcr.io/l4b4r4b4b4/portfolio-mcp:latest python -m app --help
```

---

## 🎉 Live Test Results: ALL PASSED

| Test | Description | Status |
|------|-------------|--------|
| 1 | Health Check | ✅ PASSED |
| 2 | Create Portfolio (synthetic data) | ✅ PASSED |
| 3 | Get Portfolio Metrics | ✅ PASSED |
| 4 | Analyze Returns | ✅ PASSED |
| 5 | Correlation Analysis | ✅ PASSED |
| 6 | Optimize Portfolio (max Sharpe) | ✅ PASSED |
| 7 | Efficient Frontier (15 points) | ✅ PASSED |
| 8 | Apply Optimization | ✅ PASSED |
| 9 | Crypto Data (CoinGecko API) | ✅ PASSED |
| 10 | Cleanup (delete portfolio) | ✅ PASSED |

### Key Metrics from Test:
- **Original Sharpe**: 0.093 → **Optimized Sharpe**: 1.53 (+1.43 improvement)
- **Cached results**: Large data correctly returns ref_ids with pagination
- **CoinGecko API**: 15 trending coins returned successfully
- **All 26 tools working** in live MCP context

---

## Project Overview

**Goal:** Port the existing `finquant-mcp` code into the `fastmcp-template` structure and publish as `portfolio-mcp`.

**Repository:** https://github.com/l4b4r4b4b4/portfolio-mcp

**Parent Project:** Submodule of [mcp-refcache](https://github.com/l4b4r4b4b4/mcp-refcache)

---

## What We're Building

A portfolio analysis MCP server powered by mcp-refcache featuring:

- **Portfolio Management**: Create, read, update, delete portfolios
- **Data Sources**: Yahoo Finance (stocks/ETFs), CoinGecko (crypto), Synthetic (GBM)
- **Analysis**: Returns, volatility, Sharpe, Sortino, VaR, drawdowns, correlations
- **Optimization**: Efficient Frontier, Monte Carlo simulation
- **Reference-Based Caching**: Large datasets cached via mcp-refcache

---

## Source Code Reference

Original code copied to `.agent/files/finquant-mcp/`:

| File | Description | Lines |
|------|-------------|-------|
| `server.py` | FastMCP server setup, tool registration | ~320 |
| `storage.py` | RefCache serialization helpers | ~370 |
| `models.py` | Pydantic models for I/O | ~165 |
| `data_sources.py` | Yahoo Finance + CoinGecko APIs | ~470 |
| `tools/portfolio.py` | Portfolio CRUD operations | ~540 |
| `tools/analysis.py` | Metrics, returns, correlations | ~630 |
| `tools/optimization.py` | EF and Monte Carlo tools | ~620 |
| `tools/data.py` | Data generation tools | ~535 |
| **Total** | | ~3,650 |

Tests in `.agent/files/finquant-mcp/tests/` (~88% coverage)

---

## Template Structure (Target)

```
app/
├── __init__.py
├── __main__.py      # Typer CLI entry point
├── config.py        # Pydantic settings
├── server.py        # FastMCP server setup
├── tracing.py       # Langfuse tracing (optional)
├── prompts/         # MCP prompts
└── tools/           # MCP tools
```

---

## Porting Plan

### Phase 1: Core Setup ✅
- [x] Update `app/server.py` with portfolio-mcp server config
- [x] Update `app/config.py` with portfolio-mcp settings
- [x] Update `app/__main__.py` CLI
- [x] Update `app/__init__.py` with correct package name

### Phase 2: Models & Storage ✅
- [x] Create `app/models.py` from finquant models
- [x] Create `app/storage.py` from finquant storage

### Phase 3: Data Sources ✅
- [x] Create `app/data_sources.py` (Yahoo Finance + CoinGecko)

### Phase 4: Tools ✅
- [x] Create `app/tools/portfolio.py` (CRUD operations)
- [x] Create `app/tools/analysis.py` (metrics, returns, correlations)
- [x] Create `app/tools/optimization.py` (EF, Monte Carlo)
- [x] Create `app/tools/data.py` (data generation, crypto tools)
- [x] `get_cached_result` in server.py (not separate file)
- [x] Remove unused template tools (demo, context, secrets, cache, health)
- [x] Remove unused tracing.py and prompts/
- [x] Update all imports from `finquant_mcp` to `app`
- [x] Verified: 26 tools registered successfully

### Phase 5: Tests ✅
- [x] Port tests from `.agent/files/finquant-mcp/tests/`
- [x] Fix tests to work with `@cache.cached` decorator (unwrap results properly)
- [x] Ensure >= 80% coverage (achieved: 81.08%)
- [x] 163 tests passing

### Phase 6: Documentation & Release ✅
- [x] Update README.md
- [x] Live test all 26 tools via MCP context server
- [ ] Update TOOLS.md with all tools
- [ ] Update CHANGELOG.md
- [ ] Clean up `.agent/files/` (remove after porting)

### Phase 7: Publish Workflow 🚀 IN PROGRESS
- [x] Rename current MCP server to `portfolio-mcp-dev` suffix
- [ ] PyPI publish workflow
  - [x] Verify pyproject.toml metadata
  - [x] Build with `uv build` ✅ `portfolio_mcp-0.0.1-py3-none-any.whl`
  - [ ] Test install from wheel
  - [ ] Publish to PyPI
- [ ] Docker publish workflow
  - [x] Build Docker base image ✅ `portfolio-mcp-base:latest`
  - [x] Build Docker app image ✅ `portfolio-mcp:latest`
  - [x] Test container locally ✅ CLI works
  - [ ] Push to registry (ghcr.io)
- [ ] Test published packages
  - [ ] Add PyPI-installed server to `.zed/settings.json`
  - [ ] Add Docker server to settings
  - [ ] Verify both work alongside dev server

### Phase 7: Live Testing ✅
- [x] All 10 test scenarios passed
- [x] MCP server responds correctly via Zed integration
- [x] Caching works (large results return ref_ids)
- [x] CoinGecko API integration works

### Phase 8: Publishing (IN PROGRESS)
- [ ] Rename current dev server with `-dev` suffix
- [ ] PyPI publish workflow
- [ ] Docker publish workflow
- [ ] Test published packages via MCP settings

---

## Dependencies

**Runtime (pyproject.toml):**
- `fastmcp>=2.14.0`
- `mcp-refcache>=0.1.0`
- `finquant` (from GitHub fork)
- `numpy>=2.0.0`
- `yfinance>=0.2.66`
- `pydantic>=2.10.0`
- `pydantic-settings>=2.10.0`
- `typer>=0.15.0`

**Dev:**
- pytest, pytest-asyncio, pytest-cov
- ruff, mypy, pre-commit

---

## Session Log

### Session 1 (Dec 14, 2024)
- Created repo from `fastmcp-template`
- Added as submodule to `mcp-refcache/examples/`
- Updated `pyproject.toml` and `flake.nix` for portfolio-mcp
- Copied finquant-mcp source to `.agent/files/`
- Created this scratchpad
- **Ported all core code (Phase 1-4):**
  - Updated server.py, config.py, __main__.py, __init__.py
  - Copied storage.py, models.py, data_sources.py
  - Copied all tools (portfolio, analysis, optimization, data)
  - Fixed imports from finquant_mcp → app
  - Removed unused template files (tracing, prompts, demo tools)
  - Verified 26 tools registered successfully
  - Ruff check passes
- **Tests (Phase 5 - IN PROGRESS):**
  - Copied test files from finquant-mcp
  - Fixed imports finquant_mcp → app
  - 163 tests collected
  - **ISSUE:** Tests fail due to architecture mismatch:
    - Original tests used `@cache.cached` with small preview sizes
    - Tests expect full data but get sampled previews
    - `unwrap_cached` helper needs cache to resolve full values
  - **DECISION NEEDED:** Rewrite tests for fastmcp-template patterns vs monkey-patching

---

## Test Fix Strategy (Phase 5) ✅ COMPLETE

### Root Cause Analysis
The `@cache.cached` decorator wraps tool results in a cache response structure:
- **Complete results**: `{"ref_id": ..., "value": <original>, "is_complete": True, ...}`
- **Large results**: `{"ref_id": ..., "preview": <sample>, "is_complete": False, ...}`

Tests were asserting directly on the cache response instead of unwrapping to get the inner value.

### Fix Approach Applied
1. **Use `unwrap_cached(result, cache)` helper** - centralized in conftest.py
2. **Always pass cache** when unwrapping, to resolve full values from previews
3. **Updated test fixtures** to return `(tools, cache)` tuple where needed
4. **Removed duplicate `unwrap_cached`** definitions from test files

### Files Updated
- [x] `tests/conftest.py` - `unwrap_cached` already correct
- [x] `tests/test_analysis_tools.py` - Removed local unwrap_cached, consistently use cache
- [x] `tests/test_optimization_tools.py` - Added unwrap_cached calls
- [x] `tests/test_data_tools.py` - Fixed structure expectations to match actual API
- [x] `tests/test_server.py` - Updated naming from finquant to portfolio-mcp
- [x] `tests/test_storage.py` - No changes needed
- [x] `tests/test_models.py` - Pure models, no cache issues
- [x] `tests/test_data_sources.py` - No changes needed

### Results
- **163 tests passing**
- **81.08% coverage** (exceeds 80% target)
- **Ruff check/format passing**

---

---

## Session 2 Progress (Fixing Tests) ✅ COMPLETE

### Diagnosis Complete
- Ran tests to identify failures
- `test_portfolio_tools.py` - 14/14 passed ✅ (no cache.cached decorators)
- `test_optimization_tools.py` - Fixed ✅ (added unwrap_cached calls)
- `test_data_tools.py` - Fixed ✅ (fixed structure expectations)
- `test_analysis_tools.py` - Fixed ✅ (added cache parameter to unwrap_cached)

### Key Pattern Applied
```python
# Use fixture that returns (tools, cache)
def test_example(self, tools_with_cache):
    tools, cache = tools_with_cache
    raw_result = tools["my_tool"](...)
    result = unwrap_cached(raw_result, cache)  # Pass cache!
    assert "expected_key" in result
```

### Final Results
- **163 tests passing**
- **81.08% coverage**
- All linting passing

---

## Files Modified (not yet committed)

- `app/__init__.py` - Updated package name
- `app/__main__.py` - Updated CLI for portfolio-mcp
- `app/config.py` - Simplified (removed Langfuse)
- `app/server.py` - Portfolio-mcp server setup
- `app/storage.py` - Copied from finquant
- `app/models.py` - Copied from finquant
- `app/data_sources.py` - Copied from finquant
- `app/tools/__init__.py` - Updated exports
- `app/tools/portfolio.py` - Copied, imports fixed
- `app/tools/analysis.py` - Copied, imports fixed
- `app/tools/optimization.py` - Copied, imports fixed
- `app/tools/data.py` - Copied, imports fixed
- `tests/conftest.py` - Updated with unwrap_cached helper
- `tests/test_*.py` - Copied from finquant, imports fixed

## Files Deleted

- `app/tracing.py`
- `app/prompts/`
- `app/tools/demo.py`, `cache.py`, `secrets.py`, `health.py`, `context.py`

---

## Next Steps

1. ~~**Fix test_optimization_tools.py**~~ ✅ Done
2. ~~**Fix test_data_tools.py**~~ ✅ Done
3. ~~**Fix test_analysis_tools.py**~~ ✅ Done
4. ~~**Run full test suite**~~ ✅ 163 tests passing
5. ~~**Check coverage**~~ ✅ 81.08% (exceeds 80% target)
6. ~~**Live test via MCP context**~~ ✅ All 10 scenarios passed
7. **Rename dev server** - Add `-dev` suffix to `.zed/settings.json`
8. **PyPI publish** - Build, test, publish
9. **Docker publish** - Build image, push to registry
10. **Test published packages** - Add to settings, verify alongside dev
11. **Clean up** - Remove `.agent/files/` reference code
12. **Tag release** - v0.1.0

---

## Notes

- Langfuse tracing removed (not needed for portfolio-mcp)
- Keep the Typer CLI pattern from template
- Follow `.rules` for all code (TDD, docstrings, type hints)
- Reference code in `.agent/files/finquant-mcp/` for comparison

---

## Session 3: Publish Workflow (Dec 14, 2024)

### Completed Steps

1. **Renamed dev server** ✅
   - `.zed/settings.json`: `portfolio-mcp` → `portfolio-mcp-dev`
   - Added commented placeholders for PyPI and Docker servers

2. **Updated Docker configs** ✅
   - `docker-compose.yml`: Updated service names and image tags
   - `docker/Dockerfile`: Updated naming and base image reference
   - `docker/Dockerfile.base`: Updated naming and labels

3. **Built packages** ✅
   - PyPI wheel: `dist/portfolio_mcp-0.0.1-py3-none-any.whl`
   - Docker base: `portfolio-mcp-base:latest`
   - Docker app: `portfolio-mcp:latest`

4. **Tested locally** ✅
   - All 163 tests passing
   - Docker container CLI works

### Remaining Steps

### Step 1: Rename Dev Server
Update `.zed/settings.json` to use `portfolio-mcp-dev` as the server name:
- Allows running dev and published versions side-by-side
- Clear distinction during testing

### Step 2: PyPI Publish
```bash
# Build
uv build

# Test locally
pip install dist/portfolio_mcp-*.whl

# Publish (requires PyPI token)
uv publish
```

### Step 3: Docker Publish
```bash
# Build image
docker build -t portfolio-mcp:latest .
docker build -t ghcr.io/l4b4r4b4b4/portfolio-mcp:latest .

# Test locally
docker run --rm portfolio-mcp:latest --help

# Push to registry
docker push ghcr.io/l4b4r4b4b4/portfolio-mcp:latest
```

### Commands to Publish

**PyPI:**
```bash
# Test on TestPyPI first (optional)
uv publish --publish-url https://test.pypi.org/legacy/

# Publish to PyPI (requires PYPI_TOKEN)
uv publish
```

**Docker (GHCR):**
```bash
# Tag for GHCR
docker tag portfolio-mcp-base:latest ghcr.io/l4b4r4b4b4/portfolio-mcp-base:latest
docker tag portfolio-mcp:latest ghcr.io/l4b4r4b4b4/portfolio-mcp:latest

# Login to GHCR (requires GITHUB_TOKEN with packages:write)
echo $GITHUB_TOKEN | docker login ghcr.io -u l4b4r4b4b4 --password-stdin

# Push images
docker push ghcr.io/l4b4r4b4b4/portfolio-mcp-base:latest
docker push ghcr.io/l4b4r4b4b4/portfolio-mcp:latest
```

### After Publishing - Add to settings.json

```json
{
  "context_servers": {
    "portfolio-mcp-dev": { ... },
    "portfolio-mcp": {
      "command": "uvx",
      "args": ["portfolio-mcp", "stdio"]
    },
    "portfolio-mcp-docker": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "ghcr.io/l4b4r4b4b4/portfolio-mcp:latest", "python", "-m", "app", "stdio"]
    }
  }
}
```

### Step 4: Test Published Packages
Add to `.zed/settings.json`:
```json
{
  "context_servers": {
    "portfolio-mcp-dev": { ... },  // Current dev
    "portfolio-mcp": {
      "command": "uvx",
      "args": ["portfolio-mcp", "stdio"]
    },
    "portfolio-mcp-docker": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "ghcr.io/l4b4r4b4b4/portfolio-mcp:latest", "stdio"]
    }
  }
}
```

---

## Session 4: GitHub Workflow (Pending)

### TODO
1. [ ] Create feature branch `feature/initial-port`
2. [ ] Commit all changes with conventional commit message
3. [ ] Push and create PR
4. [ ] Wait for CI to pass
5. [ ] Merge to main
6. [ ] Configure PyPI trusted publisher
7. [ ] Create GitHub release with tag `v0.0.1`
8. [ ] Verify PyPI and GHCR packages
9. [ ] Update `.zed/settings.json` with published servers
10. [ ] Final live test with all three server variants