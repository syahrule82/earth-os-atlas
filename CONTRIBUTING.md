# Contributing to ATLAS — Earth OS

> Contributions to ATLAS are themselves a form of **value creation**. 
> Once mainnet launches, your contributions will be retroactively recognized on the ATLAS ledger.

---

## 🌟 Ways to Contribute

### 1. Code Contributions
Each accepted PR is categorized as **BUILT_INFRASTRUCTURE** value creation:

- Bug fixes → `SOLVED_PROBLEM`
- Documentation → `CREATED_KNOWLEDGE`
- Performance improvements → `OPTIMIZED_PROCESS`
- Security fixes → `PROTECTED_SYSTEMS`

### 2. Research
- Academic papers about ATLAS → `CREATED_KNOWLEDGE` (1.15x multiplier)
- Economic modeling → `CREATED_KNOWLEDGE`
- Security audits → `PROTECTED_SYSTEMS` (1.10x multiplier)

### 3. Community
- Helping others in Discussions → `CONNECTED_PEOPLE`
- Creating tutorials → `CREATED_KNOWLEDGE`
- Organizing events → `CONNECTED_PEOPLE`

---

## 🛠️ Development Setup

```bash
git clone https://github.com/KOSASIH/earth-os-atlas.git
cd earth-os-atlas
pip install -e .[dev]

# Run tests
pytest tests/ -v

# Run linter
black src/ tests/
flake8 src/ tests/

# Type check
mypy src/ --ignore-missing-imports
```

---

## 📝 Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/your-feature`
3. **Commit** with conventional commits:
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation
   - `refactor:` code restructuring
   - `test:` test additions
4. **Test** your changes: `pytest tests/ -v`
5. **Submit** a PR with:
   - Clear description of what changed and why
   - Which value category your contribution represents
   - Test results
6. **Review** — at least 2 maintainer approvals required (mirrors ATLAS attestation)

---

## 🏗️ Architecture Guidelines

- Follow the existing layer architecture (18 layers)
- New modules go in `src/` with proper `__init__.py`
- All public functions need type hints
- Add tests in `tests/` for new features
- Update `CHANGELOG.md` with your changes

---

## 📜 Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Be excellent to each other.

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

**Forged by TITAN FORGE** 🔥
