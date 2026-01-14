from apiflask import (
    APIBlueprint,
)
from flask.views import MethodView

from app.db.models.author import LevelAuthorCreator
from app.schemas.author import AuthorCreatorOut

# from app.schemas.level import LevelIn, LevelOut, LevelOutExtra

app_author = APIBlueprint("level_author", __name__)


class LevelAuthorCreatorView(MethodView):
    decorators = [
        app_author.doc(responses=[404]),
    ]

    @app_author.output(AuthorCreatorOut)
    def get(self, authorship_id):
        author = LevelAuthorCreator.query.filter_by(
            id=authorship_id
        ).one_or_none()

        return author

    # @app_levelauthor.output({}, status_code=204)
    # def delete(self, credit_id):
    #     credit = LevelCredit.query.filter_by(id=credit_id).one_or_none()
    #
    #     if not credit:
    #         abort(404)
    #
    #     db.session.delete(credit)
    #     db.session.commit()

    # @app_level.input(LevelIn)
    # @app_level.output(LevelOut)
    # def put(self, level_id, json_data):
    #     pass

    # @app_level.input(LevelIn(partial=True))
    # @app_level.output(LevelOut)
    # def patch(self, level_id, json_data):
    #     pass


# app_credit.add_url_rule(
#     "/v1/level_credits", view_func=LevelCredits.as_view("level_credits")
# )
app_author.add_url_rule(
    "/v1/level_author_creator/<int:authorship_id>",
    view_func=LevelAuthorCreatorView.as_view("level_author_creator"),
)
