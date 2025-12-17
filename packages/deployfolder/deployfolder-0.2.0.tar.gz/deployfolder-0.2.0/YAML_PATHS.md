<!--
Copyright (c) 2025 Janosch Meyer (janosch.code@proton.me)
This project is licensed under the MIT License - see the LICENSE file for details.
This project was created with the assistance of artificial intelligence.
-->

# YAML Path Formatting Guide

## Issue Description

When using YAML configuration files with path strings, you may encounter errors like:

```
Error loading configuration file: while scanning a double-quoted scalar
  found unknown escape character 'd'
```

This document explains why this happens and how to avoid it.

## Why Backslashes Cause Problems in YAML

In YAML, backslashes (`\`) inside double-quoted strings are interpreted as escape characters, similar to many programming languages. For example:

- `\n` represents a newline
- `\t` represents a tab
- `\"` represents a double quote
- `\\` represents a literal backslash

When you use Windows-style paths with backslashes in YAML, like `"C:\path\to\file.txt"`, YAML tries to interpret these backslashes as escape sequences:

- `\p` is not a valid escape sequence, causing an error
- `\t` would be interpreted as a tab character, not as part of the path
- `\f` would be interpreted as a form feed character

## Solutions

### 1. Use Forward Slashes (Recommended)

The simplest solution is to use forward slashes (`/`) instead of backslashes (`\`) in all paths in your YAML files:

```yaml
# Good - Using forward slashes
- "C:/path/to/file.txt"
- directory: "{{ environment }}/docs"
```

Python's `pathlib.Path` will automatically handle the conversion to the appropriate path format for the operating system, so this works on both Windows and Linux.

### 2. Escape Backslashes by Doubling Them

If you must use backslashes, you need to escape them by doubling them:

```yaml
# Good - Escaping backslashes
- "C:\\path\\to\\file.txt"
- directory: "{{ environment }}\\docs"
```

### 3. Use Single Quotes

In YAML, strings in single quotes don't process escape sequences:

```yaml
# Good - Using single quotes
- 'C:\path\to\file.txt'
- directory: '{{ environment }}\docs'
```

However, this approach has a limitation: you can't include single quotes inside single-quoted strings without special handling.

## Common Errors and How to Fix Them

### Error: Unknown escape character

```
found unknown escape character 'd'
```

This typically happens with paths like `\docs` where `\d` is not a valid escape sequence.

**Fix:** Replace `\docs` with `/docs` or `\\docs`.

### Error: Unescaped control characters

```
found unescaped control character
```

This can happen if YAML interprets a backslash sequence as a control character.

**Fix:** Replace backslashes with forward slashes or escape them properly.

## Best Practices

1. Always use forward slashes (`/`) in YAML files, even on Windows
2. If you must use backslashes, double them (`\\`)
3. Test your YAML files with a YAML validator if you're unsure
4. Remember that this is a YAML syntax requirement, not a limitation of the DeployFolder tool

By following these guidelines, you'll avoid YAML parsing errors related to path formatting in your configuration files.