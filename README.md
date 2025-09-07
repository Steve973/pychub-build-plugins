# pychub-build-plugins

Build-tool plugins that generate a **single-file `.chub`** bundle from your
project’s wheel **after** the wheel is built. A `.chub` contains your main
wheel, dependency wheels, optional scripts, extra files, and a small bootstrap
so end-users can install/run it easily.

Supported build tools:

- **Poetry** → `pychub-poetry-plugin`
- **PDM** → `pychub-pdm-plugin`
- **Hatch** → `pychub-hatch-plugin`

---

## How it works

Each plugin hooks into its tool’s build lifecycle and, when the wheel is
produced, invokes **pychub** using options declared in the consumer project’s
`pyproject.toml`. The resulting `.chub` is written to your `dist/` (or a path
you choose).

---

## Consumer configuration

### Common `pychub` options (shared concept)

Add a `tool.pychub.package` table to your **consumer project**. The plugin will
read these during build:

```toml
[tool.pychub.package]
# Optional: where to write the chub (default is <Name>-<Version>.chub)
chub = "dist/my-app.chub"

# REQUIRED: path to the main wheel, relative to the project root
wheel = "dist/my_app-0.1.0-py3-none-any.whl"

# Optional: include extra wheels
add_wheels = ["dist/extra1.whl", "dist/extra2.whl"]

# Optional: add files into the archive (SRC::DEST inside the chub)
includes = [
  "README.md::docs/",
  "configs/app.toml::conf/",
]

[tool.pychub.package.scripts]
pre  = ["scripts/pre.sh"]
post = ["scripts/post.sh"]
```

> The plugin will `chdir` to the project root before handing control to pychub
> so relative paths (like `dist/...`) resolve correctly.

---

### Poetry

**Trigger:** `poetry build` (wheel step)

**Consumer setup:** ensure the plugin is installed in the environment that runs
the build; no special Poetry config is required beyond your
`tool.pychub.package`.

```bash
# in the consumer project
poetry add --dev pychub-poetry-plugin
poetry build
```

**Notes:**
- If you also install PDM into the same venv during tests, pin
  `findpython<0.7.0` to avoid Poetry↔PDM resolver fights.

---

### PDM

**Trigger:** `pdm build` → hook runs in `finalize` for the **wheel** artifact.

**Option A (dev-friendly):** non-isolated build (uses current venv where the
plugin is already installed)

```bash
pdm add -d pychub-pdm-plugin
pdm build --no-isolation -w
```

**Option B (isolated):** make the plugin installable in the build env

```toml
[build-system]
requires = ["pdm-backend>=2", "pychub-pdm-plugin>=0.1.0"]
build-backend = "pdm.backend"
```

```bash
pdm build -w
```

**Gotcha handled:** when PDM does “wheel from sdist” in a temp dir, the plugin
derives the real project root from the artifact path and switches CWD there
before invoking pychub.

---

### Hatch

**Trigger:** `BuildHookInterface.finalize(...)` (we only act on wheel artifacts)

Hatch’s CLI **always builds in an isolated env**. Either make your plugin
resolvable in that env **or** build via PyPA’s tool without isolation.

**Option A (dev-friendly, no isolation):** use hatchling via PyPA build

```toml
[build-system]
requires = ["hatchling>=1.13"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
# pick one layout:
packages = [{ include = "my_pkg" }]
# packages = [{ include = "my_pkg", from = "src" }]

[tool.hatch.build.targets.wheel.hooks.pychub]
# (plugin options if you add any)
```

```bash
python -m build --no-isolation -w -v
```

**Option B (true `hatch build`):** make the plugin installable in Hatch’s build
env

```toml
[build-system]
requires = ["hatchling>=1.13", "pychub-hatch-plugin>=0.1.0"]
build-backend = "hatchling.build"
```

```bash
hatch build -t wheel -v
```

*(Alternatively, point to a local wheel with a PEP 508 file URL in `requires` or
provide an index via `PIP_INDEX_URL`.)*

---

## Local development (this repo)

Editable installs so all three plugins + pychub are importable in your venv.
After cloning the repo, run the script in the root of the repo:

```bash
sh ./setup.sh
```

This will create a virtual environment, and install plugins and their
dependencies. After a successful run, then feel free to run the tests, or
open the project in your favorite IDE.

---

## Troubleshooting

- **Hatch:** `Unknown build hook: pychub`  
  Hatch’s isolated build env can’t see your plugin. Either:
  - switch to `python -m build --no-isolation`, or
  - include the plugin in `[build-system].requires` (or provide a
    `PIP_INDEX_URL` / file URL) so the build env can `pip install` it.

- **PDM:** `FileNotFoundError: .../dist/<name>.whl` in finalize  
  That’s the “via-sdist” temp CWD. The plugin already fixes this by rebasing to
  the project root; if you roll your own logic, do the same. Building with `-w`
  avoids the double pass.

- **Poetry + PDM in one venv (tests):**  
  Pin the shared finder to keep Poetry happy:

```bash
pip install "findpython<0.7.0"
```

- **Nothing built / plugin not firing:**  
  Ensure you’re running the build **from the consumer project dir** and that the
  plugin is installed in the environment that actually performs the build (or
  listed in `build-system.requires` for isolated builds).

---

## FAQ

- **Where does the `.chub` land?**  
  By default next to your wheel in `dist/`, or at
  `tool.pychub.package.chub` if you set it.

- **Do I need to list dependencies in the config?**  
  No. You can optionally add extra wheels via `add_wheels`, but pychub will
  resolve/install normal dependencies at runtime.

- **Can I run only for wheels?**  
  Yes—use `-w` with PDM/Hatch. The plugins already skip non-wheel artifacts.

---

## License

MIT. See `LICENSE` in this repository.
