from copy import deepcopy
from typing import Dict, Any, Union, List

import backoff
from gremlin_python.driver.client import Client

operator_map = {">=": "gte", ">": "gt", "<=": "lte", "<": "lt", "=": "eq", "!=": "neq"}


def is_search_criteria(param: Any):
    if not isinstance(param, Dict):
        return False

    return (len(param) == 1 and all(key in ["and", "or"] for key in param.keys())) or (
        len(param) == 3
        and all(
            key in ["value", "attribute", "operator", "attribute_target"]
            for key in param.keys()
        )
    )


def backoff_initialize_client(data: Dict):
    """A method used by the backoff decorator to reset the connection"""
    gqs: GremlinQuerySupport
    gqs = data["args"][0]
    gqs.initialize_client()


class GremlinQuerySupport:
    def __init__(
        self, host: str, port: str, query_definitions: Dict, protocol: str = "wss"
    ):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.query_definitions = query_definitions
        self.initialize_client()

    def initialize_client(self):
        self.client = Client(f"{self.protocol}://{self.host}:{self.port}/gremlin", "g")

    def execute_query(self, query_name: str, query_values: Dict) -> List[Any]:
        if query_name not in self.query_definitions:
            raise Exception(f"Query, {query_name}, not found.")

        query_definition = self.query_definitions[query_name]
        values = deepcopy(query_values)
        for key in values:
            if is_search_criteria(values[key]):
                values[key] = self._build_search_criteria(values[key])
        query_to_send = query_definition["query_template"].format(**values)
        return self._do_execute_query(query_to_send)

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_client,
        interval=1,
    )
    def _do_execute_query(self, query: str) -> List[Any]:
        return self.client.submit(query).all().result()

    def _build_search_criteria(self, search_filter: Dict[str, Union[Dict, str]]):
        if "and" in search_filter:
            return f"and({','.join([self._build_search_criteria(sub_criteria) for sub_criteria in search_filter['and']])})"
        elif "or" in search_filter:
            return f"or({','.join([self._build_search_criteria(sub_criteria) for sub_criteria in search_filter['or']])})"
        else:
            target = (
                (
                    search_filter["value"]
                    if not isinstance(search_filter["value"], str)
                    else f"'{search_filter['value']}'"
                )
                if "value" in search_filter
                else f"values('{search_filter['attribute_target']}')"
            )
            return f"values('{search_filter['attribute']}').is({operator_map[search_filter['operator']]}({target}))"

        pass
