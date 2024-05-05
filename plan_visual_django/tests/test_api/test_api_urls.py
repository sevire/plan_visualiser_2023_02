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
        #
        # NOTE: I am adopting the convention to not include a specified user in the api by default, and URLs
        # which don't include a specified user will use the currently authenticated user.  The thinking behind this
        # Is that this is the most common use case.  Later I will add URL patterns which specify either a specified user
        # or for requests for all objects regardless of user (ALL).

        # ToDo: Determine rules for different user use cases (authenticated, not-authenticated, not logged in etc)
        test_data=[
            # All plans depending upon login status from model
            ("GET", "/model/plans/", None, 200),  # All plans for the currently logged in user.
            # ModelPlanListAPI

            # # Plan data from model
            ("GET", "/model/plans/2/", None, 200),  # All activities from plan with id 2
            # # ModelPlanAPI
            #
            # # Plan activity data from model
            ("GET", "/model/plans/activities/2/", None, 200),  # All activities from plan with id 2
            # # ModelPlanActivityListAPI
            #
            # # ToDo: Included tests for URLs with spaces in activity unique id - what should happen?
            ("GET", "/model/plans/activities/2/ID-025/", None, 200),  # Specific activity from plan 2 by sticky id
            # # ModelPlanActivityAPI
            #
            # # Visual data from model
            #
            # # Data related to the visual (not graphical elements, just base data)
            ("GET", "/model/visuals/2/", None, 200),  # Get information on all visuals
            # # ModelVisualListAPI
            #
            ("GET", "/model/visuals/2/4/", None, 200),  # Get information about visual with pk=4
            # # ModelVisualAPI
            #
            # # All visual activities from model assigned to this given visual, including those added and then disabled.
            ("GET", "/model/visuals/activities/4/", None, 200),
            # # ModelVisualActivityListAPI
            #
            # # All visual activities from model assigned to this given visual, *NOT* including those added and then disabled.
            ("GET", "/model/visuals/activities/enabled/4/", None, 200),
            # # ModelVisualListAPI (with hard-coded paramter for enabled=True
            #
            # # Specific visual activity by sticky id.  Valid for any activity which has been added to the visual.  Client
            # # will need to check whether activity is enabled or not.
            ("GET", "/model/visuals/activities/4/ID-025/", None, 200),
            # # ModelVisualActivityAPI
            #
            # # Requests timeline information from model for this visual - all timelines in sequence order.
            ("GET", "/model/visuals/timelines/4/", None, 200),
            # # ModelVisualTimelineListAPI
            #
            # # Requests timeline information from model for this visual - specified timeline by sequence.
            ("GET", "/model/visuals/timelines/4/2/", None, 200),
            # # ModelVisualTimelineAPI
            #
            # # Requests swimlane information from model for this visual - all swimlanes in sequence order.
            ("GET", "/model/visuals/swimlanes/4/", None, 200),
            # # ModelVisualSwimlaneListAPI
            #
            # # Requests swimlane information from model for this visual - specified swimlane by sequence.
            ("GET", "/model/visuals/swimlanes/4/1/", None, 200),
            # ModelVisualSwimlaneAPI

            # Visual information from Canvas Rendering

            # Information at visual level required to plot the visual on a canvas.  Includes things like size,
            # and names of each canvas that needs to be plotted (as each rendered element will appear on a specific
            # canvas element on the client).
            ("GET", "/rendered/canvas/visuals/settings/4/", None, 200),

            # Get all rendered objects for a visual.
            ("GET", "/rendered/canvas/visuals/4/", None, 200),
            # RenderedCanvasVisualAPI

            # Request all rendered elements for activities visible on this visual. Will include the name of the
            # canvas to be plotted on.
            ("GET", "/rendered/canvas/visuals/activities/4/", None, 200),
            # RenderedCanvasVisualActivityListAPI

            # Requests elements for a single rendered activity for this visual. (NOTE will be two elements, one for the
            # shape and one for the text.
            ("GET", "/rendered/canvas/visuals/activities/4/ID-025/", None, 200),
            # RenderedCanvasVisualActivityAPI
            #
            # 2 URLs to get rendered timeline data.  Firstly for all timelines, secondly for single timeline identified
            # by sequence in visual.
            ("GET", "/rendered/canvas/visuals/timelines/4/", None, 200),
            # RenderedCanvasVisualTimelineListAPI
            #
            ("GET", "/rendered/canvas/visuals/timelines/4/1/", None, 200),
            # RenderedCanvasVisualTimelineAPI

            # 2 URLs to get rendered swimlane data.  Firstly for all timelines, secondly for single swimlane identified
            # by sequence in visual.
            ("GET", "/rendered/canvas/visuals/swimlanes/4/", None, 200),
            # RenderedCanvasVisualSwimlaneListAPI

            ("GET", "/rendered/canvas/visuals/swimlanes/4/1/", None, 200),
            # RenderedCanvasVisualSwimlaneAPI
        ]
    ))
    @unpack
    def test_api_urls(self, http_method, input_url, data, field_name, expected_field_value):
        base_url = "/api/v1"
        url = base_url + input_url
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
