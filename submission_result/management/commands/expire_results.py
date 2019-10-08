from django.core.management.base import BaseCommand
from submission_result.models import SubmissionResult

import datetime

class Command(BaseCommand):

    help = 'Expires submissions which are beyond the expiration time'

    def handle(self, *args, **kwargs):
        expired_submissions = SubmissionResult.objects.filter(expire_time__lt=datetime.datetime.now())
        for expired_submission in expired_submissions:
            expired_submission.delete_folder()
            expired_submission.delete()
