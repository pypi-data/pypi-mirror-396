# Driver Implementation Plan: Docker, OrbStack, and Modal

> Comprehensive plan for implementing containerized and cloud execution drivers for VibeLab.

## Overview

This document outlines the implementation plan for three new execution drivers:
1. **Docker Driver** - OCI container execution using Docker/OrbStack/Podman
2. **OrbStack Driver** - Native OrbStack integration (macOS)
3. **Modal Driver** - Cloud-based ephemeral container execution

These drivers provide isolation and reproducibility beyond the local driver's git worktree approach.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Common Requirements](#common-requirements)
3. [Docker Driver](#docker-driver)
4. [OrbStack Driver](#orbstack-driver)
5. [Modal Driver](#modal-driver)
6. [Implementation Phases](#implementation-phases)
7. [Testing Strategy](#testing-strategy)
8. [Dependencies & Configuration](#dependencies--configuration)
9. [Error Handling](#error-handling)
10. [Performance Considerations](#performance-considerations)

---

## Architecture Overview

### Driver Protocol Compliance

All drivers must implement the `Driver` protocol:

```python
class Driver(Protocol):
    @property
    def id(self) -> str: ...
    
    def setup(self, ctx: ExecutionContext) -> None: ...
    def execute(self, ctx: ExecutionContext) -> RunOutput: ...
    def cleanup(self, ctx: ExecutionContext) -> None: ...
```

### Execution Flow

```
Runner.run()
  ↓
driver.setup(ctx)          # Prepare environment, set ctx.workdir
  ↓
driver.execute(ctx)         # Run harness, capture output
  ↓
driver.cleanup(ctx)        # Clean up resources
```

### Key Differences from Local Driver

| Aspect | Local Driver | Container Drivers |
|--------|--------------|-------------------|
| Isolation | Git worktree | Container filesystem |
| Code Loading | Clone/copy to host | Mount/copy into container |
| Execution | Direct subprocess | Container exec/run |
| Cleanup | Remove directory | Stop/remove container |
| Network | Host network | Isolated network (optional) |

---

## Common Requirements

### 1. Code Loading Strategy

All container drivers need to handle three code types:

#### GitHub Code
- Clone repository to temporary host directory
- Copy into container at `/workspace`
- Checkout specific commit SHA
- Initialize git repo in container for patch generation

#### Local Code
- Copy local directory to temporary host directory
- Mount or copy into container at `/workspace`
- Initialize git repo in container

#### Empty Code
- Create empty directory
- Initialize git repo in container
- Create initial empty commit for diff baseline

### 2. Container Image Requirements

Harnesses must provide container images via `get_container_image()`:

```python
def get_container_image(self) -> str | None:
    """Return container image for Docker/Modal drivers."""
    # Example: "vibelab/claude-code:latest"
    return f"vibelab/{self.id}:latest"
```

**Default Base Image Strategy:**
- Use official language runtime images (python:3.11, node:20, etc.)
- Install harness CLI tools in image
- Pre-configure environment variables for API keys
- Include git for patch generation

### 3. Environment Variables

Containers need access to:
- `ANTHROPIC_API_KEY` (for Claude Code)
- `OPENAI_API_KEY` (for OpenAI Codex)
- `GEMINI_API_KEY` (for Gemini)
- `VIBELAB_LOG_LEVEL` (optional)

**Security Note:** Never commit API keys to images. Pass via environment variables at runtime.

### 4. Patch Generation

All drivers must generate git patches:
- Container must have git installed
- Initialize git repo in `/workspace` during setup
- After execution, run `git diff` inside container
- Copy patch output back to host

### 5. Log Streaming

Support streaming logs via harness callbacks:
- Stream stdout/stderr from container in real-time
- Forward to `on_stdout`/`on_stderr` callbacks
- Maintain compatibility with existing streaming infrastructure

### 6. Timeout Handling

- Use container runtime timeout mechanisms
- Ensure containers are killed on timeout
- Capture partial output before cleanup

---

## Docker Driver

### Implementation Details

**Driver ID:** `docker`

**OCI Runtime Selection:**
1. Check `VIBELAB_OCI_RUNTIME` environment variable
2. Auto-detect: docker → orbstack → podman
3. Fallback to error if none available

**Container Lifecycle:**

```python
class DockerDriver:
    id = "docker"
    
    def __init__(self):
        self.runtime = self._detect_runtime()
        self.client = self._create_client()
    
    def setup(self, ctx: ExecutionContext):
        # 1. Load code to temp directory
        temp_dir = self._prepare_code(ctx)
        
        # 2. Get container image from harness
        image = ctx.harness.get_container_image()
        if not image:
            raise ValueError(f"Harness {ctx.harness.id} doesn't support containers")
        
        # 3. Pull image if needed
        self._ensure_image(image)
        
        # 4. Create container with volume mount
        container_id = self._create_container(
            image=image,
            workdir_mount=temp_dir,
            env_vars=self._get_env_vars(),
            timeout=ctx.timeout_seconds,
        )
        
        ctx.workdir = Path("/workspace")  # Container path
        ctx._container_id = container_id  # Store for cleanup
        ctx._temp_dir = temp_dir  # Store for cleanup
    
    def execute(self, ctx: ExecutionContext) -> RunOutput:
        # 1. Start container
        self._start_container(ctx._container_id)
        
        # 2. Initialize git repo in container
        self._init_git(ctx._container_id)
        
        # 3. Run harness command
        output = self._run_harness(
            ctx._container_id,
            ctx.harness,
            ctx.scenario.prompt,
            ctx.provider,
            ctx.model,
            ctx.timeout_seconds,
            on_stdout=on_stdout,  # From streaming
            on_stderr=on_stderr,
        )
        
        # 4. Generate patch from container
        patch = self._generate_patch(ctx._container_id)
        
        # 5. Copy logs from container
        stdout, stderr = self._get_logs(ctx._container_id)
        
        return RunOutput(
            exit_code=output.exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_ms=output.duration_ms,
            patch=patch,
        )
    
    def cleanup(self, ctx: ExecutionContext):
        # 1. Stop container
        self._stop_container(ctx._container_id)
        
        # 2. Remove container
        self._remove_container(ctx._container_id)
        
        # 3. Remove temp directory
        shutil.rmtree(ctx._temp_dir, ignore_errors=True)
```

### OCI Runtime Detection

```python
def _detect_runtime(self) -> str:
    """Detect available OCI runtime."""
    # Check environment variable
    env_runtime = os.getenv("VIBELAB_OCI_RUNTIME")
    if env_runtime:
        if self._check_runtime_available(env_runtime):
            return env_runtime
        raise RuntimeError(f"OCI runtime '{env_runtime}' not available")
    
    # Auto-detect
    for runtime in ["docker", "orbstack", "podman"]:
        if self._check_runtime_available(runtime):
            return runtime
    
    raise RuntimeError("No OCI runtime available (docker, orbstack, or podman)")
```

### Container Image Strategy

**Option 1: Pre-built Images (Recommended)**
- Build and publish harness images to Docker Hub/GHCR
- Images tagged as `vibelab/{harness-id}:latest`
- Include harness CLI + dependencies

**Option 2: Build-on-Demand**
- Use Dockerfile per harness
- Build image during first use
- Cache built images

**Option 3: Runtime Installation**
- Use base image (python/node)
- Install harness CLI at container startup
- Slower but more flexible

**Recommendation:** Start with Option 1, support Option 2 as fallback.

### Volume Mounting

**Strategy:** Bind mount temporary directory
- Host: `/tmp/vibelab/{result_id}`
- Container: `/workspace`
- Read-write access for harness modifications

**Alternative:** Copy files into container
- Use `docker cp` or `podman cp`
- More isolation but slower

**Recommendation:** Use bind mounts for performance, copy for maximum isolation.

### Network Configuration

**Options:**
1. **Host network** - Full host access (default)
2. **Bridge network** - Isolated network
3. **No network** - Complete isolation

**Recommendation:** Use bridge network by default, allow override via config.

### Dependencies

```toml
# pyproject.toml additions
[project.optional-dependencies]
docker = [
    "docker>=6.0.0",  # Docker SDK
    "podman>=4.0.0",  # Podman Python bindings (optional)
]
```

---

## OrbStack Driver

### Implementation Details

**Driver ID:** `orbstack`

**Why Separate Driver?**
- OrbStack provides native macOS integration
- Better performance than Docker Desktop
- Simpler API for basic use cases
- Can leverage OrbStack-specific features

**Implementation Approach:**

```python
class OrbStackDriver:
    id = "orbstack"
    
    def __init__(self):
        if not self._check_orbstack_available():
            raise RuntimeError("OrbStack not available")
    
    def setup(self, ctx: ExecutionContext):
        # Similar to Docker driver but use OrbStack CLI
        # OrbStack is Docker-compatible, so can reuse Docker SDK
        # Or use OrbStack-specific CLI commands
        pass
    
    def execute(self, ctx: ExecutionContext) -> RunOutput:
        # Use OrbStack's faster container execution
        pass
```

### OrbStack Detection

```python
def _check_orbstack_available(self) -> bool:
    """Check if OrbStack is installed and running."""
    # Check if 'orbctl' CLI is available
    result = subprocess.run(
        ["which", "orbctl"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return False
    
    # Check if OrbStack daemon is running
    result = subprocess.run(
        ["orbctl", "status"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0
```

### Integration Strategy

**Option 1: Use Docker SDK**
- OrbStack is Docker-compatible
- Use Docker SDK with `DOCKER_HOST` pointing to OrbStack
- Simplest approach, reuses Docker driver code

**Option 2: Use OrbStack CLI**
- Use `orbctl` commands directly
- More control, OrbStack-specific features
- Requires parsing CLI output

**Recommendation:** Start with Option 1 (Docker SDK), add Option 2 if needed.

### Dependencies

```toml
[project.optional-dependencies]
orbstack = [
    "docker>=6.0.0",  # Docker SDK (OrbStack-compatible)
]
```

---

## Modal Driver

### Implementation Details

**Driver ID:** `modal`

**Why Modal?**
- Cloud-based execution (no local Docker required)
- Ephemeral containers (automatic cleanup)
- Built-in GPU support (future)
- Scalable for batch runs

**Modal-Specific Considerations:**
- Requires Modal account and API key
- Containers are ephemeral (no persistent storage)
- Network isolation by default
- Cost per execution time

### Implementation Approach

```python
import modal

class ModalDriver:
    id = "modal"
    
    def __init__(self):
        self.app = modal.App("vibelab")
        self._check_modal_available()
    
    def setup(self, ctx: ExecutionContext):
        # 1. Prepare code (upload to Modal volume or include in image)
        # 2. Create Modal function for harness execution
        # 3. Store function reference in context
        pass
    
    def execute(self, ctx: ExecutionContext) -> RunOutput:
        # 1. Call Modal function remotely
        # 2. Stream logs via Modal's streaming API
        # 3. Wait for completion
        # 4. Retrieve output and patch
        pass
    
    def cleanup(self, ctx: ExecutionContext):
        # Modal handles cleanup automatically
        # Just remove any uploaded volumes/files
        pass
```

### Modal Function Definition

```python
@modal.function(
    image=modal.Image.debian_slim().pip_install("..."),
    secrets=[modal.Secret.from_name("anthropic")],
    timeout=1800,
)
def run_harness(
    code_tar: bytes,
    prompt: str,
    harness_id: str,
    provider: str,
    model: str,
) -> dict:
    """Run harness in Modal container."""
    # 1. Extract code tar to /workspace
    # 2. Initialize git repo
    # 3. Run harness CLI
    # 4. Generate patch
    # 5. Return output dict
    pass
```

### Code Upload Strategy

**Option 1: Include in Image**
- Build code into container image
- Fast execution, but image rebuild needed per scenario
- Good for repeated scenarios

**Option 2: Upload to Volume**
- Upload code as tar to Modal volume
- Extract at runtime
- More flexible, slower first run

**Option 3: Mount from GitHub**
- Clone directly in container
- No upload needed
- Best for GitHub scenarios

**Recommendation:** Support all three, prefer Option 3 for GitHub, Option 2 for local/empty.

### Environment Variables

Modal uses "secrets" for sensitive data:
- Create secrets: `modal secret create anthropic ANTHROPIC_API_KEY=...`
- Reference in function: `secrets=[modal.Secret.from_name("anthropic")]`
- Access in container: `os.getenv("ANTHROPIC_API_KEY")`

### Streaming Logs

Modal provides streaming output:
```python
with function.stream() as stream:
    for log_line in stream:
        on_stdout(log_line.stdout)
        on_stderr(log_line.stderr)
```

### Dependencies

```toml
[project.optional-dependencies]
modal = [
    "modal>=0.60.0",
]
```

### Configuration

Users need:
1. Modal account (free tier available)
2. `modal token new` to authenticate
3. Secrets configured for API keys

---

## Implementation Phases

### Phase 1: Docker Driver (Foundation)

**Goal:** Working Docker driver with basic functionality

**Tasks:**
1. ✅ Create `docker.py` driver implementation
2. ✅ Implement OCI runtime detection (docker/orbstack/podman)
3. ✅ Implement code loading (GitHub/local/empty)
4. ✅ Implement container lifecycle (create/start/stop/remove)
5. ✅ Implement harness execution in container
6. ✅ Implement patch generation from container
7. ✅ Implement log streaming from container
8. ✅ Add Docker driver to `DRIVERS` registry
9. ✅ Update CLI/API to support `--driver docker`
10. ✅ Write unit tests for Docker driver
11. ✅ Write integration tests with real containers
12. ✅ Document Docker driver usage

**Deliverables:**
- `src/vibelab/drivers/docker.py`
- `tests/integration/test_docker_driver.py`
- Documentation updates

**Estimated Time:** 2-3 days

### Phase 2: Container Image Build System

**Goal:** System for building and managing harness container images

**Tasks:**
1. ✅ Create Dockerfile templates per harness
2. ✅ Implement image build command: `vibelab image build <harness>`
3. ✅ Implement image push to registry (optional)
4. ✅ Implement image pull/check logic
5. ✅ Document image building process
6. ✅ Create base images for common harnesses

**Deliverables:**
- `src/vibelab/drivers/images/` directory with Dockerfiles
- `src/vibelab/cli/image.py` CLI commands
- Documentation for image building

**Estimated Time:** 1-2 days

### Phase 3: OrbStack Driver

**Goal:** Native OrbStack integration (macOS)

**Tasks:**
1. ✅ Create `orbstack.py` driver implementation
2. ✅ Implement OrbStack detection
3. ✅ Reuse Docker SDK with OrbStack endpoint
4. ✅ Add OrbStack driver to registry
5. ✅ Write tests for OrbStack driver
6. ✅ Document OrbStack-specific features

**Deliverables:**
- `src/vibelab/drivers/orbstack.py`
- `tests/integration/test_orbstack_driver.py`
- Documentation updates

**Estimated Time:** 1 day

### Phase 4: Modal Driver

**Goal:** Cloud-based execution via Modal

**Tasks:**
1. ✅ Create `modal.py` driver implementation
2. ✅ Implement Modal function definition
3. ✅ Implement code upload strategies
4. ✅ Implement streaming log support
5. ✅ Implement secret management
6. ✅ Add Modal driver to registry
7. ✅ Write tests for Modal driver (mocked)
8. ✅ Document Modal setup and usage
9. ✅ Create example Modal deployment

**Deliverables:**
- `src/vibelab/drivers/modal.py`
- `tests/integration/test_modal_driver.py`
- Modal setup documentation
- Example Modal app configuration

**Estimated Time:** 2-3 days

### Phase 5: Polish & Optimization

**Goal:** Production-ready drivers

**Tasks:**
1. ✅ Error handling improvements
2. ✅ Performance optimization (image caching, parallel pulls)
3. ✅ Resource limits (CPU/memory) configuration
4. ✅ Network configuration options
5. ✅ Comprehensive documentation
6. ✅ E2E tests with all drivers
7. ✅ Performance benchmarking

**Estimated Time:** 1-2 days

**Total Estimated Time:** 7-11 days

---

## Testing Strategy

### Unit Tests

**Location:** `tests/unit/test_drivers.py`

**Coverage:**
- Runtime detection logic
- Code loading (GitHub/local/empty)
- Container lifecycle methods
- Patch generation
- Error handling

**Mocking:**
- Mock Docker/Modal SDKs
- Mock subprocess calls
- Mock file system operations

### Integration Tests

**Location:** `tests/integration/test_docker_driver.py`, etc.

**Coverage:**
- Full execution flow with real containers
- Real harness execution (if available)
- Patch generation verification
- Cleanup verification

**Requirements:**
- Docker/OrbStack installed (for Docker/OrbStack tests)
- Modal account configured (for Modal tests)
- Test harnesses available (or mocked)

### E2E Tests

**Location:** `tests/e2e/test_drivers.py`

**Coverage:**
- CLI commands with all drivers
- API endpoints with driver selection
- Web UI driver selection
- Cross-driver result comparison

### Test Fixtures

```python
# conftest.py
@pytest.fixture
def docker_driver():
    return DockerDriver()

@pytest.fixture
def sample_scenario():
    return Scenario(
        id=1,
        code_type=CodeType.GITHUB,
        code_ref=GitHubCodeRef(
            owner="test",
            repo="test-repo",
            commit_sha="abc123",
        ),
        prompt="Test prompt",
        created_at=datetime.now(),
    )
```

---

## Dependencies & Configuration

### New Dependencies

```toml
[project.optional-dependencies]
docker = [
    "docker>=6.0.0",
]
orbstack = [
    "docker>=6.0.0",  # Reuses Docker SDK
]
modal = [
    "modal>=0.60.0",
]
all-drivers = [
    "docker>=6.0.0",
    "modal>=0.60.0",
]
```

### Environment Variables

```bash
# OCI Runtime selection (Docker driver)
VIBELAB_OCI_RUNTIME=docker|orbstack|podman

# Modal configuration
MODAL_TOKEN_ID=...  # From `modal token new`
MODAL_TOKEN_SECRET=...

# Driver-specific timeouts
VIBELAB_DOCKER_TIMEOUT=1800
VIBELAB_MODAL_TIMEOUT=1800
```

### Configuration File (Future)

```yaml
# ~/.vibelab/config.yaml
drivers:
  docker:
    runtime: docker  # or orbstack, podman
    network: bridge  # or host, none
    resources:
      cpus: 2
      memory: 4g
  modal:
    app_name: vibelab
    image_registry: ghcr.io/vibelab
```

---

## Error Handling

### Common Error Scenarios

| Error | Handling |
|-------|----------|
| Container runtime not available | Clear error message with installation instructions |
| Image not found | Attempt to pull, if fails suggest building |
| Container creation fails | Log error, mark result as failed |
| Execution timeout | Kill container, capture partial output |
| Network errors (Modal) | Retry with exponential backoff |
| API key missing | Clear error with setup instructions |
| Code loading fails | Fail fast with clear error message |

### Cleanup Guarantees

All drivers must ensure cleanup even on failure:

```python
def _execute(self, ctx, driver, harness):
    driver.setup(ctx)
    try:
        return driver.execute(ctx)
    except Exception as e:
        logger.exception("Execution failed")
        raise
    finally:
        try:
            driver.cleanup(ctx)
        except Exception as cleanup_error:
            logger.warning(f"Cleanup failed: {cleanup_error}")
```

---

## Performance Considerations

### Image Caching

- Cache pulled images locally
- Check image existence before pulling
- Use image tags for versioning

### Parallel Execution

- Containers can run in parallel (future)
- Modal supports parallel execution natively
- Docker requires orchestration

### Resource Limits

- Set CPU/memory limits per container
- Prevent resource exhaustion
- Configurable per driver

### Network Optimization

- Use local registry for images (Docker)
- Cache code uploads (Modal)
- Minimize container startup time

---

## Open Questions

1. **Image Registry:** Where to host pre-built harness images?
   - Docker Hub (public)
   - GitHub Container Registry (GHCR)
   - User's own registry

2. **Image Versioning:** How to version harness images?
   - Semantic versioning
   - Commit SHA tags
   - `latest` tag

3. **Cost Management:** How to track/limit Modal costs?
   - Per-run cost tracking
   - Daily/monthly limits
   - Cost alerts

4. **Security:** How to handle untrusted code?
   - Sandboxing options
   - Network restrictions
   - Resource limits

5. **OrbStack vs Docker:** Should OrbStack be separate driver or Docker variant?
   - Current plan: Separate driver
   - Alternative: Docker driver with OrbStack detection

---

## Success Criteria

1. ✅ All three drivers implement the Driver protocol correctly
2. ✅ Drivers handle all code types (GitHub/local/empty)
3. ✅ Drivers generate correct git patches
4. ✅ Drivers support log streaming
5. ✅ Drivers clean up resources reliably
6. ✅ Drivers are testable and tested
7. ✅ Drivers are documented
8. ✅ CLI/API support driver selection
9. ✅ Web UI supports driver selection
10. ✅ Performance is acceptable (<2x overhead vs local)

---

## Next Steps

1. Review and approve this plan
2. Create GitHub issues for each phase
3. Start with Phase 1 (Docker Driver)
4. Iterate based on feedback and testing

---

## References

- [Docker SDK Documentation](https://docker-py.readthedocs.io/)
- [Modal Documentation](https://modal.com/docs)
- [OrbStack Documentation](https://docs.orbstack.dev/)
- PLAN.md § Driver & Harness Architecture
- Existing LocalDriver implementation

