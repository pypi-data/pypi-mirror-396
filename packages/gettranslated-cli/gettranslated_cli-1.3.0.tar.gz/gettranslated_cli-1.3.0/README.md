# GetTranslated CLI

Command-line tool for syncing translation files with [GetTranslated.ai](https://www.gettranslated.ai).

## Installation

```bash
pip install gettranslated-cli
```

## Quick Start

### Option 1: Using `init` (Recommended for First-Time Setup)

The easiest way to get started is using the `init` command:

```bash
# Navigate to your project directory
cd /path/to/your/project

# Run init to link your project
translate init
```

The `init` command will:
- Prompt you for your Server API Key (input is masked for security)
- Validate your API key by connecting to your project
- Display your project information (name, platform, base language, target languages)
- Optionally save your API key to `.gettranslated` for future use

After initialization, you can run commands like `translate sync` or `translate upload` without entering your API key again.

### Option 2: Manual Setup

1. **Get your Server API Key** from your project settings
   - ⚠️ **Important**: Use the **Server API Key**, not the Client API Key
   - The Server API Key is required for CLI operations

2. **Configure your API key** (choose one method):
   ```bash
   # Option 1: Use init command (recommended for local development)
   translate init
   
   # Option 2: Environment variable (recommended for CI/CD)
   export GETTRANSLATED_KEY="your-server-api-key-here"
   
   # Option 3: Command line flag (useful for one-off commands or overrides)
   translate sync -k your-server-api-key-here
   ```
   
   **When to use each method:**
   - **`init` command**: Best for local development setup. Guides you through the process and saves your key to `.gettranslated`.
   - **Environment variable**: Ideal for CI/CD pipelines, Docker containers, and automated workflows. Keeps keys out of files.
   - **Command line flag (`-k`)**: Useful for one-off commands, testing, or overriding other configured keys.

3. **Run a sync** from your project directory:
   ```bash
   cd /path/to/your/project
   translate sync
   ```

That's it! The CLI will:
- Upload your base language files
- Translate any new or untranslated strings
- Download all translated files to your project

### First Sync Workflow

On your first sync, the CLI will:
- **Detect existing language files** in your project
- **Warn about base language mismatches** if detected
- **Offer to upload existing translations** if you already have translation files
- Guide you through the setup process

## Usage

### Basic Commands

```bash
# Initialize project (links directory to GetTranslated project)
translate init

# Full sync (upload → translate → download)
translate sync

# Upload only
translate upload

# Download only
translate download

# Translate only
translate translate

# Grammar check
translate grammar
```

### Options

```bash
# Specify working directory (default: current directory)
translate sync /path/to/project

# Verbose output (shows detailed debug information)
translate sync -v

# Force re-upload even if files haven't changed
translate sync -f

# Bypass validation errors and continue processing
translate sync --bypass-validation

# Custom server URL
translate sync -s https://custom-server.com

# Show version number
translate --version
```

### Validation

The CLI validates your translation files during upload. If validation errors are found:
- The process will stop with detailed error messages
- Each error includes the error code, message, and location (line/column)
- Use `--bypass-validation` to continue despite validation errors
- See the [Validation Errors documentation](https://www.gettranslated.ai/developers/validation-errors/) for details

**Example validation output:**
```
VALIDATION SUMMARY
======================================================================

📄 src/i18n/locales/en.json
  ❌ Validation Errors (2):
  • INVALID_KEY: Key contains invalid characters (line 5, column 12) [key: my-key]
  • MISSING_VALUE: Translation value is empty (line 10) [key: empty_key]
======================================================================
```

## Supported Platforms

- **Android**: Automatically finds `strings.xml` files in `values/` and `values-XX/` directories
- **iOS**: Automatically finds `Localizable.strings` and `Localizable.stringsdict` files in `XX.lproj/` directories
- **React Native**: Searches for JSON files in common locations:
  - `locales/`
  - `src/locales/`
  - `assets/locales/`
  - `translations/`
  - `i18n/`
  - Root directory

## API Key Configuration

The CLI looks for your API key in the following order (first match wins):

1. Command line argument (`-k` or `--key`) - highest priority, useful for overrides
2. Project config file (`.gettranslated` in project directory) - convenient for local development
3. Environment variable (`GETTRANSLATED_KEY`) - recommended for CI/CD and automated workflows

**Note:** If no API key is found and you're using `translate init`, you'll be prompted to enter it (input is masked for security).

### Choosing the Right Method

- **Local Development**: Use `translate init` to set up your project. It creates a `.gettranslated` file automatically.
- **CI/CD Pipelines**: Use environment variables (e.g., `GETTRANSLATED_KEY`) stored as secrets in your CI/CD platform. This keeps keys secure and out of your repository.
- **One-off Commands**: Use the `-k` or `--key` flag to override other configured keys for a single command.
- **Docker Containers**: Use environment variables passed at container runtime.

### Security Note

⚠️ **Important**: Add `.gettranslated` to your `.gitignore` to avoid committing your API key:

```bash
echo ".gettranslated" >> .gitignore
```

**API Key Requirements:**
- Use the **Server API Key** (not the Client API Key)
- The Server API Key is required for all CLI operations
- Keep your API key secure and never commit it to version control
- API keys can be rotated in your project settings if needed

## Examples

### First-time Setup

**Using `init` (Recommended):**
```bash
# 1. Install the CLI
pip install gettranslated-cli

# 2. Navigate to your project
cd ~/projects/my-app

# 3. Run init to link your project
translate init

# 4. Run your first sync
translate sync
```

**Manual Setup:**
```bash
# 1. Install the CLI
pip install gettranslated-cli

# 2. Set your API key
export GETTRANSLATED_KEY="your-key-here"

# 3. Navigate to your project
cd ~/projects/my-app

# 4. Run your first sync
translate sync
```

### CI/CD Integration

**For CI/CD pipelines, always use environment variables** to securely store your API key as secrets in your CI/CD platform. This keeps keys out of your repository and follows security best practices.

```yaml
# GitHub Actions example
# Store GETTRANSLATED_KEY as a secret in GitHub Settings > Secrets
name: Sync Translations

on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  sync-translations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      
      - name: Install GetTranslated CLI
        run: pip install gettranslated-cli
      
      - name: Run translation sync
        env:
          GETTRANSLATED_KEY: ${{ secrets.GETTRANSLATED_KEY }}
        run: translate sync .
```

## Troubleshooting

### Authentication Errors

**"No API key found"**
- Make sure you've configured your API key using one of the methods above
- Check that environment variables are set correctly
- Verify config files exist and contain the key
- Ensure you're running the command from the correct directory

**"Authentication failed" (403 error)**
- Verify you're using the **Server API Key** (not the Client API Key)
- Check that your API key hasn't expired or been revoked
- Ensure the API key matches an active project
- See: [API Key Configuration Guide](https://www.gettranslated.ai/developers/cli-quickstart/#configure)

**"Project not found" (404 error)**
- Verify you're using the correct Server API Key for your project
- Check that the project is active and not deleted
- Ensure the API key matches the project you want to access
- See: [API Key Configuration Guide](https://www.gettranslated.ai/developers/cli-quickstart/#configure)

### File Not Found Errors

**"No [Platform] files found to upload"**
- Ensure your project structure matches the expected format:
  - **Android**: `app/src/main/res/values/strings.xml`
  - **iOS**: 
    - `XX.lproj/Localizable.strings` (traditional format)
    - `XX.lproj/Localizable.stringsdict` (plurals format)
  - **React Native**: JSON files in one of the common locations
- Check that you're running the command from the correct directory
- Use `-v` (verbose) flag to see what directories are being searched

**"Translation file not found" (404 on download)**
- The translation may not have been created yet
- Run `translate sync` to upload, translate, and download in sequence
- Ensure languages are configured in your project settings
- Check that the file path matches your project configuration

### Connection Errors

**Network errors or timeouts**
- Verify your internet connection
- Check that the server URL is correct (default: `https://www.gettranslated.ai`)
- Large files may take longer - the CLI uses appropriate timeouts (30-120 seconds)
- Try again if the server is experiencing high load

**Request timeouts**
- File uploads/downloads: 120 seconds timeout
- Translation/grammar check: 120 seconds timeout
- Metadata requests: 10 seconds timeout
- If timeouts persist, check your network connection or try again later

### Validation Errors

**Validation errors during upload**
- Review the validation error messages for specific issues
- Each error includes the error code, message, and file location
- See the [Validation Errors documentation](https://www.gettranslated.ai/developers/validation-errors/) for detailed information
- Use `--bypass-validation` to continue despite errors (errors are still shown)

**"No languages are configured"**
- Configure languages in your project settings
- Visit your project settings page to add target languages
- At least one target language must be configured before translating or downloading

### Other Issues

**"Unknown platform" error**
- Ensure your project type is set correctly in project settings
- Supported platforms: Android, iOS, React Native
- Contact support if your platform type is incorrect

**Grammar check not available**
- Grammar check is available on Professional and Enterprise plans
- Upgrade your plan or contact support for more information

For more help, see the [CLI Quick Start Guide](https://www.gettranslated.ai/developers/cli-quickstart/#troubleshooting)

## Command Reference

```
translate <mode> [working_directory] [options]

Modes:
  init        Link current directory to a GetTranslated project (first-time setup)
  upload      Upload base language files to server
  download    Download translated files from server
  translate   Trigger translation of untranslated strings
  sync        Run upload → translate → download (recommended)
  grammar     Run grammar check on project strings

Options:
  -k, --key KEY              Server API key
  -v, --verbose              Verbose output mode (shows debug information)
  -f, --force                Force processing even if file hash matches
  --bypass-validation        Continue processing despite validation errors
  -s, --server URL           Server URL (default: https://www.gettranslated.ai)
  --version                  Show version number and exit
  -h, --help                 Show help message
```

### Error Handling

The CLI provides comprehensive error handling with helpful messages:

- **Authentication errors** (403): Clear messages with links to API key setup guide
- **Project not found** (404): Guidance on verifying your Server API Key
- **Translation not found** (404): Explains why and how to resolve
- **Network errors**: Helpful troubleshooting steps
- **Validation errors**: Detailed error information with file locations

All errors include links to relevant documentation for quick resolution.

## License

MIT License

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes in each version.

## Support

- Documentation: https://www.gettranslated.ai/developers/cli-quickstart/
- Email: support@gettranslated.ai

