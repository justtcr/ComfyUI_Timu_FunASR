import os
import re


class Deletepunc:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "srt_text": ("STRING",),
                "Delete_Puncutuaion": (["enable", "disable"],),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("NoPuncText",)
    FUNCTION = "Depunc"
    CATEGORY = "LightFeather/Timu-FunASR"
    DESCRIPTION = "Delete all punctuation from srttext"

    def Depunc(self, srt_text, Delete_Puncutuaion):
        if Delete_Puncutuaion == "disable":
            return (srt_text,)

        punctuation_pattern = r'[^\w\s]'
        lines = srt_text.split('\n')  # 将字符串按行分割

        processed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if re.match(r'^\d+$', line):  # 检查是否为序号
                processed_lines.append(line)
                i += 1
                continue

            if re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line):  # 检查是否为时间戳
                processed_lines.append(line)
                i += 1
                continue

            # 假设接下来的是字幕内容
            subtitle_line = line.strip()
            # 替换句尾的标点符号为空字符串
            subtitle_line = re.sub(punctuation_pattern + '$', '', subtitle_line)
            # 替换其他位置的标点符号为空格
            subtitle_line = re.sub(punctuation_pattern, ' ', subtitle_line)
            processed_lines.append(subtitle_line)
            i += 1

        nopunc_text = '\n'.join(processed_lines)  # 将处理后的行重新组合成字符串

        return (nopunc_text,)


NODE_CLASS_MAPPINGS = {
    "Deletepunc": Deletepunc,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Deletepunc": "Delete SRT punc",
}