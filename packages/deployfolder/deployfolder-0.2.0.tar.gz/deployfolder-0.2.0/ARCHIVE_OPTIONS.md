# Archive Options

This document describes the archive options available in the DeployFolder tool.

## Configuration

The DeployFolder tool now supports configurable archive formats and compression methods. You can specify these options in your YAML configuration file.

### Basic Usage

To create an archive with default settings (ZIP format with LZMA compression):

```yaml
archive: true
```

### Advanced Configuration

For more control over the archive format and compression method:

```yaml
archive:
  format: "zip"  # Archive format: "zip", "tar", or "7z"
  method: "lzma"  # Compression method (see below)
  level: 9  # Compression level (if applicable)
```

### Supported Formats and Methods

#### ZIP Format

When using `format: "zip"`, the following compression methods are supported:

- `"stored"`: No compression (fastest, largest file size)
- `"deflated"`: Standard ZIP compression
- `"bzip2"`: BZIP2 compression
- `"lzma"`: LZMA compression (default, smallest file size but slowest)

Example:
```yaml
archive:
  format: "zip"
  method: "deflated"
  level: 9  # Compression level (1-9, higher = more compression)
```

#### TAR Format

When using `format: "tar"`, the following compression methods are supported:

- No method specified: Uncompressed TAR file
- `"gz"`: GZIP compression
- `"bz2"`: BZIP2 compression
- `"xz"`: XZ compression

Example:
```yaml
archive:
  format: "tar"
  method: "gz"
```

#### 7Z Format

When using `format: "7z"`, the py7zr library is used. This requires the py7zr package to be installed:

```
pip install py7zr
```

Example:
```yaml
archive:
  format: "7z"
```

Note: The py7zr library is only imported when the 7z format is selected.

## Examples

### ZIP with DEFLATE Compression

```yaml
archive:
  format: "zip"
  method: "deflated"
  level: 6
```

### TAR with GZIP Compression

```yaml
archive:
  format: "tar"
  method: "gz"
```

### 7Z Archive

```yaml
archive:
  format: "7z"
```