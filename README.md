# MinerU PDF → Markdown

使用 [MinerU](https://mineru.net) API 将 PDF 文档批量转换为 Markdown 格式。支持扫描件 OCR、数学公式识别、表格识别。

## 功能特性

- **批量转换** — 一次提交多个 PDF，自动排队处理
- **OCR 支持** — 扫描版 PDF 自动识别文字
- **公式识别** — 数学公式自动转为 LaTeX
- **表格识别** — 表格自动转为 Markdown 表格
- **图片提取** — 内嵌图片自动导出，Markdown 中直接引用
- **Token 安全** — 支持环境变量、文件、命令行参数等多种 Token 传入方式

## 快速开始

### 1. 获取 API Token

1. 访问 [MinerU 官网](https://mineru.net) 注册账号
2. 登录后进入 **API 管理页面** 获取你的 Token
3. 设置环境变量（推荐）：

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

> 免费套餐：每日 2000 页高优先级配额，单文件 ≤200 MB，≤600 页。

### 2. 安装依赖

```bash
pip install mineru-open-sdk
```

### 3. 转换你的第一个 PDF

```bash
python scripts/convert.py document.pdf
```

输出文件默认保存在 `md_output/` 目录下。

## 使用说明

### 命令行

```bash
# 单文件转换
python scripts/convert.py document.pdf

# 批量转换
python scripts/convert.py doc1.pdf doc2.pdf doc3.pdf

# 指定输出目录
python scripts/convert.py document.pdf -o my_output/

# 关闭 OCR（纯电子版 PDF 可加速）
python scripts/convert.py document.pdf --no-ocr

# 关闭公式识别
python scripts/convert.py document.pdf --no-formula

# 关闭表格识别
python scripts/convert.py document.pdf --no-table

# 指定文档语言（ch 中文 / en 英文）
python scripts/convert.py document.pdf --language en

# 显式指定 Token
python scripts/convert.py document.pdf --token "你的Token"

# 从文件读取 Token
python scripts/convert.py document.pdf --token-file /path/to/token.txt
```

### 完整参数列表

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `sources` | 位置参数 | 必填 | 一个或多个 PDF 文件路径 |
| `-o`, `--output-dir` | str | `md_output` | 输出目录 |
| `--token` | str | — | MinerU API Token |
| `--token-file` | str | — | 从文件读取 Token |
| `--no-ocr` | flag | — | 关闭 OCR |
| `--no-formula` | flag | — | 关闭公式识别 |
| `--no-table` | flag | — | 关闭表格识别 |
| `--language` | str | `ch` | 文档语言 (`ch` / `en`) |
| `--model` | str | — | 模型版本 (`pipeline` / `vlm` / `html`) |
| `--timeout` | int | `600` | 单任务超时秒数 |

### Python API

```python
from mineru import MinerU

client = MinerU(token="<YOUR_TOKEN>")

# 单文件转换
results = client.extract_batch(["document.pdf"])
for result in results:
    if result.state == "done":
        result.save_markdown("output.md", with_images=True)

client.close()
```

## Token 安全

脚本按以下优先级读取 Token（前者优先）：

1. `--token` 命令行参数
2. `--token-file` 指定的文件
3. 环境变量 `MINERU_TOKEN`
4. Windows 系统环境变量（通过 `setx` 或 `[Environment]::SetEnvironmentVariable` 设置）

**请勿将 Token 硬编码在脚本中**，也不要在公开仓库中提交包含 Token 的文件。

## 输出结构

```
md_output/
├── document.md              # Markdown 文件（含图片引用）
├── images/                  # 共享图片目录
│   ├── image_001.png
│   └── image_002.png
└── document/                # 完整导出包
    ├── document.md
    └── images/
        ├── image_001.png
        └── image_002.png
```

## Claude Code Skill 集成

本项目同时是一个 Claude Code Skill。将本目录放到 `~/.claude/skills/mineru-pdf-to-md/` 即可在 Claude Code 中使用。

触发方式：在 Claude Code 中提及 "pdf to markdown"、"pdf转md"、"mineru"、"转换pdf" 等关键词。

## 许可证

MIT License — 详见 [LICENSE](LICENSE) 文件。
