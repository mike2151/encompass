from interview_code_file.models import SupportCode
import textwrap
from interview_test_case.models import InterviewTestCase
def indent(text, amount, ch=' '):
        return textwrap.indent(text, amount * ch)


# creates the file to run for tests
def create_submission(user_code, question):
    code_file = SupportCode.objects.filter(interview_question=question).first()
    main_class = code_file.body
    # indent user solution
    indent_user_code = indent(user_code, 4)
    
    total_class = main_class + "\n" + indent_user_code

    full_test_case_list = []
    test_case_method_name_list = []
    all_test_cases = InterviewTestCase.objects.filter(interview_question=question)
    for test_case in all_test_cases:
        full_test_case_list.append(test_case.body)
        method_name = test_case.body.split(" ")[1].replace(":", "")
        test_case_method_name_list.append(method_name)
    
    test_case_full_string = "\n".join(full_test_case_list)
    test_case_method_string = "\n".join(test_case_method_name_list)

    return total_class + "\n" + test_case_full_string + "\n" + test_case_method_string