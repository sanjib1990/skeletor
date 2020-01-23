from flask import request

from skeletor.utility.decorators import login_required, authenticate
from src.services.user_context import UserContext
from .base import BaseController
from src.repositories.app_property import AppPropertyRepo


class AppPropertyController(BaseController):
    def get_search_dict(self):
        return {}

    def __init__(self, *args, **kwargs):
        self.repo = AppPropertyRepo()
        super(AppPropertyController, self).__init__(*args, **kwargs)
        pass

    # @login_required
    # @authenticate
    def get(self, object_id=None):
        return self.renderer.render(self.repo.get())

    @login_required
    @authenticate
    def post(self):
        return self.renderer.render(self.repo.upsert(request.json, UserContext().user()))
