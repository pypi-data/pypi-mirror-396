#!/usr/bin/env python3
"""Script to fix test responses to use .content attribute."""

import re

files_to_fix = [
    "tests/unit/servers/test_jira_server.py",
    "tests/unit/servers/test_confluence_server.py",
]

for filepath in files_to_fix:
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Replace isinstance(response, list) with hasattr(response, "content")
        content = re.sub(
            r"assert isinstance\(response, list\)",
            r'assert hasattr(response, "content")',
            content,
        )

        # Replace len(response) with len(response.content)
        content = re.sub(r"len\(response\)(?!\.)", r"len(response.content)", content)

        # Replace response[0] with response.content[0]
        content = re.sub(r"(\s+)response\[0\]", r"\1response.content[0]", content)

        # Replace response[1] with response.content[1] etc
        content = re.sub(r"(\s+)response\[(\d+)\]", r"\1response.content[\2]", content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ Updated {filepath}")
    except Exception as e:
        print(f"✗ Error updating {filepath}: {e}")
