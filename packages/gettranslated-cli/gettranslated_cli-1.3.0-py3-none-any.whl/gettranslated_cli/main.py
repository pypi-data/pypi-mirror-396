import argparse
import fnmatch
import getpass
import json
import os
import sys
import requests
from argparse import ArgumentParser


SERVER = "https://www.gettranslated.ai"
DEBUG = False
ENV_KEY = "GETTRANSLATED_KEY"
CONFIG_FILENAME = ".gettranslated"

# Timeout constants (in seconds)
TIMEOUT_METADATA = 10  # For simple GET requests (file list, language list)
TIMEOUT_FILE_UPLOAD = 120  # For file uploads (files can be large)
TIMEOUT_FILE_DOWNLOAD = 120  # For file downloads (files can be large)
# Increased to 200 seconds to allow for OpenAI API calls (120s) + gunicorn processing time (180s timeout)
TIMEOUT_LONG_OPERATION = 200  # For translation and grammar check (iterative operations)

# Common directories to exclude from language file detection
EXCLUDED_DIRS = {
    'node_modules', '.git', '.svn', '.hg', '.bzr',
    'build', 'dist', 'out', 'target',
    '.next', '.nuxt', '.vuepress',
    'coverage', '.nyc_output',
    '.vscode', '.idea',
    'tmp', 'temp', '.tmp', '.temp',
    '.DS_Store', 'Thumbs.db',
    'vendor', 'bower_components',
    '.cache', '.parcel-cache',
}

# Cache for fetched language codes
_SUPPORTED_LANGUAGE_CODES_CACHE = None


def format_validation_issue(issue):
    """
    Format a validation issue (error or warning) into a human-readable string.
    
    Args:
        issue: Dictionary containing validation issue data with keys:
               - code: Error/warning code
               - message: Human-readable message
               - line: Optional line number
               - column: Optional column number
               - key: Optional key name
    
    Returns:
        Formatted string representation of the validation issue
    """
    msg = f"  • {issue.get('code', 'UNKNOWN')}: {issue.get('message', 'Unknown issue')}"
    
    # Add location information if available
    if issue.get('line'):
        msg += f" (line {issue['line']}"
        if issue.get('column'):
            msg += f", column {issue['column']}"
        msg += ")"
    
    # Add key information if available
    if issue.get('key'):
        msg += f" [key: {issue['key']}]"
    
    return msg


def _extract_error_message(response):
    """
    Extract error message from HTTP response.
    
    Args:
        response: requests.Response object
    
    Returns:
        str: Error message from response JSON, or default message
    """
    try:
        error_data = response.json()
        return error_data.get("error", "Unknown error")
    except (json.JSONDecodeError, ValueError):
        return "Unknown error"


def _handle_http_error(response, operation_name="Request", context_info=None):
    """
    Handle HTTP error responses with appropriate error messages and documentation links.
    
    Args:
        response: requests.Response object
        operation_name: Name of the operation that failed (e.g., "File upload", "Translation")
        context_info: Optional dict with additional context (e.g., {"file_path": "...", "url": "..."})
    
    Returns:
        dict: Error information dict with keys: error_message, status_code, response_text
    """
    status_code = response.status_code
    error_msg = _extract_error_message(response)
    response_text = response.text[:500] if response.text else None
    
    if status_code == 403:
        message = f"❌ Authentication failed. Please check your API key configuration."
        message += "\n"
        message += f"\nThe request was denied: {error_msg}"
        message += "\nMake sure you have configured your Server API Key correctly."
        message += "\n"
        message += f"\nFor help setting up your API key, see:"
        message += f"\n  {SERVER}/developers/cli-quickstart/#configure"
        message += "\n"
        return {
            "error_message": message,
            "status_code": 403,
            "response_text": response_text,
        }
    elif status_code == 404:
        message = f"❌ Project not found. Please verify you are using the correct Server API Key."
        message += "\n"
        message += f"\nThe server key you're using doesn't match any active project: {error_msg}"
        message += "\nMake sure you are using the Server API Key (not the Client API Key)"
        message += "\nfrom your project settings."
        message += "\n"
        message += f"\nFor help setting up your API key, see:"
        message += f"\n  {SERVER}/developers/cli-quickstart/#configure"
        message += "\n"
        return {
            "error_message": message,
            "status_code": 404,
            "response_text": response_text,
        }
    else:
        message = f"❌ {operation_name} failed with status code {status_code}"
        if error_msg != "Unknown error":
            message += f"\nError: {error_msg}"
        elif response_text:
            message += f"\nResponse: {response_text}"
        message += "\n"
        message += f"\nFor troubleshooting help, see:"
        message += f"\n  {SERVER}/developers/cli-quickstart/#troubleshooting"
        message += "\n"
        return {
            "error_message": message,
            "status_code": status_code,
            "response_text": response_text,
        }


def _handle_exception(e, operation_name="Request", timeout_message=None, print_and_exit=False, context_info=None):
    """
    Unified exception handler that handles all exception types.
    
    Args:
        e: Exception object (any exception type)
        operation_name: Name of the operation that failed
        timeout_message: Optional custom timeout message (for Timeout exceptions)
        print_and_exit: If True, print error and exit. If False, return error dict.
        context_info: Optional dict with additional context (e.g., {"file_path": "...", "url": "..."})
    
    Returns:
        dict: Error information dict with keys: error_message, and optionally status_code, response_text
              Returns None if print_and_exit is True (function exits instead)
    
    Raises:
        SystemExit: If print_and_exit is True
    """
    error_info = {}
    
    # Handle different exception types
    if isinstance(e, requests.exceptions.Timeout):
        if timeout_message:
            message = timeout_message
        else:
            message = f"❌ Request timed out during {operation_name.lower()}."
            message += "\n"
            message += "\nThe server may be experiencing high load. Please try again."
        message += "\n"
        message += f"\nFor troubleshooting help, see:"
        message += f"\n  {SERVER}/developers/cli-quickstart/#troubleshooting"
        message += "\n"
        error_info = {"error_message": message}
    
    elif isinstance(e, requests.exceptions.RequestException):
        message = f"❌ Network error during {operation_name.lower()}: {e}"
        message += "\n"
        message += "\nPlease check your internet connection and try again."
        message += "\n"
        message += f"\nFor troubleshooting help, see:"
        message += f"\n  {SERVER}/developers/cli-quickstart/#troubleshooting"
        message += "\n"
        error_info = {"error_message": message}
    
    elif isinstance(e, IOError) or isinstance(e, OSError):
        # File I/O errors
        if context_info and "file_path" in context_info:
            message = f"❌ File operation failed for {context_info['file_path']}: {e}"
        else:
            message = f"❌ File operation failed: {e}"
        message += "\n"
        message += "\nPlease check file permissions and disk space."
        message += "\n"
        message += f"\nFor troubleshooting help, see:"
        message += f"\n  {SERVER}/developers/cli-quickstart/#troubleshooting"
        message += "\n"
        error_info = {"error_message": message}
    
    elif isinstance(e, json.JSONDecodeError):
        message = f"❌ Invalid response format from server: {e}"
        message += "\n"
        message += "\nThe server returned an invalid response. Please try again or contact support."
        message += "\n"
        message += f"\nFor troubleshooting help, see:"
        message += f"\n  {SERVER}/developers/cli-quickstart/#troubleshooting"
        message += "\n"
        error_info = {"error_message": message}
    
    elif isinstance(e, UnicodeDecodeError):
        message = f"❌ Failed to decode file content: {e}"
        message += "\n"
        message += f"\nFor troubleshooting help, see:"
        message += f"\n  {SERVER}/developers/cli-quickstart/#troubleshooting"
        message += "\n"
        error_info = {"error_message": message}
    
    else:
        # Generic exception handler
        message = f"❌ Unexpected error during {operation_name.lower()}: {e}"
        message += "\n"
        message += f"\nFor troubleshooting help, see:"
        message += f"\n  {SERVER}/developers/cli-quickstart/#troubleshooting"
        message += "\n"
        error_info = {"error_message": message}
    
    if print_and_exit:
        print(error_info["error_message"])
        sys.exit(1)
    
    return error_info


def _parse_json_response(response, operation_name="Request"):
    """
    Parse JSON response and handle parsing errors.
    
    Args:
        response: requests.Response object
        operation_name: Name of the operation (for error messages)
    
    Returns:
        dict: Parsed JSON data
    
    Raises:
        SystemExit: If JSON parsing fails
    """
    try:
        return response.json()
    except Exception as e:
        _handle_exception(e, operation_name, print_and_exit=True)


def upload_file(file_path, root_dir, token, force=False, language=None, is_base_language=False):
    """
    Upload a file to the server.
    
    Args:
        file_path: Path to the file to upload
        root_dir: Root directory for relative path calculation
        token: Authentication token
        force: Whether to force processing even if file hash matches
        language: Language code (defaults to "en")
        is_base_language: Whether this is a base language file
    
    Returns:
        dict with keys:
            - success: bool indicating if upload succeeded
            - response_data: dict with response data (if success)
            - validation_errors: list of validation errors
            - validation_warnings: list of validation warnings
            - file_path: path to the uploaded file
            - error_message: str with error message (if not success)
            - url: upload URL (if error)
            - response_text: response text (if error)
            - status_code: HTTP status code (if error)
    """
    # Determine the language to use
    if language is None:
        language = "en"

    # Use os.path.relpath to get the relative path, which handles . correctly
    path = os.path.relpath(file_path, root_dir).replace("\\", "/")
    if path.startswith("/"):
        path = path[1:]
    upload_url = f"{SERVER}/sync/file/{language}/{path}"

    # Create a dictionary with the file key and the file to be uploaded
    # Use context manager to ensure file is closed
    try:
        with open(file_path, "rb") as f:
            files = {"file": ("filename", f)}
            
            # Send a POST request to the server
            headers = {"Authorization": f"Bearer {token}"}
            data = {"force": "true"} if force else {}
            response = requests.post(upload_url, files=files, headers=headers, data=data, timeout=TIMEOUT_FILE_UPLOAD)
    except Exception as e:
        error_info = _handle_exception(
            e,
            "File upload",
            timeout_message="Request timed out. The server may be experiencing high load. Please try again.",
            context_info={"file_path": file_path, "url": upload_url}
        )
        return {
            "success": False,
            "error_message": error_info["error_message"],
            "file_path": file_path,
            "url": upload_url,
            "response_text": None,
        }

    # Check the response
    if response.status_code == 200:
        try:
            response_data = response.json()
        except Exception as e:
            error_info = _handle_exception(
                e,
                "File upload",
                context_info={"file_path": file_path, "url": upload_url}
            )
            return {
                "success": False,
                "error_message": error_info["error_message"],
                "file_path": file_path,
                "url": upload_url,
                "response_text": response.text[:500] if response.text else None,
            }
        
        debug(json.dumps(response_data, indent=4))
        
        # Extract validation errors and warnings
        validation_errors = response_data.get("validation_errors", [])
        validation_warnings = response_data.get("validation_warnings", [])
        
        # Extract plan limit warnings and skipped keys (new fields from partial processing)
        plan_warning = response_data.get("warning")  # String warning message
        skipped_keys = response_data.get("skipped keys", 0)  # Number of skipped strings
        
        return {
            "success": True,
            "response_data": response_data,
            "validation_errors": validation_errors,
            "validation_warnings": validation_warnings,
            "plan_warning": plan_warning,
            "skipped_keys": skipped_keys,
            "file_path": file_path,
        }
    else:
        error_info = _handle_http_error(response, "File upload", {"file_path": file_path, "url": upload_url})
        return {
            "success": False,
            "error_message": error_info["error_message"],
            "file_path": file_path,
            "url": upload_url,
            "response_text": error_info.get("response_text"),
            "status_code": error_info["status_code"],
        }


def find_files(directory, file_list, language=None):
    # If language is specified, find files for that language; otherwise use base language
    target_language = language if language else file_list["base_language"]
    
    if file_list["platform"] == "Android":
        # check for Android strings.xml files
        values_dir = "values" if target_language == "en" else f"values-{target_language}"
        return find_files_helper(directory, "strings.xml", values_dir)

    elif file_list["platform"] == "iOS":
        # check for iOS strings files (.strings, .stringsdict)
        results = []
        
        # Look for .strings files in .lproj directories
        strings_files = find_files_helper(
            directory, "*.strings", f"{target_language}.lproj"
        )
        results.extend(strings_files)
        
        # Look for .stringsdict files in .lproj directories
        stringsdict_files = find_files_helper(
            directory, "*.stringsdict", f"{target_language}.lproj"
        )
        results.extend(stringsdict_files)
        
        return results
    elif file_list["platform"] == "React Native":
        # check for React Native JSON files in common locations
        # Priority order: locales/, src/locales/, assets/locales/, translations/, i18n/, root
        common_dirs = ["locales", "src/locales", "assets/locales", "translations", "i18n", ""]
        
        for dir_path in common_dirs:
            results = find_files_helper(
                directory, f"{target_language}.json", dir_path
            )
            if results:
                return results
        
        return []
    else:
        print(f"❌ Unknown platform: {file_list['platform']}")
        print()
        print("Supported platforms are: Android, iOS, React Native")
        print()
        print(f"For troubleshooting help, see:")
        print(f"  {SERVER}/developers/cli-quickstart/#troubleshooting")
        print()
        sys.exit(1)


def _process_directory_item(item_path, item, excluded_dirs, callback, search_recursive, depth, max_depth):
    """Process a single directory item (file or subdirectory)."""
    # Skip excluded directories
    if os.path.isdir(item_path) and item in excluded_dirs:
        return
    
    # Try callback first (might match a file)
    if os.path.isfile(item_path):
        callback(item_path, item)
    
    # Recurse into subdirectories
    if os.path.isdir(item_path):
        search_recursive(item_path, callback, depth + 1, max_depth)


def _search_recursive_for_languages(directory, excluded_dirs=None):
    """
    Shared recursive search function for all platforms.
    Returns a function that searches recursively for language files.
    """
    if excluded_dirs is None:
        excluded_dirs = EXCLUDED_DIRS.copy()
    
    def search_recursive(search_dir, callback, depth=0, max_depth=5):
        """
        Recursively search directory and call callback for each file.
        callback(file_path, item_name) should return True if file matches and was processed.
        """
        if depth > max_depth:
            return
        
        try:
            if not os.path.isdir(search_dir):
                return
                
            for item in os.listdir(search_dir):
                item_path = os.path.join(search_dir, item)
                _process_directory_item(item_path, item, excluded_dirs, callback, search_recursive, depth, max_depth)
        except PermissionError:
            # Skip directories we can't read
            pass
    
    return search_recursive


def _detect_android_languages(directory, token):
    """Detect Android language files by recursively scanning for values-* directories"""
    detected_languages = {}
    
    excluded_dirs = EXCLUDED_DIRS.copy()
    excluded_dirs.update({'android', 'ios'})
    
    search_recursive = _search_recursive_for_languages(directory, excluded_dirs)
    supported_codes = get_supported_languages(token)
    
    def handle_file(file_path, item_name):
        # Look for values directories containing strings.xml
        parent_dir = os.path.basename(os.path.dirname(file_path))
        if parent_dir.startswith("values") and item_name == "strings.xml":
            lang_code = parent_dir.replace("values", "").replace("-", "") if parent_dir != "values" else "en"
            # Only consider supported language codes
            if lang_code in supported_codes:
                if lang_code not in detected_languages:
                    detected_languages[lang_code] = []
                detected_languages[lang_code].append(file_path)
                return True
        return False
    
    search_recursive(directory, handle_file)
    return detected_languages


def _detect_ios_languages(directory, token):
    """Detect iOS language files by recursively scanning for .lproj directories"""
    detected_languages = {}
    
    excluded_dirs = EXCLUDED_DIRS.copy()
    excluded_dirs.update({'android', 'ios'})
    
    search_recursive = _search_recursive_for_languages(directory, excluded_dirs)
    supported_codes = get_supported_languages(token)
    
    def handle_file(file_path, item_name):
        # Look for .lproj directories containing iOS localization files
        parent_dir = os.path.basename(os.path.dirname(file_path))
        
        # Check for .strings and .stringsdict files in .lproj directories
        if parent_dir.endswith(".lproj"):
            if item_name in ("Localizable.strings", "Localizable.stringsdict"):
                lang_code = parent_dir.replace(".lproj", "")
                # Only consider supported language codes
                if lang_code in supported_codes:
                    if lang_code not in detected_languages:
                        detected_languages[lang_code] = []
                    detected_languages[lang_code].append(file_path)
                    return True
        
        return False
    
    search_recursive(directory, handle_file)
    return detected_languages


def _detect_react_native_languages(directory, token):
    """Detect React Native language files by recursively scanning for JSON files"""
    detected_languages = {}
    
    excluded_dirs = EXCLUDED_DIRS.copy()
    excluded_dirs.update({'android', 'ios'})
    
    search_recursive = _search_recursive_for_languages(directory, excluded_dirs)
    supported_codes = get_supported_languages(token)

    def handle_file(file_path, item_name):
        # Look for language JSON files (format: lang.json)
        if item_name.endswith(".json"):
            lang_code = item_name.replace(".json", "")
            if lang_code in supported_codes:
                if lang_code not in detected_languages:
                    detected_languages[lang_code] = []
                detected_languages[lang_code].append(file_path)
                return True
        return False
    
    search_recursive(directory, handle_file)
    return detected_languages


def detect_all_languages_in_project(directory, file_list, token):
    """Detect all language files present in the project directory"""
    platform = file_list["platform"]
    
    if platform == "Android":
        return _detect_android_languages(directory, token)
    elif platform == "iOS":
        return _detect_ios_languages(directory, token)
    elif platform == "React Native":
        return _detect_react_native_languages(directory, token)
    
    return {}


def find_translation_files(directory, file_list):
    """Find translation files for all configured languages (excluding base language)"""
    translation_files = {}
    
    # Get all configured languages
    all_languages = file_list.get("languages", [])
    
    for language in all_languages:
        files = find_files(directory, file_list, language)
        if files:
            translation_files[language] = files
    
    return translation_files


def find_files_helper(directory, filename_pattern, filedir, results=None, root_dir=None):
    """
    Recursively search for files matching the given filename in the specified directory.

    Args:
        directory (str): The directory to start the search from.
        filename (str): The filename to search for.
        filedir (str): The immediate file directory to match.
        results (list, optional): A list to store the matching file paths. Defaults to None.
        root_dir (str, optional): The root directory for the search. Used for empty filedir searches.

    Returns:
        list: A list of file paths matching the given filename.
    """
    if results is None:
        results = []
    if root_dir is None:
        root_dir = directory

    # Directories to exclude from search (reuse global constant)
    excluded_dirs = EXCLUDED_DIRS.copy()

    # Iterate over all items in the directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # Skip excluded directories
        if os.path.isdir(item_path) and item in excluded_dirs:
            continue

        # If item is a directory, recursively search within it
        if os.path.isdir(item_path):
            find_files_helper(item_path, filename_pattern, filedir, results, root_dir)
        # If item is a file and matches the filename, add it to results
        elif (
            os.path.isfile(item_path)
            and fnmatch.fnmatch(item, filename_pattern)
            and (
                (filedir == "" and directory == root_dir) or  # Root search - only files in root directory
                (filedir != "" and directory.endswith(filedir))  # Specific directory search
            )
        ):
            results.append(item_path)

    return results


def translate(token, first_call=True):
    url = f"{SERVER}/sync/translate"

    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers, timeout=TIMEOUT_LONG_OPERATION)
    except Exception as e:
        _handle_exception(
            e,
            "Translation",
            timeout_message="Translation requests can take longer. Please try again.",
            print_and_exit=True
        )

    # Check the response
    if response.status_code == 200:
        data = _parse_json_response(response, "Translation")

        if (
            first_call
            and data.get("translated", 0) == 0
            and not data.get("continue", False)
            and not data.get("error", False)
        ):
            print("Nothing to translate")
            return

        debug(json.dumps(data, indent=4))
        print(f"Translating {data.get('language', 'unknown')}... {data.get('percent_done', '0%')}")
        if data.get("continue", False):
            translate(token, first_call=False)
        elif data.get("error", False):
            print("❌ LLM error translating strings. Please try again, or contact support if this persists.")
            print()
            print(f"For troubleshooting help, see:")
            print(f"  {SERVER}/developers/cli-quickstart/#troubleshooting")
            print()
            sys.exit(1)
    else:
        error_info = _handle_http_error(response, "Translation")
        print(error_info["error_message"])
        sys.exit(1)


def run_validate_mode(token, force=False, working_dir=None, file_list=None):
    """
    Validate translations.
    
    Args:
        token: API authentication token
        force: If True, re-validate all translations (including already checked ones)
               and re-validate the most recent project source files
        working_dir: Working directory path (required if force=True to re-validate source files)
        file_list: File list data from server (optional, will be fetched if not provided and force=True)
    """
    # If force is specified, re-validate source files first
    if force and working_dir:
        if file_list is None:
            file_list = get_file_list(token)
        
        print("Re-validating most recent project source files...")
        base_language = file_list.get("base_language", "en")
        matching_files = find_files(working_dir, file_list)
        
        if matching_files:
            source_files_uploaded = 0
            source_files_with_errors = 0
            
            for file_path in matching_files:
                print(f"Re-validating source file: {file_path}")
                result = upload_file(file_path, working_dir, token, force=True, language=base_language, is_base_language=True)
                
                if result["success"]:
                    source_files_uploaded += 1
                    validation_errors = result.get("validation_errors", [])
                    validation_warnings = result.get("validation_warnings", [])
                    
                    if validation_errors:
                        source_files_with_errors += 1
                        print(f"  ❌ Validation Errors ({len(validation_errors)}):")
                        for error in validation_errors:
                            print(format_validation_issue(error))
                    
                    if validation_warnings:
                        print(f"  ⚠️  Validation Warnings ({len(validation_warnings)}):")
                        for warning in validation_warnings:
                            print(format_validation_issue(warning))
                else:
                    source_files_with_errors += 1
                    print(f"  ❌ Failed to re-validate {file_path}")
                    print(f"     Error: {result['error_message']}")
            
            print(f"\nRe-validated {source_files_uploaded} source file(s)")
            if source_files_with_errors > 0:
                print(f"  ⚠️  {source_files_with_errors} source file(s) had validation issues")
            print()
        else:
            print("No source files found to re-validate")
            print()
    
    # Validate translations
    url = f"{SERVER}/sync/validate"
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add force parameter in POST body if specified
    data = {}
    if force:
        data['force'] = 'true'
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=TIMEOUT_LONG_OPERATION)
    except Exception as e:
        _handle_exception(
            e,
            "Translation Validation",
            timeout_message="Validation requests can take longer. Please try again.",
            print_and_exit=True
        )
    
    # Check the response
    if response.status_code == 200:
        data = _parse_json_response(response, "Translation Validation")
        
        total_checked = data.get("total_checked", 0)
        invalid_count = data.get("invalid_count", 0)
        valid_count = data.get("valid_count", 0)
        
        print(f"Validated {total_checked} translation(s)")
        if invalid_count > 0:
            print(f"  ❌ {invalid_count} invalid translation(s) queued for re-translation")
        if valid_count > 0:
            print(f"  ✅ {valid_count} valid translation(s)")
        
        if total_checked == 0:
            print("No translations to validate")
    else:
        error_info = _handle_http_error(response, "Translation Validation")
        print(error_info["error_message"])
        sys.exit(1)


def grammar_check(token):
    url = f"{SERVER}/sync/grammar/check"

    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers, timeout=TIMEOUT_LONG_OPERATION)
    except Exception as e:
        _handle_exception(
            e,
            "Grammar check",
            timeout_message="Grammar check requests can take longer. Please try again.",
            print_and_exit=True
        )

    # Check the response
    if response.status_code == 200:
        data = _parse_json_response(response, "Grammar check")
        debug(json.dumps(data, indent=4))
        
        print(f"Grammar checking... {data.get('percent_done', '0%')}")

        if data.get("continue", False):
            grammar_check(token)
        if data.get("error", False):
            print("❌ Error running grammar check. Please try again, or contact support if this persists.")
            print()
            print(f"For troubleshooting help, see:")
            print(f"  {SERVER}/developers/cli-quickstart/#troubleshooting")
            print()
            sys.exit(1)
    elif response.status_code == 403:
        error_msg = _extract_error_message(response)
        print("❌ Grammar check request denied.")
        print()
        print(f"Error: {error_msg}")
        if "not available" in error_msg.lower() or "plan" in error_msg.lower():
            print("Grammar check is available on Professional and Enterprise plans.")
            print("Please upgrade your plan or contact support for more information.")
        else:
            print("Make sure you have configured your Server API Key correctly.")
            print()
            print(f"For help setting up your API key, see:")
            print(f"  {SERVER}/developers/cli-quickstart/#configure")
        print()
        sys.exit(1)
    else:
        error_info = _handle_http_error(response, "Grammar check")
        print(error_info["error_message"])
        sys.exit(1)


def get_token(args, working_dir):
    """Get API token from various sources in order of precedence."""
    # First, check if the key was specified as a command line argument
    if args.key is not None:
        debug(f"Using key from command line: {args.key}")
        return args.key

    # Next, check for .gettranslated file in project directory (hidden, less likely to be committed)
    project_config = os.path.join(working_dir, CONFIG_FILENAME)
    if os.path.exists(project_config):
        debug(f"Using key from {CONFIG_FILENAME} file: {project_config}")
        try:
            with open(project_config, "r", encoding="utf-8") as file:
                token = file.read().strip()
                # Return None if token is empty (whitespace-only tokens are invalid)
                return token if token else None
        except (IOError, OSError, UnicodeDecodeError) as e:
            debug(f"Error reading {CONFIG_FILENAME} file: {e}")
            # Don't fail here - fall through to return None so user gets helpful error message
            return None

    # Finally, check if the key is set as an environment variable
    if os.environ.get(ENV_KEY) is not None:
        debug(f"Using key from environment variable: {os.environ.get(ENV_KEY)}")
        return os.environ.get(ENV_KEY)

    return None


def debug(message):
    """
    Print debug message if DEBUG mode is enabled.
    
    Args:
        message: Message to print
    """
    if DEBUG:
        print(message)


def get_supported_languages(token):
    """
    Fetch supported language codes from the server.
    Returns a set of language codes.
    Exits with error if the request fails.
    
    Args:
        token: Required authentication token. Must be provided.
    """
    
    global _SUPPORTED_LANGUAGE_CODES_CACHE
    
    # Return cached value if available
    if _SUPPORTED_LANGUAGE_CODES_CACHE is not None:
        return _SUPPORTED_LANGUAGE_CODES_CACHE
    
    # Try to fetch from server
    url = f"{SERVER}/sync/languages"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT_METADATA)
        if response.status_code == 200:
            data = _parse_json_response(response, "Fetching supported languages")
            
            if "languages" in data and isinstance(data["languages"], list):
                _SUPPORTED_LANGUAGE_CODES_CACHE = set(data["languages"])
                debug(f"Fetched {len(_SUPPORTED_LANGUAGE_CODES_CACHE)} supported languages from server")
                return _SUPPORTED_LANGUAGE_CODES_CACHE
            else:
                print("❌ Invalid response format: missing 'languages' field")
                sys.exit(1)
        else:
            error_info = _handle_http_error(response, "Fetching supported languages")
            print(error_info["error_message"])
            sys.exit(1)
    except Exception as e:
        _handle_exception(e, "Fetching supported languages", print_and_exit=True)


def get_file_list(token):
    url = f"{SERVER}/sync/file/list"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT_METADATA)
    except Exception as e:
        _handle_exception(e, "Fetching file list", print_and_exit=True)

    # Check the response
    if response.status_code == 200:
        data = _parse_json_response(response, "Fetching file list")
        debug(json.dumps(data, indent=4))
        return data
    else:
        error_info = _handle_http_error(response, "File list request")
        print(error_info["error_message"])
        sys.exit(1)


def sync(dir, fileset, token):
    url = f"{SERVER}/sync/{fileset['uri']}"
    headers = {"Authorization": f"Bearer {token}"}
    file_path = fileset.get('local_path', 'unknown')
    
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT_FILE_DOWNLOAD)
    except Exception as e:
        _handle_exception(
            e,
            f"Downloading {file_path}",
            print_and_exit=True,
            context_info={"file_path": file_path}
        )

    # Check the response status code and stop if not 200
    if response.status_code == 200:
        try:
            content = response.content.decode("utf-8")
        except Exception as e:
            _handle_exception(e, f"Decoding {file_path}", print_and_exit=True, context_info={"file_path": file_path})

        output_file = os.path.join(dir, fileset["local_path"])
        print(f"Syncing {output_file}...")

        directory = os.path.dirname(output_file)
        if not os.path.exists(directory):
            debug(f"Creating directory {directory}")
            try:
                os.makedirs(directory)
            except Exception as e:
                _handle_exception(e, f"Creating directory {directory}", print_and_exit=True, context_info={"file_path": directory})

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            _handle_exception(e, f"Writing file {output_file}", print_and_exit=True, context_info={"file_path": output_file})
    elif response.status_code == 404:
        error_msg = _extract_error_message(response)
        print(f"❌ Translation file not found: {file_path}")
        print()
        print(f"Error: {error_msg}")
        print()
        print("This usually means:")
        print("  • The translation hasn't been created yet for this language")
        print("  • The file path doesn't match what's configured in your project")
        print("  • The translation file was deleted or hasn't been synced")
        print()
        print("To resolve this, run `translate sync`")
        print()
        print(f"For more help, see:")
        print(f"  {SERVER}/developers/cli-quickstart/#troubleshooting")
        print()
        sys.exit(1)
    else:
        error_info = _handle_http_error(response, f"Downloading {file_path}", {"file_path": file_path})
        print(error_info["error_message"])
        sys.exit(1)


class CustomHelpFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        # Override the _split_lines method to handle newlines
        lines = []
        for line in text.splitlines():
            lines.extend(argparse.HelpFormatter._split_lines(self, line, width))
        return lines


def handle_first_sync_warnings(working_dir, file_list, token):
    """Handle warnings and language detection on first sync."""
    detected_languages = detect_all_languages_in_project(working_dir, file_list, token)
    base_language = file_list["base_language"]
    
    if len(detected_languages) > 1:
        print()
        print("Detected multiple language files in your project:")
        for lang, files in detected_languages.items():
            print(f"  - {lang}: {len(files)} file(s)")
        
        if base_language not in detected_languages:
            print()
            print(f"⚠️  Warning: Base language configured as '{base_language}' but no files found for that language!")
            print("   You may need to change the base language in project settings.")
            print()
            response = input("Continue anyway? (y/n): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Upload cancelled.")
                sys.exit(0)
        print()


def _print_translation_files(translation_files):
    """Print list of found translation files."""
    print()
    print("Found existing translation files in your project:")
    for language, files in translation_files.items():
        for file_path in files:
            print(f"  - {file_path}")


def _upload_translation_files(translation_files, working_dir, token, force):
    """Upload translation files to the server."""
    print("Uploading translation files...")
    for language, files in translation_files.items():
        for file_path in files:
            print(f"Uploading {file_path} as {language}...")
            result = upload_file(file_path, working_dir, token, force, language)
            
            if not result["success"]:
                print(f"❌ Failed to upload {file_path}")
                print(f"   Error: {result['error_message']}")
                if result.get("response_text"):
                    print(f"   Response: {result['response_text']}")
                
                # Provide helpful guidance for common errors
                if result.get("status_code") == 403:
                    print()
                    print("   Authentication failed. Make sure your Server API Key is correct.")
                    print(f"   For help: {SERVER}/developers/cli-quickstart/#configure")
                elif result.get("status_code") == 404:
                    print()
                    print("   Project or file not found. Verify your API key matches an active project.")
                    print(f"   For help: {SERVER}/developers/cli-quickstart/#configure")
                
                continue
            
            # Display validation warnings for translation files (errors are less critical)
            validation_warnings = result.get("validation_warnings", [])
            if validation_warnings:
                print(f"  ⚠️  Validation Warnings ({len(validation_warnings)}):")
                for warning in validation_warnings:
                    print(format_validation_issue(warning))


def handle_upload_translations(working_dir, file_list, token, force):
    """Offer to upload existing translation files on first sync."""
    all_detected_languages = detect_all_languages_in_project(working_dir, file_list, token)
    base_language = file_list["base_language"]
    
    # Filter out the base language - those are translation files
    translation_files = {lang: files for lang, files in all_detected_languages.items() 
                       if lang != base_language}
    
    if not translation_files:
        return
    
    _print_translation_files(translation_files)
    print()
    response = input("Would you like to upload these translations? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        _upload_translation_files(translation_files, working_dir, token, force)
    else:
        print("Skipping translation file upload.")


def run_upload_mode(working_dir, file_list, token, force, is_first_sync, bypass_validation=False):
    """Handle upload mode operations."""
    if is_first_sync:
        handle_first_sync_warnings(working_dir, file_list, token)
    
    print("Beginning upload...")
    matching_files = find_files(working_dir, file_list)

    if len(matching_files) == 0:
        base_language = file_list.get("base_language", "unknown")
        platform = file_list.get("platform", "unknown")
        
        print(f"❌ No {platform} files found to upload for base language '{base_language}'")
        print()
        print(f"Searched in: {working_dir}")
        print()
        
        # Platform-specific guidance
        if platform == "Android":
            print("Expected file locations:")
            print(f"  • {working_dir}/app/src/main/res/values/strings.xml")
            print(f"  • {working_dir}/res/values/strings.xml")
            print()
            print("For base language 'en', look for: values/strings.xml")
            print(f"For other languages, look for: values-{base_language}/strings.xml")
        elif platform == "iOS":
            print("Expected file locations:")
            print(f"  • {working_dir}/**/{base_language}.lproj/Localizable.strings")
            print(f"  • {working_dir}/**/{base_language}.lproj/Localizable.stringsdict")
            print()
            print(f"Look for .strings or .stringsdict files in {base_language}.lproj directories")
        elif platform == "React Native":
            print("Expected file locations (searched in order):")
            print(f"  • {working_dir}/locales/{base_language}.json")
            print(f"  • {working_dir}/src/locales/{base_language}.json")
            print(f"  • {working_dir}/assets/locales/{base_language}.json")
            print(f"  • {working_dir}/translations/{base_language}.json")
            print(f"  • {working_dir}/i18n/{base_language}.json")
            print(f"  • {working_dir}/{base_language}.json")
        
        print()
        print("Troubleshooting:")
        print("  1. Verify you're running the command from your project root directory")
        print("  2. Check that your base language matches your project configuration")
        print("  3. Ensure your project structure matches the expected format")
        print()
        print("For more help, see:")
        print(f"  {SERVER}/developers/cli-quickstart/#troubleshooting")
        print()
        sys.exit(1)

    # Collect validation results from all files before displaying/exiting
    upload_results = []
    has_any_validation_errors = False
    
    for file_path in matching_files:
        print(f"Syncing {file_path}...")
        result = upload_file(file_path, working_dir, token, force, is_base_language=True)
        upload_results.append(result)
        
        if result["success"] and result.get("validation_errors"):
            has_any_validation_errors = True
    
    # Display all validation results
    if upload_results:
        # Include files with validation issues OR plan limit warnings
        files_with_issues = [r for r in upload_results if not r["success"] or r.get("validation_errors") or r.get("validation_warnings") or r.get("plan_warning")]
        
        if files_with_issues:
            print("\n" + "="*70)
            print("VALIDATION SUMMARY")
            print("="*70)
            
            for result in files_with_issues:
                if not result["success"]:
                    print(f"\n❌ Failed to upload {result['file_path']}")
                    print(f"   Error: {result['error_message']}")
                    if result.get("response_text"):
                        print(f"   Response: {result['response_text']}")
                    
                    # Provide helpful guidance for common errors
                    if result.get("status_code") == 403:
                        print()
                        print("   Authentication failed. Make sure your Server API Key is correct.")
                        print(f"   For help: {SERVER}/developers/cli-quickstart/#configure")
                    elif result.get("status_code") == 404:
                        print()
                        print("   Project or file not found. Verify your API key matches an active project.")
                        print(f"   For help: {SERVER}/developers/cli-quickstart/#configure")
                    
                    continue
                
                file_path = result["file_path"]
                validation_errors = result.get("validation_errors", [])
                validation_warnings = result.get("validation_warnings", [])
                plan_warning = result.get("plan_warning")
                skipped_keys = result.get("skipped_keys", 0)
                
                print(f"\n📄 {file_path}")
                
                # Display plan limit warning if strings were skipped
                if plan_warning:
                    print(f"  ⚠️  Plan Limit Warning:")
                    print(f"     {plan_warning}")
                    if skipped_keys > 0:
                        print(f"     {skipped_keys} string(s) were skipped due to plan limits.")
                
                if validation_errors:
                    print(f"  ❌ Validation Errors ({len(validation_errors)}):")
                    for error in validation_errors:
                        print(format_validation_issue(error))
                
                if validation_warnings:
                    print(f"  ⚠️  Validation Warnings ({len(validation_warnings)}):")
                    for warning in validation_warnings:
                        print(format_validation_issue(warning))
            
            print("\n" + "="*70)
        else:
            # All files uploaded successfully with no validation issues
            print(f"\n✅ Successfully uploaded {len(upload_results)} file(s) with no validation issues.")
    
    # Exit with error code if there were any validation errors
    if has_any_validation_errors:
        if bypass_validation:
            print("\n⚠️  --bypass-validation flag is set - continuing despite validation errors")
        else:
            print("\n❌ File upload completed but validation errors were found. For detailed information about validation errors and how to resolve them, see our Validation Errors documentation: https://www.gettranslated.ai/developers/validation-errors/")
            print("\nFix these issues and try again, or run with --bypass-validation to continue anyway.")
            sys.exit(1)
    
    if is_first_sync:
        handle_upload_translations(working_dir, file_list, token, force)


def run_download_mode(working_dir, file_list, token):
    """Handle download mode operations."""
    print("Beginning download...")
    for fileset in file_list["files"]:
        sync(working_dir, fileset, token)


def check_languages_configured(file_list):
    """
    Check if languages are configured for the project.
    
    Args:
        file_list: The file list response from the server
    
    Returns:
        bool: True if languages are configured, False otherwise
    
    Exits with error code 1 if no languages are configured.
    """
    configured_languages = file_list.get("languages", [])
    if not configured_languages:
        project_slug = file_list.get("slug", "")
        if project_slug:
            settings_url = f"{SERVER}/home/project/{project_slug}/edit/"
        else:
            settings_url = f"{SERVER}/home/"
        
        print()
        print("⚠️  No languages are configured for this project.")
        print(f"   You can configure languages in your project settings. Visit {settings_url}")
        print()
        print(f"   For more information, see:")
        print(f"   {SERVER}/developers/cli-quickstart/#first-sync")
        print()
        sys.exit(1)
    return True


def run_translate_mode(token):
    """Handle translate mode operations."""
    print("Beginning translation...")
    translate(token)


def get_token_with_prompt(args, working_dir):
    """
    Get API token from various sources in order of precedence, with prompting if not found.
    
    Order: --key flag -> .gettranslated file -> GETTRANSLATED_KEY env var -> prompt
    
    Args:
        args: Command line arguments
        working_dir: Working directory path
    
    Returns:
        str: API token (never None - will prompt if needed)
    """
    # Try to get token using standard resolution
    token = get_token(args, working_dir)
    
    # If token found, return it (strip whitespace for consistency)
    if token:
        return token.strip()
    
    # If no token found, prompt the user with masked input
    print("Please enter your Server API Key:")
    print("(You can find this in your project settings)")
    print()
    token = getpass.getpass("API Key: ").strip()
    
    if not token:
        print("❌ API key is required.")
        sys.exit(1)
    
    return token


def read_config_file(working_dir):
    """Read the .gettranslated config file if it exists."""
    config_path = os.path.join(working_dir, CONFIG_FILENAME)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except (IOError, OSError, UnicodeDecodeError):
            return None
    return None


def write_config_file(working_dir, token):
    """Write the API key to the .gettranslated config file."""
    config_path = os.path.join(working_dir, CONFIG_FILENAME)
    try:
        with open(config_path, "w", encoding="utf-8") as file:
            file.write(token)
        return True
    except (IOError, OSError) as e:
        print(f"❌ Error writing {CONFIG_FILENAME} file: {e}")
        return False


def get_file_list_for_init(token):
    """
    Get file list for init mode - shows error and returns None on failure.
    
    Args:
        token: API token
    
    Returns:
        dict: File list data if successful, None if error
    """
    url = f"{SERVER}/sync/file/list"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT_METADATA)
    except Exception as e:
        error_info = _handle_exception(e, "Fetching file list", print_and_exit=False)
        if error_info:
            print(error_info.get("error_message", "Unknown error"))
        return None

    # Check the response
    if response.status_code == 200:
        try:
            data = _parse_json_response(response, "Fetching file list")
            debug(json.dumps(data, indent=4))
            return data
        except Exception:
            return None
    else:
        error_info = _handle_http_error(response, "File list request")
        if error_info:
            print(error_info.get("error_message", "Unknown error"))
        return None


def run_init_mode(working_dir, args):
    """Handle init mode operations - link directory to GetTranslated project."""
    # Get token (with prompting if needed) - prompt happens first
    token = get_token_with_prompt(args, working_dir)
    
    # Now validate the key
    print("Validating API key...")
    file_list = get_file_list_for_init(token)
    
    if file_list is None:
        print()
        print(f"For help, see: {SERVER}/developers/cli-quickstart/#configure")
        sys.exit(1)
    
    print()
    
    # Extract project information
    project_name = file_list.get("name", "Unknown Project")
    platform = file_list.get("platform", "Unknown")
    base_language = file_list.get("base_language", "unknown")
    target_languages = file_list.get("languages", [])
    
    # Display project information
    print(f'Connected to project "{project_name}"')
    print(f"Platform: {platform}")
    print(f"Base language: {base_language}")
    
    if target_languages:
        languages_str = ", ".join(target_languages)
        print(f"Configured target languages: {languages_str}")
    else:
        print("Configured target languages: none configured yet")
    
    print()
    
    # Manage the .gettranslated file
    existing_key = read_config_file(working_dir)
    
    if existing_key is None:
        # No config file exists - ask if user wants to create one
        response = input(f"Save this API key to {CONFIG_FILENAME} so you don't have to enter it next time? (y/n): ").strip().lower()
        
        if response in ('y', 'yes'):
            if write_config_file(working_dir, token):
                print(f"✅ API key saved to {CONFIG_FILENAME}")
            else:
                print(f"⚠️  Could not save API key to {CONFIG_FILENAME}")
        else:
            print("Skipping API key save.")
    elif existing_key.strip() == token.strip():
        # Config file exists with same key - do nothing
        print("Existing API key matches. Nothing to update.")
    else:
        # Config file exists with different key - prompt to replace
        print("A different API key is already saved in .gettranslated.")
        response = input("Replace it? (y/n): ").strip().lower()
        
        if response in ('y', 'yes'):
            if write_config_file(working_dir, token):
                print(f"✅ API key updated in {CONFIG_FILENAME}")
            else:
                print(f"⚠️  Could not update API key in {CONFIG_FILENAME}")
        else:
            print("Keeping existing API key.")
    
    print()
    print("✅ Initialization complete!")
    print()
    print("You can now run commands like:")
    print("  translate sync")
    print("  translate upload")
    print()


def main():
    """
    Modes for running this script:
    * upload: Syncs project strings with your project
    * download: Downloads translated string resources to your project
    * translate: Translates any new or untranslated strings in your project
    * sync: Runs upload / translate / download in sequence
    * grammar: Runs a grammar check on your project strings

    API keys can be specified in a few different ways, in order of precedence:
    1. As a command line argument with -k or --key
    2. In a .gettranslated file in your project directory
    3. As an environment variable named GETTRANSLATED_KEY

    Server URL can be specified with -s or --server (default: https://www.gettranslated.ai)
    """

    # Import version for --version flag
    from . import __version__
    
    # command line parsing
    parser = ArgumentParser(
        formatter_class=CustomHelpFormatter,
        description="GetTranslated CLI - Sync translation files with GetTranslated.ai",
        prog="translate"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version number and exit"
    )
    parser.add_argument(
        "mode",
        nargs='?',
        help="Script mode(s). Can specify a single mode or comma-separated list:\n"
        "* upload (syncs project strings with your project)\n"
        "* download (syncs translated string resources to your project)\n"
        "* translate (translates any new or untranslated strings in your project)\n"
        "* sync (runs upload / translate / download in sequence)\n"
        "* grammar (runs a grammar check on your project strings)\n"
        "* validate (re-validates base strings and translations)\n"
        "* init (links current directory to a GetTranslated project)\n"
        "\n"
        "When multiple modes are specified, they execute in logical order:\n"
        "upload -> grammar -> translate -> download (regardless of input order)\n"
        "\n"
        "Examples:\n"
        "  translate upload                    # Single mode\n"
        "  translate upload,translate          # Multiple modes\n"
        "  translate download,upload,translate # Reordered: upload -> translate -> download",
    )
    parser.add_argument(
        "working_directory",
        nargs='?',
        default='.',
        help="Your main project directory (default: current directory)"
    )
    parser.add_argument(
        "-k", "--key", help="API key, if not specified by config file or environment variable"
    )
    parser.add_argument(
        "-v", "--verbose", help="Verbose output mode", action="store_true"
    )
    parser.add_argument(
        "-f", "--force", help="Force processing even if file hash matches last processed file", action="store_true"
    )
    parser.add_argument(
        "--bypass-validation", help="Bypass validation checks and continue despite validation errors", action="store_true"
    )
    parser.add_argument(
        "-s", "--server", help="Server URL (default: https://www.gettranslated.ai)", default="https://www.gettranslated.ai"
    )
    args = parser.parse_args()
    
    # Check if mode is required (not provided when --version is used)
    if args.mode is None:
        parser.error("the following arguments are required: mode")

    # Parse comma-separated modes
    valid_modes = {"upload", "download", "translate", "sync", "grammar", "validate", "init"}
    modes = [m.strip().lower() for m in args.mode.split(",")]
    
    # Validate all modes
    invalid_modes = [m for m in modes if m not in valid_modes]
    if invalid_modes:
        parser.error(f"invalid mode(s): {', '.join(invalid_modes)}. Valid modes are: {', '.join(sorted(valid_modes))}")
    
    # Check for init mode (cannot be combined with other modes)
    if "init" in modes and len(modes) > 1:
        parser.error("'init' mode cannot be combined with other modes")
    
    # Expand 'sync' mode into its component modes
    if "sync" in modes:
        modes.remove("sync")
        modes.extend(["upload", "translate", "download"])
        # Remove duplicates while preserving order
        seen = set()
        modes = [m for m in modes if not (m in seen or seen.add(m))]

    # Normalize server URL (remove trailing slash if present)
    global SERVER, DEBUG
    SERVER = args.server.rstrip('/')
    DEBUG = args.verbose

    working_dir = os.path.abspath(args.working_directory)
    if not os.path.exists(working_dir):
        print(f"❌ Directory {working_dir} does not exist")
        sys.exit(1)

    # Handle init mode separately (it doesn't need token validation upfront)
    if "init" in modes:
        run_init_mode(working_dir, args)
        return

    token = get_token(args, working_dir)
    if not token or not token.strip():
        print("❌ No API key found.")
        print()
        print("Quick setup options:")
        print("  1. Run with -k flag: translate sync -k YOUR_KEY")
        print(f"  2. Set environment: export {ENV_KEY}=YOUR_KEY")
        print(f"  3. Create config file: echo 'YOUR_KEY' > {CONFIG_FILENAME}")
        print()
        print("Get your API key from your project settings")
        sys.exit(1)
    
    # Normalize token (remove any extra whitespace)
    token = token.strip()

    file_list = get_file_list(token)
    print(f"Connected to project {file_list['name']}")

    is_first_sync = file_list.get("is_first_sync", False)

    # Execute modes in logical order (regardless of input order)
    if "upload" in modes:
        run_upload_mode(working_dir, file_list, token, args.force, is_first_sync, args.bypass_validation)
        # Refresh file list after upload in case it changed
        file_list = get_file_list(token)

    if "grammar" in modes:
        print("Beginning grammar check...")
        grammar_check(token)

    if "translate" in modes:
        check_languages_configured(file_list)
        run_translate_mode(token)

    if "validate" in modes:
        print("Beginning translation validation...")
        run_validate_mode(token, force=args.force, working_dir=working_dir, file_list=file_list)

    if "download" in modes:
        check_languages_configured(file_list)
        run_download_mode(working_dir, file_list, token)

    print("✅ Done!")


if __name__ == "__main__":
    main()

