"""
Markdown文件处理工具

根据二级标题（##）分块，如果文本长度超过设定长度，则根据三级标题（###）继续分块。
主要用于将长文档分块后喂给大模型处理。

使用示例:
    # 1. 处理Markdown文件并分块
    processor = MarkdownProcessor(max_chunk_length=2000)
    chunks = processor.process_file("input.md")
    
    # 2. 导出分块结果到JSON
    processor.export_chunks_to_json(chunks, "chunks.json")
    
    # 3. 查看分块结果（生成可读的Markdown视图）
    processor.json_to_chunks_view("chunks.json", "chunks_view.md")
    
    # 4. 重构完整文档
    processor.export_full_markdown("chunks.json", "reconstructed.md")
"""

import json
import os
from pathlib import Path
from typing import Dict, List


class MarkdownProcessor:
    """Markdown文档处理器"""

    def __init__(
        self, max_chunk_length: int = 2000, preserve_metadata: bool = True, modify_length_for_titles: List[str] = None
    ):
        """
        初始化处理器

        Args:
            max_chunk_length: 最大块长度，超过此长度会按三级标题继续分块
            preserve_metadata: 是否保留Markdown元数据（如YAML front matter）
            modify_length_for_titles: 需要修改长度限制的标题关键词列表，支持智能匹配：
                - 完全匹配：如 ["知识基础"] 匹配 "知识基础"
                - 前缀匹配：如 ["知识基础"] 匹配 "知识基础1", "知识基础：xxx", "知识基础-实践"
                - 包含匹配：如 ["知识基础"] 匹配 "xxx知识基础xxx"
                示例：["知识基础", "动手实践", "应用案例"] 会匹配所有包含这些关键词的章节标题
                注意：匹配的标题只在内容长度超过限制时才分割，不匹配的标题任何情况下都不分割
        """
        self.max_chunk_length = max_chunk_length
        self.preserve_metadata = preserve_metadata
        self.modify_length_for_titles = modify_length_for_titles or []

    def _create_chunk(self, title: str, level: int, content: str, metadata: Dict, start_line: int = 0, modify_length: bool = False) -> Dict:
        """创建chunk的辅助方法"""
        return {
            "title": title,
            "level": level,
            "content": content,
            "length": len(content),
            "start_line": start_line,
            "metadata": metadata,
            "modify_length": modify_length,
        }

    def _save_current_chunk(self, current_chunk: Dict, current_content: List[str], chunks: List[Dict]) -> None:
        """保存当前chunk的辅助方法"""
        if current_chunk is not None:
            current_chunk["content"] = "\n".join(current_content)
            current_chunk["length"] = len(current_chunk["content"])
            chunks.append(current_chunk)

    def should_modify(self, title: str) -> bool:
        """检查标题是否应该修改
        
        支持多种匹配模式：
        1. 完全匹配：如 "知识基础" 匹配 "知识基础"
        2. 前缀匹配：如 "知识基础" 匹配 "知识基础1", "知识基础：xxx"
        3. 包含匹配：如 "知识基础" 匹配 "xxx知识基础xxx"
        
        Args:
            title: 要检查的标题
            
        Returns:
            bool: 如果标题匹配任何关键词则返回True，否则返回False
        """
        if not self.modify_length_for_titles:
            return False
            
        title_lower = title.lower().strip()
        
        for keyword in self.modify_length_for_titles:
            keyword_lower = keyword.lower().strip()
            
            # 完全匹配
            if title_lower == keyword_lower:
                return True
                
            # 前缀匹配：标题以关键词开头
            if title_lower.startswith(keyword_lower):
                # 检查关键词后是否跟着数字、冒号、空格等分隔符
                next_char = title_lower[len(keyword_lower):len(keyword_lower)+1] if len(title_lower) > len(keyword_lower) else ""
                if not next_char or next_char in [' ', '：', ':', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '_', '（', '(']:
                    return True
                    
            # 包含匹配：标题包含关键词（作为备选方案）
            if keyword_lower in title_lower:
                return True
                
        return False

    def _get_content_length(self, content_lines: List[str]) -> int:
        """获取内容长度的辅助方法"""
        return len("\n".join(content_lines))

    def _safe_file_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """安全的文件操作辅助方法"""
        try:
            return operation_func(*args, **kwargs)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"文件未找到: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON文件格式错误: {e}")
        except Exception as e:
            raise Exception(f"{operation_name}失败: {e}")

    def _simplify_chunk_for_export(self, chunk: Dict) -> Dict:
        """简化chunk用于导出的辅助方法"""
        return {
            "title": chunk["title"],
            "level": chunk["level"],
            "content": chunk["content"],
            "length": chunk["length"],
            "start_line": chunk["start_line"],
        }

    def read_markdown_file(self, file_path: str) -> str:
        """读取Markdown文件内容"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"文件未找到: {file_path}")
        except Exception as e:
            raise Exception(f"读取文件失败: {e}")

    def extract_metadata(self, content: str) -> Dict:
        """提取Markdown文件的元数据（YAML front matter）"""
        metadata = {}
        lines = content.split("\n")

        if lines and lines[0].strip() == "---":
            metadata_lines = []
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    break
                metadata_lines.append(line)

            # 解析YAML格式的元数据
            for line in metadata_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    metadata[key] = value

        return metadata

    def get_metadata_section(self, content: str) -> tuple:
        """获取Markdown文件的元数据部分和剩余内容"""
        lines = content.split("\n")
        metadata_lines = []
        remaining_lines = []
        in_metadata = False
        metadata_end_index = 0

        for i, line in enumerate(lines):
            if line.strip() == "---":
                if not in_metadata:
                    in_metadata = True
                    metadata_lines.append(line)
                else:
                    metadata_lines.append(line)
                    metadata_end_index = i
                    break
            elif in_metadata:
                metadata_lines.append(line)
            else:
                remaining_lines.append(line)

        # 如果找到了完整的元数据块，返回元数据和剩余内容
        if in_metadata and metadata_end_index > 0:
            remaining_lines = lines[metadata_end_index + 1 :]
            return metadata_lines, remaining_lines
        else:
            return [], lines

    def split_by_headings(self, content: str) -> List[Dict]:
        """按标题分块处理Markdown内容"""
        # 提取元数据
        metadata = self.extract_metadata(content) if self.preserve_metadata else {}

        # 分离元数据和内容
        metadata_lines, content_lines = self.get_metadata_section(content)

        chunks = []
        current_chunk = None
        current_content = []
        in_code_block = False

        for line in content_lines:
            # 检查是否进入或退出代码块
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                if current_chunk:
                    current_content.append(line)
                continue

            # 如果在代码块中，直接添加到当前内容，不进行标题检测
            if in_code_block:
                if current_chunk:
                    current_content.append(line)
                continue

            # 检查是否为二级标题（不在代码块中）
            if line.startswith("## ") and not line.startswith("### "):
                # 保存前一个块
                self._save_current_chunk(current_chunk, current_content, chunks)

                # 开始新块
                title = line[3:].strip()

                # 检查这个标题是否应该修改长度限制
                should_modify_length = self.should_modify(title)

                current_chunk = self._create_chunk(
                    title,
                    2,
                    "",
                    metadata,
                    len(chunks) + 1,
                    should_modify_length,  # True表示需要修改长度限制
                )
                current_content = [line]

            # 如果这是第一个块且还没有开始任何块，需要处理元数据结束后的空行
            elif current_chunk is None and line.strip() == "":
                if not chunks:  # 还没有任何块
                    current_chunk = self._create_chunk(
                        "元数据后空行",
                        1,
                        "",
                        metadata,
                        0,
                        False,
                    )
                    current_content = []

            # 检查是否为三级标题（不在代码块中）
            elif line.startswith("### ") and not in_code_block:
                # 使用二级标题时设置的修改长度标记
                should_modify_length = current_chunk.get("modify_length", False) if current_chunk else False

                # 如果需要修改长度限制，只在内容过长时分割
                if (
                    current_chunk
                    and should_modify_length
                    and self._get_content_length(current_content) > self.max_chunk_length
                ):
                    # 保存当前块
                    self._save_current_chunk(current_chunk, current_content, chunks)

                    # 开始新的三级标题块
                    title = line[4:].strip()
                    current_chunk = self._create_chunk(
                        f"{current_chunk['title']} - {title}",
                        3,
                        "",
                        metadata,
                        len(chunks) + 1,
                    )
                    current_content = [line]
                # 如果不需要修改长度限制，任何情况下都不分割
                else:
                    # 继续添加到当前块
                    current_content.append(line)

            else:
                # 普通内容行
                current_content.append(line)

        # 保存最后一个块
        self._save_current_chunk(current_chunk, current_content, chunks)

        # 添加元数据块
        if metadata_lines and self.preserve_metadata:
            metadata_chunk = self._create_chunk(
                "文档元数据",
                0,
                "\n".join(metadata_lines),
                metadata,
                0,
                False,
            )
            chunks.insert(0, metadata_chunk)

        return chunks

    def process_file(self, file_path: str) -> List[Dict]:
        """处理Markdown文件"""
        content = self.read_markdown_file(file_path)
        return self.split_by_headings(content)

    def export_chunks_to_json(self, chunks: List[Dict], output_path: str) -> None:
        """将分块结果导出为JSON文件"""
        def _export():
            # 简化chunks，只保留指定字段
            simplified_chunks = [self._simplify_chunk_for_export(chunk) for chunk in chunks]

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(simplified_chunks, f, ensure_ascii=False, indent=2)
            print(f"分块结果已导出到: {output_path}")

        self._safe_file_operation("导出JSON", _export)

    def json_to_chunks_view(self, json_file_path: str, output_path: str) -> None:
        """从JSON文件读取分块结果并导出为可读的Markdown视图文件"""
        def _export():
            # 从JSON文件读取chunks
            with open(json_file_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("# 文档分块结果\n\n")
                for i, chunk in enumerate(chunks, 1):
                    f.write(f"## 块 {i}: {chunk['title']}\n\n")
                    f.write(f"**级别**: {'二级' if chunk['level'] == 2 else '三级'}\n")
                    f.write(f"**长度**: {chunk['length']} 字符\n\n")
                    f.write("**内容**:\n\n")
                    f.write(chunk["content"])
                    f.write("\n\n---\n\n")
            print(f"分块结果视图已导出到: {output_path}")

        self._safe_file_operation("导出分块视图", _export)

    def json_to_full_markdown(self, json_file_path: str, key="rewritten_content", fallback_key="content") -> str:
        """从JSON文件读取chunks并重构完整的Markdown内容
        
        Args:
            json_file_path: JSON文件路径
            key: 主要的内容字段名
            fallback_key: 备选的内容字段名，如果key不存在则使用此字段
        """
        def _export():
            with open(json_file_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)

            # 重新拼接分块后的内容，恢复原始Markdown文件
            # 如果没有key，则使用fallback_key，如果都没有则使用空字符串
            reconstructed_lines = []
            for chunk in chunks:
                # 尝试获取主要字段
                content = chunk.get(key)
                if content is not None:
                    reconstructed_lines.append(content)
                else:
                    # 尝试获取备选字段
                    fallback_content = chunk.get(fallback_key)
                    if fallback_content is not None:
                        reconstructed_lines.append(fallback_content)
                    else:
                        # 如果都没有，尝试找到任何可用的内容字段
                        # 排除一些不应该作为内容的字段
                        excluded_keys = {"title", "level", "length", "modify_length"}
                        available_keys = [
                            k for k, v in chunk.items() 
                            if isinstance(v, str) and v.strip() and k not in excluded_keys
                        ]
                        if available_keys:
                            # 使用第一个可用的内容字段
                            reconstructed_lines.append(chunk[available_keys[0]])
                        else:
                            # 如果没有任何内容字段，使用空字符串
                            reconstructed_lines.append("")
            
            return "\n".join(reconstructed_lines)

        return self._safe_file_operation("重构Markdown", _export)

    def export_full_markdown(self, json_file_path: str, output_path: str) -> None:
        """从JSON文件重构并导出完整的Markdown文件"""
        def _export():
            reconstructed_content = self.json_to_full_markdown(json_file_path)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(reconstructed_content)
            print(f"重构的完整Markdown文件已导出到: {output_path}")

        self._safe_file_operation("导出完整Markdown", _export)

    def get_chunks_summary(self, chunks: List[Dict]) -> Dict:
        """获取分块统计摘要"""
        if not chunks:
            return {
                "total_chunks": 0,
                "level_2_chunks": 0,
                "level_3_chunks": 0,
                "total_length": 0,
                "average_length": 0,
                "max_chunk_length": 0,
                "min_chunk_length": 0,
            }

        total_chunks = len(chunks)
        level_2_chunks = sum(1 for c in chunks if c["level"] == 2)
        level_3_chunks = sum(1 for c in chunks if c["level"] == 3)
        total_length = sum(c["length"] for c in chunks)
        avg_length = total_length / total_chunks

        return {
            "total_chunks": total_chunks,
            "level_2_chunks": level_2_chunks,
            "level_3_chunks": level_3_chunks,
            "total_length": total_length,
            "average_length": round(avg_length, 2),
            "max_chunk_length": max(c["length"] for c in chunks),
            "min_chunk_length": min(c["length"] for c in chunks),
        }

    def get_chunks_by_title(self, chunks: List[Dict], title_keyword: str) -> List[Dict]:
        """根据标题关键词查找块"""
        return [chunk for chunk in chunks if title_keyword.lower() in chunk["title"].lower()]

    def get_chunks_by_length_range(self, chunks: List[Dict], min_length: int = 0, max_length: int = None) -> List[Dict]:
        """根据长度范围筛选块"""
        if max_length is None:
            return [chunk for chunk in chunks if chunk["length"] >= min_length]
        return [chunk for chunk in chunks if min_length <= chunk["length"] <= max_length]


def generate_output_filenames(source_file_path: str, output_dir: Path) -> Dict[str, Path]:
    """根据源文件路径生成唯一的输出文件名"""
    # 获取源文件名（不含扩展名）
    source_filename = Path(source_file_path).stem

    # 生成唯一的输出文件名
    filenames = {
        "json": output_dir / f"{source_filename}_chunks.json",
        "chunks_view": output_dir / f"{source_filename}_chunks_view.md",
        "reconstructed": output_dir / f"{source_filename}_reconstructed.md"
    }

    return filenames


def batch_process_markdown_files(file_paths: List[str], output_dir: str = None, max_chunk_length: int = 2000) -> Dict[str, Dict[str, str]]:
    """批量处理多个Markdown文件
    
    Args:
        file_paths: Markdown文件路径列表
        output_dir: 输出目录，如果为None则使用默认的baicai_tutor/output
        max_chunk_length: 最大块长度
    
    Returns:
        处理结果字典，格式为 {源文件路径: {输出文件类型: 输出文件路径}}
    """
    # 确定输出目录
    if output_dir is None:
        output_dir = Path.home() / ".baicai" / "textbook"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(exist_ok=True)

    # 创建处理器
    processor = MarkdownProcessor(max_chunk_length=max_chunk_length, preserve_metadata=True)

    def process_single_file(file_path: str) -> Dict[str, str]:
        """处理单个文件的内部函数"""
        try:
            print(f"正在处理: {file_path}")

            # 处理文件
            chunks = processor.process_file(file_path)
            print(f"  - 分块完成: {len(chunks)} 个块")

            # 生成输出文件名
            filenames = generate_output_filenames(file_path, output_dir)

            # 导出文件
            processor.export_chunks_to_json(chunks, str(filenames["json"]))
            processor.json_to_chunks_view(str(filenames["json"]), str(filenames["chunks_view"]))
            processor.export_full_markdown(str(filenames["json"]), str(filenames["reconstructed"]))

            print(f"  - 导出完成: {filenames['json'].name}")

            return {
                "json": str(filenames["json"]),
                "chunks_view": str(filenames["chunks_view"]),
                "reconstructed": str(filenames["reconstructed"]),
                "chunks_count": len(chunks)
            }

        except Exception as e:
            print(f"  - 处理失败: {e}")
            return {"error": str(e)}

    # 处理所有文件
    results = {file_path: process_single_file(file_path) for file_path in file_paths}

    return results


def main():
    print("MarkdownProcessor 功能演示")
    print("=" * 40)

    # 计算路径 - 只计算一次
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    baicai_tutor_root = os.path.dirname(current_file_dir)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))
    test_file = os.path.join(project_root, "baicai_webui", "AI_intro_book", "第5章 人工智能的关键：学习.md")

    try:
        if not Path(test_file).exists():
            print(f"测试文件不存在: {test_file}")
            return

        # 基本处理 - 只创建一次处理器实例
        processor = MarkdownProcessor(
            max_chunk_length=2000,
            preserve_metadata=True,
            modify_length_for_titles=["动手实践", "应用案例", "课后练习", "参考答案"]
        )
        chunks = processor.process_file(test_file)
        print(f"成功处理文件，共分块 {len(chunks)} 个")

        # 统计信息
        summary = processor.get_chunks_summary(chunks)
        print(f"文档统计: {summary['total_chunks']} 块, 平均长度: {summary['average_length']} 字符")

        # 导出功能 - 使用已计算的路径，生成唯一文件名
        output_dir = Path.home() / ".baicai" / "textbook"
        output_dir.mkdir(exist_ok=True)

        # 生成基于源文件的唯一文件名
        filenames = generate_output_filenames(test_file, output_dir)

        # 批量导出所有文件
        export_operations = [
            (processor.export_chunks_to_json, chunks, str(filenames["json"])),
            (processor.json_to_chunks_view, str(filenames["json"]), str(filenames["chunks_view"])),
            (processor.export_full_markdown, str(filenames["json"]), str(filenames["reconstructed"]))
        ]

        for operation, *args in export_operations:
            operation(*args)

        print(f"所有文件已导出到: {output_dir}")
        print("输出文件:")
        for key, path in filenames.items():
            print(f"  - {key}: {path.name}")

    except Exception as e:
        print(f"处理失败: {e}")

    # 显示使用示例
    print("\n" + "="*60 + "\n")
    simple_usage_example()


def simple_usage_example():
    """简单使用示例 - 展示优化后的工作流程"""
    print("MarkdownProcessor 优化后的使用示例")
    print("=" * 50)

    # 示例：假设你已经有了JSON分块文件
    source_file = "第1章 你好，人工智能！.md"
    output_dir = "output"

    print("工作流程:")
    print("1. 查看分块结果:")
    print(f"   processor.json_to_chunks_view('{source_file}_chunks.json', '{output_dir}/{source_file}_chunks_view.md')")
    print()
    print("2. 重构完整文档:")
    print(f"   processor.export_full_markdown('{source_file}_chunks.json', '{output_dir}/{source_file}_reconstructed.md')")
    print()
    print("3. 或者直接获取重构内容:")
    print(f"   content = processor.json_to_full_markdown('{source_file}_chunks.json')")
    print()
    print("4. 批量处理多个文件:")
    print("   markdown_files = ['file1.md', 'file2.md', 'file3.md']")
    print("   results = batch_process_markdown_files(markdown_files)")
    print("   # 自动生成唯一文件名:")
    print("   # - file1_chunks.json, file1_chunks_view.md, file1_reconstructed.md")
    print("   # - file2_chunks.json, file2_chunks_view.md, file2_reconstructed.md")
    print("   # - file3_chunks.json, file3_chunks_view.md, file3_reconstructed.md")
    print()
    print("5. 自定义输出目录:")
    print("   results = batch_process_markdown_files(markdown_files, output_dir='custom_output')")
    print()
    print("优化说明:")
    print("- 删除了不必要的 reconstruct_markdown() 函数")
    print("- 统一了函数命名规范")
    print("- 简化了参数传递")
    print("- 专注于JSON到Markdown的转换流程")
    print("- 支持多文件处理，自动生成唯一文件名")
    print("- 提供批量处理函数，提高效率")


if __name__ == "__main__":
    # 运行主演示
    main()
