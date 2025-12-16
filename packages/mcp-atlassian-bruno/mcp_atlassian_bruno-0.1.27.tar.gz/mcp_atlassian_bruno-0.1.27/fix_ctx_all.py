import re

with open('src/mcp_atlassian/servers/confluence.py', 'r') as f:
    lines = f.readlines()

# Find all lines with 'confluence_fetcher = await get_confluence_fetcher(ctx)'
# and add 'ctx = get_context()' before them if not already there

output = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this line contains confluence_fetcher = await get_confluence_fetcher(ctx)
    if 'confluence_fetcher = await get_confluence_fetcher(ctx)' in line:
        # Check if the previous line already has ctx = get_context()
        if i > 0 and 'ctx = get_context()' in lines[i-1]:
            # Already there, just add the line
            output.append(line)
        else:
            # Add ctx = get_context() before this line
            # Determine indentation from current line
            indent = len(line) - len(line.lstrip())
            output.append(' ' * indent + 'ctx = get_context()\n')
            output.append(line)
    else:
        output.append(line)
    
    i += 1

with open('src/mcp_atlassian/servers/confluence.py', 'w') as f:
    f.writelines(output)

print("Added ctx = get_context() to all functions")
