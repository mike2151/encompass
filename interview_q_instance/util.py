from interview_code_file.models import SupportCode
import textwrap
from interview_test_case.models import InterviewTestCase
import os
import shutil
from django.conf import settings
from starter_code.models import StarterCode
from distutils.dir_util import copy_tree
from interview_test_case.models import InterviewTestCase
from compile.util.runner import run_submission_file
import re

def copy_folder_contents(src, dest):
    if os.path.exists(src) and os.path.exists(dest):
        copy_tree(src, dest)

# creates the file to run for tests
def create_and_run_submission(request, question, instance):
    # create files from the users' submission
    base_question_dir = os.path.join(settings.MEDIA_ROOT, '{0}'.format(question.pk))
    instance_dir = os.path.join(base_question_dir, 'instances')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)

    user_submission_dir = os.path.join(instance_dir, str(instance.pk)) 
    if os.path.exists(user_submission_dir):
        shutil.rmtree(user_submission_dir)
    os.makedirs(user_submission_dir)

    # go through each submitted file and create it
    starter_code_objs = StarterCode.objects.filter(interview_question=question)
    for starter_code_obj in starter_code_objs:
        filename = starter_code_obj.code_file.name.split("/")[-1]
        file_contents = request.POST.get("file_" + filename, False)
        if file_contents:
           file_path = os.path.join(user_submission_dir, filename)
           f = open(file_path, "w")
           f.write(file_contents)
           f.close()

    # copy over all files from other dirs in submission
    supporting_code_dir = os.path.join(base_question_dir, 'supporting_code_files')
    test_code_dir = os.path.join(base_question_dir, 'test_code_files')

    copy_folder_contents(supporting_code_dir, user_submission_dir)
    copy_folder_contents(test_code_dir, user_submission_dir)
    
    # parse language info
    language_option = question.language.lower()
    language = ''
    version = 0
    match = re.match(r"([a-z]+)([0-9]+)", language_option, re.I)
    if match:
        items = match.groups()
        language = items[0]
        version = int(items[1])

    # if python add __init__.py
    if language == 'python':
        file_path = os.path.join(user_submission_dir, '__init__.py')
        f = open(file_path, "w")
        f.close()         

    # now run the test file
    test_files = InterviewTestCase.objects.filter(interview_question=question)
    all_tests_passed = True
    test_output = {}
    for test in test_files:
        passed = False
        test_case_name = str(test.code_file.name.split('/')[-1])
        try:
            result = run_submission_file(test_case_name, user_submission_dir, language, version)
            if len(result) == 0:
                passed = True
                test_output[test_case_name] = ''
            else:
                passed = False
                test_output[test_case_name] = str(result)
        except e:
            passed = False
            test_output[test_case_name] = str(e)
        
        if not passed:
            all_tests_passed = False

    return all_tests_passed, test_output.copy()


    