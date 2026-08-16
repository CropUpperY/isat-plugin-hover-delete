from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).parent
ABOUT = {}
exec((ROOT / "isat_plugin_hover_delete" / "__init__.py").read_text(encoding="utf-8"), ABOUT)


setup(
    name="isat-plugin-hover-delete",
    version=ABOUT["__version__"],
    author=ABOUT["__author__"],
    description=ABOUT["__description__"],
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/CropUpperY/isat-plugin-hover-delete",
    project_urls={
        "Source": "https://github.com/CropUpperY/isat-plugin-hover-delete",
        "iSAT-SAM": "https://github.com/yatengLG/ISAT_with_segment_anything",
    },
    license="Apache-2.0",
    keywords=["isat-sam", "isat plugin", "annotation", "hover delete"],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=["isat-sam>=1.4.0"],
    entry_points={
        "isat.plugins": [
            "hover_delete = isat_plugin_hover_delete.main:HoverDeletePlugin",
        ]
    },
)

