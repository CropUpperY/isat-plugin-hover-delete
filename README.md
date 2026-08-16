# iSAT-SAM Hover Delete

<div align="center">

**English** | [简体中文](README.zh-CN.md)

[![Python](https://img.shields.io/badge/Python-%3E%3D3.8-blue)](https://www.python.org/)
[![iSAT-SAM](https://img.shields.io/badge/iSAT--SAM-%3E%3D1.4.0-green)](https://github.com/yatengLG/ISAT_with_segment_anything)
[![License](https://img.shields.io/badge/License-Apache--2.0-orange)](LICENSE)

</div>

An [iSAT-SAM](https://github.com/yatengLG/ISAT_with_segment_anything) plugin that lets you delete a polygon vertex by hovering over it and pressing `Delete`—no click selection required.

## Features

- Delete the vertex currently under the mouse cursor with `Delete`.
- No click or selection is required.
- Polygon fills and edges are ignored, preventing accidental deletion of an entire annotation.
- Works in both View and Edit modes.
- Preserves iSAT-SAM shortcuts such as `Ctrl+Delete`.
- Ignores key auto-repeat, so holding `Delete` does not remove multiple vertices.
- Supports both the PyPI iSAT-SAM 1.5.2 vertex API and the newer GitHub API.
- Keeps polygon geometry, area, dirty state, annotation list, and layer order synchronized.

## Deletion behavior

Move the cursor onto a polygon vertex. When iSAT-SAM changes the cursor to an open hand, press `Delete`.

- Five or more vertices: only the hovered vertex is removed.
- Four vertices: deleting one vertex removes the entire annotation instead of leaving a triangle.
- Anywhere other than a vertex: the plugin does nothing.

## Requirements

- Python 3.8 or later
- iSAT-SAM 1.4.0 or later (plugin system required)
- Windows, Linux, or macOS

## Installation

Install the plugin in the same Python or Conda environment as iSAT-SAM.

### From GitHub Releases (recommended)

Download `isat_plugin_hover_delete-0.3.2-py3-none-any.whl` from the [v0.3.2 release](https://github.com/CropUpperY/isat-plugin-hover-delete/releases/tag/v0.3.2), open a terminal in the download folder, and run:

```bash
python -m pip install isat_plugin_hover_delete-0.3.2-py3-none-any.whl
```

### From source

```bash
git clone https://github.com/CropUpperY/isat-plugin-hover-delete.git
cd isat-plugin-hover-delete
python -m pip install .
```

Restart iSAT-SAM, open the plugin manager, and enable `HoverDeletePlugin`.

To upgrade an existing installation from a downloaded wheel:

```bash
python -m pip install --upgrade isat_plugin_hover_delete-0.3.2-py3-none-any.whl
```

## Usage

1. Open an annotation in iSAT-SAM.
2. Move the mouse precisely over the vertex you want to remove.
3. Wait for the cursor to change to an open hand.
4. Press `Delete` once.

The plugin is inactive while drawing, using SAM prompts, or repainting.

## Uninstallation

```bash
python -m pip uninstall isat-plugin-hover-delete
```

## Development

Run the tests with:

```bash
python -m unittest discover -s tests -v
```

The test suite covers hover detection, PyPI/GitHub API compatibility, shortcut handling, vertex-only deletion, and four-point polygon cleanup.

## Acknowledgements

Thanks to the developers of [iSAT-SAM](https://github.com/yatengLG/ISAT_with_segment_anything) for providing the annotation tool and plugin API.

This is a third-party plugin and is not affiliated with or officially maintained by the iSAT-SAM project.

## License

Licensed under the [Apache License 2.0](LICENSE).


