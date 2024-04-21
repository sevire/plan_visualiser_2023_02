import os
from ddt import ddt, data, unpack
from django.test import TestCase
from plan_visual_django.tests.resources.test_configuration import test_fixtures_folder, test_data_base_folder
from resources.utilities import generate_test_data_field_stream_multiple_inputs

"""
Simply tests that all URLs are working.  Doesn't check content, just that the api is processed.
"""


@ddt
class TestApiUrls(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json')
    ]

    @data(*generate_test_data_field_stream_multiple_inputs(
        expected_value_field_names=("status",),

        # Implemented tests for the full api, if a valid url is not implemented it should still recognise and return 501
        # Note what is returned in practice will depend upon which user is logged in.  Usually will only return objects
        # owned by currently logged in user, but if user has admin status (yet to be defined!) will return all.
        # ToDo: Determine rules for API for different user use cases.
        test_data=[
            # Plan data from model
            ("GET", "/api/v1/model/plans/2/", None, 200),  # All activities from plan

            # Plan activity data from model
            ("GET", "/api/v1/model/plans/activities/2/", None, 200),  # All activities from plan
            ("GET", "/api/v1/model/plans/activities/model/2/ID-025", None, 501),  # Specific activity from plan by sticky id

            # Visual data from model

            # Data related to the visual (not graphical elements, just base data)
            ("GET", "/api/v1/model/visuals/4/", None, 200),

            # All visual activities from model assigned to this given visual, including those added and then disabled.
            ("GET", "/api/v1/model/visuals/activities/all/4/", None, 200),

            # All visual activities from model assigned to this given visual, *NOT* including those added and then disabled.
            ("GET", "/api/v1/model/visuals/activities/enabled/4/", None, 200),

            # Specific visual activity by sticky id.  Valid for any activity which has been added to the visual.  Client
            # will need to check whether activity is enabled or not.
            ("GET", "/api/v1/model/visuals/activities/4/ID-025/", None, 200),

            # Requests timeline information from model for this visual - all timelines in sequence order.
            ("GET", "/api/v1/model/visuals/timelines/4/", None, 200),

            # Requests timeline information from model for this visual - specified timeline by sequence.
            ("GET", "/api/v1/model/visuals/timelines/4/1", None, 200),

            # Requests swimlane information from model for this visual - all swimlanes in sequence order.
            ("GET", "/api/v1/model/visuals/timelines/4/1", None, 200),

            # Requests swimlane information from model for this visual - specified swimlane by sequence.
            ("GET", "/api/v1/model/visuals/timelines/4/1", None, 200),

            # Visual information from Canvas Rendering

            # Information at visual level required to plot the visual on a canvas.  Includes things like size,
            # and names of each canvas that needs to be plotted (as each rendered element will appear on a specific
            # canvas element on the client.
            ("GET", "/api/v1/canvas/visuals/4/", None, 200),

            # Request all rendered elements for activities visible on this visual. Will include the name of the
            # canvas to be plotted on.
            ("GET", "/api/v1/canvas/visuals/actvities/4/", None, 200),

            # Requests elements for a single rendered activity for this visual. (NOTE will be two elements, one for the
            # shape and one for the text.
            ("GET", "/api/v1/canvas/visuals/actvities/4/ID-025/", None, 200),

            # 2 URLs to get rendered timeline data.  Firstly for all timelines, secondly for single timeline identified
            # by sequence in visual.
            ("GET", "/api/v1/canvas/visuals/timelines/4/", None, 200),
            ("GET", "/api/v1/canvas/visuals/timelines/4/1/", None, 200),

            # 2 URLs to get rendered swimlane data.  Firstly for all timelines, secondly for single swimlane identified
            # by sequence in visual.
            ("GET", "/api/v1/canvas/visuals/swimlanes/4/", None, 200),
            ("GET", "/api/v1/canvas/visuals/swimlanes/4/1", None, 200),

        ]
    ))
    @unpack
    def test_api_urls(self, http_method, url, data, field_name, expected_field_value):
        if http_method == "GET":
            response = self.client.get(url)
        elif http_method == "PUT":
            response = self.client.put(url, data=data)
        elif http_method == "POST":
            response = self.client.post(url, data=data)
        else:
            self.fail(f"Unexpected HTTP method {http_method}")

        if field_name in {"status"}:
            self.assertEqual(response.status_code, expected_field_value)
        else:
            self.fail(f"Unexpected field name {field_name}")


