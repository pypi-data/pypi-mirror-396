# uvt - Project Analysis & Roadmap

## Executive Summary

**uvt** is a modern Python task runner built on top of `uv` that solves the common pain points of running Python scripts: virtual environment management, PYTHONPATH configuration, and dependency isolation.

---

## Competitive Landscape

### Existing Python Task Runners

| Tool | Pros | Cons | uvt Advantage |
|------|------|------|---------------|
| **Taskipy** | Simple, Poetry integration | Limited features, no profiles | Profiles, inheritance, conditions, watch mode |
| **Poe the Poet** | Good Poetry integration | Tied to Poetry, limited .env support | Better .env, works with any project, task inheritance |
| **Invoke** | Mature, flexible | Code-based (not config), steeper learning curve | Config-based, easier onboarding |
| **Nox** | Excellent for testing | Session-focused, not general purpose | General purpose, PEP 723 support |
| **Make/Just** | Universal, fast | Not Python-specific, awkward syntax | Python-native, TOML config |

### uvt's Unique Position

1. **Built on `uv`**: Leverages the fastest Python package manager
2. **PEP 723 Support**: First-class inline script metadata
3. **Modern DX**: Profiles, inheritance, aliases, private tasks
4. **.env Integration**: Better than competitors
5. **Watch Mode**: Built-in file watching

---

## Market Viability

### Target Audience
- ✅ Teams already using or migrating to `uv`
- ✅ Projects with multiple environments (dev/staging/prod)
- ✅ Developers tired of Makefiles and bash scripts
- ✅ Teams wanting DRY task definitions (via inheritance)
- ✅ CI/CD pipelines needing flexible configuration

### Adoption Barriers
- ❌ Requires `uv` installation (additional dependency)
- ❌ Yet another task runner (ecosystem fatigue)
- ❌ Early stage / unproven in production

### Will People Use It?

**Likely YES if:**
- `uv` adoption continues to grow (current trajectory is strong)
- Positioned as "the task runner for uv projects"
- Documentation and examples are excellent
- Integration with popular tools (pre-commit, GitHub Actions)

**Market Size:**
- Growing `uv` user base (100k+ GitHub stars)
- Every Python project needs task automation
- Can replace: Makefiles, bash scripts, Invoke, Taskipy

---

## What's Missing / Improvements Needed

### Critical (Must Have)

1. **Better Documentation**
   - [ ] Comprehensive README with real-world examples
   - [ ] Migration guide from Make/Taskipy/Invoke
   - [ ] Video/GIF demos
   - [ ] API documentation

2. **Error Messages**
   - [ ] Improve validation error messages
   - [ ] Better task not found errors (suggest similar names)
   - [ ] Clearer circular dependency errors

3. **Testing**
   - [ ] Comprehensive test suite (currently basic)
   - [ ] Integration tests
   - [ ] Test coverage reporting

### High Priority (Should Have)

4. **Shell Completion**
   - [ ] Bash completion
   - [ ] Zsh completion
   - [ ] Fish completion

5. **Task Hooks**
   - [ ] Pre/post task hooks
   - [ ] Global hooks (before_all, after_all)

6. **Better Output**
   - [ ] Progress indicators
   - [ ] Colored diff for env vars
   - [ ] Summary statistics

7. **Retry Logic**
   - [ ] Retry failed tasks with backoff
   - [ ] Configurable retry count

8. **Task Groups/Tags**
   - [ ] Tag tasks (e.g., `tags = ["ci", "local"]`)
   - [ ] Run by tag: `pyr run --tag ci`

### Nice to Have

9. **Interactive Mode**
   - [ ] `pyr run --interactive` to select task from menu
   - [ ] Task search/filter

10. **Plugins**
    - [ ] Plugin system for extensions
    - [ ] Community plugins (e.g., Docker integration)

11. **Config Templates**
    - [ ] `pyr init --template django`
    - [ ] Templates for common frameworks

12. **Task Dependencies Graph**
    - [ ] `pyr graph taskname` - visualize dependency tree
    - [ ] Export to DOT/SVG

---

## Technical Debt & Code Quality

### Current State
- ✅ Type hints throughout
- ✅ Pydantic for validation
- ✅ Decent separation of concerns
- ⚠️ Limited test coverage
- ⚠️ No CI/CD pipeline yet

### Recommended Improvements

1. **Add mypy to CI** (now configured)
   ```toml
   [tool.mypy]
   strict = true
   ```

2. **Add pre-commit hooks**
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/astral-sh/ruff-pre-commit
       hooks:
         - id: ruff
         - id: ruff-format
     - repo: https://github.com/pre-commit/mirrors-mypy
       hooks:
         - id: mypy
   ```

3. **GitHub Actions CI**
   - Run tests on Python 3.10, 3.11, 3.12, 3.13
   - Check types with mypy
   - Lint with ruff
   - Test coverage with pytest-cov

4. **Release Automation**
   - Semantic versioning
   - Automated PyPI releases
   - Changelog generation

---

## uv Dependency

### Current Situation
**Yes, users MUST install `uv` first** - this is a hard requirement.

### Pros
- ✅ Leverages uv's speed and modern features
- ✅ Positions uvt in the growing uv ecosystem
- ✅ Simpler implementation (don't need to bundle/manage Python env)

### Cons
- ❌ Extra installation step
- ❌ Users without uv can't use uvt

### Recommendation: **Embrace it as a feature**

**Marketing approach:**
- "The task runner built for `uv`"
- "Modern Python task automation for the `uv` era"

**Installation should be:**
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install uvt with uv
uv tool install uvt

# Or with pipx
pipx install uvt
```

**Detect and guide users:**
```python
# In CLI, if uv not found:
console.print("[red]Error:[/red] uv is not installed")
console.print("Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh")
console.print("Then run: uv tool install uvt")
```

---

## Roadmap

### v0.1.0 (Current - Alpha)
- [x] Core task running
- [x] Dependency management
- [x] PYTHONPATH support
- [x] Task dependencies and parallel execution
- [x] Profiles and .env loading
- [x] Task inheritance
- [x] Aliases and private tasks
- [x] Watch mode
- [x] Conditions

### v0.2.0 (Beta)
- [ ] Comprehensive test suite (80%+ coverage)
- [ ] Shell completion (bash/zsh/fish)
- [ ] Better error messages
- [ ] Documentation website
- [ ] CI/CD pipeline

### v0.3.0
- [ ] Task hooks (pre/post)
- [ ] Retry logic
- [ ] Task tags/groups
- [ ] Interactive mode
- [ ] Performance benchmarks

### v1.0.0 (Stable)
- [ ] Battle-tested in production
- [ ] Full documentation
- [ ] Migration guides
- [ ] Plugin system
- [ ] Community adoption

---

## Success Metrics

**Short-term (3 months)**
- 100+ GitHub stars
- 5+ contributors
- Featured in Python Weekly / Hacker News

**Medium-term (6 months)**
- 500+ PyPI downloads/month
- Integration with popular frameworks
- Mentioned in uv documentation

**Long-term (12 months)**
- 1000+ GitHub stars
- Default task runner for uv projects
- Community plugins ecosystem

---

## Recommendations

### Immediate Actions (Week 1)
1. ✅ Add mypy configuration
2. [ ] Write comprehensive README
3. [ ] Add CI/CD pipeline
4. [ ] Create examples directory
5. [ ] Publish to PyPI

### Short-term (Month 1)
1. [ ] Add test coverage to 80%+
2. [ ] Create documentation site
3. [ ] Add shell completion
4. [ ] Write blog post / tutorial
5. [ ] Submit to Hacker News / Reddit

### Medium-term (Months 2-3)
1. [ ] Build community
2. [ ] Add requested features based on feedback
3. [ ] Integration examples (Django, FastAPI, etc.)
4. [ ] Performance optimization

---

## Conclusion

**uvt has strong potential** if positioned correctly:

✅ **Strengths:**
- Modern tooling (uv, Pydantic, type-safe)
- Rich feature set competitive with established tools
- Excellent DX (profiles, inheritance, aliases)
- Growing market (uv adoption)

⚠️ **Risks:**
- Crowded market (many task runners)
- uv dependency could limit adoption
- Needs strong documentation and examples

**Verdict: Build it, but focus on:**
1. Excellent documentation
2. uv ecosystem integration
3. Migration path from existing tools
4. Community building

The Python ecosystem doesn't have a task runner quite like this, especially one that embraces `uv` and modern Python features. With good execution, uvt could become the standard task runner for the growing `uv` community.
