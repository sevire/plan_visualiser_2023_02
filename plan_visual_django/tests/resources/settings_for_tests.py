"""
File which contains various common information which helps to run tests.  Includes things like the folders where test
files are, or test data crafted for specific tests.
"""
import os.path

TEST_BASE = "plan_visual_django/tests/"
TEST_INPUT_FILE_FOLDER = os.path.join(TEST_BASE, "resources/input_files")
EXCEL_PLAN_FILE_FOLDER = os.path.join(TEST_INPUT_FILE_FOLDER, "excel_plan_files")