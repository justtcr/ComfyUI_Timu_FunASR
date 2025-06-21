import folder_paths
import os
import comfy.model_management as mm
import time
import torchaudio
import torchvision.utils as vutils
import torch
import json
import uuid
from comfy.comfy_types import FileLocator

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from funasr import AutoModel
from .format import Format_json2Sub



name_maps_ms = {
    "paraformer": "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    "paraformer-zh": "iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    "paraformer-en": "iic/speech_paraformer-large-vad-punc_asr_nat-en-16k-common-vocab10020",
    "paraformer-en-spk": "iic/speech_paraformer-large-vad-punc_asr_nat-en-16k-common-vocab10020",
    "paraformer-zh-streaming": "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online",
    "fsmn-vad": "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
    "ct-punc": "iic/punc_ct-transformer_cn-en-common-vocab471067-large",
    "ct-punc-c": "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
    "fa-zh": "iic/speech_timestamp_prediction-v1-16k-offline",
    "cam++": "iic/speech_campplus_sv_zh-cn_16k-common",
    "Whisper-large-v2": "iic/speech_whisper-large_asr_multilingual",
    "Whisper-large-v3": "iic/Whisper-large-v3",
    "Qwen-Audio": "Qwen/Qwen-Audio",
    "emotion2vec_plus_large": "iic/emotion2vec_plus_large",
    "emotion2vec_plus_base": "iic/emotion2vec_plus_base",
    "emotion2vec_plus_seed": "iic/emotion2vec_plus_seed",
    "Whisper-large-v3-turbo": "iic/Whisper-large-v3-turbo",
}


class AsrRun2json:
    infer_ins_cache = None
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "batch_size_s": ("INT", {"default": 300, "min": 30, "max": 300, "step": 1}),
                "unload_model": ("BOOLEAN", {"default": False}),
                "hotkey": ("STRING",{"multiline":True, "default":"热词", "lazy":True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "json_result")
    FUNCTION = "infer"
    CATEGORY = "LightFeather/Timu-FunASR"
    DESCRIPTION = "get speech timestamp"

    def infer(self, audio, batch_size_s, unload_model,hotkey):
        temp_dir = folder_paths.get_temp_directory()
        os.makedirs(temp_dir, exist_ok=True)

        if AsrRun2json.infer_ins_cache is None:
            model_root = os.path.join(folder_paths.models_dir, "ASR/FunASR")
            model_dir = os.path.join(model_root, name_maps_ms["paraformer-zh"])
            vad_model = os.path.join(model_root, name_maps_ms["fsmn-vad"])
            func_model = os.path.join(model_root, name_maps_ms["ct-punc"])
            os.makedirs(model_dir, exist_ok=True)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            AsrRun2json.infer_ins_cache = AutoModel(
                model=model_dir,
                vad_model=vad_model,
                punc_model=func_model,
                device=device,  # GPU加速
                disable_update=True
            )
        # save 
        uuidv4 = str(uuid.uuid4())
        audio_save_path = os.path.join(temp_dir, f"{uuidv4}.wav")
        # 重新采样为16k
        waveform = audio['waveform']
        sr = audio["sample_rate"]
        waveform = torchaudio.functional.resample(waveform, sr, 16000)
        torchaudio.save(audio_save_path, waveform.squeeze(0), 16000)

        rec_result = AsrRun2json.infer_ins_cache.generate(input=audio_save_path, batch_size_s=batch_size_s,hotword=hotkey)
        # print(rec_result)
        if rec_result:
            rec_result = rec_result[0]

        # infer
        if unload_model:
            import gc
            if AsrRun2json.infer_ins_cache is not None:
                AsrRun2json.infer_ins_cache = None
                gc.collect()
                torch.cuda.empty_cache()
                print("AsrRun2json memory cleanup successful")
        # jr = json.dumps(rec_result, indent=4)
        text = rec_result.get("text")
        jr = json.dumps(rec_result, ensure_ascii=False)
        # print((text, jr, rec_result))
        return (text, jr)




class SubtitleFunc:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "gen_text":  ("STRING",),
            },
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("FuncText", )
    FUNCTION = "text2func"
    CATEGORY = "LightFeather/Timu-FunASR"
    DESCRIPTION = "make text func"

    def text2func(self, gen_text):
        model_root = os.path.join(folder_paths.models_dir, "ASR/FunASR")
        func_model = os.path.join(model_root, name_maps_ms["ct-punc"])
        device = "cuda" if torch.cuda.is_available() else "cpu"
        infer_func = AutoModel(model=func_model,device=device, disable_update=True)

        func_result = infer_func.generate(input=gen_text)
        if func_result:
            func_result = func_result[0]
        out_text = func_result.get("text")
        return (out_text,)


class json2Srt:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_result": ("STRING",),
                "min_length":  ("INT", {"default": 5,"min": 1,"max": 8,"step": 1,"display": "number"}),

            },
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("subtitle", )
    FUNCTION = "format_subtitle"
    CATEGORY = "LightFeather/Timu-FunASR"
    DESCRIPTION = "format asr result to subtitle"

    def format_subtitle(self, json_result, min_length):
        f = Format_json2Sub(json_result, min_length)
        content = f.run_format()
        
        return (content, )
    

class SaveSubtitles:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "subtitles": ("STRING", {"tooltip": "The subtitles to save."}),
                "filename_prefix": ("STRING", {"default": "subtitles", "tooltip": "The prefix for the file to save. "})
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_subtitles"

    OUTPUT_NODE = True

    CATEGORY = "LightFeather/Timu-FunASR"
    DESCRIPTION = "Saves the subtitles to a file."

    def save_subtitles(self, subtitles, filename_prefix="subtitles"):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir)
        results: list[FileLocator] = []

        file = f"{filename}_{counter:05}_.srt"
        with open(os.path.join(full_output_folder, file), 'w', encoding='utf-8') as f:
            f.write(subtitles)
        results.append({
            "filename": file,
            "subfolder": subfolder,
            "type": self.type
        })
        counter += 1

        return { "ui": { "subtitles": results } }


    

NODE_CLASS_MAPPINGS = {
    "AsrRun2json": AsrRun2json,
    "SubtitleFunc": SubtitleFunc,
    "json2Srt": json2Srt,
    "SaveSubtitles": SaveSubtitles,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AsrRun2json": "FunASR Speech Recognition",
    "SubtitleFunc": "Text Find Punc",
    "json2Srt": "Format json to Srt",
    "SaveSubtitles": "Save Srt",
}