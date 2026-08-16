# iSAT-SAM 悬停删除顶点插件

<div align="center">

[English](README.md) | **简体中文**

[![Python](https://img.shields.io/badge/Python-%3E%3D3.8-blue)](https://www.python.org/)
[![iSAT-SAM](https://img.shields.io/badge/iSAT--SAM-%3E%3D1.4.0-green)](https://github.com/yatengLG/ISAT_with_segment_anything)
[![License](https://img.shields.io/badge/License-Apache--2.0-orange)](LICENSE)

</div>

这是一个 [iSAT-SAM](https://github.com/yatengLG/ISAT_with_segment_anything) 插件。鼠标悬停在多边形顶点上时，直接按 `Delete` 即可删除该顶点，无需先点击选中。

## 功能特点

- 使用 `Delete` 删除鼠标当前悬停的顶点。
- 无需点击或选中顶点。
- 悬停在多边形填充区域或轮廓线上不会触发，防止误删整个标注。
- 支持查看和编辑模式。
- 保留 `Ctrl+Delete` 等 iSAT-SAM 原有快捷键。
- 忽略键盘自动重复，长按 `Delete` 不会连续删除多个顶点。
- 同时兼容 PyPI iSAT-SAM 1.5.2 和 GitHub 新版的顶点接口。
- 自动同步多边形形状、面积、未保存状态、右侧标注列表和图层顺序。

## 删除规则

把鼠标移动到多边形顶点上。当 iSAT-SAM 将鼠标指针变成张开的手掌时，按下 `Delete`。

- 顶点数量不少于 5 个：只删除当前悬停顶点。
- 只剩 4 个顶点：再删除一个顶点时会删除整个标注，不保留三角形。
- 鼠标不在顶点上：插件不执行任何操作。

## 环境要求

- Python 3.8 或更高版本
- iSAT-SAM 1.4.0 或更高版本（需要官方插件系统）
- Windows、Linux 或 macOS

## 安装

请在安装 iSAT-SAM 的同一个 Python 或 Conda 环境中安装插件：

```bash
git clone https://github.com/CropUpperY/isat-plugin-hover-delete.git
cd isat-plugin-hover-delete
python -m pip install .
```

安装后重启 iSAT-SAM，打开插件管理器并启用 `HoverDeletePlugin`。

拉取新版本后可执行以下命令升级：

```bash
python -m pip install --upgrade .
```

## 使用方法

1. 在 iSAT-SAM 中打开一个标注。
2. 把鼠标准确移动到需要删除的顶点上。
3. 等待鼠标指针变成张开的手掌。
4. 按一下 `Delete`。

插件在绘制、使用 SAM 提示或重绘过程中不会触发。

## 卸载

```bash
python -m pip uninstall isat-plugin-hover-delete
```

## 开发与测试

运行测试：

```bash
python -m unittest discover -s tests -v
```

测试覆盖悬停检测、PyPI/GitHub 接口兼容、快捷键处理、仅删除顶点以及四点多边形清理规则。

## 致谢

感谢 [iSAT-SAM](https://github.com/yatengLG/ISAT_with_segment_anything) 开发者提供标注工具和插件接口。

这是第三方插件，与 iSAT-SAM 项目没有从属关系，也不由 iSAT-SAM 官方维护。

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。


