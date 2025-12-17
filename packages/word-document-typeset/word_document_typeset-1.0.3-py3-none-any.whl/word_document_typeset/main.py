"""
Word文档排版 MCP 服务主程序

仅提供一个工具：Style the Heading（为指定级别标题应用样式）
"""

import os
import sys

# 设置FastMCP所需的环境变量
os.environ.setdefault('FASTMCP_LOG_LEVEL', 'INFO')

from fastmcp import FastMCP
from . import tools

# 初始化FastMCP服务器
mcp = FastMCP("Word文档排版")


def register_tools():
    """注册唯一工具：Style the Heading"""

    @mcp.tool(name="Style_the_Heading")
    async def style_the_heading_tool(
        filename: str,
        level: int,
        bold: str = "",
        italic: str = "",
        underline: str = "",
        color: str = "",
        font_size: int = 0,
        font_name: str = "",
        align: str = "",
        spacing_before: int = -1,
        spacing_after: int = -1,
        add_numbering: str = "",
        numbering_separator: str = "",
        numbering_suffix: str = "",
        remove_numbering: str = "",
        remove_all_levels: str = "",
    ):
        """
        为指定级别标题（Heading 1-9）应用统一样式。
        - level: 标题级别（1-9）
        - bold/italic/underline: "true"/"false"/""(不变)
        - color: 颜色名或十六进制（如 "red" 或 "#FF0000"）
        - font_size: 字号（pt），0表示不变
        - font_name: 字体名，不传表示不变
        - align: 对齐方式（left/center/right/justify），空表示不变
        - spacing_before/spacing_after: 段前/段后间距（磅），-1表示不变
        - add_numbering: 是否为标题添加自动多级编号（"true"/"false"/"" 不变）
        - numbering_separator: 多级编号的分隔符（默认 "."）
        - numbering_suffix: 编号后缀（默认空格 " "），例如设置为 ". " 可得到 "1. 标题"
        """
        # 字符串布尔入参转换为Python布尔/None
        def to_bool_or_none(v: str):
            if not isinstance(v, str) or not v.strip():
                return None
            vl = v.strip().lower()
            if vl == "true":
                return True
            if vl == "false":
                return False
            return None

        return await tools.style_heading(
            filename=filename,
            level=level,
            bold=to_bool_or_none(bold),
            italic=to_bool_or_none(italic),
            underline=to_bool_or_none(underline),
            color=color if color.strip() else None,
            font_size=font_size if isinstance(font_size, int) and font_size > 0 else None,
            font_name=font_name if font_name.strip() else None,
            align=align if align.strip() else None,
            spacing_before=spacing_before if isinstance(spacing_before, int) and spacing_before >= 0 else None,
            spacing_after=spacing_after if isinstance(spacing_after, int) and spacing_after >= 0 else None,
            add_numbering=to_bool_or_none(add_numbering),
            numbering_separator=numbering_separator if numbering_separator.strip() else None,
            numbering_suffix=numbering_suffix if numbering_suffix.strip() else None,
            remove_numbering=to_bool_or_none(remove_numbering),
            remove_all_levels=to_bool_or_none(remove_all_levels),
        )


def main():
    """服务器的主入口点 - 仅支持stdio传输"""
    register_tools()

    print("启动Word文档排版MCP服务器...")
    print("提供以下功能:")
    print("- Style_the_Heading: 为指定级别标题应用样式")

    try:
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("\n正在关闭Word文档排版服务器...")
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
