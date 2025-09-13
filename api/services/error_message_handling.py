"""
Components which implement the passing and processing of error messages from the server back to the
client as part of processing and api request.
"""
import json
from django.contrib.messages import get_messages


class MessagesToHeaderMixin:
    """
    Drains Django messages and attaches to a response header as JSON.  Note, we are placing the messages
    in the header to avoid breaking existing code if the messages are placed in the body in the case where the
    response is a list, not a dict.
    """
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)

        try:
            drained_messages = [{"level": m.level_tag, "message": m.message} for m in get_messages(request)]
            if drained_messages:
                response["X-Server-Messages"] = json.dumps(drained_messages)
        except Exception:
            # We don't want to break the API if we can't drain the messages.
            pass

        return response