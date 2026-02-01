# Windrunner — README for Git

This repository contains a small utility (Windrunner) that fetches
artifact metadata from a Harbor registry, resolves the platform
digest for Linux images, retrieves the image configuration blob and
persists a few runtime values to disk for downstream consumption.

Files of interest
- `src/env.py`: Holds environment-derived configuration values used
  throughout the project (mount paths and Harbor credentials/URL).
- `src/main.py`: CLI entrypoint that performs the Harbor API calls,
  validates the image configuration and writes `WorkingDir`, the
  executable and its arguments to files under the configured volume.

Behavior overview
- Build the Harbor API URL using `HARBORHOST`, `proj`, `repo` and
  `tag`.
- Fetch artifact metadata and use `get_linux_digest` to find the
  linux-specific manifest digest.
- Fetch the configuration blob for that digest and extract fields
  such as `WorkingDir` and `Cmd`.
- Persist `WorkingDir` to `<VOLUME>/digitalforge/path.txt`, the
  command (first `Cmd` entry) to `cmd.txt` and remaining `Cmd`
  elements as a JSON array to `args.txt`.

Configuration (environment variables)
- `VOLUME`: path where Windrunner will write the output files. If
  not set, the code defaults to `/mnt/vol`.
- `HARBORHOST`: base URL for the Harbor API (default
  `http://harbor-core.harbor/api/v2.0`).
- `HARBORUSER` / `HARBORPASS`: credentials used to access Harbor if
  needed by the Harbor client (defaults provided in `env.py`).

How to run

Install dependencies from `requirements.txt` and run:

```bash
python -m src.main --proj YOUR_PROJECT --repo YOUR_REPO --tag YOUR_TAG
```

Or use the default parameters (for local testing) by running:

```bash
python -m src.main
```

Notes
- The tool currently does not support images that declare an
  `Entrypoint` — `main` will raise `NotImplementedError` in that
  case so the calling environment can handle it.
- The `windbinder` package (Harbor client helpers) is expected to
  provide `get_artifact`, `get_linux_digest` and `get_config` used
  by `main.py`.

If you want, I can also add more detailed examples, update
documentation for the Harbor helper package, or run quick tests.
