# Implementation Status: Four New Features for uvt

## ✅ COMPLETED PHASES

### Phase 1: Task Variables/Templating ✅

**What it does:** Allows defining reusable variables in config and referencing them in tasks using `{variable}` syntax.

**Files Modified:**
- [src/uvt/models.py](src/uvt/models.py) - Added `variables` dict to PtConfig and ProfileConfig, `use_vars` to ProjectConfig and TaskConfig
- [src/uvt/variables.py](src/uvt/variables.py) - NEW module with interpolation logic, circular reference detection
- [src/uvt/config.py](src/uvt/config.py) - Added `apply_variable_interpolation()` function
- [src/uvt/runner.py](src/uvt/runner.py) - Integrated variable interpolation in `from_config_file()`
- [tests/test_variables.py](tests/test_variables.py) - Comprehensive test suite

**Example Usage:**
```toml
[project]
use_vars = true

[variables]
src_dir = "src"
test_dir = "tests"

[tasks.test]
cmd = "pytest {test_dir}"

[tasks.lint]
cmd = "ruff check {src_dir}"
```

**Features:**
- Global variables in `[variables]` section
- Profile-specific variable overrides
- Recursive variable expansion
- Circular reference detection
- Per-task opt-in with `use_vars = true`
- Global default with `[project] use_vars = true`
- Interpolates: cmd, script, args, env values, cwd, dependencies, hooks

---

### Phase 2: Global Runner/Command Prefix ✅

**What it does:** Automatically prefixes all task commands with a common runner (e.g., "dotenv run", "docker exec").

**Files Modified:**
- [src/uvt/models.py](src/uvt/models.py) - Added `runner` to ProjectConfig and ProfileConfig, `disable_runner` to TaskConfig
- [src/uvt/executor.py](src/uvt/executor.py) - Added `runner` field to UvCommand, modified `build()` to prepend runner
- [src/uvt/config.py](src/uvt/config.py) - Added `get_effective_runner()` function
- [src/uvt/runner.py](src/uvt/runner.py) - Integrated runner in `build_command()` and `_build_hook_command()`

**Example Usage:**
```toml
[project]
runner = "dotenv run"

[tasks.test]
cmd = "pytest tests/"
# Actually runs: uv run dotenv run pytest tests/

[tasks.without-runner]
cmd = "echo 'no prefix'"
disable_runner = true  # Opt-out
```

**Features:**
- Global runner via `[project] runner = "..."`
- Profile-specific runner override
- Per-task opt-out with `disable_runner = true`
- Works with both `cmd` and `script` tasks
- Hooks inherit runner from parent task
- Uses `shlex.split()` for proper parsing

---

## 🚧 REMAINING PHASES

### Phase 3: Task Output Capture/Redirection (TODO)

**What it needs:**
1. Add `stdout` and `stderr` fields to TaskConfig in [models.py](src/uvt/models.py)
2. Add validator for redirection values ("null", "inherit", or file path)
3. Add `stdout_redirect` and `stderr_redirect` to UvCommand in [executor.py](src/uvt/executor.py)
4. Create `_prepare_output_redirect()` helper function
5. Modify `execute_sync()` to handle file descriptors
6. Modify `execute_async()` to fall back to sync for file redirection
7. Update `build_command()` in [runner.py](src/uvt/runner.py) to pass redirection
8. Create [tests/test_output_redirect.py](tests/test_output_redirect.py)

**Example (target):**
```toml
[tasks.build]
cmd = "python build.py"
stdout = "logs/build.log"  # Append to file
stderr = "logs/build.err"

[tasks.quiet]
cmd = "ruff check ."
stdout = "null"  # Silence output
```

**Implementation Notes:**
- File paths relative to project root or task cwd
- Append mode for log files (don't overwrite)
- Auto-create parent directories
- Special values: "null" (DEVNULL), "inherit" (default)
- Handle file descriptor cleanup in finally blocks

---

### Phase 4: Inline Task Definitions (TODO)

**What it needs:**
1. Add `--inline` option to `uvt run` command in [cli.py](src/uvt/cli.py)
2. Add `--env`, `--cwd`, `--timeout`, `--python` options
3. Implement `_run_inline_task()` helper function
4. Parse environment variables from KEY=VALUE format
5. Optionally load config for settings/profile support
6. Build environment from config + inline vars
7. Get effective runner from config if present
8. Create UvCommand and execute
9. Create [tests/test_inline_tasks.py](tests/test_inline_tasks.py)

**Example (target):**
```bash
# Simple inline task
uvt run --inline "pytest tests/"

# With environment variables
uvt run --inline "python deploy.py" --env STAGE=prod --env DEBUG=0

# With working directory
uvt run --inline "make build" --cwd workspace/

# Works without config file
uvt run --inline "echo 'hello world'"
```

**Implementation Notes:**
- Works with or without config file
- Respects global settings (runner, env, profile) if config present
- Inline `--env` overrides config env
- Supports additional CLI arguments
- Task name not required with `--inline`

---

## Testing Status

### ✅ Completed Tests
- [tests/test_variables.py](tests/test_variables.py) - Full test suite for variable interpolation
  - Simple interpolation
  - Multiple variables
  - Recursive variables
  - Circular reference detection
  - Missing variable errors
  - Per-task opt-in
  - Profile variable overrides
  - Complex substitutions

### 🚧 Tests TODO
- Tests for runner functionality (add to [tests/test_runner.py](tests/test_runner.py))
  - Runner prepended to cmd
  - Task can disable runner
  - Profile runner override
  - Hooks inherit runner
- [tests/test_output_redirect.py](tests/test_output_redirect.py) (new file needed)
  - Redirect stdout to file
  - Redirect stderr to file
  - Redirect to null
  - Append mode
  - Relative path resolution
- [tests/test_inline_tasks.py](tests/test_inline_tasks.py) (new file needed)
  - Inline simple command
  - With env vars
  - With multiple env vars
  - With timeout
  - With config settings inheritance
  - No config required
  - With args

---

## Next Steps

### Immediate (Phase 3):

1. **Add schema fields to TaskConfig:**
   ```python
   stdout: str | None = None  # "null", "inherit", or file path
   stderr: str | None = None
   ```

2. **Add validator:**
   ```python
   @model_validator(mode="after")
   def validate_output_redirection(self) -> TaskConfig:
       for field_name in ("stdout", "stderr"):
           value = getattr(self, field_name)
           if value is not None and value not in ("null", "inherit"):
               if not value.strip():
                   raise ValueError(f"{field_name} file path cannot be empty")
       return self
   ```

3. **Modify UvCommand and executor.py** - See detailed plan in [plan file](/home/mikko/.claude/plans/sunny-humming-wreath.md)

### After Phase 3 (Phase 4):

1. **Modify cli.py** - Add new options to `run` command
2. **Implement _run_inline_task()** - Parse args, load config, execute
3. **Create comprehensive tests**

---

## Backwards Compatibility

✅ **No breaking changes** - All features are opt-in:
- Variables require `use_vars = true`
- Runner is optional setting
- Output redirection is optional
- Inline tasks are new CLI feature

---

## How to Test Implemented Features

### Test Variables:
```bash
# Create test config
cat > uvt.toml <<'EOF'
[project]
use_vars = true

[variables]
test_dir = "tests"

[tasks.test]
cmd = "echo Testing: {test_dir}"
EOF

# Run (when tests pass)
python -m uvt run test
```

### Test Runner:
```bash
# Create test config
cat > uvt.toml <<'EOF'
[project]
runner = "echo PREFIX:"

[tasks.test]
cmd = "echo hello"
EOF

# Run (when tests pass)
python -m uvt run test
# Expected: PREFIX: echo hello (then executes)
```

---

## Documentation Updates Needed

After all phases complete:

1. **README.md** - Add sections for each feature with examples
2. **CLAUDE.md** - Update key concepts section
3. **Example configs** - Provide real-world usage examples
4. **CHANGELOG** - Document new features

---

## Files Summary

**New Files Created:**
- `src/uvt/variables.py` - Variable interpolation module
- `tests/test_variables.py` - Variable tests
- `IMPLEMENTATION_STATUS.md` - This file

**Modified Files:**
- `src/uvt/models.py` - Schema changes for all features
- `src/uvt/config.py` - Variable interpolation and runner resolution
- `src/uvt/executor.py` - Runner prefix in UvCommand
- `src/uvt/runner.py` - Integration of variables and runner

**Files Pending Modification:**
- `src/uvt/cli.py` - Inline task CLI (Phase 4)
- `tests/test_runner.py` - Add runner tests
- Create `tests/test_output_redirect.py` (Phase 3)
- Create `tests/test_inline_tasks.py` (Phase 4)
