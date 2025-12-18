# 🚀 Nushyax

**Nushyax** is a *framework-agnostic developer CLI* that lets you run common project commands using **short, memorable aliases** — without caring which framework, tool, or stack you’re using.

Think of it as a **universal command layer** on top of Django, Flask, Next.js, Docker, Node, and more.

---

## ✨ Why Nushyax?

Every framework has its own long, repetitive commands:

```bash
python manage.py runserver
flask run --debug
npm run dev
docker-compose up -d
```

With **Nushyax**, you run everything through a **single, explicit interface**:

```bash
nushyax exec s
nushyax exec d
nushyax exec b
```

Same aliases. Same muscle memory. Any framework.

---

## 🧠 How it works (high level)

1. **Auto-detects your project framework**
2. Loads **framework-specific defaults**
3. Merges them with your **global + local config**
4. Resolves aliases → real commands
5. Executes them via `nushyax exec`

All of this happens automatically.

---

## 📦 Supported frameworks (auto-detected)

| Framework | Detection signal |
|---------|------------------|
| Django | `manage.py` |
| Flask | `Flask(__name__)`, `.flaskenv`, deps |
| Next.js | `next.config.*`, `next` dependency |
| Node.js | `package.json` |
| Docker | `docker-compose.yml` |

> More frameworks (FastAPI, Rails, Spring) are planned.

---

## ⚡ Installation

```bash
pip install nushyax
```

Make sure your virtual environment is activated.

---

## 🚀 Quick start

### 1️⃣ Initialize configuration

```bash
nushyax init
```

This creates a `.nushyax.yaml` file with **smart defaults** for your detected framework.

---

### 2️⃣ Run commands using aliases

All project commands are executed explicitly via `exec`:

```bash
nushyax exec s   # start server
nushyax exec d   # dev / debug mode
nushyax exec b   # build
```

This keeps execution **clear, predictable, and unambiguous**.

---

## 🧾 Example `.nushyax.yaml`

```yaml
framework: django

aliases:
  s: run
  mm: makemigrations
  m: migrate

commands:
  run:
    desc: Start development server
    exec: python manage.py runserver
```

You are free to rename, override, or add commands.

---

## 🌍 Configuration layers (important)

Nushyax merges configuration from **three levels**:

1. **Framework defaults** (built-in)
2. **Global user config**
   ```text
   ~/.nushyax/config.yaml
   ```
3. **Project config**
   ```text
   .nushyax.yaml
   ```

Priority:
```
project > global > defaults
```

---

## 🧩 Commands

### `nushyax init`
Generate a project config file.

```bash
nushyax init
nushyax init --force
```

---

### `nushyax list`
List all available commands and aliases for the current project.

```bash
nushyax list
```

---

### `nushyax describe <alias>`
Show what an alias resolves to.

```bash
nushyax describe s
```

---

### `nushyax exec <alias>`
Execute a resolved command.

```bash
nushyax exec s
nushyax exec s --dry-run
```

> All project commands are executed through `exec` by design.

---

## 🔍 Framework detection philosophy

Nushyax uses **robust detection**, not rigid rules.

Instead of relying on one fixed file, it looks for:

- Strong signals (e.g. `manage.py`, `Flask(__name__)`)
- Dependency hints
- Environment clues

This makes Nushyax work in **real-world projects**, not just ideal ones.

---

## 🔐 Safety & clarity

- Commands are **explicitly executed** via `exec`
- No hidden or implicit execution
- `--dry-run` lets you preview commands before running

---

## 🧱 Project structure

```text
nushyax/
├── cli.py          # Typer CLI entry
├── detector.py     # Framework detection
├── templates.py    # Default templates
├── config.py       # Config loading & merging
├── dispatcher.py   # Alias resolution
├── runner.py       # Command execution
```

---

## 🛣 Roadmap

- [ ] FastAPI support
- [ ] Multi-framework monorepo support
- [ ] `nushyax doctor` (diagnostics)
- [ ] Plugin system
- [ ] Shell autocompletion

---

## 🤝 Contributing

Contributions are welcome.

Ideas:
- Add new framework detectors
- Improve robustness
- Write docs & examples

---

## 📄 License

MIT License

---

## 💡 Philosophy

> One brain. One muscle memory. Any framework.

Nushyax exists to reduce **context switching**, not replace frameworks.

