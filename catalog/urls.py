from django.urls import path
from . import views

app_name = "catalog"
urlpatterns = [
    path('toText/', views.receiveAudioBase64Data, name='toText'),
    path('toSpeech/', views.transsferTextToSpeech, name='toSpeech'),
    path('chatWithGPT/', views.chatWithGPT, name='chatWithGPT'),
    path('chat/', views.chatWithUser, name='chat')
]
