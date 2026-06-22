---
name: mineru-pdf-to-md
description: Use when the user wants to convert PDF documents to Markdown format using MinerU API. Triggered by mentions of "pdf to markdown", "pdf转md", "pdf转markdown", "mineru", "转换pdf", "解析pdf", "提取pdf内容", or any request to extract text/content from PDF files.
---

# MinerU PDF → Markdown 转换 Skill

## ⛔ 硬性约束（最高优先级）

**本 skill 的唯一转换方案是 MinerU API。严禁使用任何本地 PDF 解析库作为"备选方案"。**

以下工具/方案在触发本 skill 时绝对禁止使用：
- ❌ `pymupdf` / `fitz`
- ❌ `pdfplumber`
- ❌ `pdfminer` / `pdfminer.six`
- ❌ `PyPDF2` / `pypdf`
- ❌ 任何其他本地 PDF 解析库
- ❌ 命令行 `pdftotext` 等工具
- ❌ 手动逐页截图再 OCR

**如果 MinerU API 不可用（Token 未配置、网络不通、配额耗尽等），唯一正确的做法是：停止操作，按下方 Token 配置流程引导用户完成配置。不要尝试任何"先用其他方式凑合"的做法。**

## 概述

使用 [MinerU](https://mineru.net) API（`mineru-open-sdk`）将 PDF 文件批量转换为 Markdown 格式。支持扫描件 OCR、公式识别、表格识别。

## 执行流程

每次触发本 skill 时，严格按以下顺序执行：

### 步骤 0：Token 预检（必须先完成）

在开始任何转换工作之前，必须检查 MinerU Token 是否可用：

**检查方式（按优先级尝试）：**

```bash
# 方式 1：检查环境变量
echo $MINERU_TOKEN

# 方式 2：检查 Windows 系统环境变量（Git Bash 场景）
powershell.exe -Command "[Environment]::GetEnvironmentVariable('MINERU_TOKEN','User')"

# 方式 3：用 Python 测试 Token 是否有效
python -c "
from mineru import MinerU
import os, subprocess, sys

# 尝试多种来源获取 token
token = os.environ.get('MINERU_TOKEN')
if not token:
    try:
        r = subprocess.run(['powershell.exe','-Command',
            \"[Environment]::GetEnvironmentVariable('MINERU_TOKEN','User')\"],
            capture_output=True, text=True, timeout=10)
        token = r.stdout.strip()
    except:
        pass

if not token:
    print('TOKEN_NOT_FOUND')
    sys.exit(1)

try:
    client = MinerU(token=token)
    print('TOKEN_VALID')
    client.close()
except Exception as e:
    print(f'TOKEN_INVALID: {e}')
    sys.exit(1)
"
```

### 步骤 1A：Token 已配置 → 执行转换

Token 验证通过后，直接使用 `scripts/convert.py` 执行转换：

```bash
python scripts/convert.py <PDF文件路径>
```

### 步骤 1B：Token 未配置 → 引导配置（不可跳过）

如果 Token 预检失败，**停止一切 PDF 处理操作**，按以下内容引导用户：

---

## Token 配置引导

当 Token 未配置时，向用户输出以下引导内容：

> **需要 MinerU API Token** 才能高质量转换 PDF（支持 OCR、公式、表格识别）。
> 免费注册即可获得，无需付费。请按以下步骤操作：
>
> **第 1 步 — 注册获取 Token（约 1 分钟）：**
> 1. 打开 https://mineru.net 注册账号
> 2. 登录后进入 API 管理页面：https://mineru.net/api/manage
> 3. 复制你的 API Token
>
> **第 2 步 — 告诉我你的 Token：** 直接发给我，我会帮你配置到系统环境变量中（安全存储，不会泄露）。
>
> 或者你也可以自行配置：
> - **Windows (CMD):** `setx MINERU_TOKEN "你的Token"`
> - **Windows (PowerShell):** `[Environment]::SetEnvironmentVariable('MINERU_TOKEN', '你的Token', 'User')`
> - **macOS / Linux:** `echo 'export MINERU_TOKEN="你的Token"' >> ~/.bashrc && source ~/.bashrc`
>
> 配置完成后，重新告诉我转换 PDF 即可。

**当用户提供 Token 时，执行以下配置命令：**

```bash
# Windows - 写入用户环境变量（持久化，新终端也生效）
powershell.exe -Command "[Environment]::SetEnvironmentVariable('MINERU_TOKEN', '<用户提供的Token>', 'User')"

# 同时在当前 session 设置（当前对话立即可用）
export MINERU_TOKEN="<用户提供的Token>"
```

配置完成后验证 Token 有效性，然后继续执行转换。

---

## 转换脚本

脚本 `scripts/convert.py` 提供了完整的批处理封装。Token 查找优先级：`--token` 参数 > `--token-file` 参数 > 环境变量 `MINERU_TOKEN` > Windows 系统环境变量。

```bash
# 单文件转换
python scripts/convert.py 文档.pdf

# 批量转换
python scripts/convert.py 文档1.pdf 文档2.pdf 文档3.pdf

# 指定输出目录
python scripts/convert.py 文档.pdf -o output_dir/

# 显式传入 Token
python scripts/convert.py 文档.pdf --token "你的Token"
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

## 安装依赖

```bash
pip install mineru-open-sdk
```

## 注意事项

- **Token 安全**: Token 不应硬编码在脚本中，优先从环境变量或文件读取
- **文件大小限制**: 单个文件 ≤200 MB，≤600 页
- **配额**: 免费用户每日 2000 页高优先级
- **网络**: 需要能够访问 `https://mineru.net`
- **批量转换顺序**: MinerU API 并行处理文件，返回结果顺序可能与提交顺序不一致。脚本已通过 `result.filename` 属性匹配源文件，确保输出命名正确。如果遇到顺序问题，脚本会打印源文件名供核对。

## 文件清单

- `SKILL.md` — 本文件（skill 定义）
- `README.md` — 项目文档
- `scripts/convert.py` — 通用转换脚本（支持批量/单文件模式）
- `LICENSE` — MIT 许可证
- `.gitignore` — Git 忽略规则
