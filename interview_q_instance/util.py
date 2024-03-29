from interview_code_file.models import SupportCode
import textwrap
from interview_test_case.models import InterviewTestCase
import os
import subprocess
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

def file_exists_bad_import(question, file_content):
    bad_imports = question.banned_imports
    bad_import_list = bad_imports.split(",")
    lines = file_content.split("\n")
    for line in lines:
        if line.startswith("import "):
            import_name = line.split(" ")[1].strip()
            if import_name in bad_import_list:
                return True
        elif line.startswith("from "):
            if "import" in line:
                import_name = line.split(" ")[1].strip()
                if import_name in bad_import_list:
                    return True
    return False

def exists_bad_import(question, user_submission_dir):
    bad_imports = question.banned_imports
    bad_import_list = bad_imports.split(",")
    for submitted_file in os.listdir(user_submission_dir):
        actual_file = os.path.join(user_submission_dir, submitted_file)
        if str(actual_file).endswith(".py"):
            with open(actual_file, 'r') as read_file:
                lines = read_file.readlines()
                read_file.close()
            for line in lines:
                if line.startswith("import "):
                    import_name = line.split(" ")[1].strip()
                    if import_name in bad_import_list:
                        return True
                elif line.startswith("from "):
                    if "import" in line:
                        import_name = line.split(" ")[1].strip()
                        if import_name in bad_import_list:
                            return True
    return False

def prepend_to_test_file(user_submission_dir, test_case_file_name, language):
    if language == "python":
        actual_file = os.path.join(user_submission_dir, test_case_file_name)
        data = ''
        with open(actual_file, 'r') as read_file:
            data = read_file.read()
        with open(actual_file, 'w') as write_file:
            write_file.write("def visible(ob):\n\treturn ob\ndef not_visible(ob):\n\treturn ob\n" + data)
            write_file.close()

def prepend_to_user_submitted_files(user_submission_dir, support_code_dir, language):
    if (os.path.exists(support_code_dir)):
        if language == "python":
            prepend_string = ""
            for support_file in os.listdir(support_code_dir):
                file_str_split = str(support_file).split(".")
                if file_str_split[1] == "py":
                    prepend_string = prepend_string + "import " + file_str_split[0] + "\n"
            for user_submitted_file_str in os.listdir(user_submission_dir):
                if user_submitted_file_str.endswith(".py"):
                    actual_file = os.path.join(user_submission_dir, user_submitted_file_str)
                    data = ''
                    with open(actual_file, 'r') as read_file:
                        data = read_file.read()
                    with open(actual_file, 'w') as write_file:
                        write_file.write(prepend_string + data)
                        write_file.close()

def generate_network_prepend():
    return "import socket\ndef guard(*args, **kwargs):\n\traise Exception('Network is disabled')\nsocket.socket = guard\n"

def create_runner_file(user_submission_dir, test_case_file_name, language, question, dependencies, is_network_enabled):
    if language == "python":
        # copy the original file
        runner_dir = os.path.join(settings.MEDIA_ROOT, 'core/runner.py')
        shutil.copy(runner_dir, user_submission_dir)
        # prepend the network disabling code
        network_prepend_str = ""
        if not is_network_enabled:
            network_prepend_str = generate_network_prepend()
        # prepend the single test case import import 
        single_import_prepend_str = "from " + test_case_file_name.split(".")[0] + " import TestCases\n"

        prepend_contents = network_prepend_str + single_import_prepend_str

        new_file = os.path.join(user_submission_dir, "runner.py")

        data = ''
        with open(new_file, 'r') as read_file:
            data = read_file.read()
            if question.allow_stdout:
                data.replace("runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2, buffer=True)", "runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)")
        with open(new_file, 'w') as write_file:
            write_file.write(prepend_contents + data)
            write_file.close()

def get_not_visible_test_cases(test_file_path):
    not_visible_test_cases = {}
    is_not_visible_line = False
    with open(test_file_path, "r") as read_file:
        for line in read_file:
            if "@not_visible" in line and not (line.startswith("#")):
                is_not_visible_line = True
            else:
                if is_not_visible_line:
                    if "def" in line:
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

    starter_code_names = []
    if (not question.allow_new_files):
        starter_code_objects = StarterCode.objects.filter(interview_question=question)
        for starter_code_obj in starter_code_objects:
            starter_code_names.append(str(starter_code_obj.code_file.name.split("/")[-1]))

    if creator_run:
        # copy over solution
        solution_code_dir = os.path.join(base_question_dir, 'solution_code_files')
        copy_folder_contents(solution_code_dir, user_submission_dir)
    else:
        for key in request.POST:
            if key.startswith("wfile_"):
                filename = key.split("wfile_")[1]
                file_contents = request.POST.get("wfile_" + filename, False)
                if file_contents and len(file_contents) > 0:
                    file_path = os.path.join(user_submission_dir, filename)
                    f = open(file_path, "w")
                    f.write(file_contents)
                    f.close()
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
                    for zip_info in zip_ref.infolist():
                        if "__MACOSX" not in zip_info.filename:
                            if (not question.allow_new_files):
                                z_name = zip_info.filename.split("/")[-1]
                                if z_name in starter_code_names:
                                    zip_ref.extract(zip_info, user_submission_dir)
                            else:
                                zip_ref.extract(zip_info, user_submission_dir)
                # delete file
                os.remove(file_path)

    # parse language info
    language_option = question.language.lower()
    language = ''
    version = 0
    match = re.match(r"([a-z]+)([0-9]+)", language_option, re.I)
    if match:
        items = match.groups()
        language = items[0]
        str_base_version = items[1]
        str_sub_version_list = language_option.split(".")
        str_sub_version = ""
        if len(str_sub_version_list) > 1:
            str_sub_version = "." + str_sub_version_list[1]
        version = float(str_base_version + str_sub_version)

    # see if there are any banned imports
    does_bad_import_exist = exists_bad_import(question, user_submission_dir)
    if does_bad_import_exist:
        return {"Compilation_Output": False}, {"Compilation_Output": "You are using a banned import"}, {"Compilation_Output": True}

    # copy over all files from other dirs in submission
    supporting_code_dir = os.path.join(base_question_dir, 'supporting_code_files')
    test_code_dir = os.path.join(base_question_dir, 'test_code_files')

    # automatically add the imports
    prepend_to_user_submitted_files(user_submission_dir, supporting_code_dir, language)

    copy_folder_contents(supporting_code_dir, user_submission_dir)

    # if user test case
    if len(user_test_case) > 0:
        # see if file contains bad imports
        test_does_bad_import_exist = file_exists_bad_import(question, user_test_case)
        if test_does_bad_import_exist:
            return {"Compilation_Output": False}, {"Compilation_Output": "You are using a banned import"}, {"Compilation_Output": True}
        # create the test file
        user_test_case_dir = os.path.join(user_submission_dir, 'user_test_cases')
        if os.path.exists(user_test_case_dir):
            shutil.rmtree(user_test_case_dir)
        os.makedirs(user_test_case_dir)
        file_dir = os.path.join(user_test_case_dir, "user_test.py")
        with open(file_dir, "w") as write_file:
            write_file.write(user_test_case)
        write_file.close()
        test_code_dir = user_test_case_dir
    
    copy_folder_contents(test_code_dir, user_submission_dir)

    runner_file_name = ""

    # if python add __init__.py
    if language == 'python':
        runner_file_name = "runner.pye"
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
    return_test_visibility = {}
    if len(test_case_file_name) > 0:    
        # prepend decorators to test file
        prepend_to_test_file(user_submission_dir, test_case_file_name, language)
        # create the runner file
        create_runner_file(user_submission_dir, test_case_file_name, language, question, question.dependencies, question.network_enabled)

        # encrypt the files
        p = subprocess.Popen(["pyconcrete-admin.py", "compile", "--source=.", "--pye"], cwd=user_submission_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        error_str = error.decode("utf-8") 

        # delete all .py files that are supporting
        supporting_file_names = []
        for support_file in os.listdir(supporting_code_dir):
            if support_file.endswith(".py"):
                supporting_file_names.append(support_file.split("/")[-1])
        for filename in os.listdir(user_submission_dir):
            if filename.endswith(".py") and (filename.split("/")[-1]) in supporting_file_names:
                os.remove(os.path.join(user_submission_dir, filename))

        # if compilation error from encryption
        if len(error_str) > 0:
            return_test_passed["Code Compilation"] = False
            return_test_output["Code Compilation"] = "Code did not compile and no test cases were able to be run. Output:<br><br>" + error_str
            return_test_visibility["Code Compilation"] = True
            return return_test_passed.copy(), return_test_output.copy(), return_test_visibility.copy()

        run_submission_result = run_submission_file(runner_file_name, user_submission_dir, language, version)
        all_unit_tests_results = run_submission_result['result']
        all_unit_tests_results_str = all_unit_tests_results
        if not isinstance(all_unit_tests_results_str, str):
            all_unit_tests_results_str = all_unit_tests_results.decode("utf-8") 

        test_file_path = os.path.join(user_submission_dir, test_case_file_name)

        # get list of not visible
        not_visible_test_cases = get_not_visible_test_cases(test_file_path)

        if (all_unit_tests_results_str.startswith("Exception ignored in")):
            # inform that the code did not compile for all test cases
            return_test_passed["Code Compilation"] = False
            return_test_output["Code Compilation"] = "Code did not compile and no test cases were able to be run"
            return_test_visibility["Code Compilation"] = True
            return return_test_passed.copy(), return_test_output.copy(), return_test_visibility.copy()

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
                        if ('AssertionError' in curr_failure_output) and len(parts_of_output) > 1:
                            output_msg_to_show = parts_of_output[1]
                            if not question.allow_stdout:
                                output_msg_to_show = output_msg_to_show.split("Stdout:")[0]
                                
                        output_msg_to_show = output_msg_to_show.replace("Stdout:", "<br>Stdout:<br>")
                        test_output[curr_failure_name] = output_msg_to_show
                        curr_failure_output = ""
                        curr_failure_name = ""
        # anonymize test cases
        for key, value in test_passed.items():
            is_test_visable = key not in not_visible_test_cases 
            test_name = "Test Case: " + key if is_test_visable else "(Not Visible To User) Test Case: " + key
            return_test_passed[test_name] = value
            new_output_str = ""
            if value == False:
                new_output_str = "Output: \n" + test_output[key]
            return_test_output[test_name] = new_output_str
            return_test_visibility[test_name] = is_test_visable
    return return_test_passed.copy(), return_test_output.copy(), return_test_visibility.copy()


    