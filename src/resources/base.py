import abc
from flask import request
from flask_restful import Resource

from skeletor import JSONRenderer
from skeletor.utility.decorators import login_required, authenticate
from skeletor.utility.exceptions.already_exists_exception import AlreadyExistsException
from src.services.user_context import UserContext


class BaseController(Resource):
    repo = None

    def __init__(self, *args, **kwargs):
        super(BaseController, self).__init__(*args, **kwargs)
        self.renderer = JSONRenderer()

    @abc.abstractmethod
    def get_search_dict(self):
        """
        get a dict to verify existence of an entity
        format {db_column _name:request_param_name}
        :return: dict
        """
        pass

    @login_required
    @authenticate
    def get(self, object_id=None):
        args = request.args
        if object_id:
            entity = self.repo.find(object_id=object_id)
            if not isinstance(entity, dict):
                if args:
                    entity = entity.asdict(includes=args.get('includes')) if entity else {}
                else:
                    entity = entity.asdict() if entity else {}            
        else:
            entity = self.repo.fetch(**args)
            for indx, grp in enumerate(entity):
                if not isinstance(grp, dict):
                    if args:
                        grp = grp.asdict(includes=args.get('includes'))
                    else:
                        grp = grp.asdict()
                entity[indx] = grp
        return self.renderer.render(entity)

    @login_required
    @authenticate
    def post(self):
        error = self.repo.validate_data(request.json)
        if error:
            return self.renderer.render({"errors": error}, 400)

        if self.get_search_dict():
            existing = self.repo.find(**self.get_search_dict())

            if existing:
                raise AlreadyExistsException

        entity = self.repo.create(
            request.json,
            UserContext().user().asdict()
        )

        if isinstance(entity, dict):
            return self.renderer.render(entity)

        return self.renderer.render(entity.asdict())

    @login_required
    @authenticate
    def put(self, object_id: str):
        error = self.repo.validate_data(request.json)
        if error:
            return self.renderer.render({"errors": error}, 400)

        request.json['object_id'] = object_id
        entity = self.repo.update(
            request.json,
            UserContext().user().asdict()
        )
        if isinstance(entity, dict):
            return self.renderer.render(entity)

        return self.renderer.render(entity.asdict(**{}))

    @login_required
    @authenticate
    def delete(self, object_id: str):
        self.repo.delete(object_id, UserContext().user().asdict())
        return self.renderer.render({})
