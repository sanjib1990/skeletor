import traceback
from skeletor.utility.exceptions.general_error import GeneralException
from skeletor.utility.exceptions.not_found_exception import NotFoundException
from skeletor.utility.exceptions.validation_exception import ValidationException
from src.models import User
from src.models.arango.app_property import AppProperty
from src.repositories.arango.base import Base


class AppPropertyRepo(Base):
    model: AppProperty
    __index_key__ = '__app_properties__'

    def __init__(self, *args, **kwargs):
        self.model = AppProperty()
        self._schema = {}
        super(AppPropertyRepo).__init__(*args, **kwargs)

    @property
    def schema(self):
        return self._schema

    def get(self):
        cached = self.get_from_cache(self.__index_key__)
        if cached is not None:
            return cached
        props = self.__get()

        if props:
            self.store_in_cache(self.__index_key__, props['data'])
            return props['data']

        return None

    def upsert(self, data: dict, user: User):
        current = self.__get()
        if not current:
            return self.__create(data, user)
        current['data'] = data
        return self.__update(current, user)

    def __update(self, updated_data, user: User):
        updated_data['updated_by'] = user.email

        try:
            self.model.db.replace(updated_data)
            # self.model.db.delete(updated_data.get('_key'))
            # self.__create(updated_data, user)
            self.evict_cache()
            self.store_in_cache(self.__index_key__, updated_data['data'])
        except Exception as e:
            self.logger.fatal(f'Update error: {traceback.format_exc()}')
            raise GeneralException(message=str(e))

        return updated_data['data']

    def __create(self, data, user: User):
        app_prop = AppProperty()
        app_prop.data = data if 'data' not in data else data['data']
        app_prop.is_active = True
        app_prop.created_by = user.email
        if '_key' in data and data['_key'] and len(data['_key']) > 0:
            app_prop._key = data['_key']
        ins = app_prop.asdict()
        self.model.db.insert(ins)
        self.evict_cache()
        self.store_in_cache(self.__index_key__, app_prop.data)
        return data

    def __get(self):
        query = 'for x in ' + self.model.__collection_name__ \
                + ' filter x.is_active == true return x'
        cursor = self.model.aql.execute(query)
        res = []
        for x in cursor:
            res.append(x)
            pass

        if not res:
            return None

        return res[0]

    def partially_update(self, data: dict, user: User):
        """
        in app property update only specific part of the config. Basically inside data
        :param user:
        :param data:
        :return:
        """
        current = self.__get()
        if not current:
            raise NotFoundException
        _data_ = current['data']
        for k, v in data.items():
            if k not in _data_:
                raise ValidationException(message=f"Invalid key {k}")
            _data_[k] = v
            pass

        current['data'] = _data_
        return self.__update(current, user)
