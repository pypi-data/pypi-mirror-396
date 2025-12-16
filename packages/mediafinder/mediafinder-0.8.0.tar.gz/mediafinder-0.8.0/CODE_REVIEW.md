# Code Review: mf (mediafinder)

**Review Date**: 2025-12-10
**Reviewer**: Claude Code
**Scope**: Complete codebase analysis

---

## Priority Rankings

Issues are ranked by:
- **CRITICAL**: Bugs, security vulnerabilities, data loss risks
- **HIGH**: Significant architectural issues, major maintainability problems
- **MEDIUM**: Code quality issues, performance problems, missing tests
- **LOW**: Minor improvements, documentation gaps, style issues

---

## CRITICAL Priority

### 1. String Formatting Bug in IMDB Error Message ✔
**File**: `src/mf/utils/misc.py:68`
**Severity**: CRITICAL (Broken functionality)

```python
print_and_raise("No IMDB results found for parsed title {title}.")
```

**Issue**: Missing `f` prefix on f-string. Error message displays literal `{title}` instead of the variable value.

**Impact**: Users see confusing error message: "No IMDB results found for parsed title {title}."

**Fix**:
```python
print_and_raise(f"No IMDB results found for parsed title {title}.")
```

---

## HIGH Priority

### 2. Complex Progress Bar Function with Duplicated Code ✔
**File**: `src/mf/utils/scan.py:107-223`
**Severity**: HIGH (Maintainability)

**Issue**: The `_scan_with_progress_bar()` function has 117 lines with duplicated future-checking logic appearing 3 times (lines 137-145, 175-182, 212-219):

```python
# This pattern appears 3 times:
done_futures = []
for future in remaining_futures:
    if future.done():
        path_results.append(future.result())
        done_futures.append(future)

for future in done_futures:
    remaining_futures.remove(future)  # Also O(n²) performance issue
```

**Impact**:
- Hard to maintain (bug fixes need 3 places)
- Performance issue: `list.remove()` in loop is O(n²)
- Difficult to test individual branches

**Recommendation**: Extract future-checking to helper function:
```python
def _process_completed_futures(futures: list[Future]) -> tuple[FileResults, list[Future]]:
    """Check futures, collect completed results, return remaining."""
    completed_results = FileResults()
    remaining = []

    for future in futures:
        if future.done():
            completed_results.append(future.result())
        else:
            remaining.append(future)

    return completed_results, remaining
```

---

### 3. Global Config Cache Without Invalidation
**File**: `src/mf/utils/config.py:25, 69-74`
**Severity**: HIGH (Architecture)

**Issue**: Global mutable singleton with no way to refresh:

```python
_config = None

def read_config() -> TOMLDocument:
    global _config
    if _config is None:
        _config = _read_config()
    return _config
```

**Impact**:
- Tests must manually manage global state
- Config file changes during execution not reflected
- Hidden coupling throughout codebase
- Makes testing harder

**Recommendation**: Add cache invalidation:
```python
def _clear_config_cache():
    """Clear cached config (primarily for testing)."""
    global _config
    _config = None

def reload_config():
    """Force reload config from disk."""
    _clear_config_cache()
    return read_config()
```

Or use a Config class with explicit instance management.

---

### 4. Circular Import Workaround - WONTFIX, not actually a problem
**File**: `src/mf/utils/settings.py:25-31`
**Severity**: HIGH (Architecture)

**Issue**: Lazy imports to avoid circular dependency:

```python
def _rebuild_cache_if_enabled():
    # Helper function with lazy imports to avoid circular import
    from .cache import rebuild_library_cache
    from .config import read_config
```

**Impact**:
- Indicates architectural smell
- Fragile dependency structure
- Could break if imports reorganized

**Recommendation**: Restructure to break circular dependency:
- Move cache rebuild trigger to a separate module
- Or use dependency injection pattern
- Or make `after_update` hooks accept a callback

---

### 5. JSON Schema Validation Missing
**Files**: `src/mf/utils/cache.py:99-108`, `src/mf/utils/search.py:77-82`
**Severity**: HIGH (Security/Robustness)

**Issue**: Cache files are loaded without validation:

```python
with open_utf8(get_library_cache_file()) as f:
    cache_data: CacheData = json.load(f)  # No validation!
```

**Impact**:
- Maliciously modified cache files could:
  - Contain invalid paths
  - Cause DoS with deeply nested structures
  - Crash the application
- Type hint `CacheData` isn't enforced

**Recommendation**: Add schema validation:
```python
def _validate_cache_data(data: dict) -> CacheData:
    """Validate cache structure and types."""
    if not isinstance(data, dict):
        raise ValueError("Cache must be a dictionary")

    required_keys = {"timestamp", "files"}
    if not required_keys.issubset(data.keys()):
        raise ValueError(f"Cache missing required keys: {required_keys - data.keys()}")

    if not isinstance(data["files"], list):
        raise ValueError("Cache 'files' must be a list")

    return data  # Or use pydantic/dataclasses for stronger typing
```

---

### 6. Overly Complex Scanner Selection Logic ✔
**File**: `src/mf/utils/scan.py:24-104`
**Severity**: HIGH (Code Quality)

**Issue**: 81-line function with 5+ levels of conditional nesting for choosing between fd/Python scanners

**Impact**:
- Hard to follow control flow
- Difficult to add new scanner types
- Hard to test all branches

**Recommendation**: Use strategy pattern:
```python
class ScanStrategy(ABC):
    @abstractmethod
    def scan(self, paths: list[Path]) -> FileResults:
        ...

class FdScanStrategy(ScanStrategy):
    def scan(self, paths: list[Path]) -> FileResults:
        # fd scanning logic
        ...

class PythonScanStrategy(ScanStrategy):
    def scan(self, paths: list[Path]) -> FileResults:
        # Python scanning logic with optional progress
        ...

def get_scan_strategy(prefer_fd: bool, need_mtime: bool, show_progress: bool) -> ScanStrategy:
    """Select appropriate scanning strategy."""
    if prefer_fd and not need_mtime:
        try:
            return FdScanStrategy()
        except RuntimeError:
            pass  # Fall through to Python

    return PythonScanStrategy(with_mtime=need_mtime, show_progress=show_progress)
```

---

## MEDIUM Priority

### 7. Type Hint Inaccuracies ✔
**Files**: `src/mf/utils/scan.py:107`, `src/mf/utils/stats.py:19`
**Severity**: MEDIUM (Code Quality)

**Issues**:

1. `_scan_with_progress_bar()` parameter:
```python
def _scan_with_progress_bar(
    futures: list,  # Should be list[Future]
    # ...
)
```

2. `show_histogram()` sort_key signature:
```python
sort_key: Callable[[str], Any] | None = None,  # Misleading
# Actually used with: sorted(bins, key=sort_key, ...)
# Where bins is list[tuple[str, int]]
```

**Recommendation**:
```python
from concurrent.futures import Future
from typing import TypeAlias

BinData: TypeAlias = tuple[str, int]

def _scan_with_progress_bar(
    futures: list[Future],
    estimated_total: int | None,
    progress_counter: ProgressCounter,
) -> FileResults:
    # ...

def show_histogram(
    bins: list[BinData],
    title: str,
    # ...
    sort_key: Callable[[BinData], Any] | None = None,
):
    # ...
```

---

### 8. Overly Broad Exception Handling ✔
**Files**: `src/mf/version.py:24`, `src/mf/utils/scan.py:58-65`
**Severity**: MEDIUM (Error Handling)

**Issue 1**: Version check catches all exceptions:
```python
except Exception as e:
    print_and_raise(f"Version check failed with error: {e}", raise_from=e)
```

**Issue 2**: fd scanner fallback catches redundant exceptions:
```python
except (
    FileNotFoundError,
    subprocess.CalledProcessError,
    OSError,  # PermissionError is subclass of OSError
    PermissionError,  # Redundant!
):
```

**Recommendation**:
```python
# version.py
try:
    with request.urlopen(url, timeout=5) as response:
        data = json.loads(response.read().decode())
        return Version(data["info"]["version"])
except urllib.error.URLError as e:
    print_and_raise(f"Network error checking version: {e}")
except json.JSONDecodeError as e:
    print_and_raise(f"Invalid response from PyPI: {e}")
except KeyError as e:
    print_and_raise(f"Unexpected PyPI API response format: {e}")

# scan.py
except (FileNotFoundError, subprocess.CalledProcessError, OSError):
    # PermissionError removed (it's an OSError subclass)
    partial_fd_scanner = partial(scan_path_with_python, with_mtime=False)
```

---

### 9. Silent Error Suppression in Directory Scanning - WONTFIX (is wrong)
**File**: `src/mf/utils/scan.py:297-298`
**Severity**: MEDIUM (Error Handling)

**Issue**: Permission errors are silently skipped:

```python
except PermissionError:
    print_warn(f"Missing access permissions for directory {path}, skipping.")
```

**Impact**: If an entire branch is inaccessible, user gets no summary of missing data

**Recommendation**: Track and report skipped directories:
```python
def scan_path_with_python(
    search_path: Path,
    with_mtime: bool = False,
    progress_callback: Callable[[FileResult], None] | None = None,
) -> tuple[FileResults, list[Path]]:  # Return skipped paths too
    """..."""
    results = FileResults()
    skipped_dirs = []

    def scan_dir(path: str):
        try:
            # ... existing logic
        except PermissionError:
            skipped_dirs.append(Path(path))
            print_warn(f"Missing access permissions for directory {path}, skipping.")

    scan_dir(str(search_path))

    if skipped_dirs:
        console.print(f"[yellow]Skipped {len(skipped_dirs)} inaccessible directories[/yellow]")

    return results, skipped_dirs
```

---

### 10. Duplicated Config Action Handlers
**File**: `src/mf/cli_config.py:56-85`
**Severity**: MEDIUM (Code Quality)

**Issue**: Nearly identical functions for set/add/remove:

```python
def set(key: str, values: list[str]):
    cfg = read_config()
    cfg = apply_action(cfg, key, "set", values)
    write_config(cfg)

def add(key: str, values: list[str]):
    cfg = read_config()
    cfg = apply_action(cfg, key, "add", values)
    write_config(cfg)

def remove(key: str, values: list[str]):
    cfg = read_config()
    cfg = apply_action(cfg, key, "remove", values)
    write_config(cfg)
```

**Recommendation**: Could be unified but Typer requires separate commands. At minimum, extract common logic:

```python
def _update_config(key: str, action: Action, values: list[str] | None):
    """Common config update logic."""
    cfg = read_config()
    cfg = apply_action(cfg, key, action, values)
    write_config(cfg)

@app_config.command()
def set(key: str, values: list[str]):
    """Set a setting."""
    _update_config(key, "set", values)

@app_config.command()
def add(key: str, values: list[str]):
    """Add value(s) to a list setting."""
    _update_config(key, "add", values)
```

---

### 11. Inefficient List Operations in Loops ✔
**File**: `src/mf/utils/scan.py:144-145, 181-182, 218-219`
**Severity**: MEDIUM (Performance)

**Issue**: Removing items from list during iteration is O(n²):

```python
for future in done_futures:
    remaining_futures.remove(future)  # O(n) operation in O(n) loop
```

**Impact**: For large file collections with many futures, this becomes slow

**Recommendation**:
```python
# Instead of removing, rebuild list:
remaining_futures = [f for f in remaining_futures if not f.done()]
```

---

### 12. Missing Edge Case Handling in fd Output
**File**: `src/mf/utils/scan.py:255-259`
**Severity**: MEDIUM (Robustness)

**Issue**: fd output is split and used without validation:

```python
for line in result.stdout.strip().split("\n"):
    if line:
        files.append(FileResult(Path(line)))
```

**Impact**:
- Empty lines silently ignored (ok)
- Invalid paths could crash
- Encoding issues not handled

**Recommendation**:
```python
for line in result.stdout.strip().split("\n"):
    if not line:
        continue

    try:
        path = Path(line)
        if not path.is_absolute():
            print_warn(f"fd returned non-absolute path: {line}")
            continue
        files.append(FileResult(path))
    except Exception as e:
        print_warn(f"Invalid path from fd: {line} ({e})")
```

---

### 13. Inefficient Progress Bar Polling - WONTFIX (doesn't work with current implementation, file i/o is slower anyway)
**File**: `src/mf/utils/scan.py:152, 202, 221`
**Severity**: MEDIUM (Performance)

**Issue**: Hardcoded 100ms polling interval:

```python
time.sleep(0.1)  # Why 100ms?
```

**Impact**: Arbitrary delay that's either too fast (CPU waste) or too slow (laggy UI)

**Recommendation**: Use `concurrent.futures.as_completed()`:

```python
from concurrent.futures import as_completed

# Instead of polling:
for future in as_completed(futures):
    path_results.append(future.result())
    current_count = progress_counter.count
    # Update progress bar
```

---

### 14. Cache Rebuild Triggers Multiple Times - WONTFIX (expected behaviour)
**File**: `src/mf/utils/settings.py:77, 127`
**Severity**: MEDIUM (Performance)

**Issue**: If user runs multiple config updates, cache rebuilds after each:

```bash
mf config set search_paths /a  # Rebuilds cache
mf config set search_paths /b  # Rebuilds cache again
```

**Impact**: Unnecessary work on large collections

**Recommendation**:
- Document behavior
- Or batch config updates: `mf config set search_paths /a /b`
- Or defer rebuild: `mf config set --no-rebuild search_paths /a`

---

## LOW Priority

### 15. Magic Numbers Not Documented ✔
**Files**: Multiple
**Severity**: LOW (Maintainability)

**Examples**:
- `src/mf/utils/scan.py:169`: `update_threshold = max(1, estimated_total // 20)` - Why 20?
- `src/mf/utils/stats.py:61`: `max_bar_panel_width = 50` - Why 50?
- `src/mf/cli_main.py:58`: Default of 20 for `new` command
- `src/mf/utils/misc.py:109`: Binary (1024) vs SI (1000) for file sizes

**Recommendation**: Extract to constants with explanatory names:

```python
# constants.py
PROGRESS_UPDATE_FREQUENCY = 20  # Update every 5% (100/20)
HISTOGRAM_MAX_WIDTH = 50  # Terminal width for histogram bars
DEFAULT_NEWEST_COUNT = 20  # Default number of files for 'mf new'
FILE_SIZE_BINARY_UNIT = 1024  # Use binary (Ki/Mi/Gi) not SI (k/M/G)
FUTURE_POLL_INTERVAL_MS = 100  # Milliseconds between checking futures
```

---

### 16. Hardcoded VLC Paths
**File**: `src/mf/utils/misc.py:132-135`
**Severity**: LOW (Portability)

**Issue**: Only checks 2 Windows paths:

```python
vlc_paths = [
    r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
]
```

**Missing**:
- Windows Store installation
- Portable VLC
- Custom install locations

**Recommendation**: Check Windows registry or add more paths:

```python
def _get_windows_vlc_path() -> str | None:
    """Try to find VLC on Windows."""
    # Common installation paths
    paths = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "VideoLAN" / "VLC" / "vlc.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "VideoLAN" / "VLC" / "vlc.exe",
        Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps" / "vlc.exe",  # Store
    ]

    for path in paths:
        if path.exists():
            return str(path)

    return None
```

---

### 17. Typo in Setting Help Text ✔
**File**: `src/mf/utils/settings.py:138`
**Severity**: LOW (Documentation)

**Issue**: Missing space in help text:

```python
"Set to 0 to turn off automaticcache rebuilding."
#                             ^^^ missing space
```

**Fix**:
```python
"Set to 0 to turn off automatic cache rebuilding."
```

---

### 18. Missing Docstring Examples - WONTFIX (self explanatory)
**File**: `src/mf/utils/normalizers.py`
**Severity**: LOW (Documentation)

**Issue**: Normalization functions lack examples

**Recommendation**: Add doctest examples:

```python
def normalize_pattern(pattern: str) -> str:
    """Normalize a search pattern.

    Wraps patterns without glob characters with wildcards.

    Args:
        pattern: Raw pattern (may lack wildcards).

    Returns:
        Pattern wrapped with * on both sides if no glob characters found.

    Examples:
        >>> normalize_pattern("batman")
        '*batman*'
        >>> normalize_pattern("*.mkv")
        '*.mkv'
        >>> normalize_pattern("s01e??")
        's01e??'
    """
    if not any(ch in pattern for ch in ["*", "?", "[", "]"]):
        return f"*{pattern}*"
    return pattern
```

---

### 19. Missing main() Docstring ✔
**File**: `src/mf/__init__.py:15-16`
**Severity**: LOW (Documentation)

**Issue**: Entry point lacks documentation:

```python
def main():
    app_mf()
```

**Recommendation**:
```python
def main():
    """Main entry point for the mf CLI application.

    This function is called when the package is executed as a script
    or via the installed console script 'mf' or 'mediafinder'.
    """
    app_mf()
```

---

### 20. Inconsistent Path Format - WONTFIX (is consistent and intentional)
**File**: `src/mf/utils/file.py:135-138`
**Severity**: LOW (UX)

**Issue**: Always uses POSIX format even on Windows:

```python
return (
    self.file.as_posix()
    if self.file.is_absolute()
    else self.file.resolve().as_posix()
)
```

**Impact**: Windows users see forward slashes everywhere

**Discussion**: This might be intentional (consistency), but worth documenting the choice.

---

### 21. No Symlink Cycle Protection
**File**: `src/mf/utils/scan.py:284, 295`
**Severity**: LOW (Robustness)

**Issue**: Scanner uses `follow_symlinks=False` but doesn't detect cycles:

```python
if entry.is_file(follow_symlinks=False):
    # ...
elif entry.is_dir(follow_symlinks=False):
    scan_dir(entry.path)  # Could infinitely recurse on symlink cycle
```

**Impact**: Symlink cycles could cause infinite recursion

**Recommendation**: Track visited inodes or add max depth limit

---

### 22. No Duplicate File Detection - WONTFIX
**Severity**: LOW (Feature Gap)

**Issue**: Same file in multiple search paths appears multiple times in results

**Impact**: Confusing for users with overlapping search paths

**Recommendation**: Optional deduplication by inode (Unix) or hash (Windows)

---

### 23. Editor Selection Inconsistency - WONTFIX (don't see the point)
**File**: `src/mf/utils/misc.py:34-45`
**Severity**: LOW (UX)

**Issue**: Windows tries Notepad++, then Notepad. Unix tries nano, vim, vi. No consistent priority.

**Recommendation**: Standardize priority:
1. `$VISUAL` / `$EDITOR`
2. VSCode (cross-platform, common)
3. nano / Notepad (beginner-friendly)
4. vim / vi (power user)

---

## Testing Gaps

### 24. Missing Edge Case Tests
**Severity**: MEDIUM

**Not tested**:
- Empty search paths configuration
- Very large collections (1000s of files)
- Symlinks in search paths
- Special characters in filenames (Unicode, spaces, etc.)
- Cache corruption recovery
- Concurrent cache access
- VLC not installed scenarios
- Network timeouts in version check
- fd binary permissions issues

**Recommendation**: Add systematic edge case testing

---

### 25. Missing Integration Tests ✔
**Severity**: MEDIUM

**Issue**: `play()` command has 12+ code paths but sparse testing

**Recommendation**: Test matrix:
- target: None | "next" | "list" | valid_index | invalid_index
- VLC: present | absent
- Cache: valid | empty | corrupted
- Files: exist | deleted

---

## Summary Statistics

| Priority | Count | Categories |
|----------|-------|------------|
| CRITICAL | 1 | Bugs |
| HIGH | 6 | Architecture, Security, Maintainability |
| MEDIUM | 14 | Code Quality, Performance, Error Handling |
| LOW | 11 | Documentation, Minor UX, Edge Cases |
| **TOTAL** | **32** | |

---

## Quick Wins (High Impact, Low Effort)

1. **Fix f-string bug** (misc.py:68) - 1 character fix
2. **Add docstring to main()** - 2 minutes
3. **Fix typo** in settings help text - 10 seconds
4. **Remove redundant PermissionError** from exception tuple - 1 line
5. **Add config cache invalidation function** - 5 lines

---

## Recommended Next Steps

1. **Immediate**: Fix the f-string bug (CRITICAL)
2. **This week**: Address HIGH priority issues (6 items)
3. **This month**: Tackle MEDIUM priority refactors
4. **Ongoing**: Add edge case tests as bugs are discovered
5. **Future**: Consider LOW priority improvements during regular maintenance

---

*End of Code Review*
