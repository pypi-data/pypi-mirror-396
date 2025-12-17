import re
from pathlib import Path
from setuptools import setup, find_packages

def get_version():
    version_file = Path(__file__).parent / "src" / "physlab" / "__version__.py"
    content = version_file.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if match:
        return match.group(1)
    return "0.0.0"

setup(
    version=get_version(),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)