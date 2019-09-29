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
import zipfile

def copy_folder_contents(src, dest):
    if os.path.exists(src) and os.path.exists(dest):
        copy_tree(src, dest)

def prepend_to_test_file(user_submission_dir, test_case_file_name, language):
    if language == "python":
        actual_file = os.path.join(user_submission_dir, test_case_file_name)
        data = ''
        with open(actual_file, 'r') as read_file:
            data = read_file.read()
        with open(actual_file, 'w') as write_file:
            write_file.write("def visible(ob):\n\treturn ob\ndef not_visible(ob):\n\treturn ob\n" + data)
            write_file.close()
 
def create_runner_file(user_submission_dir, test_case_file_name, language):
    if language == "python":
        # copy the original file
        runner_dir = os.path.join(settings.MEDIA_ROOT, 'core/runner.py')
        shutil.copy(runner_dir, user_submission_dir)
        # prepend the import 
        prepend_str = "from " + test_case_file_name.split(".")[0] + " import TestCases\n"

        new_file = os.path.join(user_submission_dir, "runner.py")

        data = ''
        with open(new_file, 'r') as read_file:
            data = read_file.read()
        with open(new_file, 'w') as write_file:
            write_file.write(prepend_str + data)
            write_file.close()

def get_not_visible_test_cases(test_file_path):
    not_visible_test_cases = {}
    is_not_visible_line = False
    with open(test_file_path, "r") as read_file:
        for line in read_file:
            if "@not_visible" in line:
                is_not_visible_line = True
            else:
                if is_not_visible_line:
                    test_case_name = (line.split("def")[1]).split("(")[0].replace(" ", "")
                    not_visible_test_cases[test_case_name] = True
                    is_not_visible_line = False
    return not_visible_test_cases.copy()

# creates the file to run for tests
def create_and_run_submission(request, question, instance, creator_run, user_test_case):
    # create files from the users' submission
    base_question_dir = os.path.join(settings.MEDIA_ROOT, '{0}'.format(question.pk))
    instance_dir = os.path.join(base_question_dir, 'instances')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)

    user_submission_dir = os.path.join(instance_dir, str(instance.pk)) 
    if os.path.exists(user_submission_dir):
        shutil.rmtree(user_submission_dir)
    os.makedirs(user_submission_dir)

    if creator_run:
        # copy over solution
        solution_code_dir = os.path.join(base_question_dir, 'solution_code_files')
        copy_folder_contents(solution_code_dir, user_submission_dir)
    else:
        starter_code_objs = StarterCode.objects.filter(interview_question=question)
        # see if there is a zip file
        if request.FILES.get("zip_file", False):
            file = request.FILES['zip_file']
            if ".zip" in file.name:
                file_path = os.path.join(user_submission_dir, "submission.zip")
                f = open(file_path, "wb")
                f.write(file.read())
                f.close()
                # unzip 
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(user_submission_dir)
                # delete file
                os.remove(file_path)
        else:
            # go through each submitted file and create it
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
    

    # if user test case
    if len(user_test_case) > 0:
        # create the test file
        user_test_case_dir = os.path.join(base_question_dir, 'user_test_cases')
        if os.path.exists(user_test_case_dir):
            shutil.rmtree(user_test_case_dir)
        os.makedirs(user_test_case_dir)
        file_dir = os.path.join(user_test_case_dir, "user_test.py")
        with open(file_dir, "w") as write_file:
            write_file.write(user_test_case)
        write_file.close()
        test_code_dir = user_test_case_dir
    
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

    runner_file_name = ""

    # if python add __init__.py
    if language == 'python':
        runner_file_name = "runner.py"
        file_path = os.path.join(user_submission_dir, '__init__.py')
        f = open(file_path, "w")
        f.close()         

    # now run the test file

    test_case_file_name = ""
    test_passed = {}
    test_output = {}
    if len(user_test_case) > 0:
        test_case_file_name = "user_test.py"
    else:
        test_file = InterviewTestCase.objects.filter(interview_question=question).first()
        if test_file is not None:
            test_case_file_name = str(test_file.code_file.name.split('/')[-1])

    return_test_passed = {}
    return_test_output = {}
    if len(test_case_file_name) > 0:    
        # prepend decorators to test file
        prepend_to_test_file(user_submission_dir, test_case_file_name, language)
        # create the runner file
        create_runner_file(user_submission_dir, test_case_file_name, language)

        run_submission_result = run_submission_file(runner_file_name, user_submission_dir, language, version)
        all_unit_tests_results = run_submission_result['result']
        all_unit_tests_results_str = all_unit_tests_results
        if not isinstance(all_unit_tests_results_str, str):
            all_unit_tests_results_str = all_unit_tests_results.decode("utf-8") 

        test_file_path = os.path.join(user_submission_dir, test_case_file_name)

        # get list of not visible
        not_visible_test_cases = get_not_visible_test_cases(test_file_path)

        curr_failure_output = ""
        is_tracking_failure = False
        curr_failure_name = ''

        # see if compilation error
        split_test_res = all_unit_tests_results_str.split("\n")
        if len(split_test_res) < 2:
            test_passed["compilation"] = False
            test_output["compilation"] = "Compilation Error: " + all_unit_tests_results_str
        else:
            # parse results
            for line in split_test_res:
                if is_tracking_failure:
                    if ("---" not in line) and ("====" not in line):
                        curr_failure_output = curr_failure_output + line
                if "..." in line:
                    line_split = line.split(" ")
                    test_case_name = line_split[0]
                    test_case_result = line_split[-1]
                    did_test_passed = "ok" in test_case_result
                    test_passed[test_case_name] = did_test_passed
                    if did_test_passed:
                        test_output[test_case_name] = ''
                elif ("FAIL:" in line) or ("ERROR:" in line):
                    is_tracking_failure = True
                    curr_failure_name = line.split(" ")[1]
                elif "---" in line or "====" in line:
                    if is_tracking_failure and len(curr_failure_output) > 0:
                        is_tracking_failure = False
                        output_msg_to_show = curr_failure_output
                        parts_of_output = curr_failure_output.split('",')
                        if 'AssertionError' in curr_failure_output and len(parts_of_output) > 1:
                            output_msg_to_show = parts_of_output[1]
                        
                        test_output[curr_failure_name] = output_msg_to_show
                        curr_failure_output = ""
                        curr_failure_name = ""
        # anonymize test cases
        curr_test_case_num = 1
        for key, value in test_passed.items():
            if key not in not_visible_test_cases:
                return_test_passed["Test Case " + str(curr_test_case_num)] = value
                new_output_str = ""
                if value == False:
                    new_output_str = "Output: \n" + test_output[key]
                return_test_output["Test Case " + str(curr_test_case_num)] = new_output_str
                curr_test_case_num = curr_test_case_num + 1
            else:
                if creator_run:
                    return_test_passed["(Hidden To User) Test Case " + str(curr_test_case_num)] = value
                    new_output_str = ""
                    if value == False:
                        new_output_str = "Output: \n" + test_output[key]
                    return_test_output["(Hidden To User) Test Case " + str(curr_test_case_num)] = new_output_str
                    curr_test_case_num = curr_test_case_num + 1
    return return_test_passed.copy(), return_test_output.copy()


    