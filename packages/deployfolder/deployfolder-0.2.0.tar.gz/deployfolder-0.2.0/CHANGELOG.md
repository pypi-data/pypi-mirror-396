# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [0.2.0] - 2025-12-14
### Added
- Deploy pipeline now publishes releases to PyPI (wheel and sdist)
- Optional dependency extra for 7z support (`[7z]`)
- Unit test for the module entry point (`python -m deployfolder`)

### Fixed
- TAR archives now get correct extensions for gzip/bzip2/xz methods when no custom path is provided

### Changed
- README focuses on PyPI usage; local usage and path handling moved to `LOCAL_USAGE.md` (not packaged)


## [0.1.0] - 2025-11-29

### Added
- Initial release of DeployFolder
- Create deployment folders with a specified structure
- Copy files from source to target paths
- Optionally rename files during copying
- Support for placeholders in filenames and folder names
- Replace placeholders with values from a JSON file
- Create empty folders
- Generate files from Jinja2 templates (inline or from external files)
- Archive functionality with configurable options
  - Support for multiple archive formats: ZIP, TAR, and 7Z
  - Configurable compression methods for each format
    - ZIP: stored, deflated, bzip2, lzma
    - TAR: uncompressed, gz, bz2, xz
    - 7Z: default 7z compression
  - Support for configurable compression levels
  - YAML configuration options under `archive` key
  - Detailed documentation in ARCHIVE_OPTIONS.md
- Cross-platform compatibility (Windows and Linux)
- Support for nested JSON placeholders using dot notation
- Comprehensive documentation and examples
- Support for glob patterns in file paths
  - Wildcard pattern matching for source file paths using Python's glob module
  - Ability to specify multiple files using patterns like *.txt or file?.txt
  - Special handling for directory targets with glob patterns

