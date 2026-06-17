---
name: mineru-pdf-to-md
description: Use when the user wants to convert PDF documents to Markdown format using MinerU API. Triggered by mentions of "pdf to markdown", "pdf转md", "pdf转markdown", "mineru", "转换pdf", "解析pdf", "提取pdf内容", or any request to extract text/content from PDF files.
---

# MinerU PDF → Markdown 转换 Skill

## 概述

使用 [MinerU](https://mineru.net) API（`mineru-open-sdk`）将 PDF 文件批量转换为 Markdown 格式。支持扫描件 OCR、公式识别、表格识别。

## 前置条件

### 1. 获取 MinerU API Token

你需要一个 MinerU API Token 才能使用此 skill。获取方式：

1. 访问 [MinerU 官网](https://mineru.net) 注册账号
2. 登录后进入 [API 管理页面](https://mineru.net/api/manage) 获取你的 Token
3. 将 Token 设置为环境变量（推荐）：

   **Windows (CMD):**
   ```cmd
   setx MINERU_TOKEN "你的Token"
   ```

   **Windows (PowerShell):**
   ```powershell
   [Environment]::SetEnvironmentVariable('MINERU_TOKEN', '你的Token', 'User')
   ```

   **macOS / Linux:**
   ```bash
   echo 'export MINERU_TOKEN="你的Token"' >> ~/.bashrc
   source ~/.bashrc
   ```

   或者每次调用时通过 `--token` 参数传入。

> 注意：免费套餐每日 2000 页高优先级配额，单文件 ≤200 MB，≤600 页。

### 2. 安装依赖

```bash
pip install mineru-open-sdk
```

## 核心工作流

### 调用转换脚本

脚本 `scripts/convert.py` 提供了完整的批处理封装。Token 查找优先级：`--token` 参数 > `--token-file` 参数 > 环境变量 `MINERU_TOKEN` > Windows 系统环境变量。

```bash
# 单文件转换（从环境变量读取 Token）
python scripts/convert.py 文档.pdf

# 批量转换
python scripts/convert.py 文档1.pdf 文档2.pdf 文档3.pdf

# 指定输出目录
python scripts/convert.py 文档.pdf -o output_dir/

# 关闭 OCR（纯电子版 PDF 可加速）
python scripts/convert.py 文档.pdf --no-ocr

# 显式传入 Token
python scripts/convert.py 文档.pdf --token "你的Token"
```

### API 调用示例（Python）

```python
from mineru import MinerU

client = MinerU(token="<YOUR_TOKEN>")
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `ocr` | True | 启用 OCR（扫描件支持） |
| `formula` | True | 公式识别 |
| `table` | True | 表格识别 |
| `language` | "ch" | 文档语言（ch/en） |
| `model` | None | "pipeline", "vlm", "html" |
| `timeout` | 600s | 单个任务最长等待时间 |

### 输出结构

```
output_dir/
├── 文件名.md                       # Markdown 文件（含图片引用）
├── images/                         # 内嵌图片（公共目录）
└── 文件名/                         # 完整导出包（含 images/）
    └── images/
```

## 注意事项

- **Token 安全**: Token 不应硬编码在脚本中，优先从环境变量或文件读取
- **文件大小限制**: 单个文件 ≤200 MB，≤600 页
- **配额**: 免费用户每日 2000 页高优先级
- **网络**: 需要能够访问 `https://mineru.net`
- **输出目录**: 建议与输入目录分开，默认 `md_output/`

## 文件清单

- `SKILL.md` — 本文件（skill 定义）
- `README.md` — 项目文档
- `scripts/convert.py` — 通用转换脚本（支持批量/单文件模式）
- `LICENSE` — MIT 许可证
- `.gitignore` — Git 忽略规则
