from django.urls import path
from .views import *

urlpatterns = [

    # path('aura/', create_quiz, name='aura_page'),



    path('', aura_page, name='aura_page'),
    path('update_quiz/<int:quiz_id>/',update_quiz, name='update_quiz'),
    path('download_quiz_pdf/<int:attempt_id>/',generate_pdf, name='download_quiz_pdf'),
    path('create-multiple-questions/', create_questions, name='add_questions'),
    path('add-skill/', add_skill, name='add_skill'),
    path('add-tag/', add_tag, name='add_tag'),
    path('quiz/<int:quiz_id>', take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/attempt/<int:attempt_id>/submit/', submit_quiz, name='submit_quiz'),
    path('quiz/<int:quiz_id>/attempt/<int:attempt_id>/result/',quiz_result, name='quiz_result'),
    path('clear-session/', clear_session, name='clear_session'),


    
    
    
    
    
]