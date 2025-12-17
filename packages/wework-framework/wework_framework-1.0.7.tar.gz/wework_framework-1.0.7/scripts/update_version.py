"""
اسکریپت به‌روزرسانی نسخه در همه فایل‌ها
این اسکریپت نسخه را از version.json می‌خواند و در همه فایل‌های پروژه به‌روزرسانی می‌کند
"""
import json
import re
import sys
from pathlib import Path
from typing import List, Tuple, Callable, Union

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# مسیر ریشه پروژه
PROJECT_ROOT = Path(__file__).parent.parent

# فایل نسخه مرکزی
VERSION_FILE = PROJECT_ROOT / "version.json"

# فایل‌هایی که باید به‌روزرسانی شوند
FILES_TO_UPDATE = [
    {
        "path": "frontend/package.json",
        "patterns": [
            (r'"version"\s*:\s*"[^"]+"', lambda v: f'"version": "{v}"')
        ]
    },
    {
        "path": "src/api/app.py",
        "patterns": [
            (r"version\s*=\s*'[^']+'", lambda v: f"version='{v}'"),
            (r'"version"\s*:\s*"[^"]+"', lambda v: f'"version": "{v}"')
        ]
    },
    {
        "path": "src/cli/main.py",
        "patterns": [
            (r'version\s*=\s*"[^"]+"', lambda v: f'version="{v}"')
        ]
    },
    {
        "path": "src/cli/commands.py",
        "patterns": [
            (r'"version"\s*:\s*"[^"]+"', lambda v: f'"version": "{v}"')
        ]
    },
    {
        "path": "setup.py",
        "patterns": [
            (r'version\s*=\s*"[^"]+"', lambda v: f'version="{v}"')
        ]
    },
    {
        "path": "pyproject.toml",
        "patterns": [
            (r'version\s*=\s*"[^"]+"', lambda v: f'version = "{v}"')
        ]
    }
]


def read_version() -> str:
    """خواندن نسخه از فایل version.json"""
    if not VERSION_FILE.exists():
        raise FileNotFoundError(f"فایل {VERSION_FILE} پیدا نشد!")
    
    with open(VERSION_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get("version", "")


def write_version(version: str):
    """نوشتن نسخه در فایل version.json"""
    data = {"version": version}
    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[OK] نسخه در {VERSION_FILE} به‌روزرسانی شد: {version}")


def update_file(file_path: Path, patterns: List[Tuple[str, Union[str, Callable]]], version: str) -> bool:
    """به‌روزرسانی یک فایل با استفاده از الگوهای regex"""
    if not file_path.exists():
        print(f"[WARNING] فایل پیدا نشد: {file_path}")
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # اعمال همه الگوها
        for pattern, replacement in patterns:
            if callable(replacement):
                # اگر replacement یک تابع است، آن را با version فراخوانی کن
                new_text = replacement(version)
            else:
                new_text = replacement
            content = re.sub(pattern, new_text, content)
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"[OK] {file_path} به‌روزرسانی شد")
            return True
        else:
            print(f"[SKIP] {file_path} تغییری نداشت")
            return False
            
    except Exception as e:
        print(f"[ERROR] خطا در به‌روزرسانی {file_path}: {e}")
        return False


def update_all_files(version: str):
    """به‌روزرسانی همه فایل‌ها با نسخه جدید"""
    print(f"\nبه‌روزرسانی نسخه به {version}...\n")
    
    updated_count = 0
    for file_config in FILES_TO_UPDATE:
        file_path = PROJECT_ROOT / file_config["path"]
        patterns = file_config["patterns"]
        
        if update_file(file_path, patterns, version):
            updated_count += 1
    
    print(f"\n{updated_count} فایل به‌روزرسانی شد\n")


def main():
    """تابع اصلی"""
    
    if len(sys.argv) > 1:
        # اگر نسخه جدید داده شده، آن را تنظیم کن
        new_version = sys.argv[1]
        write_version(new_version)
        update_all_files(new_version)
    else:
        # فقط فایل‌ها را با نسخه فعلی همگام‌سازی کن
        current_version = read_version()
        print(f"نسخه فعلی: {current_version}")
        update_all_files(current_version)


if __name__ == "__main__":
    main()
