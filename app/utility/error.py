from apiflask import HTTPError


class RYLUpdateNoChange(HTTPError):
    status_code = 422
    message = "Your update request must change at least one field."
