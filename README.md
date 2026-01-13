# AutoOps ⚙️

**AutoOps** is a modular, extensible, and user-friendly automation orchestrator built with Python.  
It provides a clean CLI to run reusable automation jobs safely, with preview and dry-run support.

> Think of AutoOps as a toolbox for daily automation — structured, testable, and scalable.

---

## ✨ Features

- 🧠 Modular job system (easy to add new automations)
- 🖥️ Human-friendly CLI (built with Typer)
- 🧪 Dry-run & preview modes (safe by default)
- 📦 YAML-based configuration
- 🧩 Extensible architecture (core / jobs / config)
- ✅ Fully tested (pytest)
- 🧼 Zero-configuration defaults (works out of the box)

---

## 📦 Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/JhonatanRodrigues22/autoops.git
cd autoops
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
````

Verify installation:

```bash
autoops --help
```

---

## 🧭 CLI Overview

```bash
autoops --help
```

Available commands:

```text
version   Show the current AutoOps version
list      List available jobs
run       Run a job by name
```

---

## 📋 Listing Available Jobs

```bash
autoops list
```

Example output:

```text
example
organize-files
```

---

## ▶️ Running a Job

```bash
autoops run <job-name> [options]
```

Example:

```bash
autoops run example
```

---

## 🗂️ Job: organize-files

The **organize-files** job automatically organizes files inside a folder into categorized subfolders based on file extensions.

### 🔍 What it does

* Scans a directory (default: your system Downloads folder)
* Detects file extensions
* Creates category folders **only when needed**
* Moves files into their correct folders
* Preserves existing folders and avoids overwriting files

---

### 📂 Default Categories

Examples of supported categories:

* `documents`
* `pdf`
* `spreadsheets`
* `presentations`
* `ebooks`
* `images`
* `audio`
* `videos`
* `archives`
* `apps`
* `code`
* `config`
* `fonts`
* `backups`
* `torrents`
* `others` (fallback for unknown extensions)

All categories and extensions are defined in:

```text
configs/organize_files.yaml
```

---

## 🧪 Dry-Run Mode (Safe Preview)

Simulate the operation without touching any files:

```bash
autoops run organize-files --dry-run
```

Example output:

```text
✅ organize-files (DRY-RUN)
Source: C:\Users\You\Downloads
Destination: C:\Users\You\Downloads

Would move: 7 file(s)
  apps: 7
```

---

## 👀 Preview Mode (Detailed)

Preview exactly **what would be moved and where**:

```bash
autoops run organize-files --preview
```

Example output:

```text
Preview moves:
  DockerInstaller.exe  ->  apps/DockerInstaller.exe
  VSCodeSetup.exe      ->  apps/VSCodeSetup.exe
```

> No files are modified in preview mode.

---

## ⚠️ Running for Real

Once you're comfortable:

```bash
autoops run organize-files
```

This will **actually move the files**.

---

## 🛠️ Configuration (YAML)

The job behavior can be customized via YAML:

```yaml
organize_files:
  source_dir: ${HOME}/Downloads
  dry_run: true
  others_dir: others

  categories:
    documents:
      - .txt
      - .md
      - .docx
    images:
      - .jpg
      - .png
    apps:
      - .exe
      - .msi
```

You can also provide a custom config file:

```bash
autoops run organize-files --config my_config.yaml
```

---

## 🧪 Tests

Run the full test suite:

```bash
pytest
```

All core components, jobs, and CLI behavior are covered.

---

## 🧩 Project Structure

```text
autoops/
├── src/autoops/
│   ├── cli.py           # CLI entrypoint
│   ├── core/            # Core abstractions (Job, Registry, Runner)
│   ├── jobs/            # Automation jobs
│   └── config/          # Config loaders
├── configs/             # YAML job configs
├── tests/               # Pytest suite
└── pyproject.toml
```

---

## 🚀 Roadmap

* [ ] Add more automation jobs
* [ ] Profiles (work / personal / gaming)
* [ ] Verbose & quiet modes
* [ ] JSON-only output mode
* [ ] Plugin-based jobs

---

## 📜 License

MIT License.

---

## 👨‍💻 Author

Developed by **Jhonatan Rodrigues**
Focused on automation, Python tooling, and clean architecture.

````