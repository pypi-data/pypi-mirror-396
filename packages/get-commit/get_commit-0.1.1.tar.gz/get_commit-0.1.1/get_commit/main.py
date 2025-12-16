"""Main module for the get CLI tool."""

import argparse
import os
import subprocess
import sys

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


def generate_commit_message(staged_files: list[str], diff: str) -> str:
    """Generate a commit message using Gemini AI based on staged changes."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    staged_files_str = "\n".join(staged_files) if staged_files else "No files"

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that generates concise commit messages.",
            ),
            (
                "human",
                """Generate a concise, clear commit message based on the following 
staged files and their changes.

Staged files:
{staged_files}

Diff:
{diff}

The commit message should:
- Use natural language
- Describe what was changed and why
- Be written in imperative mood (e.g., "Add feature" not "Added feature")

Return only the commit message, nothing else.""",
            ),
        ]
    )

    chain = prompt | llm
    result = chain.invoke({"staged_files": staged_files_str, "diff": diff})
    return result.content.strip()


def commit() -> None:
    """Generate a commit message using Gemini AI based on staged changes."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    staged_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

    if not staged_files:
        print("No staged files found.")
        return

    diff_result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    commit_message = generate_commit_message(staged_files, diff_result.stdout)
    print(commit_message)
    print("\n")

    response = input("Do you want to commit with this message? (y/n): ").strip().lower()
    print("\n")

    if response in ("y", "yes"):
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            check=True,
        )
        return

    print("Commit cancelled.")
    return


def main() -> None:
    """Main entry point for the get CLI tool."""
    parser = argparse.ArgumentParser(
        description="Get is a CLI tool that automates commit messages using Gemini AI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser(
        "commit",
        help="Generate a commit message using Gemini AI based on staged changes.",
    )

    args = parser.parse_args()

    # Check GOOGLE_API_KEY is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY is not set. Please set it in the environment variables.")
        sys.exit(1)

    if args.command == "commit":
        commit()
    elif args.command is None:
        parser.print_help()
        sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
