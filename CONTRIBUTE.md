# Contributing to AI Resume Builder 🤝

Thank you for your interest in contributing! This project welcomes contributions of all kinds — bug reports, feature requests, documentation improvements, and pull requests.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Issue Reporting](#issue-reporting)
- [Adding New Templates](#adding-new-templates)
- [Adding New Agent Models](#adding-new-agent-models)

---

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct.
Please be respectful and inclusive in all interactions.

---

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/resume-builder.git
   cd resume-builder
   ```
3. Set up the development environment (see [Development Setup](#development-setup)).
4. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```
5. Make your changes.
6. Push and open a Pull Request.

---

## How to Contribute

### 🐛 Bug Reports

Open an issue with:
- A clear, descriptive title
- Steps to reproduce
- Expected vs actual behaviour
- Your OS, Python version, and relevant `.env` settings (redact API keys!)
- Any relevant error messages / tracebacks

### 💡 Feature Requests

Open an issue with:
- The problem you're trying to solve
- Your proposed solution
- Alternatives you've considered

### 📖 Documentation

- Fix typos or unclear sections in `README.md` or `CONTRIBUTE.md`
- Add docstrings to functions that lack them
- Add usage examples

### 🧩 Pull Requests

All contributions go through pull requests. See [Submitting a Pull Request](#submitting-a-pull-request).

---

## Development Setup

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt
pip install ruff black mypy   # dev tools

# 3. Copy env
cp .env.example .env
# Edit .env with your keys

# 4. Start MongoDB (Docker example)
docker run -d -p 27017:27017 --name mongo mongo:7

# 5. Run the app
streamlit run app.py
```

---

## Project Structure

```
agents/         ← AI agent modules (generator, verifier, compiler, pipeline)
auth/           ← Authentication (bcrypt + JWT)
config/         ← Centralised settings via pydantic-settings
database/       ← MongoDB connection + Pydantic document models
mcp/            ← FastMCP server for LaTeX→PDF + in-process client
pages/          ← Streamlit multipage pages
templates/      ← Built-in LaTeX resume skeletons
utils/          ← UI helpers, CSS design system
app.py          ← Streamlit main entry point
```

---

## Coding Standards

### Style

- **Formatter**: `black` (line length 100)
- **Linter**: `ruff`
- **Type hints**: required for all public functions
- **Docstrings**: Google-style for modules and public functions

```bash
# Format
black .

# Lint
ruff check .

# Type check
mypy agents/ auth/ config/ database/ mcp/ utils/
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new template for data-science roles
fix: handle missing profile gracefully in agent1
docs: update README with OpenRouter setup
refactor: extract PDF compilation to separate helper
```

### Branch Naming

```
feature/short-description
fix/bug-description
docs/what-you-documented
refactor/what-you-refactored
```

---

## Submitting a Pull Request

1. **Ensure your branch is up to date** with `main`:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run quality checks**:
   ```bash
   black .
   ruff check .
   ```

3. **Write a clear PR description**:
   - What does this PR do?
   - Why is this change needed?
   - How was it tested?
   - Screenshots (if UI changes)

4. **Link related issues**: Use `Closes #123` in the PR description.

5. **Request a review** from a maintainer.

PRs are merged with **squash & merge** to keep history clean.

---

## Adding New Templates

1. Create `templates/template_yourname.py` with a `YOURNAME_TEMPLATE` string constant.
   - Use `{{PLACEHOLDER}}` tokens consistent with the existing templates.
   - Ensure the template produces a one-page document with typical resume content.

2. Register it in `templates/__init__.py`:
   ```python
   from templates.template_yourname import YOURNAME_TEMPLATE

   BUILTIN_TEMPLATES["yourname"] = {
       "name": "Your Template Name",
       "description": "Short description.",
       "preview_color": "#hexcolor",
       "template": YOURNAME_TEMPLATE,
   }
   ```

3. Test with the UI: select it from the Generate Resume page.

---

## Adding New Agent Models

### Change Agent 1 model (Groq-compatible)

Edit `.env`:
```env
AGENT1_MODEL=qwen-qwq-32b
# or any model available at console.groq.com
```

### Change Agent 2 model (OpenRouter-compatible)

```env
AGENT2_MODEL=mistralai/mistral-large-2411
# or any model at openrouter.ai/models
```

### Add a new LLM provider

1. Add the client library to `requirements.txt`.
2. Add config keys to `config/settings.py`.
3. Create or update the relevant agent module in `agents/`.
4. Update `.env.example` with the new keys.

---

## Questions?

Open a [Discussion](https://github.com/your-org/resume-builder/discussions) or reach out via Issues.

Happy contributing! 🚀
