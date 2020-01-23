from typing import List
from flask import jsonify, make_response


class JSONRenderer(object):
    def render(self, data, status=200, only: List[str] = None, exclude: List[str] = None):
        """
        Render a JSON response.
        :param data: dict/List/ serializeable object
        :param status: int
        :param only: list of attributes only to be sent
        :param exclude: list of attributes to be excluded
        :return:
        """
        ok_flag = 200 <= status <= 208
        err_flag = not ok_flag

        if data and err_flag and "errors" in data and isinstance(data.get('errors'), str):
            data["errors"] = [data["errors"]]

        response = {
            "is_success": ok_flag,
            "has_error": err_flag,
            "data": data,
            "status": status
        }

        self.handle_only(response, only)
        self.handle_exclude(response, exclude)

        return make_response(jsonify(response), status)

    def handle_only(self, response: dict, only: List[str]):
        data = response.get('data')

        if response.get('has_error') or (only is None) or (not only):
            return

        if response.get('data', None) and isinstance(response.get('data', None), dict):
            data = self.handle_dict_only(response.get('data'), only)

        if response.get('data', None) and isinstance(response.get('data', None), list):
            data = self.handle_list_dict_only(response.get('data'), only)

        response['data'] = data

    def handle_dict_only(self, data: dict, only: List[str]):
        new_data = {}
        for k, v in data.items():
            if k in only:
                new_data[k] = v

        return new_data

    def handle_list_dict_only(self, data: List[dict], only: List[str]):
        new_list: List[dict] = []
        for k, v in enumerate(data):
            new_list.append(self.handle_dict_only(v, only))

        return new_list

    def handle_exclude(self, response: dict, exclude: List[str]):
        data = response.get('data')

        if response.get('has_error') or (exclude is None) or (not exclude):
            return

        if response.get('data', None) and isinstance(response.get('data', None), dict):
            keys = list(response.get('data').keys())
            for v in exclude:
                try:
                    keys.remove(v)
                except ValueError:
                    pass

            data = self.handle_dict_only(response.get('data'), keys)

        if response.get('data', None) and isinstance(response.get('data', None), list):
            keys = list(response.get('data')[0].keys())
            for v in exclude:
                try:
                    keys.remove(v)
                except ValueError:
                    pass
            data = self.handle_list_dict_only(response.get('data'), keys)

        response['data'] = data
