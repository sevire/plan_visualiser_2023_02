"""
Contains information which sets up the tests.  Includes things like location of test resources
etc.
"""
import os

from plan_visualiser_2023_02 import settings

# files relative to base
test_fixtures_folder = 'resources/test_fixtures'

# base folder for finding test related files such as fixtures, data files etc.
test_data_base_folder = os.path.join(settings.BASE_DIR, 'plan_visual_django', 'tests')
