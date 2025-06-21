import json
import re
import os

class Format_json2Sub:
    def __init__(self, json_result, min_length):
        self.json_result = json_result
        self.min_length = min_length

    def format_time(self,ms):
        """将毫秒转换为SRT时间格式 (HH:MM:SS,mmm)"""
        seconds, milliseconds = divmod(ms, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def align_text_with_timestamps(self,text, timestamps):
        """
        对齐带标点的文本和原始时间戳
        返回新的时间戳数组，其中标点符号的时间戳使用相邻字符的时间戳
        """
        # 中文标点符号集合
        punctuation = r'[，。！？；：、（）《》【】"「」『』"“”‘’…—]'

        aligned_timestamps = []
        char_index = 0  # 原始字符索引（不包括标点）
        new_text = ""

        for char in text:
            if re.match(punctuation, char):
                # 标点符号：使用前一个字符的时间戳
                if aligned_timestamps:
                    aligned_timestamps.append(aligned_timestamps[-1].copy())
                else:
                    aligned_timestamps.append(timestamps[0].copy() if timestamps else [0, 0])
                new_text += char
            else:
                # 非标点字符：使用原始时间戳
                if char_index < len(timestamps):
                    aligned_timestamps.append(timestamps[char_index])
                    new_text += char
                    char_index += 1
                else:
                    break

        # 处理末尾多余的时间戳
        if char_index < len(timestamps):
            print(f"警告: 有 {len(timestamps) - char_index} 个未使用的时间戳")

        return new_text, aligned_timestamps

    def smart_split_sentences(self,text, timestamps, min_length=5):
        """
        智能分句：基于标点符号的分割逻辑
        参数:
            min_length: 分段的最小字符长度（避免过短分段）
        """
        # 标点符号定义
        end_punctuation = r'[。！？]'  # 句尾标点（必须分割）
        mid_punctuation = r'[，；：、]'  # 句中标点（条件分割）

        segments = []
        current_segment = []
        current_timestamps = []
        current_start = timestamps[0][0] if timestamps else 0

        for i, char in enumerate(text):
            if i >= len(timestamps):
                break

            current_segment.append(char)
            current_timestamps.append(timestamps[i])

            # 检查当前字符是否是标点
            is_end_punc = re.match(end_punctuation, char) is not None
            is_mid_punc = re.match(mid_punctuation, char) is not None

            # 分割条件：
            # 1. 遇到句尾标点（必须分割）
            # 2. 遇到句中标点且当前分段长度足够（避免过短分段）
            if is_end_punc or (is_mid_punc and len(''.join(current_segment)) >= min_length):
                segment_text = ''.join(current_segment)
                segment_end = timestamps[i][1]

                segments.append((segment_text, current_start, segment_end))

                # 重置当前分段
                current_segment = []
                current_timestamps = []
                if i + 1 < len(timestamps):
                    current_start = timestamps[i + 1][0]

        # 添加最后一段
        if current_segment:
            segment_text = ''.join(current_segment)
            segment_end = current_timestamps[-1][1] if current_timestamps else current_start
            segments.append((segment_text, current_start, segment_end))

        return segments

    def json_to_srt(self,json_data, min_length=5):
        """
        将FunASR JSON转换为SRT字幕
        参数:
            min_length: 分段的最小字符长度（避免过短分段）
        """
        srt_lines = []

        # 确保json_data是字典
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                print("错误: 无法解析JSON字符串")
                return ""

        # 检查必需字段
        if "text" not in json_data or "timestamp" not in json_data:
            print("错误: JSON缺少必要字段 'text' 或 'timestamp'")
            return ""

        raw_text = json_data["text"]
        raw_timestamps = json_data["timestamp"]

        # 检查数据有效性
        if not raw_text or not raw_timestamps:
            return ""

        # 对齐文本和时间戳
        aligned_text, aligned_timestamps = self.align_text_with_timestamps(raw_text, raw_timestamps)

        # 验证对齐后的长度
        if len(aligned_text) != len(aligned_timestamps):
            print(f"警告: 对齐后长度仍不匹配 (文本: {len(aligned_text)}, 时间戳: {len(aligned_timestamps)})")
            min_len = min(len(aligned_text), len(aligned_timestamps))
            aligned_text = aligned_text[:min_len]
            aligned_timestamps = aligned_timestamps[:min_len]

        # 智能分句（基于标点符号）
        segments = self.smart_split_sentences(aligned_text, aligned_timestamps, min_length)

        # 生成SRT
        for idx, (text, start_time, end_time) in enumerate(segments, 1):
            srt_lines.append(f"{idx}\n"
                             f"{self.format_time(start_time)} --> {self.format_time(end_time)}\n"
                             f"{text.strip()}\n\n")

        return "".join(srt_lines)

    def run_format(self, output=None):
        # print(rec_result)
        try:
            json_data = json.loads(self.json_result)
        except json.JSONDecodeError:
            print("尝试直接处理JSON内容...")
        srt_content = self.json_to_srt(json_data, min_length=self.min_length)
        if not srt_content:
            print("错误: 无法生成SRT内容")
            exit(1)
        if output is not None:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(srt_content)
        return srt_content