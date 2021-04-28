import traceback
from typing import List, Dict

from elasticsearch import helpers
from elasticsearch.exceptions import NotFoundError

from skeletor import es
from skeletor.utility.logger import Logger
from skeletor.utility.exceptions.general_error import GeneralException
from skeletor.utility.text_helper import TextOperations


class BaseElasticRepo:
    def __init__(self, *args, **kwargs):
        self.logger = Logger().get(self.__class__.__name__)
        self.__txt__ = TextOperations()
        self.settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "index": {
                    "analysis": {
                        "filter": {
                            "filter_shingle": {
                                "type": "shingle",
                                "min_shingle_size": "2",
                                "max_shingle_size": "15",
                                "output_unigrams_if_no_shingles": "true",
                                "output_unigrams": "false"
                            },
                            "filter_stop": {
                                "type": "stop"
                            },
                            "filter_stemmer": {
                                "type": "snowball",
                                "language": "English"
                            },
                            "filter_edge_ngram": {
                                "type": "edgeNGram",
                                "min_gram": "2",
                                "max_gram": "50"
                            },
                            "filter_ngram": {
                                "type": "nGram",
                                "min_gram": "2",
                                "max_gram": "50"
                            }
                        },
                        "tokenizer": {
                            "edge_ngram_tokenizer": {
                                "type": "edge_ngram",
                                "min_gram": "1",
                                "max_gram": "50",
                                "token_chars": [
                                    "letter",
                                    "digit",
                                    "whitespace",
                                    "symbol"
                                ]
                            }
                        },
                        "analyzer": {
                            "keyword_analyzer": {
                                "filter": [
                                    "lowercase",
                                    "asciifolding",
                                    "trim",
                                    "reverse",
                                    "filter_ngram"
                                ],
                                "type": "custom",
                                "tokenizer": "keyword"
                            },
                            "shingle_analyzer": {
                                "filter": [
                                    "lowercase",
                                    "asciifolding",
                                    "trim",
                                    "reverse",
                                    "filter_stop",
                                    "filter_stemmer",
                                    "filter_shingle"
                                ],
                                "type": "custom",
                                "tokenizer": "standard"
                            },
                            "edge_ngram_analyzer": {
                                "filter": [
                                    "lowercase",
                                    "asciifolding",
                                    "trim",
                                    "reverse",
                                    "filter_edge_ngram"
                                ],
                                "type": "custom",
                                "tokenizer": "edge_ngram_tokenizer"
                            }
                        }
                    }
                }
            }
        }
        self.mappings = lambda x: {x: {"properties": {}}}

        self.text_mapping = {
            "type": "keyword",
            "fields": {
                "keywordstring": {
                    "type": "text",
                    "analyzer": "keyword_analyzer"
                },
                "edgengram": {
                    "type": "text",
                    "analyzer": "edge_ngram_analyzer"
                },
                "shingle": {
                    "type": "text",
                    "analyzer": "shingle_analyzer"
                },
                "completion": {
                    "type": "completion"
                }
            }
        }
        self.date_mapping = {
            "type": "date",
            "format": "yyyy-MM-dd HH:mm:ss"
        }
        self.boolean_mapping = {
            "type": "keyword",
            "fields": {
                "keywordstring": {
                    "type": "text",
                    "analyzer": "keyword_analyzer"
                }
            }
        }
        self.id_mapping = self.email_mapping = self.boolean_string_mapping = {
            "type": "keyword",
            "fields": {
                "keywordstring": {
                    "type": "text",
                    "analyzer": "keyword_analyzer"
                }
            }
        }
        self.list_mapping = {"type": "nested"}
        self.object_mapping = {"type": "object"}
        self.dict_mapping = {"properties": {}}

    def index_exits(self, _index):
        try:
            return es.indices.exists(_index)
        except NotFoundError:
            self.logger.info(f"{_index} not found")
            raise NotFoundError
        except Exception as e:
            self.logger.error(f'ERROR WHILE CHECKING INDEX EXITS {_index}' +
                              traceback.format_exc()
                              )
            raise GeneralException(message=str(e))

    def delete_database(self, _index):
        try:
            return es.indices.delete(index=_index)
        except NotFoundError:
            self.logger.error(f"{_index} not found")
            raise NotFoundError
        except Exception as e:
            self.logger.error(f'ERROR WHILE DELETING INDEX {_index}' +
                              traceback.format_exc()
                              )
            raise GeneralException(message=str(e))

    def delete_by_id(self, params: Dict):
        for k, __id in params.items():
            try:
                es.delete(index=k, doc_type=k + '_index', id=str(__id))
            except NotFoundError:
                self.logger.error(f"{k} {__id} not found")
            except Exception as e:
                self.logger.error(f'ERROR WHILE DELETING INDEX {k} {__id}' +
                                  traceback.format_exc()
                                  )
                raise GeneralException(message=str(e))
            pass
        pass

    def create_index(self, _index, _type, mappings=None):
        if self.is_connected:
            if '_index' not in _index:
                _index += '_index'
            if not es.indices.exists(_index):
                if mappings:
                    if _type not in mappings:
                        self.settings.update({"mappings": {_type: mappings}})
                    else:
                        self.settings.update({"mappings": mappings})
                es.indices.create(index=_index, body=self.settings)
            return _index
        raise GeneralException(message="Invalid Connection")

    def delete_index(self, _index):
        if self.is_connected:
            if '_index' not in _index:
                _index += '_index'
            if es.indices.exists(_index):
                es.indices.delete(index=_index)
                pass
            pass
        return _index


class ElasticInsertRepo(BaseElasticRepo):
    def __init__(self):
        super(ElasticInsertRepo, self).__init__()

    def reindex(self, source_index, target_index=None):
        if not target_index:
            target_index = source_index
        try:
            helpers.reindex(es, source_index, target_index)
        except Exception as e:
            self.logger.error(f'ERROR WHILE REINDEXING SOURCE: {source_index} TARGET: {target_index}' +
                              traceback.format_exc()
                              )
            raise GeneralException(message=str(e))

    def insert_record(self, _index, _type, _id, record):
        try:
            es.index(index=_index, doc_type=_type, id=_id, body=record)
            return True
        except NotFoundError:
            self.logger.error(f"{_index}/{_type}/{_id}/{record} not found")
            raise NotFoundError
        except Exception as e:
            self.logger.error(f'ERROR WHILE CREATING RECORD {_index}/{_type}/{_id}/{record}' +
                              traceback.format_exc()
                              )
            raise GeneralException(message=str(e))

    def update_by_query(self, _index, _type, query, key, params):
        try:
            if isinstance(params, dict) or isinstance(params, list):
                body = {
                    "script": {
                        "source": f"ctx._source.{key}=params;",
                        "lang": "painless",
                        "params": params
                    },
                    "query": query
                }
            else:
                body = {
                    "script": {
                        "source": f"ctx._source.{key}={params};",
                        "lang": "painless"
                    },
                    "query": query
                }

            result = es.update_by_query(
                index=_index, doc_type=_type, body=body)
            self.logger.info(f"UPDATE_BY_QUERY RESULT {_index}/{_type}/_update_by_query {body} => {result}")
            return result.get("total"), result.get("updated")
        except NotFoundError:
            self.logger.error(f"{_index}/{_type} not found")
            raise NotFoundError
        except Exception as e:
            self.logger.error(f'ERROR WHILE UPDATE_BY_QUERY {_index}/{_type}/{body}' +
                              traceback.format_exc()
                              )
            raise GeneralException(message=str(e))

    def update_doc(self, _index, _type, _id, doc, upsert=True):
        try:
            body = {'doc': doc, 'doc_as_upsert': True} if upsert else {
                'doc': doc}
            result = es.update(index=_index, doc_type=_type, id=_id, body=body)
            self.logger.info(f"UPDATE_DOC {upsert} RESULT {result}")
            return True if result.get("result", "noop") != "noop" and result.get("result",
                                                                                 "noop") == "updated" else False
        except NotFoundError:
            self.logger.error(f"{_index}/{_type} not found")
            raise NotFoundError
        except Exception as e:
            self.logger.error(f'ERROR WHILE UPSERT RECORD {_index}/{_type}/{_id}/{doc}' +
                              traceback.format_exc()
                              )
            raise GeneralException(message=str(e))

    def insert_bulk_record(self, records):
        try:
            record_size = len(records)
            batch_state = 0
            batch_size = 30
            while (batch_state < record_size):
                if (record_size - (batch_state + batch_size)) > batch_size:
                    batch = records[batch_state:(batch_state + batch_size)]
                    batch_state += batch_size
                else:
                    batch = records[batch_state:]
                    batch_state = record_size
                if batch:
                    helpers.bulk(es, batch)
        except Exception as e:
            self.logger.error(f'ERROR WHILE INSERTING BULK RECORD' +
                              traceback.format_exc()
                              )
            raise GeneralException(message=str(e))


class ElasticSearchRepo(BaseElasticRepo):
    def __init__(self, *args, **kwargs):
        super(ElasticSearchRepo, self).__init__(*args, **kwargs)

    def __process__(self, data):
        result = None
        if "hits" in data:
            result = data.get("hits", {}).get("hits", [{}]) if data.get(
                "hits", {}).get("total", 0) else []
        elif "_source" in data:
            result = data.get("_source", {})
        return result

    def __check_search_after__(self, _index, _type, query, search_after=None):
        _from = query.get("from", 0)
        _size = query.get("size", 10)
        if 10000000 < (_from + _size) <= self.get_doc_count(_index, _type):
            if not search_after:
                temp_size = 0
                for hop in range(10000000 - _size, _from, _size):
                    if hop < 10000000:
                        query.update({"from": hop})
                        hits = self.get_by_search(_index, _type, query)
                        search_after = hits[-1].get("sort", [None]).pop()
                    else:
                        temp_size += _size
                    if temp_size == 1000 and search_after:
                        query.pop("from", None)
                        query.update(
                            {"size": temp_size, "search_after": [search_after]})
                        hits = self.get_by_search(_index, _type, query)
                        search_after = hits[-1].get("sort", [None]).pop()
                        temp_size = 0
                query.pop("from", None)
                query.update({"search_after": [search_after], "size": _size})
                hits = self.get_by_search(_index, _type, query)
                search_after = hits[-1].get("sort", [None]).pop()
            query.pop("from", None)
            query.update({"search_after": [search_after], "size": _size})
        self.logger.info(f"[INFO] QUERY {query}")
        return query

    def get_all_indices(self):
        indices = es.indices.get_alias()
        indices.pop(".kibana", None)
        return list(indices)

    def get_doc_count(self, _index, _type, doc=None):
        try:
            if doc:
                doc.pop("_source", None)
                doc.pop("sort", None)
                doc.pop("size", None)
                res = es.count(_index, _type, doc)
            else:
                res = es.count(_index, _type)
            return res.get('count', -1)
        except NotFoundError:
            self.logger.error(f"{_index}/{_type} not found")
            raise NotFoundError
        except Exception as e:
            self.logger.error(f'ERROR WHILE GETTING COUNT {_index}/{_type}' +
                              traceback.format_exc()
                              )
            raise GeneralException(message=str(e))

    def get_by_id(self, _index, _type, _id):
        try:
            return self.__process__(es.get(_index, _type, _id))
        except NotFoundError:
            self.logger.error(f"{_index}/{_type}/{_id} not found")
            return None
        except Exception as e:
            self.logger.error(f'ERROR WHILE GETTING RECORD BY ID {_index}/{_type}/{_id}' +
                              traceback.format_exc()
                              )
            raise GeneralException(message=str(e))

    def get_by_scan(self, _index, _type, query, _source=None):
        try:
            if _source:
                query.update({"_source": _source})
            self.logger.info(f"GET {_index}/{_type}/_search\n{query}")
            return helpers.scan(
                es, index=_index, doc_type=_type,
                query=query, scroll='10m', timeout='10m'
            )
        except NotFoundError:
            self.logger.error(f"{_index}/{_type} NOT FOUND")
            raise NotFoundError
        except Exception as e:
            self.logger.error(f'ERROR WHILE GETTING RECORD BY SCAN {_index}/{_type}/{query}' +
                              traceback.format_exc()
                              )
            raise GeneralException(message=str(e))

    def get_by_search(self, _index, _type, query, _source=None):
        try:
            if _source:
                query.update({"_source": _source})
            self.logger.info(f"GET {_index}/{_type}/_search\n{query}")
            return self.__process__(es.search(_index, _type, query))
        except NotFoundError:
            self.logger.error(f"{_index}/{_type} NOT FOUND")
            raise NotFoundError
        except Exception as e:
            self.logger.error(f'ERROR WHILE GETTING RECORD BY SEARCH {_index}/{_type}/{query}' +
                              traceback.format_exc()
                              )
            raise GeneralException(message=str(e))

    def get_suggestions(self, _index, _type, key, prefix, size=500, _source=None, fuzzy=False, fuzziness=None):
        try:
            query = {
                "query": {
                    "bool": {
                        "minimum_should_match": 1,
                        "should": [
                            {
                                "match": {
                                    key: prefix
                                }
                            },
                            {
                                "match_phrase": {
                                    f"{key}.{'keywordstring' if key == 'name' else 'keyword'}": prefix
                                }
                            },
                            {
                                "match_phrase_prefix": {
                                    f"{key}.{'keywordstring' if key == 'name' else 'keyword'}": prefix
                                }
                            }
                        ]
                    }
                },
                "size": size,
                "sort": [
                    {
                        "_score": {
                            "order": "desc"
                        }
                    }
                ]
            }
            if key == "name" or (_type == 'user' and key == 'email'):
                query.get("query", {}).get("bool", {}).get("should", []).append({
                    "match": {
                        f"{key}.edgengram": prefix
                    }
                })
            if _source:
                query.update({"_source": _source})
            if fuzzy:
                query.get("query", {}).get("bool", {}).get("should", []).append({
                    "fuzzy": {
                        f"{key}.edgengram": {
                            "value": prefix,
                            "fuzziness": 1,
                            "max_expansions": 50,
                            "prefix_length": 0
                        }
                    }
                })
            self.logger.info(f"GET {_index}/{_type}/_search\n{query}")
            return self.__process__(es.search(_index, _type, query))
        except NotFoundError:
            self.logger.info(f"{_index}/{_type} NOT FOUND")
            raise NotFoundError
        except Exception as e:
            self.logger.info(f"ERROR WHILE GETTING SUGGESTIONS {_index}/{_type}/{query}" +
                             traceback.format_exc()
                             )
            raise GeneralException(message=str(e))

    def get_by_scroll(self, **kwargs):
        """ kwargs: _scroll_id=None, _index=None, _type=None, query=None """
        try:
            result = {
                "scroll_id": None,
                "record_count": -1,
                "batch_count": 1000,
                "data": []
            }
            data = {}
            if kwargs.get("_scroll_id", None):
                data = es.scroll(
                    scroll_id=kwargs.get("_scroll_id"), scroll='2m'
                )
            elif kwargs.get("_index", None) and kwargs.get("_type", None) and kwargs.get("query", None):
                data = es.search(
                    index=kwargs.get("_index"), doc_type=kwargs.get("_type"), body=kwargs.get("query"),
                    size=1000, scroll='2m'
                )
            result.update({
                "scroll_id": data.get("_scroll_id", None),
                "record_count": data.get("hits", {}).get("total", 0)
            })
            data = self.__process__(data)
            if data:
                result.update({"data": data, "batch_count": len(data)})
            else:
                result.update({"data": [], "batch_count": 0})
            return result
        except NotFoundError:
            self.logger.info(f"{kwargs.get('_index')}/{kwargs.get('_type')} NOT FOUND")
            raise NotFoundError
        except Exception as e:
            self.logger.info(
                f"ERROR WHILE GETTING RECORD BY SEARCH AFTER {kwargs.get('_index')}/{kwargs.get('_type')}/{kwargs.get('query')}" +
                traceback.format_exc()
                )
            raise GeneralException(message=str(e))

    def get_by_search_after(self, *args, **kwargs):
        """ kwargs: _index=None, _type=None, query=None, size=10, page=1, search_after=None"""
        try:
            result = {"total": 0, "size": 0, "data": []}
            if ("_index" in kwargs and "_type" in kwargs) or len(args) >= 2:
                _index = kwargs.get("_index", None) or args[0]
                _type = kwargs.get("_type", None) or args[1]
                try:
                    query = kwargs.get("query", {}) or args[2] or {
                        "query": {"match_all": {}}}
                except IndexError:
                    query = {"query": {"match_all": {}}}
                try:
                    _size = self.__txt__._int(kwargs.get(
                        "size", 0)) or self.__txt__._int(args[3]) or 10
                except IndexError:
                    _size = 10
                try:
                    _from = _size * (
                            (self.__txt__._int(kwargs.get("page", 0))
                             or self.__txt__._int(args[4]) or 1) - 1
                    )
                except IndexError:
                    _from = 0
                try:
                    search_after = kwargs.get(
                        "search_after", None) or args[5] or None
                except IndexError:
                    search_after = None
                try:
                    sort_by = kwargs.get("sort_by", None) or args[6] or None
                except IndexError:
                    sort_by = "_id:desc"
                sort_by = sort_by.split(":")
                sort_by = {sort_by[0] or "_id" if len(
                    sort_by) > 0 else "_id": sort_by[1] or "desc" if len(sort_by) > 1 else "desc"}

                query.update({"size": _size, "sort": [sort_by], "from": _from})
                query = self.__check_search_after__(
                    _index, _type, query, search_after)
                self.logger.info(f"GET {_index}/{_type}/_search\n{query}")
                hits = es.search(_index, _type, query)
                result.update({"total": hits.get("hits", {}).get("total", 0)})
                hits = self.__process__(hits)
                result.update({
                    "data": hits,
                    "size": len(hits) if hits else 0,
                    "search_after": hits[-1].get("sort", [None])[0] if query.get("search_after",
                                                                                 None) or 10000 == _from + _size else None
                })
            return result
        except NotFoundError:
            self.logger.info(f"{_index}/{_type} NOT FOUND")
            raise NotFoundError
        except Exception as e:
            self.logger.info(f'ERROR WHILE GETTING RECORD BY SEARCH AFTER {_index}/{_type}/{query}' +
                             traceback.format_exc()
                             )
            raise GeneralException(message=str(e))
