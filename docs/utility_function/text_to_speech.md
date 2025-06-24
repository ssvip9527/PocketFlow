---
layout: default
title: "文本转语音"
parent: "实用函数"
nav_order: 7
---

# 文本转语音

| **服务**          | **免费额度**         | **定价模式**                                            | **文档**                                                            |
|----------------------|-----------------------|--------------------------------------------------------------|---------------------------------------------------------------------|
| **Amazon Polly**     | 5M 标准 + 1M 神经   | 免费额度后：约 $4 /M (标准), 约 $16 /M (神经)               | [Polly 文档](https://aws.amazon.com/polly/)                         |
| **Google Cloud TTS** | 4M 标准 + 1M WaveNet  | 约 $4 /M (标准), 约 $16 /M (WaveNet) 按量付费                | [Cloud TTS 文档](https://cloud.google.com/text-to-speech)           |
| **Azure TTS**        | 500K 神经持续         | 约 $15 /M (神经)，量大有折扣                                  | [Azure TTS 文档](https://azure.microsoft.com/products/cognitive-services/text-to-speech/) |
| **IBM Watson TTS**   | 10K 字符精简计划      | 约 $0.02 /1K (即约 $20 /M)。提供企业选项                     | [IBM Watson 文档](https://www.ibm.com/cloud/watson-text-to-speech)   |
| **ElevenLabs**       | 每月 10K 字符         | 从约 $5/月 (30K 字符) 到 $330/月 (2M 字符)。企业版          | [ElevenLabs 文档](https://elevenlabs.io)                            |

## Python 代码示例

### Amazon Polly
```python
import boto3

polly = boto3.client("polly", region_name="us-east-1",
                     aws_access_key_id="YOUR_AWS_ACCESS_KEY_ID",
                     aws_secret_access_key="YOUR_AWS_SECRET_ACCESS_KEY")

resp = polly.synthesize_speech(
    Text="Hello from Polly!",
    OutputFormat="mp3",
    VoiceId="Joanna"
)

with open("polly.mp3", "wb") as f:
    f.write(resp["AudioStream"].read())
```

### Google Cloud TTS
```python
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()
input_text = texttospeech.SynthesisInput(text="Hello from Google Cloud TTS!")
voice = texttospeech.VoiceSelectionParams(language_code="en-US")
audio_cfg = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

resp = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_cfg)

with open("gcloud_tts.mp3", "wb") as f:
    f.write(resp.audio_content)
```

### Azure TTS
```python
import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(
    subscription="AZURE_KEY", region="AZURE_REGION")
audio_cfg = speechsdk.audio.AudioConfig(filename="azure_tts.wav")

synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_cfg
)

synthesizer.speak_text_async("Hello from Azure TTS!").get()
```

### IBM Watson TTS
```python
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

auth = IAMAuthenticator("IBM_API_KEY")
service = TextToSpeechV1(authenticator=auth)
service.set_service_url("IBM_SERVICE_URL")

resp = service.synthesize(
    "Hello from IBM Watson!",
    voice="en-US_AllisonV3Voice",
    accept="audio/mp3"
).get_result()

with open("ibm_tts.mp3", "wb") as f:
    f.write(resp.content)
```

### ElevenLabs
```python
import requests

api_key = "ELEVENLABS_KEY"
voice_id = "ELEVENLABS_VOICE"
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {"xi-api-key": api_key, "Content-Type": "application/json"}

json_data = {
    "text": "Hello from ElevenLabs!",
    "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}
}

resp = requests.post(url, headers=headers, json=json_data)

with open("elevenlabs.mp3", "wb") as f:
    f.write(resp.content)
```

