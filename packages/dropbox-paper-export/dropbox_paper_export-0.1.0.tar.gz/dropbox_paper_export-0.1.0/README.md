# Dropbox Paper Export

Tool to export Dropbox Paper documents to Markdown files with embedded images downloaded locally.

## Features

- Exports all `.paper` documents from a Dropbox folder (including subfolders) to Markdown format
- Downloads and saves images locally, updating markdown links to reference local files
- Supports both personal and team Dropbox accounts
- Shows progress with a progress bar during export
- Preserves folder structure from Dropbox

## How It Works

1. Connects to Dropbox using the API
2. Recursively scans for `.paper` files in the specified directory
3. Exports each document to Markdown format using Dropbox's export API
4. Scans the exported markdown for image links
5. Downloads each image and saves it to a local `assets/` folder
6. Updates the markdown to reference the local image paths

## Requirements

- Python 3.12+
- Dropbox API access token with appropriate permissions

## Usage

1. Create a Dropbox App at https://www.dropbox.com/developers/apps
2. Generate an access token with the following permissions:
   - `account_info.read`
   - `files.metadata.read`
   - `files.content.read`
   - `sharing.read`
3. Install:

```bash
pip install dropbox-paper-export
```

4. Run

```bash
dropbox-paper-export --access-token ACCESS_TOKEN
```

Sample output:

```plaintext
Dropbox Paper to Markdown + Images Exporter ---
   * Detected Team Account. Namespace ID: 1862260163
   * Switching API context to Team Root...
1. Scanning Dropbox for .paper files... (This takes a moment)
2. Found 138 Paper documents. Starting export...

Exporting:  28%|██        | 39/138 [01:43<02:35,  1.57s/doc]
   -> Downloading 15 images for 'Meeting summary'...
```

## Development

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Running locally
uv run main.py --access-token YOUR_TOKEN

# Linting
uv run ruff check .
uv run ruff format .

# Building release
uv build
```
