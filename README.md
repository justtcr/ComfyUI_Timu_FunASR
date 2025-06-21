## ComfyUI_Timu_FunASR

***

语音识别技术基于阿里通义实验室的[FunASR](https://github.com/modelscope/FunASR)语音识别项目，ComfyUI节点代码基于[avenstack
\ComfyUI-AV-FunASR](https://github.com/avenstack/ComfyUI-AV-FunASR)的节点进行了优化。让comfyui也能实现快速语音识别，生成流畅自然的SRT字幕。

## 功能特色

***

- 🥖 语音转自然文本

- 🧀 语音转SRT字幕，可选择是否带标点符号

## 安装

***

😀首先你的有自己的**comfyui**：

```
cd ComfyUI/custom_nodes
git clone https://github.com/justtcr/ComfyUI_Timu_FunASR.git
cd ComfyUI-AV-FunASR
pip install -r requirements.txt
```

## 模型下载

模型来源于魔塔平台

1. 🦻🏼 [语音识别](https://modelscope.cn/models/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch/files)
2. 🎶 [语音端点检测](modelscope.cn/models/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch/files)
3. ❗ [断剧和标点恢复](https://www.modelscope.cn/models/iic/punc_ct-transformer_cn-en-common-vocab471067-large)

模型存放目录：`models/ASR/FunASR/iic`
```
 iic
    ├── speech_fsmn_vad_zh-cn-16k-common-pytorch
    │   ├── README.md
    │   ├── am.mvn
    │   ├── config.yaml
    │   ├── configuration.json
    │   ├── example
    │   ├── fig
    │   └── model.pt
    ├── speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
    │   ├── README.md
    │   ├── am.mvn
    │   ├── asr_example_hotword.wav
    │   ├── config.yaml
    │   ├── configuration.json
    │   ├── example
    │   ├── fig
    │   ├── model.pt
    │   ├── seg_dict
    │   └── tokens.json
    └── punc_ct-transformer_cn-en-common-vocab471067-large
        ├── fig
        ├── .mdl
        ├── .msc
        ├── .mv
        ├── config.yaml
        ├── configuration.json
        ├── jieba.c.dict
        ├── jieba_usr_dict
        ├── model.pt
        ├── README.md
        └── tokens.json
```

## 鸣谢🦀

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [avenstack ComfyUI-AV-FunASR](https://github.com/avenstack/ComfyUI-AV-FunASR)
