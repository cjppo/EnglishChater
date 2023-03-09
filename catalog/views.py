import base64
import json
import os
import openai

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from google.cloud import speech, texttospeech

message_log = [
    {"role": "system", "content": "You are a helpful english teacher."}
]
speech_to_text_service_url = 'https://speech.googleapis.com/v1/speech:recognize'
text_to_speech_service_url = 'https://texttospeech.googleapis.com/v1/text:synthesize'


@api_view(['POST'])
@csrf_exempt
def chatWithUser(request):
    message = json.loads(request.body)['data']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './data/cjkl1317-07f0da05283b.json'
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(content=base64.b64decode(message, altchars=None, validate=False))
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        sample_rate_hertz=48000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    print(response)
    if len(response.results) == 0:
        return HttpResponse("")

    answer = chat(response.results[0].alternatives[0].transcript)
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=answer)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Neural2-J", ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    if len(response.audio_content) > 0:
        return HttpResponse(base64.encodebytes(response.audio_content))
    else:
        return HttpResponse("")

# Create your views here.
@api_view(['POST'])
@csrf_exempt
def receiveAudioBase64Data(request):
    data = json.loads(request.body)

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './data/cjkl1317-07f0da05283b.json'
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=base64.b64decode(data['data'], altchars=None, validate=False))
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        sample_rate_hertz=48000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    if len(response.results) > 0:
        return HttpResponse("result:{}".format(response.results[0].alternatives[0].transcript))
    else:
        return HttpResponse("result: ")


@api_view(['POST'])
@csrf_exempt
def transsferTextToSpeech(request):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './data/cjkl1317-07f0da05283b.json'
    client = texttospeech.TextToSpeechClient()
    data = json.loads(request.body)
    message = data['data']
    synthesis_input = texttospeech.SynthesisInput(text=message)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Neural2-J", ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    if len(response.audio_content) > 0:
        return HttpResponse(base64.encodebytes(response.audio_content))
    else:
        return HttpResponse("result: ")

@api_view(['POST'])
@csrf_exempt
def chatWithGPT(request):
    data = json.loads(request.body)
    message = data['data']
    return HttpResponse(chat(message))

def chat(message):
    openai.api_key = os.environ['OPENAI_KEY']
    if message == 'clear context':
        clearTheContext()
        return HttpResponse("done")
    message_log.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_log,
        max_tokens=1000,
        stop=None,
        temperature=0.9,
    )
    for choice in response.choices:
        if "message" in choice:
            return choice.message.content
    return "something error"

def clearTheContext():
    global message_log
    message_log.clear()
