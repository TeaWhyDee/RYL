from apiflask.fields import Integer
from apiflask import Schema
from apiflask.validators import Range


class PageSchema(Schema):
    page = Integer(load_default=1)
    per_page = Integer(load_default=20, validate=Range(min=1, max=100))
