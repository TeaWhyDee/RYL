from apiflask import APIBlueprint

# from app.utility.auth import auth

app_test = APIBlueprint("test", __name__)


@app_test.route("/ping")
@app_test.doc(summary="Say pong", description="Some description")
def ping():
    return "pong"
