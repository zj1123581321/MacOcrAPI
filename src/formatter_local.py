"""
本地智能分段排版模块
根据 OCR 结果的坐标信息进行智能排版
"""
import logging
from typing import List, Tuple
from dataclasses import dataclass

from .models import OCRResult, FormattedResult

logger = logging.getLogger(__name__)


@dataclass
class TextBlock:
    """文本块，包含文本和位置信息"""
    text: str
    x: float  # 左上角 x
    y: float  # 左上角 y
    width: float
    height: float
    score: float

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    @property
    def bottom_y(self) -> float:
        return self.y + self.height


def _ocr_result_to_block(result: OCRResult) -> TextBlock:
    """将 OCRResult 转换为 TextBlock"""
    boxes = result.dt_boxes
    # dt_boxes 格式: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
    x1, y1 = boxes[0]
    x2, y2 = boxes[2]
    return TextBlock(
        text=result.rec_txt,
        x=x1,
        y=y1,
        width=x2 - x1,
        height=y2 - y1,
        score=result.score
    )


def _group_into_lines(blocks: List[TextBlock], y_threshold_ratio: float = 0.5) -> List[List[TextBlock]]:
    """
    将文本块按行分组
    y_threshold_ratio: Y 坐标差异阈值（相对于行高的比例）
    """
    if not blocks:
        return []

    # 按 Y 坐标排序
    sorted_blocks = sorted(blocks, key=lambda b: b.y)

    lines: List[List[TextBlock]] = []
    current_line: List[TextBlock] = [sorted_blocks[0]]

    for block in sorted_blocks[1:]:
        # 使用当前行的平均高度计算阈值
        avg_height = sum(b.height for b in current_line) / len(current_line)
        y_threshold = avg_height * y_threshold_ratio

        # 检查是否属于同一行
        current_line_center_y = sum(b.center_y for b in current_line) / len(current_line)
        if abs(block.center_y - current_line_center_y) <= y_threshold:
            current_line.append(block)
        else:
            # 新行
            lines.append(current_line)
            current_line = [block]

    # 添加最后一行
    if current_line:
        lines.append(current_line)

    # 每行内按 X 坐标排序
    for line in lines:
        line.sort(key=lambda b: b.x)

    return lines


def _detect_paragraph_breaks(lines: List[List[TextBlock]],
                             gap_threshold_ratio: float = 1.5) -> List[int]:
    """
    检测段落分隔位置
    返回需要在其前面添加空行的行索引列表
    """
    if len(lines) <= 1:
        return []

    paragraph_breaks = []
    line_gaps = []

    # 计算相邻行之间的间距
    for i in range(1, len(lines)):
        prev_line = lines[i - 1]
        curr_line = lines[i]

        prev_bottom = max(b.bottom_y for b in prev_line)
        curr_top = min(b.y for b in curr_line)
        gap = curr_top - prev_bottom
        line_gaps.append(gap)

    if not line_gaps:
        return []

    # 计算平均行间距
    avg_gap = sum(line_gaps) / len(line_gaps)

    # 检测大间距（段落分隔）
    for i, gap in enumerate(line_gaps):
        if avg_gap > 0 and gap > avg_gap * gap_threshold_ratio:
            paragraph_breaks.append(i + 1)

    return paragraph_breaks


def _is_potential_heading(line: List[TextBlock],
                          all_lines: List[List[TextBlock]],
                          image_width: float) -> bool:
    """
    判断一行是否可能是标题
    启发式规则：
    - 独立短行
    - 居中或靠左
    - 文本较短
    """
    if not line:
        return False

    # 合并行文本
    line_text = " ".join(b.text for b in line)

    # 标题通常较短
    if len(line_text) > 50:
        return False

    # 计算行宽度占比
    line_start = min(b.x for b in line)
    line_end = max(b.x + b.width for b in line)
    line_width = line_end - line_start

    # 如果行宽度小于图像宽度的 60%，可能是标题
    if image_width > 0 and line_width < image_width * 0.6:
        # 检查是否居中或靠左
        center_x = (line_start + line_end) / 2
        image_center = image_width / 2

        # 居中（中心偏移小于 20%）或靠左
        is_centered = abs(center_x - image_center) < image_width * 0.2
        is_left_aligned = line_start < image_width * 0.15

        if is_centered or is_left_aligned:
            return True

    return False


def format_locally(results: List[OCRResult],
                   image_size: Tuple[int, int]) -> FormattedResult:
    """
    使用本地算法对 OCR 结果进行智能排版

    Args:
        results: OCR 结果列表
        image_size: 图像尺寸 (width, height)

    Returns:
        FormattedResult 包含排版后的 markdown 文本
    """
    try:
        if not results:
            return FormattedResult(markdown="", success=True)

        image_width, image_height = image_size

        # 转换为 TextBlock
        blocks = [_ocr_result_to_block(r) for r in results]

        # 按行分组
        lines = _group_into_lines(blocks)

        if not lines:
            return FormattedResult(markdown="", success=True)

        # 检测段落分隔
        paragraph_breaks = set(_detect_paragraph_breaks(lines))

        # 构建 markdown
        markdown_parts = []

        for i, line in enumerate(lines):
            # 合并行内文本
            line_text = " ".join(b.text for b in line)

            # 检查是否是段落开始
            if i in paragraph_breaks:
                markdown_parts.append("")  # 空行表示段落分隔

            # 检查是否是标题
            if _is_potential_heading(line, lines, image_width):
                # 简单标题检测：使用 ## 标记
                # 如果是第一行且较短，用 #
                if i == 0 and len(line_text) < 30:
                    markdown_parts.append(f"# {line_text}")
                else:
                    markdown_parts.append(f"## {line_text}")
            else:
                markdown_parts.append(line_text)

        # 合并段落内的连续行
        markdown = _merge_paragraphs(markdown_parts)

        logger.debug(f"本地排版完成，共 {len(lines)} 行")
        return FormattedResult(markdown=markdown, success=True)

    except Exception as e:
        logger.error(f"本地排版失败: {str(e)}")
        return FormattedResult(
            markdown="",
            success=False,
            error=str(e)
        )


def _merge_paragraphs(parts: List[str]) -> str:
    """
    合并段落内的连续行
    空字符串表示段落分隔
    """
    if not parts:
        return ""

    result_lines = []
    current_paragraph = []

    for part in parts:
        if part == "":
            # 段落分隔
            if current_paragraph:
                result_lines.append(" ".join(current_paragraph))
                current_paragraph = []
            result_lines.append("")
        elif part.startswith("#"):
            # 标题单独成行
            if current_paragraph:
                result_lines.append(" ".join(current_paragraph))
                current_paragraph = []
            result_lines.append(part)
        else:
            current_paragraph.append(part)

    # 处理最后一个段落
    if current_paragraph:
        result_lines.append(" ".join(current_paragraph))

    # 移除开头和结尾的空行，保留中间的段落分隔
    while result_lines and result_lines[0] == "":
        result_lines.pop(0)
    while result_lines and result_lines[-1] == "":
        result_lines.pop()

    return "\n\n".join(line for line in result_lines if line or result_lines.count("") > 0).replace("\n\n\n", "\n\n")
