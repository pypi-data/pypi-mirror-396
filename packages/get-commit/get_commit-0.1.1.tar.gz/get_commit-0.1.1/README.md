# get-commit

A CLI tool that automates commit messages using Gemini AI.

## Installation

```bash
pip install get-commit
```

## Setup

Set your Google API key as an environment variable:

```bash
export GOOGLE_API_KEY=your_api_key_here # Linus
$env:GOOGLE_API_KEY="your_api_key_here" # Windows
```

## Usage

Stage your changes and run:

```bash
get commit
```

The tool will generate a commit message based on your staged changes and ask for confirmation before committing.

