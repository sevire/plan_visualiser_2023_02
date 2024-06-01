// Functions which access API to get data with some simple pre-processing where necessary - no business logic!

import axios, {HttpStatusCode} from "axios";

async function api_get(url_string: string) {
  const base_url = "http://localhost:8002"
  axios.defaults.xsrfCookieName = 'csrftoken'
  axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

  let ret_response = undefined
  return await axios.get(base_url + url_string)
}

async function api_put(url_string: string, data: undefined | object) {
  const base_url = ""
  axios.defaults.xsrfCookieName = 'csrftoken'
  axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

  let ret_response = undefined
  return axios.put(base_url + url_string, data);
}

async function api_delete(url_string: string) {
  const base_url = "http://localhost:8002"
  axios.defaults.xsrfCookieName = 'csrftoken'
  axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

  let ret_response = undefined
  return axios.delete(base_url + url_string);
}

export async function api_patch(url_string: string, data: object) {
  const base_url = "http://localhost:8002"
  const api_data = JSON.stringify(data)
  axios.defaults.xsrfCookieName = 'csrftoken'
  axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

  const config = {
    headers: {
    'Content-Type': 'application/json'
   }
  }
  return axios.patch(base_url + url_string, api_data, config);
}

export async function get_plan_activity_data(visual_id: number) {
  // Returns array of activities mirroring the order in the plan.
  // Each activity includes fields from the original uploaded plan, and fields relating to the layout of that activity
  // in the visual, but those fields are only populated if the activity has at some point been in the visual.
  // There is an enabled flag which indicates whether the activity is currently in the visual.

  console.log("get_plan_activity_data: Start")
  const url_string = `/api/v1/model/plans/activities/visuals/${visual_id}/`
  const response = await api_get(url_string);

  (window as any).plan_activity_data = response.data
}

export async function get_visual_activity_data(visual_id: number) {
  // Returns array of activities mirroring the order in the plan.
  // Each activity includes fields from the original uploaded plan, and fields relating to the layout of that activity
  // in the visual, but those fields are only populated if the activity has at some point been in the visual.
  // There is an enabled flag which indicates whether the activity is currently in the visual.
  console.log(`Requesting activity data for visual ${visual_id}`)

  const url_string = `/api/v1/rendered/canvas/visuals/${visual_id}/`
  const response = await api_get(url_string);

  if (response.status === HttpStatusCode.NoContent) {
    // No activities in visual so use empty object
    console.log(`No activity data returned for visual ${visual_id}`);
    (window as any).visual_activity_data = {}
  }

  console.log(`Activity data returned for visual ${visual_id}`);
  (window as any).visual_activity_data = response.data
}

export async function add_activity_to_visual(visual_id: number, unique_id: string) {
  // Adds specified plan activity to the visual with supplied id.

  const url_string = `/api/v1/model/visuals/activities/${visual_id}/${unique_id}/`
  const response = await api_put(url_string, undefined);

  console.log(`Status from adding activity to visual is ${response.status}`)
}

export async function remove_activity_from_visual(visual_id: number, unique_id: string) {
  // Adds specified plan activity to the visual with supplied id.

  const url_string = `/api/v1/model/visuals/activities/${visual_id}/${unique_id}/`;
  const response = await api_delete(url_string);

  console.log(`Status from removing activity from visual is ${response.status}`)
}

export async function update_activities(visual_id:number, activity_field_updatas:any) {
  const url_string = `/api/v1/model/visuals/activities/${visual_id}/`;
  const response = await api_patch(url_string, activity_field_updatas);

  console.log(`Status from updating activity for visual ${visual_id} is ${response.status}`)
}

export async function get_swimlane_data(visual_id: number) {
  // Adds specified plan activity to the visual with supplied id.

  const url_string = `/api/v1/model/visuals/swimlanes/${visual_id}/`;
  const response = await api_get(url_string);

  (window as any).swimlane_data = response.data

  console.log(`Status from removing activity from visual is ${response.status}`)
}

export async function update_swimlane_records(visual_id:number, data:object) {
  const url_string = `/api/v1/model/visuals/swimlanes/${visual_id}/`;

  return await api_patch(url_string, data)
}

export async function update_visual_activities(visual_id:number, data:object) {
  const url_string = `/api/v1/model/visuals/activities/${visual_id}/`;

  return await api_patch(url_string, data)
}