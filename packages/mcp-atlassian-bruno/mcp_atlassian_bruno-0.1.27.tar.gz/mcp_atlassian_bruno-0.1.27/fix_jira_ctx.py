#!/usr/bin/env python3
"""Fix ctx parameter in jira.py tool functions."""

import re

# Read the file
with open("src/mcp_atlassian/servers/jira.py", "r") as f:
    content = f.read()

# First, add the import if not already present
if "from fastmcp.server.dependencies import get_context" not in content:
    # Find the last import statement in the imports section
    import_section_match = re.search(
        r"(from mcp_atlassian\.utils\.decorators import.*?\n)",
        content,
        re.DOTALL
    )
    if import_section_match:
        insert_pos = import_section_match.end()
        content = (
            content[:insert_pos]
            + "\nfrom fastmcp.server.dependencies import get_context\n"
            + content[insert_pos:]
        )

# Pattern to match async function definitions with ctx: Context parameter
# This pattern captures: @decorator async def function_name(ctx: Context, ...
pattern = r'(async def \w+\(\s*)ctx: Context,\s*'

# Replace all occurrences: remove ctx: Context, parameter
content = re.sub(pattern, r'\1', content)

# Now add ctx = get_context() to each function body
# Pattern to find function docstrings and add ctx injection after them
def add_ctx_injection(content):
    """Add ctx = get_context() after docstrings in all async functions."""
    
    # Pattern to find: async def name(...): """ ... """
    # We need to insert ctx = get_context() after the closing """
    
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        result.append(line)
        
        # Check if this line starts a docstring (triple quotes)
        if '"""' in line or "'''" in line:
            quote_type = '"""' if '"""' in line else "'''"
            # Check if the docstring ends on the same line
            if line.count(quote_type) >= 2:
                # Single-line docstring, add ctx injection on next line
                i += 1
                if i < len(lines):
                    # Get indentation from current line
                    indent_match = re.match(r'^(\s*)', line)
                    indent = indent_match.group(1) if indent_match else ''
                    result.append(indent + "ctx = get_context()")
                    # Don't append the next line yet, we'll get it in the next iteration
                    i -= 1
            else:
                # Multi-line docstring, find the closing quotes
                i += 1
                while i < len(lines):
                    result.append(lines[i])
                    if quote_type in lines[i]:
                        # Found closing quotes, add ctx injection after
                        indent_match = re.match(r'^(\s*)', lines[i])
                        indent = indent_match.group(1) if indent_match else ''
                        result.append(indent + "ctx = get_context()")
                        break
                    i += 1
        
        i += 1
    
    return '\n'.join(result)

content = add_ctx_injection(content)

# Write back
with open("src/mcp_atlassian/servers/jira.py", "w") as f:
    f.write(content)

print("Fixed all ctx parameters in jira.py")
