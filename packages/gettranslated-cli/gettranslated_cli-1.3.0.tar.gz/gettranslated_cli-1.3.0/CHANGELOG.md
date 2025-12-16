# Changelog

All notable changes to the GetTranslated CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-12-11

### Added
- Added `validate` command with `--force` option:
  - Validates translation correctness
  - When `--force` is specified, the command now re-validates the most recent project source files as well as all project translations
  - Provides summary of re-validated files and any validation issues found

## [1.2.0] - 2025-12-08

### Added
- New `init` command for easy project setup:
  - Guides users through API key configuration with masked input
  - Validates API key by connecting to GetTranslated project
  - Displays project information (name, platform, base language, target languages)
  - Optionally saves API key to `.gettranslated` file for future use
  - Provides helpful links to project settings when languages aren't configured

### Changed
- Updated API key resolution precedence order: command line → `.gettranslated` file → environment variable
  - Project-specific config files now take precedence over global environment variables
  - Better support for multi-project workflows
- Improved error messages for "No files found" scenarios:
  - Added "Have you specified the correct directory?" prompt
  - Enhanced React Native error messages with prominent documentation links
  - Platform-specific file location guidance with troubleshooting links
- Enhanced documentation:
  - Added comprehensive `init` command documentation
  - Updated quick start guide to recommend `init` for first-time setup
  - Clarified when to use each API key configuration method (local dev vs CI/CD)
  - Removed manual `echo` instructions in favor of `init` command

### Improved
- Better user experience for first-time setup with guided `init` workflow
- More secure API key input using masked prompts
- Clearer separation between local development and CI/CD workflows

## [1.1.1] - 2025-12-03

### Changed
- Updated README with comprehensive documentation:
  - Added Server API Key clarification and requirements
  - Documented first sync workflow and language detection
  - Added validation section with examples
  - Expanded troubleshooting guide with detailed error scenarios
  - Added error handling documentation
  - Documented all command options including `--bypass-validation` and `--version`

## [1.1.0] - 2025-12-03

### Added
- Comprehensive error handling with helpful user messages
- Error messages include links to relevant documentation sections
- Unified exception handling system for consistent error reporting
- Timeouts for different operation types
- Better 404 error handling for missing translations with actionable guidance

### Changed
- Improved authentication error messages (403) with links to configuration guide
- Enhanced project not found error messages (404) with troubleshooting steps
- Translation file not found errors now return 404 (not 500) with helpful messages

### Fixed
- Bug fixes and improvements

### Improved
- Code organization and maintainability
- User-facing error messages with clear next steps
- Documentation links in error messages

## [1.0.2] - 2025-XX-XX

### Changed
- Initial public release improvements

## [1.0.1] - 2025-XX-XX

### Changed
- Bug fixes and improvements

## [1.0.0] - 2025-XX-XX

### Added
- Initial release of GetTranslated CLI
- Support for Android, iOS, and React Native platforms
- Commands: `upload`, `download`, `translate`, `sync`, `grammar`
- API key configuration via command line, environment variable, or config file
- Automatic language file detection
- First sync workflow with language detection and warnings
- Validation error reporting
- Force upload option
- Verbose output mode
- Custom server URL support

[1.3.0]: https://pypi.org/project/gettranslated-cli/1.3.0/
[1.2.0]: https://pypi.org/project/gettranslated-cli/1.2.0/
[1.1.1]: https://pypi.org/project/gettranslated-cli/1.1.1/
[1.1.0]: https://pypi.org/project/gettranslated-cli/1.1.0/
[1.0.2]: https://pypi.org/project/gettranslated-cli/1.0.2/
[1.0.1]: https://pypi.org/project/gettranslated-cli/1.0.1/
[1.0.0]: https://pypi.org/project/gettranslated-cli/1.0.0/

