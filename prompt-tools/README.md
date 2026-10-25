# prompt-tools

Three tools sharing one Python venv:

- [`image-studio/`](image-studio/) &mdash; FastAPI UI: Gemma 3 12B expands a one-line idea, FLUX.2 renders it.
- [`compressor/`](compressor/) &mdash; FastAPI service: LLMLingua-2 compresses any prompt.
- [`extension/`](extension/) &mdash; Chrome extension that calls the compressor (Deep mode).

## Set up the shared venv

### Windows (PowerShell)

```powershell
py -m venv .venv
. .\activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source ./activate.sh
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### CUDA extras (NVIDIA only, skip on Mac)

```powershell
python -m pip install unsloth "bitsandbytes>=0.44.0"
```

The combined `requirements.txt` pulls in both `image-studio/requirements.txt`
and `compressor/requirements.txt`. First install pulls torch + transformers +
diffusers + llmlingua &mdash; several GB &mdash; so give it a few minutes.

## Run the services

```bash
# image-studio UI at http://localhost:7860
python image-studio/app.py

# compressor API at http://127.0.0.1:7870
python compressor/app.py
```

Both are standalone; run whichever you need.
