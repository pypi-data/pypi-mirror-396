"""
Word文档排版工具的辅助函数

仅保留当前工具所需的通用文件处理能力。
"""

import os


def ensure_docx_extension(filename: str) -> str:
    """
    确保文件名有 .docx 扩展名
    """
    if not filename.lower().endswith('.docx'):
        return filename + '.docx'
    return filename


def check_file_writeable(filename: str) -> tuple[bool, str]:
    """
    检查文件是否可写
    Returns: (是否可写, 错误信息)
    """
    try:
        if not os.path.exists(filename):
            return False, "File does not exist"
        if not os.access(filename, os.W_OK):
            return False, "File is not writable (permission denied)"
        try:
            with open(filename, 'r+b') as f:
                pass
        except PermissionError:
            return False, "File is currently open in another application"
        except IOError as e:
            return False, f"File access error: {str(e)}"
        return True, ""
    except Exception as e:
        return False, f"Error checking file: {str(e)}"
