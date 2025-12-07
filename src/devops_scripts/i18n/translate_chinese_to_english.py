"""
Translate Chinese comments and log messages to English in Python files.

This script scans all .py files under the src directory and translates
Chinese comments and log messages to English using LLM, while preserving
all code logic unchanged.

CRITICAL RULES:
    1. DO NOT modify any code logic - this is the most important rule
    2. Only translate Chinese comments and Chinese log messages
    3. Never change variable names, function names, class names, etc.
    4. Never change any code structure or behavior
    5. Violations of these rules are STRICTLY FORBIDDEN

Usage:
    python -m devops_scripts.i18n.translate_chinese_to_english
    python -m devops_scripts.i18n.translate_chinese_to_english --dry-run
    python -m devops_scripts.i18n.translate_chinese_to_english --max-concurrency 5
    python -m devops_scripts.i18n.translate_chinese_to_english --check  # Check for remaining Chinese
"""

import os
import sys
import re
import asyncio
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add src to path for imports
SRC_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SRC_DIR))

# Load environment variables first
from dotenv import load_dotenv
from common_utils.project_path import PROJECT_DIR

env_file_path = PROJECT_DIR / ".env"
if env_file_path.exists():
    load_dotenv(env_file_path)
    print(f"Loaded environment from {env_file_path}")

# Progress file to track which files have been processed
PROGRESS_FILE = Path(__file__).parent / ".translation_progress.json"
# Maximum file size to process (in bytes) - about 100KB
MAX_FILE_SIZE = 100 * 1024

# Directories to skip (relative to SRC_DIR)
# These directories contain content that should not be auto-translated (e.g., prompt templates)
SKIP_DIRECTORIES = ["memory_layer/prompts"]

# Files to skip (relative to SRC_DIR)
# These files contain Chinese text that is business logic or example data, not comments
SKIP_FILES = [
    # Chinese date text mapping for business logic
    "memory_layer/memory_extractor/profile_memory/conversation.py",
    # Contains Chinese examples in docstring
    "common_utils/text_utils.py",
    # Contains Chinese tokenization examples in comments
    "core/oxm/es/analyzer.py",
    # Contains Chinese skill level examples in comments (e.g., "高级")
    "memory_layer/memory_extractor/profile_memory/types.py",
    # Contains Chinese value mapping for skill levels
    "memory_layer/memory_extractor/profile_memory/value_helpers.py",
]

from memory_layer.llm import OpenAIProvider


# Translation prompt template - emphasizes NOT modifying code logic
TRANSLATION_PROMPT = '''You are a translation assistant. Your task is to translate Chinese comments and Chinese log messages in Python code to English.

**CRITICAL RULES - MUST FOLLOW:**
1. **ABSOLUTELY DO NOT modify any code logic** - This is the most important rule. Violations are STRICTLY FORBIDDEN.
2. **ONLY translate Chinese text** in:
   - Single-line comments (# ...)
   - Multi-line docstrings (""" ... """ or \'\'\' ... \'\'\')
   - String literals used in logging (logger.info(), logger.debug(), logger.warning(), logger.error(), print(), etc.)
   - f-string literals used in logging
3. **DO NOT change:**
   - Variable names, function names, class names
   - Code structure, indentation, line breaks
   - Any Python syntax or operators
   - Non-Chinese text
   - Import statements
   - Type hints
   - Any actual code behavior
4. Keep the original formatting and indentation exactly as is
5. If there is no Chinese text to translate, return the code unchanged
6. Return ONLY the translated code, no explanations

**Example translations:**
- `# 初始化配置` → `# Initialize configuration`
- `logger.info("开始处理数据")` → `logger.info("Start processing data")`
- `"""这是一个测试函数"""` → `"""This is a test function"""`
- `print(f"处理完成，共 {{count}} 条")` → `print(f"Processing completed, total {{count}} items")`

Now translate the following Python code:

```python
{code}
```

Return the translated Python code:'''


def contains_chinese(text: str) -> bool:
    """Check if text contains Chinese characters."""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_pattern.search(text))


def should_skip_directory(dir_path: Path, src_dir: Path) -> bool:
    """Check if a directory should be skipped based on SKIP_DIRECTORIES config."""
    try:
        rel_path = dir_path.relative_to(src_dir)
        rel_path_str = str(rel_path).replace('\\', '/')
        for skip_dir in SKIP_DIRECTORIES:
            # Check if the directory path starts with or equals the skip directory
            if rel_path_str == skip_dir or rel_path_str.startswith(skip_dir + '/'):
                return True
    except ValueError:
        pass
    return False


def should_skip_file(file_path: Path, src_dir: Path) -> bool:
    """Check if a file should be skipped based on SKIP_FILES config."""
    try:
        rel_path = file_path.relative_to(src_dir)
        rel_path_str = str(rel_path).replace('\\', '/')
        return rel_path_str in SKIP_FILES
    except ValueError:
        pass
    return False


def get_all_python_files(src_dir: Path) -> list[Path]:
    """Get all Python files under the src directory."""
    python_files = []
    skipped_dirs = []
    skipped_files = []
    for root, dirs, files in os.walk(src_dir):
        root_path = Path(root)

        # Skip __pycache__ and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        # Skip configured directories
        dirs_to_remove = []
        for d in dirs:
            dir_path = root_path / d
            if should_skip_directory(dir_path, src_dir):
                dirs_to_remove.append(d)
                skipped_dirs.append(dir_path)
        for d in dirs_to_remove:
            dirs.remove(d)

        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                # Skip configured files
                if should_skip_file(file_path, src_dir):
                    skipped_files.append(file_path)
                else:
                    python_files.append(file_path)

    if skipped_dirs:
        print(f"Skipped directories: {[str(d) for d in skipped_dirs]}")
    if skipped_files:
        print(f"Skipped files: {[str(f) for f in skipped_files]}")

    return python_files


def filter_files_with_chinese(
    python_files: list[Path], progress: dict
) -> tuple[list[Path], int, int]:
    """
    Pre-filter files to only include those with Chinese characters.

    Always re-check file content regardless of progress status to ensure
    files with remaining Chinese are not skipped.

    Args:
        python_files: List of Python file paths
        progress: Progress dict to check already processed files

    Returns:
        Tuple of (files_to_process, skipped_no_chinese, skipped_already_done)
    """
    files_to_process = []
    skipped_no_chinese = 0
    skipped_already_done = 0

    print("Pre-scanning files for Chinese content...")
    for file_path in python_files:
        file_str = str(file_path)

        try:
            # Check file size first
            file_size = file_path.stat().st_size
            if file_size > MAX_FILE_SIZE:
                # Large files will be handled separately
                if file_str not in progress.get("processed", []):
                    files_to_process.append(file_path)
                else:
                    skipped_already_done += 1
                continue

            # Read and check for Chinese - always check regardless of progress
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if contains_chinese(content):
                # File has Chinese, need to process (even if previously marked as done)
                if file_str in progress.get("processed", []):
                    # Remove from processed list since it still has Chinese
                    progress["processed"].remove(file_str)
                    print(f"  [RE-PROCESS] {file_path} - Still has Chinese content")
                files_to_process.append(file_path)
            else:
                skipped_no_chinese += 1
                # Mark as processed since no Chinese
                if file_str not in progress.get("processed", []):
                    progress["processed"].append(file_str)
                else:
                    skipped_already_done += 1
        except Exception as e:
            # If we can't read the file, include it for processing
            print(f"  Warning: Could not pre-scan {file_path}: {e}")
            files_to_process.append(file_path)

    # Save progress after pre-scan
    save_progress(progress)
    print(
        f"Pre-scan complete: {len(files_to_process)} files with Chinese to translate, "
        f"{skipped_no_chinese} without Chinese (skipped), {skipped_already_done} already done (no Chinese)"
    )

    return files_to_process, skipped_no_chinese, skipped_already_done


def check_chinese_in_files(
    src_dir: Path, specific_files: list[str] | None = None
) -> int:
    """
    Check all Python files for remaining Chinese characters.

    Args:
        src_dir: Source directory to scan
        specific_files: Optional list of specific file paths to check

    Returns:
        Number of files that still contain Chinese characters
    """
    print("=" * 60)
    print("Chinese Content Check Mode")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # Get files to check
    if specific_files:
        python_files = [Path(f) for f in specific_files]
    else:
        python_files = get_all_python_files(src_dir)

    python_files.sort()
    total_files = len(python_files)
    print(f"Scanning {total_files} Python files for Chinese content...")
    print()

    files_with_chinese = []
    files_checked = 0

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            files_checked += 1

            if contains_chinese(content):
                # Find lines with Chinese for detailed report
                lines_with_chinese = []
                for line_num, line in enumerate(content.split('\n'), 1):
                    if contains_chinese(line):
                        lines_with_chinese.append((line_num, line.strip()[:80]))

                files_with_chinese.append(
                    {
                        'path': file_path,
                        'lines': lines_with_chinese,
                        'total_chinese_lines': len(lines_with_chinese),
                    }
                )

        except Exception as e:
            print(f"  [ERROR] Could not read {file_path}: {e}")

    # Print results
    print("=" * 60)
    print("Check Results")
    print("=" * 60)
    print(f"Total files checked: {files_checked}")
    print(f"Files with Chinese: {len(files_with_chinese)}")
    print()

    if files_with_chinese:
        print("Files containing Chinese characters:")
        print("-" * 60)
        for file_info in files_with_chinese:
            print(f"\n📄 {file_info['path']}")
            print(f"   ({file_info['total_chinese_lines']} lines with Chinese)")
            # Show first 5 lines as examples
            for line_num, line_content in file_info['lines'][:5]:
                print(f"   Line {line_num}: {line_content}...")
            if len(file_info['lines']) > 5:
                print(f"   ... and {len(file_info['lines']) - 5} more lines")
        print()
        print("-" * 60)
        print(f"❌ Found {len(files_with_chinese)} files with Chinese content")
        print("   Run without --check to translate them")
    else:
        print("✅ No Chinese content found in any Python files!")

    return len(files_with_chinese)


def load_progress() -> dict:
    """Load progress from file."""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"processed": [], "errors": []}
    return {"processed": [], "errors": []}


def save_progress(progress: dict):
    """Save progress to file."""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def clear_progress():
    """Clear progress file."""
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()


async def translate_file(
    provider: OpenAIProvider,
    file_path: Path,
    semaphore: asyncio.Semaphore,
    progress: dict,
    progress_lock: asyncio.Lock,
    dry_run: bool = False,
    index: int = 0,
    total: int = 0,
) -> tuple[Path, bool, Optional[str]]:
    """
    Translate a single Python file.

    Args:
        provider: LLM provider
        file_path: Path to the Python file
        semaphore: Semaphore for concurrency control
        progress: Progress tracking dict
        progress_lock: Lock for thread-safe progress updates
        dry_run: If True, don't actually write changes
        index: Current file index (for progress display)
        total: Total number of files (for progress display)

    Returns:
        Tuple of (file_path, success, error_message)
    """
    file_str = str(file_path)
    progress_prefix = f"[{index}/{total}]" if total > 0 else ""

    # Skip if already processed (double check)
    if file_str in progress.get("processed", []):
        print(f"{progress_prefix} [ALREADY-DONE] {file_path}")
        return (file_path, True, None)

    async with semaphore:
        try:
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > MAX_FILE_SIZE:
                print(
                    f"{progress_prefix} [SKIP-LARGE] {file_path} - File too large ({file_size/1024:.1f}KB > {MAX_FILE_SIZE/1024:.1f}KB)"
                )
                async with progress_lock:
                    progress["processed"].append(file_str)
                    save_progress(progress)
                return (file_path, True, f"Skipped: file too large ({file_size} bytes)")

            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Double check for Chinese (should have been pre-filtered)
            if not contains_chinese(original_content):
                print(f"{progress_prefix} [SKIP] {file_path} - No Chinese text found")
                async with progress_lock:
                    progress["processed"].append(file_str)
                    save_progress(progress)
                return (file_path, True, None)

            print(
                f"{progress_prefix} [TRANSLATING] {file_path} ({file_size/1024:.1f}KB)"
            )

            # Call LLM for translation
            prompt = TRANSLATION_PROMPT.format(code=original_content)
            translated_content = await provider.generate(
                prompt, temperature=0.1  # Low temperature for consistent translation
            )

            # Clean up response (remove markdown code blocks if present)
            translated_content = translated_content.strip()
            if translated_content.startswith('```python'):
                translated_content = translated_content[9:]
            if translated_content.startswith('```'):
                translated_content = translated_content[3:]
            if translated_content.endswith('```'):
                translated_content = translated_content[:-3]
            translated_content = translated_content.strip()

            # Basic validation: ensure we still have valid Python-like content
            if (
                not translated_content
                or len(translated_content) < len(original_content) * 0.5
            ):
                error_msg = "Translation result seems too short or empty"
                async with progress_lock:
                    progress["errors"].append({"file": file_str, "error": error_msg})
                    save_progress(progress)
                return (file_path, False, error_msg)

            # Write back if not dry run
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(translated_content)
                print(f"{progress_prefix} [DONE] {file_path}")
            else:
                print(f"{progress_prefix} [DRY-RUN] {file_path} - Would translate")

            # Mark as processed with lock
            async with progress_lock:
                progress["processed"].append(file_str)
                save_progress(progress)
            return (file_path, True, None)

        except Exception as e:
            error_msg = str(e)
            print(f"{progress_prefix} [ERROR] {file_path}: {error_msg}")
            async with progress_lock:
                progress["errors"].append({"file": file_str, "error": error_msg})
                save_progress(progress)
            return (file_path, False, error_msg)


async def main(
    max_concurrency: int = 10,
    dry_run: bool = False,
    specific_files: list[str] | None = None,
    reset_progress: bool = False,
):
    """
    Main function to translate all Python files.

    Args:
        max_concurrency: Maximum number of concurrent translations
        dry_run: If True, don't actually write changes
        specific_files: Optional list of specific file paths to translate
        reset_progress: If True, clear previous progress and start fresh
    """
    print("=" * 60)
    print("Chinese to English Translation Script")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    print("CRITICAL RULES:")
    print("  1. DO NOT modify any code logic")
    print("  2. Only translate Chinese comments and log messages")
    print("  3. Preserve all code structure and behavior")
    print()

    # Handle progress
    if reset_progress:
        clear_progress()
        print("Progress cleared, starting fresh")
    progress = load_progress()
    if progress.get("processed"):
        print(
            f"Resuming from previous run: {len(progress['processed'])} files already processed"
        )

    # Initialize LLM provider using environment variables
    provider = OpenAIProvider(
        model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0.1,
    )

    # Get files to process
    if specific_files:
        python_files = [Path(f) for f in specific_files]
    else:
        python_files = get_all_python_files(SRC_DIR)

    # Sort files for consistent ordering
    python_files.sort()

    total_files = len(python_files)
    print(f"Found {total_files} Python files in total")
    print(f"Max concurrency: {max_concurrency}")
    print(f"Max file size: {MAX_FILE_SIZE/1024:.1f}KB")
    print(f"Dry run: {dry_run}")
    print(f"Progress file: {PROGRESS_FILE}")
    print()

    # Pre-filter files to only process those with Chinese content
    files_to_process, skipped_no_chinese, skipped_already_done = (
        filter_files_with_chinese(python_files, progress)
    )

    if not files_to_process:
        print("No files with Chinese content to process!")
        return

    print()
    print(f"Files to translate: {len(files_to_process)}")
    print()

    # Create semaphore and lock for concurrency control
    semaphore = asyncio.Semaphore(max_concurrency)
    progress_lock = asyncio.Lock()

    # Create translation tasks with index for progress display
    tasks = [
        translate_file(
            provider,
            file_path,
            semaphore,
            progress,
            progress_lock,
            dry_run,
            index=idx + 1,
            total=len(files_to_process),
        )
        for idx, file_path in enumerate(files_to_process)
    ]

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Summarize results
    success_count = 0
    error_count = 0
    errors = []

    for result in results:
        if isinstance(result, Exception):
            error_count += 1
            errors.append(str(result))
        else:
            file_path, success, error_msg = result
            if success:
                success_count += 1
            else:
                error_count += 1
                errors.append(f"{file_path}: {error_msg}")

    print()
    print("=" * 60)
    print("Summary")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"Total Python files found: {total_files}")
    print(f"Files skipped (no Chinese): {skipped_no_chinese}")
    print(f"Files skipped (already done): {skipped_already_done}")
    print(f"Files translated this run: {len(files_to_process)}")
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")
    print(
        f"Total processed (including previous runs): {len(progress.get('processed', []))}"
    )

    if errors:
        print()
        print("Errors encountered:")
        for error in errors[:20]:  # Limit to first 20 errors
            print(f"  - {error}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors")

    print()
    print(f"Progress saved to: {PROGRESS_FILE}")
    print("Run with --reset to start fresh")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Translate Chinese comments and logs to English in Python files"
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=5,
        help="Maximum number of concurrent translations (default: 5)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually write changes, just show what would be done",
    )
    parser.add_argument(
        "--files", nargs="*", help="Specific files to translate (optional)"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Clear previous progress and start fresh"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: only check if there are any Chinese characters in .py files, without translating",
    )

    args = parser.parse_args()

    if args.check:
        # Check mode: only report files with Chinese content
        exit_code = check_chinese_in_files(SRC_DIR, specific_files=args.files)
        sys.exit(0 if exit_code == 0 else 1)
    else:
        # Translation mode
        asyncio.run(
            main(
                max_concurrency=args.max_concurrency,
                dry_run=args.dry_run,
                specific_files=args.files,
                reset_progress=args.reset,
            )
        )
