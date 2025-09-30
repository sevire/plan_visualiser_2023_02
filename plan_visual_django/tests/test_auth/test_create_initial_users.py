from django.contrib.auth import get_user_model
from django.test import TestCase
from plan_visual_django.services.initialisation.db_initialisation import set_initial_user_data, create_initial_users
from plan_visual_django.tests.resources.utilities import set_env_variables

User = get_user_model()

"""
Tests the creation of initial users from supplied set of configuration data.  The actual user data such as usernam
and password are held in environment variables.  The configuration data sets the parameters for what variables to look 
for and the users are created from that.
"""
class TestCreateInitialUsers(TestCase):
    user_setup_test_data = [
        {
            'env_variables': {
                "SHARED_USER_NAME": "shared_user",
                "SHARED_USER_PASSWORD": "abcde12345",
                "APP_USER_1_NAME": "app_user_01",
                "APP_USER_1_PASSWORD": "fghij7891011",
                "ADMIN_NAME": "admin",
                "ADMIN_PASSWORD": "klmno121314",
                "INITIAL_USER_EMAIL_DOMAIN": "test_domain.co.uk"
            },
            "initial_users_config": [
                # Name of env variable, superuser flag, user index
                ("SHARED_USER", False, 1, True),
                ("ADMIN", True, 2, False),
                ("APP_USER_1", False, 3, False),
            ],
            'expected_results_config_data': {
                'shared_user': {
                    'password': "abcde12345",
                    'email': 'shared_user@test_domain.co.uk',
                    'superuser_flag': False,
                    'id': 1,
                },
                'admin': {
                    'password': "klmno121314",
                    'email': 'admin@test_domain.co.uk',
                    'superuser_flag': True,
                    'id': 2,
                },
                'app_user_01': {
                    'password': "fghij7891011",
                    'email': 'app_user_01@test_domain.co.uk',
                    'superuser_flag': False,
                    'id': 3,
                },
            },
        }
    ]

    def test_create_user_data_config(self):
        """
        Simulates what will happen when deploying the app and setting up initial users. There should be a set of
        env variables which hold the username and password for each initial user.  There is also a hard-coded structure
        which indicates for each user, whether it is a superuser or not, and what the index should be.

        The index needs to be set explicitly for two reasons.  Firstly, because some of the other initial data structures
        will use a hard-coded index for the user.  Secondly, because we want to allocate the first few records explicitly
        before we then (later) reset all the id counts on the database for once the app is running normally.
        (Not sure if this is a great explanation - maybe re-visit?)
        :return:
        """
        for test_case in self.user_setup_test_data:
            # Set up env variables for this test
            set_env_variables(test_case["env_variables"])
            user_data = set_initial_user_data(test_case['initial_users_config'])

            actual_user_data = {user_record['username']: {
                'password': user_record['password'],
                'email': user_record['email'],
                'superuser_flag': user_record['superuser_flag'],
                'id': user_record['id'],
            }
                for user_record in user_data}

            for expected_result_data_user, expected_result_data in test_case['expected_results_config_data'].items():
                # Check that the user data calculated from the env variables and the user config are correct.
                # This is the data which will be passed to the create_initial_users() function to actually create
                # the users.
                with self.subTest("Checking username exists in user data"):
                    self.assertIn(expected_result_data_user, actual_user_data)

                if expected_result_data_user in actual_user_data:
                    actual_user_data_for_user = actual_user_data[expected_result_data_user]
                    with self.subTest("Checking email is correct"):
                        self.assertEqual(expected_result_data['email'], actual_user_data_for_user['email'])
                    with self.subTest("Checking password is correct"):
                        self.assertEqual(expected_result_data['password'], actual_user_data_for_user['password'])
                    with self.subTest("Checking superuser flag is correct"):
                        self.assertEqual(expected_result_data['superuser_flag'], actual_user_data_for_user['superuser_flag'])
                    with self.subTest("Checking id is correct"):
                        self.assertEqual(expected_result_data['id'], actual_user_data_for_user['id'])

    def test_create_initial_user_accounts(self):
        for test_case in self.user_setup_test_data:
            # Set up env variables for this test
            set_env_variables(test_case["env_variables"])
            user_data = set_initial_user_data(test_case['initial_users_config'])

            create_initial_users(user_data, delete=False)

            for expected_result_data_user, expected_result_data in test_case['expected_results_config_data'].items():
                # Check that the user data calculated from the env variables and the user config are correct.
                # This is the data which will be passed to the create_initial_users() function to actually create
                # the users.
                with self.subTest("Checking user account has been created"):
                    try:
                        user = User.objects.get(username=expected_result_data_user)
                    except User.DoesNotExist:
                        # Fail the test as user not found
                        self.fail("User with username " + expected_result_data_user + " not found")

                with self.subTest("Checking password is correct"):
                    password_matches = user.check_password(expected_result_data['password'])
                    self.assertTrue(password_matches)

                with self.subTest("Checking email is correct"):
                    self.assertEqual(expected_result_data["email"], user.email)


    def test_create_initial_users_user_exists_same_password(self):
        # Create users from test data, then create them again and check all is well
        # This simulates multiple deployments where user details won't change (the most common case)
        for test_case in self.user_setup_test_data:
            # Set up env variables for this test
            set_env_variables(test_case["env_variables"])
            user_data = set_initial_user_data(test_case['initial_users_config'])

            create_initial_users(user_data, delete=False)

            # Now create the users again.  Should still work, no passwords changed.
            create_initial_users(user_data, delete=False)

            for expected_result_data_user, expected_result_data in test_case['expected_results_config_data'].items():
                # Check that the user data calculated from the env variables and the user config are correct.
                # This is the data which will be passed to the create_initial_users() function to actually create
                # the users.
                with self.subTest("Checking user account has been created"):
                    try:
                        user = User.objects.get(username=expected_result_data_user)
                    except User.DoesNotExist:
                        # Fail the test as user not found
                        self.fail("User with username " + expected_result_data_user + " not found")

                with self.subTest("Checking password is correct"):
                    password_matches = user.check_password(expected_result_data['password'])
                    self.assertTrue(password_matches)

                with self.subTest("Checking email is correct"):
                    self.assertEqual(expected_result_data["email"], user.email)


    def test_create_initial_users_user_exists_different_password(self):
        # Create users from test data, then adjust passwords so slightly different
        # Then create users again, should keep users but update passwords, so check that this is what happens
        for test_case in self.user_setup_test_data:
            # Set up env variables for this test
            set_env_variables(test_case["env_variables"])
            user_data = set_initial_user_data(test_case['initial_users_config'])

            create_initial_users(user_data, delete=False)

            # Modify passwords and create users again, then check against new passwords.
            # Just add constant string to each password for ease
            for user_record in user_data:
                user_record['password'] = user_record['password'] + "123"

            # Now create the users again.  Should still work, but passwords changed.
            create_initial_users(user_data, delete=False)

            for expected_result_data_user, expected_result_data in test_case['expected_results_config_data'].items():
                # Check that the user data calculated from the env variables and the user config are correct.
                # This is the data which will be passed to the create_initial_users() function to actually create
                # the users.
                with self.subTest("Checking user account has been created"):
                    try:
                        user = User.objects.get(username=expected_result_data_user)
                    except User.DoesNotExist:
                        # Fail the test as user not found
                        self.fail("User with username " + expected_result_data_user + " not found")

                with self.subTest("Checking password is correct"):
                    password_matches = user.check_password(expected_result_data['password']+'123')
                    self.assertTrue(password_matches)

                with self.subTest("Checking email is correct"):
                    self.assertEqual(expected_result_data["email"], user.email)
