"""
MinerU PDF → Markdown 通用转换脚本
=====================================

用法:
    # 单文件转换
    python scripts/convert.py 文档.pdf

    # 批量转换
    python scripts/convert.py 文档1.pdf 文档2.pdf 文档3.pdf

    # 指定输出目录
    python scripts/convert.py 文档.pdf -o output_dir/

    # 关闭 OCR（纯电子版 PDF 可加速）
    python scripts/convert.py 文档.pdf --no-ocr

    # 从文件读取 Token
    python scripts/convert.py 文档.pdf --token-file /path/to/token.txt

    # 环境变量 MINERU_TOKEN 或直接 --token 指定
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

from mineru import MinerU


def _read_windows_env(var: str) -> str | None:
    """从 Windows 系统环境变量读取（解决 Git Bash 不继承 setx 变量的问题）。"""
    try:
        result = subprocess.run(
            ["powershell.exe", "-Command",
             f"[Environment]::GetEnvironmentVariable('{var}','User')"],
            capture_output=True, text=True, timeout=10,
        )
        val = result.stdout.strip()
        return val if val else None
    except Exception:
        return None


def load_token(token: str | None, token_file: str | None) -> str:
    """按优先级: 参数 > 文件 > 环境变量 > Windows 系统变量。"""
    if token:
        return token
    if token_file:
        path = Path(token_file)
        if not path.is_file():
            print(f"[ERROR] Token 文件不存在: {path}")
            sys.exit(1)
        return path.read_text(encoding="utf-8").strip()
    env_token = os.environ.get("MINERU_TOKEN")
    if env_token:
        return env_token
    # Git Bash 不继承 setx 变量，从 Windows 注册表读取
    win_token = _read_windows_env("MINERU_TOKEN")
    if win_token:
        return win_token
    print("[ERROR] 未提供 Token。请通过 --token, --token-file 或 MINERU_TOKEN 环境变量提供。")
    sys.exit(1)


def check_files(sources: list[str]) -> list[str]:
    """检查文件存在性，返回有效文件列表。"""
    valid = []
    for s in sources:
        p = Path(s)
        if not p.is_file():
            print(f"[WARN] 文件不存在，跳过: {s}")
            continue
        size_mb = p.stat().st_size / 1024 / 1024
        print(f"  [OK] {p.name} ({size_mb:.1f} MB)")
        valid.append(str(p.resolve()))
    if not valid:
        print("[ERROR] 没有有效的 PDF 文件可处理。")
        sys.exit(1)
    return valid


def main() -> None:
    parser = argparse.ArgumentParser(
        description="使用 MinerU API 将 PDF 转换为 Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("sources", nargs="+", help="PDF 文件路径（支持多个）")
    parser.add_argument("-o", "--output-dir", default="md_output",
                        help="输出目录 (default: md_output)")
    parser.add_argument("--token", help="MinerU API Token（直接提供）")
    parser.add_argument("--token-file", help="从文件读取 Token")
    parser.add_argument("--no-ocr", action="store_true", help="关闭 OCR")
    parser.add_argument("--no-formula", action="store_true", help="关闭公式识别")
    parser.add_argument("--no-table", action="store_true", help="关闭表格识别")
    parser.add_argument("--language", default="ch", help="文档语言 (default: ch)")
    parser.add_argument("--model", choices=["pipeline", "vlm", "html"],
                        default=None, help="模型版本")
    parser.add_argument("--timeout", type=int, default=600,
                        help="单任务超时秒数 (default: 600)")
    args = parser.parse_args()

    # --- Token ---
    api_token = load_token(args.token, args.token_file)

    # --- 检查文件 ---
    sources = check_files(args.sources)

    # --- 输出目录 ---
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n输出目录: {out_dir.resolve()}\n")

    # --- 转换 ---
    # 构建源文件名 -> 源文件路径的映射（用于匹配返回结果）
    source_map = {Path(s).name: s for s in sources}

    client = MinerU(token=api_token)
    try:
        print(f"[START] 提交 {len(sources)} 个文件...")
        results_list = list(client.extract_batch(
            sources,
            ocr=None if args.no_ocr else True,
            formula=None if args.no_formula else True,
            table=None if args.no_table else True,
            language=args.language,
            model=args.model,
            timeout=args.timeout,
        ))

        # MinerU API 并行处理文件，返回顺序可能与提交顺序不一致。
        # 使用 result.filename 匹配回源文件，确保输出命名正确。
        for idx, result in enumerate(results_list):
            # 优先用 result.filename 匹配，找不到时回退到索引
            src_filename = getattr(result, "filename", None) or Path(sources[idx]).name
            src_path = source_map.get(src_filename, sources[idx])
            basename = Path(src_path).stem

            print(f"\n[{idx+1}/{len(results_list)}] {basename} (源文件: {src_filename})")
            print(f"   状态: {result.state}")

            if result.state == "done":
                md_path = out_dir / f"{basename}.md"
                saved = result.save_markdown(str(md_path), with_images=True)
                print(f"   [OK] Markdown: {saved}")

                zip_dir = out_dir / basename
                result.save_all(str(zip_dir))
                print(f"   [OK] 导出包已保存到: {zip_dir}/")
            else:
                print(f"   [FAIL] {result.error} (code: {result.err_code})")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise
    finally:
        client.close()

    print("\n[OK] 全部完成！")


if __name__ == "__main__":
    main()
