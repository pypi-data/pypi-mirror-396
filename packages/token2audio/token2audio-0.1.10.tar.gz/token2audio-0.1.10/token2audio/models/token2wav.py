import io
import time
import base64
import logging
from typing import List, Dict, Any
import tempfile
import os

import torch
import torchaudio
import s3tokenizer
import onnxruntime
import numpy as np
import librosa
from scipy.io import wavfile
import psutil

import torchaudio.compliance.kaldi as kaldi
from token2audio.flashcosyvoice.flashcosyvoice.modules.hifigan import HiFTGenerator
from token2audio.flashcosyvoice.flashcosyvoice.utils.audio import mel_spectrogram
from hyperpyyaml import load_hyperpyyaml

logger = logging.getLogger(__name__)


def fade_in_out(
    fade_in_mel: torch.Tensor, fade_out_mel: torch.Tensor, window: torch.Tensor
):
    """perform fade_in_out in tensor style"""
    mel_overlap_len = int(window.shape[0] / 2)
    fade_in_mel = fade_in_mel.clone()
    fade_in_mel[..., :mel_overlap_len] = (
        fade_in_mel[..., :mel_overlap_len] * window[:mel_overlap_len]
        + fade_out_mel[..., -mel_overlap_len:] * window[mel_overlap_len:]
    )
    return fade_in_mel


class Token2wav:
    """Token2Audio 模型类，负责音频合成"""

    def __init__(
        self,
        model_path: str,
        voice_list: List[Dict[str, str]],
        float16: bool = False,
        use_rocm: bool = False,
    ):
        self.float16 = float16
        self.use_rocm = use_rocm
        self.health_status = True
        self.voice_list = voice_list

        # 检测可用的设备
        if torch.cuda.is_available():
            self.device = "cuda"
            if use_rocm:
                logger.info(f"使用 ROCm GPU: {torch.cuda.get_device_name()}")
            else:
                logger.info(f"使用 CUDA GPU: {torch.cuda.get_device_name()}")
        else:
            self.device = "cpu"
            logger.info("使用 CPU")

        # 加载音频分词器
        self.audio_tokenizer = (
            s3tokenizer.load_model(f"{model_path}/speech_tokenizer_v2_25hz.onnx")
            .to(self.device)
            .eval()
        )

        # ONNX 运行时配置 - AMD 优化
        option = onnxruntime.SessionOptions()
        option.graph_optimization_level = (
            onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
        )

        # AMD CPU 优化：使用更多线程
        cpu_count = psutil.cpu_count(logical=True)
        option.intra_op_num_threads = min(cpu_count, 8)  # 限制最大线程数
        option.inter_op_num_threads = min(cpu_count // 2, 4)  # 并行操作线程数

        # 选择执行提供者
        if use_rocm and torch.cuda.is_available():
            providers = ["ROCMExecutionProvider", "CPUExecutionProvider"]
        else:
            providers = ["CPUExecutionProvider"]

        self.spk_model = onnxruntime.InferenceSession(
            f"{model_path}/campplus.onnx", sess_options=option, providers=providers
        )

        # 加载流模型配置
        with open(f"{model_path}/flow.yaml", "r") as f:
            configs = load_hyperpyyaml(f)
            self.flow = configs["flow"]
        if float16:
            self.flow.half()
        self.flow.load_state_dict(
            torch.load(f"{model_path}/flow.pt", map_location="cpu", weights_only=True),
            strict=True,
        )
        self.flow.to(self.device).eval()

        # 加载 HiFT 生成器
        self.hift = HiFTGenerator()
        hift_state_dict = {
            k.replace("generator.", ""): v
            for k, v in torch.load(
                f"{model_path}/hift.pt", map_location="cpu", weights_only=True
            ).items()
        }
        self.hift.load_state_dict(hift_state_dict, strict=True)
        self.hift.to(self.device).eval()

        self.cache = {}
        # 使用字典存储 prompt 缓存，根据 voice_list 提前加载
        self.prompt_caches = {}

        # 根据 voice_list 提前加载所有语音的缓存
        self._preload_voice_caches()

        # 流配置
        self.mel_cache_len = 8  # 硬编码，160ms
        self.source_cache_len = int(self.mel_cache_len * 480)  # 50hz mel -> 24kHz wave
        self.speech_window = torch.from_numpy(np.hamming(2 * self.source_cache_len)).to(
            self.device
        )

        # hifigan 缓存
        self.hift_cache_dict = {}
        self.stream_cache = None

    def _preload_voice_caches(self):
        """根据 voice_list 提前加载所有语音的缓存"""
        logger.info(f"开始预加载 {len(self.voice_list)} 个语音的缓存...")
        for voice_info in self.voice_list:
            voice_id = voice_info["voice_id"]
            voice_path = voice_info["path"]

            try:
                # 检查文件是否存在
                if not os.path.exists(voice_path):
                    logger.warning(f"语音文件不存在: {voice_path}")
                    continue

                # 加载并缓存语音数据
                prompt_dict = self._prepare_prompt(voice_path)
                self.prompt_caches[voice_id] = prompt_dict
                logger.info(f"成功预加载语音缓存: {voice_id}")

            except Exception as e:
                logger.error(f"预加载语音缓存失败 {voice_id}: {str(e)}")
                continue

        logger.info(f"语音缓存预加载完成，共加载 {len(self.prompt_caches)} 个语音")

    def get_voice_cache(self, voice_id: str):
        """根据 voice_id 获取预加载的语音缓存"""
        if voice_id not in self.prompt_caches:
            raise ValueError(f"语音 ID '{voice_id}' 未在预加载的缓存中找到")
        return self.prompt_caches[voice_id]

    @staticmethod
    def decode_audio(audio: str):
        """解码 base64 编码的音频数据"""
        if audio.startswith("data:"):
            media_type, data = audio[5:].split(",", 1)
            if media_type.endswith(";base64"):
                audio_data = base64.b64decode(data)
                audio_io = io.BytesIO(audio_data)
                # 使用 scipy 读取 WAV，避免 torchcodec 依赖
                sr, wav_int = wavfile.read(audio_io)
                # 转换为 float32 并归一化到 [-1, 1]
                wav = wav_int.astype(np.float32) / 32768.0
                # 转换为 [channels, samples] 格式
                if wav.ndim == 1:
                    wav = wav[np.newaxis, :]
                else:
                    wav = wav.T  # [samples, channels] -> [channels, samples]
                return torch.from_numpy(wav), sr
            else:
                raise ValueError("Invalid audio data, must be base64 encoded")
        else:
            raise ValueError("Invalid audio data protocol, must be start with 'data:'")

    @staticmethod
    def encode_wav(wav, sr):
        """编码音频为 base64"""
        if isinstance(wav, torch.Tensor):
            wav = wav.cpu().numpy()

        # 处理维度: [channels, samples] -> [samples] 或 [samples, channels]
        if wav.ndim == 2:
            wav = wav.squeeze(0)  # 单声道取第一个通道

        duration = len(wav) / sr

        # 使用 scipy 保存 WAV，避免 torchcodec 依赖
        wav = np.clip(wav, -1.0, 1.0)
        wav_int16 = (wav * 32767.0).astype(np.int16)

        with io.BytesIO() as wavio:
            wavfile.write(wavio, sr, wav_int16)
            audio_bytes = wavio.getvalue()
            encoded_wav = base64.b64encode(audio_bytes).decode("ascii")

        return encoded_wav, duration

    def _prepare_prompt(self, prompt_wav):
        """准备提示音频"""
        # 使用 librosa 加载音频，避免 torchcodec 问题
        audio, sr = librosa.load(prompt_wav, sr=16000)  # 直接加载为 16000 Hz
        audio = torch.from_numpy(audio).to(self.device)  # 转换为 torch tensor
        mels = s3tokenizer.log_mel_spectrogram(audio)
        mels, mels_lens = s3tokenizer.padding([mels])
        prompt_speech_tokens, prompt_speech_tokens_lens = self.audio_tokenizer.quantize(
            mels.to(self.device), mels_lens.to(self.device)
        )

        spk_feat = kaldi.fbank(
            audio.unsqueeze(0), num_mel_bins=80, dither=0, sample_frequency=16000
        )
        spk_feat = spk_feat - spk_feat.mean(dim=0, keepdim=True)
        spk_emb = torch.tensor(
            self.spk_model.run(
                None,
                {
                    self.spk_model.get_inputs()[0]
                    .name: spk_feat.unsqueeze(dim=0)
                    .cpu()
                    .numpy()
                },
            )[0],
            device=self.device,
        )

        # 使用 librosa 加载音频，避免 torchcodec 问题
        audio, sample_rate = librosa.load(prompt_wav, sr=24000)  # 直接加载为 24000 Hz
        audio = torch.from_numpy(audio).unsqueeze(0).to(self.device)  # [1, T]
        prompt_mel = mel_spectrogram(audio).transpose(1, 2).squeeze(0)  # [T, num_mels]
        prompt_mels = prompt_mel.unsqueeze(0).to(self.device)
        prompt_mels_lens = torch.tensor(
            [prompt_mels.shape[1]], dtype=torch.int32, device=self.device
        )
        prompt_mels = torch.nn.functional.pad(
            prompt_mels,
            (
                0,
                0,
                0,
                prompt_speech_tokens.shape[1] * self.flow.up_rate
                - prompt_mels.shape[1],
            ),
            mode="replicate",
        )
        return (
            prompt_speech_tokens,
            prompt_speech_tokens_lens,
            spk_emb,
            prompt_mels,
            prompt_mels_lens,
        )

    def _token2audio_impl_(self, prompt_audio_data: str, token: List[int]):
        """同步音频合成实现"""
        # Manage prompt caches
        prompt_key = hash(prompt_audio_data)
        if prompt_key not in self.prompt_caches:
            prompt_audio, prompt_audio_sr = self.decode_audio(prompt_audio_data)
            # Mono channel & max of 29s
            prompt_audio = prompt_audio[:1, : int(prompt_audio_sr * 29)]
            prompt_dict = self._prepare_prompt_from_audio(prompt_audio, prompt_audio_sr)
            self.prompt_caches[prompt_key] = prompt_dict
        prompt_dict = self.prompt_caches[prompt_key]

        # Synthesis
        token = torch.tensor(token).unsqueeze(0)
        audio, audio_sr = self.token2audio_nonstream(token, prompt_dict)
        return audio, audio_sr

    def _prepare_prompt_from_audio(self, prompt_audio, prompt_audio_sr):
        """从音频张量准备 prompt"""
        # 使用 scipy 保存临时文件，避免 torchcodec 依赖
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            if isinstance(prompt_audio, torch.Tensor):
                prompt_audio = prompt_audio.cpu().numpy()
            # 处理维度: [channels, samples] -> [samples]
            if prompt_audio.ndim == 2:
                prompt_audio = prompt_audio.squeeze(0)
            # 转换为 int16
            prompt_audio = np.clip(prompt_audio, -1.0, 1.0)
            wav_int16 = (prompt_audio * 32767.0).astype(np.int16)
            wavfile.write(tmp_file.name, prompt_audio_sr, wav_int16)
            prompt_dict = self._prepare_prompt(tmp_file.name)
            os.unlink(tmp_file.name)
            return prompt_dict

    def token2audio_nonstream(self, token, prompt_dict):
        """非流式音频合成"""
        (
            prompt_speech_tokens,
            prompt_speech_tokens_lens,
            spk_emb,
            prompt_mels,
            prompt_mels_lens,
        ) = prompt_dict

        generated_speech_tokens_lens = torch.tensor(
            [token.shape[1]], dtype=torch.int32, device=self.device
        )

        # 根据设备选择是否使用混合精度
        if self.device == "cuda" and not self.float16:
            with torch.amp.autocast("cuda", dtype=torch.float16):
                mel = self.flow.inference(
                    token,
                    generated_speech_tokens_lens,
                    prompt_speech_tokens,
                    prompt_speech_tokens_lens,
                    prompt_mels,
                    prompt_mels_lens,
                    spk_emb,
                    10,
                )
        else:
            mel = self.flow.inference(
                token,
                generated_speech_tokens_lens,
                prompt_speech_tokens,
                prompt_speech_tokens_lens,
                prompt_mels,
                prompt_mels_lens,
                spk_emb,
                10,
            )

        wav, _ = self.hift(speech_feat=mel)
        return wav, 24000  # 固定采样率

    def token2wav_stream(self, tokens, prompt_dict, session_id, last_chunk=False):
        """流式音频合成"""
        if self.stream_cache is None:
            raise ValueError("stream_cache is not set")

        (
            prompt_speech_tokens,
            prompt_speech_tokens_lens,
            spk_emb,
            prompt_mels,
            prompt_mels_lens,
        ) = prompt_dict

        generated_speech_tokens = torch.tensor(
            [tokens], dtype=torch.int32, device=self.device
        )

        # 根据设备选择是否使用混合精度
        if self.device == "cuda" and not self.float16:
            with torch.amp.autocast("cuda", dtype=torch.float16):
                chunk_mel, self.stream_cache = self.flow.inference_chunk(
                    token=generated_speech_tokens,
                    spk=spk_emb,
                    cache=self.stream_cache,
                    last_chunk=last_chunk,
                    n_timesteps=10,
                )
        else:
            chunk_mel, self.stream_cache = self.flow.inference_chunk(
                token=generated_speech_tokens,
                spk=spk_emb,
                cache=self.stream_cache,
                last_chunk=last_chunk,
                n_timesteps=10,
            )

        if self.stream_cache["estimator_att_cache"].shape[4] > (
            prompt_mels.shape[1] + 100
        ):
            self.stream_cache["estimator_att_cache"] = torch.cat(
                [
                    self.stream_cache["estimator_att_cache"][
                        :, :, :, :, : prompt_mels.shape[1]
                    ],
                    self.stream_cache["estimator_att_cache"][:, :, :, :, -100:],
                ],
                dim=4,
            )

        # vocoder 缓存
        hift_cache_mel = self.hift_cache_dict["mel"]
        hift_cache_source = self.hift_cache_dict["source"]
        hift_cache_speech = self.hift_cache_dict["speech"]
        mel = torch.concat([hift_cache_mel, chunk_mel], dim=2)

        speech, source = self.hift(mel, hift_cache_source)

        # 重叠语音平滑
        if hift_cache_speech.shape[-1] > 0:
            speech = fade_in_out(speech, hift_cache_speech, self.speech_window)

        # 更新 vocoder 缓存
        self.hift_cache_dict = dict(
            mel=mel[..., -self.mel_cache_len :].clone().detach(),
            source=source[:, :, -self.source_cache_len :].clone().detach(),
            speech=speech[:, -self.source_cache_len :].clone().detach(),
        )
        if not last_chunk:
            speech = speech[:, : -self.source_cache_len]

        return speech, 24000  # 固定采样率

    def clean_up(self):
        """清理会话缓存"""
        if hasattr(self, "stream_cache"):
            self.stream_cache = None
        if hasattr(self, "hift_cache_dict"):
            self.hift_cache_dict = dict(
                mel=torch.zeros(1, 80, 0, device=self.device),
                source=torch.zeros(1, 1, 0, device=self.device),
                speech=torch.zeros(1, 0, device=self.device),
            )

    def __call__(self, generated_speech_tokens, prompt_wav):
        """直接调用接口"""
        if prompt_wav not in self.cache:
            self.cache[prompt_wav] = self._prepare_prompt(prompt_wav)
        (
            prompt_speech_tokens,
            prompt_speech_tokens_lens,
            spk_emb,
            prompt_mels,
            prompt_mels_lens,
        ) = self.cache[prompt_wav]

        generated_speech_tokens = torch.tensor(
            [generated_speech_tokens], dtype=torch.int32, device=self.device
        )
        generated_speech_tokens_lens = torch.tensor(
            [generated_speech_tokens.shape[1]], dtype=torch.int32, device=self.device
        )

        # 根据设备选择是否使用混合精度
        if self.device == "cuda" and not self.float16:
            with torch.amp.autocast("cuda", dtype=torch.float16):
                mel = self.flow.inference(
                    generated_speech_tokens,
                    generated_speech_tokens_lens,
                    prompt_speech_tokens,
                    prompt_speech_tokens_lens,
                    prompt_mels,
                    prompt_mels_lens,
                    spk_emb,
                    10,
                )
        else:
            mel = self.flow.inference(
                generated_speech_tokens,
                generated_speech_tokens_lens,
                prompt_speech_tokens,
                prompt_speech_tokens_lens,
                prompt_mels,
                prompt_mels_lens,
                spk_emb,
                10,
            )

        wav, _ = self.hift(speech_feat=mel)
        output = io.BytesIO()
        # 使用 scipy 保存音频，避免 torchcodec 问题
        wav_np = wav.cpu().numpy().squeeze(0)  # 转换为 numpy 数组
        wav_np = np.clip(wav_np, -1.0, 1.0)  # 裁剪到 [-1, 1]
        wav_int16 = (wav_np * 32767.0).astype(np.int16)  # 转换为 16-bit
        wavfile.write(output, 24000, wav_int16)
        output.seek(0)
        return output.getvalue()

    def set_stream_cache(self, prompt_wav):
        """设置流式缓存"""
        if prompt_wav not in self.cache:
            self.cache[prompt_wav] = self._prepare_prompt(prompt_wav)
        (
            prompt_speech_tokens,
            prompt_speech_tokens_lens,
            spk_emb,
            prompt_mels,
            prompt_mels_lens,
        ) = self.cache[prompt_wav]
        self.stream_cache = self.flow.setup_cache(
            torch.cat([prompt_speech_tokens, prompt_speech_tokens[:, :3]], dim=1),
            prompt_mels,
            spk_emb,
            n_timesteps=10,
        )

        # hift 缓存
        self.hift_cache_dict = dict(
            mel=torch.zeros(1, prompt_mels.shape[2], 0, device=self.device),
            source=torch.zeros(1, 1, 0, device=self.device),
            speech=torch.zeros(1, 0, device=self.device),
        )

    def set_stream_cache_from_prompt_dict(self, prompt_dict):
        """从预加载的 prompt_dict 设置流式缓存"""
        (
            prompt_speech_tokens,
            prompt_speech_tokens_lens,
            spk_emb,
            prompt_mels,
            prompt_mels_lens,
        ) = prompt_dict
        self.stream_cache = self.flow.setup_cache(
            torch.cat([prompt_speech_tokens, prompt_speech_tokens[:, :3]], dim=1),
            prompt_mels,
            spk_emb,
            n_timesteps=10,
        )

        # hift 缓存
        self.hift_cache_dict = dict(
            mel=torch.zeros(1, prompt_mels.shape[2], 0, device=self.device),
            source=torch.zeros(1, 1, 0, device=self.device),
            speech=torch.zeros(1, 0, device=self.device),
        )

    def stream(self, generated_speech_tokens, prompt_wav, last_chunk=False):
        """流式处理"""
        if prompt_wav not in self.cache:
            self.cache[prompt_wav] = self._prepare_prompt(prompt_wav)
        (
            prompt_speech_tokens,
            prompt_speech_tokens_lens,
            spk_emb,
            prompt_mels,
            prompt_mels_lens,
        ) = self.cache[prompt_wav]

        generated_speech_tokens = torch.tensor(
            [generated_speech_tokens], dtype=torch.int32, device=self.device
        )
        generated_speech_tokens_lens = torch.tensor(
            [generated_speech_tokens.shape[1]], dtype=torch.int32, device=self.device
        )

        if self.stream_cache is None:
            raise ValueError("stream_cache is not set")

        # 根据设备选择是否使用混合精度
        if self.device == "cuda" and not self.float16:
            with torch.amp.autocast("cuda", dtype=torch.float16):
                chunk_mel, self.stream_cache = self.flow.inference_chunk(
                    token=generated_speech_tokens,
                    spk=spk_emb,
                    cache=self.stream_cache,
                    last_chunk=last_chunk,
                    n_timesteps=10,
                )
        else:
            chunk_mel, self.stream_cache = self.flow.inference_chunk(
                token=generated_speech_tokens,
                spk=spk_emb,
                cache=self.stream_cache,
                last_chunk=last_chunk,
                n_timesteps=10,
            )

        if self.stream_cache["estimator_att_cache"].shape[4] > (
            prompt_mels.shape[1] + 100
        ):
            self.stream_cache["estimator_att_cache"] = torch.cat(
                [
                    self.stream_cache["estimator_att_cache"][
                        :, :, :, :, : prompt_mels.shape[1]
                    ],
                    self.stream_cache["estimator_att_cache"][:, :, :, :, -100:],
                ],
                dim=4,
            )

        # vocoder 缓存
        hift_cache_mel = self.hift_cache_dict["mel"]
        hift_cache_source = self.hift_cache_dict["source"]
        hift_cache_speech = self.hift_cache_dict["speech"]
        mel = torch.concat([hift_cache_mel, chunk_mel], dim=2)

        speech, source = self.hift(mel, hift_cache_source)

        # 重叠语音平滑
        if hift_cache_speech.shape[-1] > 0:
            speech = fade_in_out(speech, hift_cache_speech, self.speech_window)

        # 更新 vocoder 缓存
        self.hift_cache_dict = dict(
            mel=mel[..., -self.mel_cache_len :].clone().detach(),
            source=source[:, :, -self.source_cache_len :].clone().detach(),
            speech=speech[:, -self.source_cache_len :].clone().detach(),
        )
        if not last_chunk:
            speech = speech[:, : -self.source_cache_len]

        wav_np = speech.cpu().numpy()
        # 裁剪到 [-1, 1] 避免溢出，然后缩放到 int16
        wav_np = np.clip(wav_np, -1.0, 1.0)
        wav_int16 = (wav_np * 32767.0).astype("<i2")  # 16位小端 PCM
        pcm_bytes = wav_int16.tobytes()
        return pcm_bytes
