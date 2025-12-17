# Word文档排版 MCP服务

仅提供一个工具：Style_the_Heading（为指定级别标题应用样式）。

## 功能概述
- Style_the_Heading：为文档内的内置标题样式（Heading 1-9）统一设置字体、颜色、对齐及段前/段后间距。该操作直接修改文档样式，所有使用该标题样式的段落将统一更新。

## 安装要求
- Python 3.10+
- python-docx >= 1.1.0
- fastmcp >= 2.8.1

## 安装与运行

使用 uv（推荐）：
```bash
uv sync
```

或使用 pip：
```bash
pip install python-docx fastmcp
```

启动 MCP 服务器（两种方式均可）：
```bash
# 使用 uv 运行
uv run python -m word-document-typeset.main

# 或直接运行
python -m word-document-typeset.main
```

## MCP 客户端配置示例
将如下配置添加到您的 MCP 客户端配置文件中：
```json
{
  "mcpServers": {
    "Word文档排版": {
      "command": "uvx",
      "args": [
        "word-document-typeset"
      ],
      "env": {}
    }
  }
}
```

## 工具：Style_the_Heading

调用名称："Style_the_Heading"

参数说明：
- filename: 文档路径（可不带 .docx 扩展名）
- level: 标题级别（1-9）
- bold/italic/underline: "true" / "false" / ""（空表示不改）
- color: 颜色名称或十六进制（如 "red"、"#FF0000"）
- font_size: 字号（磅），>0 时生效
- font_name: 字体名称
- align: 对齐方式（left/center/right/justify）
- spacing_before/spacing_after: 段前/段后间距（磅，>=0 时生效）
- add_numbering: 是否添加多级编号（"true"/"false"/"" 不变）
- numbering_separator: 多级编号分隔符（默认 "."）
- numbering_suffix: 编号后缀（默认空格 " "，如设为 ". " 得到 "1. 标题"）
- remove_numbering: 是否移除编号前缀（"true"/"false"/"" 不变；优先级高于 add_numbering）
- remove_all_levels: 是否对所有标题级别移除编号（当 remove_numbering="true" 时生效）

示例（自然语言指令）：
```
请将文档 "example.docx" 的 Heading 1 设置为：居中、粗体、字号16、颜色蓝色，段前12磅、段后6磅。
```
示例（编号相关）：
```
移除 Heading 2 的编号：remove_numbering="true"，remove_all_levels="false"，level=2
移除所有级别编号：remove_numbering="true"，remove_all_levels="true"
为 Heading 2 添加多级编号：add_numbering="true"，level=2，numbering_separator=".", numbering_suffix=". "
```
```
请将文档 "example.docx" 的 Heading 1 设置为：居中、粗体、字号16、颜色蓝色，段前12磅、段后6磅。
```

## 颜色支持
- 预定义颜色：red, blue, green, black, white, yellow, orange, purple, gray/grey
- 十六进制：#RRGGBB 或 RRGGBB（如 #FF0000）

## 错误与校验
- 文件存在性与可写性校验（避免被其他程序占用）
- 标题级别范围校验（1-9）
- 样式存在校验（必须为内置样式，如 "Heading 1"）
- 参数类型与取值校验（字号/间距需为整数且有效）

## 注意事项
1. 修改的是样式对象（如 "Heading 1"），所有使用该样式的段落都会受影响。
2. 请确保文档未在其他软件中打开，以避免写入失败。
3. 间距与字号单位为磅（pt）。
4. 对齐值仅支持 left/center/right/justify。

## 许可证
MIT License

## 作者
Word MCP Services
