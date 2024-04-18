"""
Contains information which sets up the tests.  Includes things like location of test resources
etc.
"""
import os
from django.conf import settings

# files relative to base
test_fixtures_folder = 'resources/test_fixtures'

# base folder for finding test related files such as fixtures, data files etc.
test_data_base_folder = os.path.join(settings.BASE_DIR, 'plan_visual_django', 'tests')
excel_input_files_folder = os.path.join(test_data_base_folder, "resources", "input_files", "excel_plan_files")
