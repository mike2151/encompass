from django.core.management.base import BaseCommand
from interview_q_instance.models import InterviewQuestionInstance

import datetime

class Command(BaseCommand):

    help = 'Removes Questions By Anon Accounts'

    def handle(self, *args, **kwargs):
        anon_questions = InterviewQuestionInstance.objects.filter(is_anon_user = True)
        for anon_question in anon_questions:
            anon_question.delete_folder()
            anon_question.delete()
