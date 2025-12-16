from http_misc import services, http_utils, retry_policy

policy = retry_policy.AsyncRetryPolicy()


class BaseIIKOGateway:
    """ Base IIKO Gateway """
    version = ''

    def __init__(self, base_url: str, service: services.BaseService):
        self.base_url = base_url
        self.service = service

    async def send_and_validate(self, relative_url: str, json_request: dict | None = None,
                                method: str | None = 'POST',
                                expected_status: int | None = 200):
        url = http_utils.join_str(self.base_url, self.version, relative_url)

        if json_request is None:
            json_request = {}

        request = {
            'method': method,
            'url': url,
            'cfg': {
                'json': json_request
            }
        }

        return await http_utils.send_and_validate(self.service, request, expected_status=expected_status, policy=policy)


def filter_list_by_key(filter_data: list, id_key: str, key_value,
                       find_first: bool | None = True,
                       raise_if_not_found: bool | None = False) -> list | dict:
    if not isinstance(filter_data, list):
        raise KeyError('Invalid filter data - expected list.')

    if not isinstance(key_value, str):
        key_value = str(key_value)

    data_filter = filter(lambda x: str(x[id_key]) == key_value, filter_data)
    if find_first:
        data = next(data_filter, None)
        if data is None and raise_if_not_found:
            raise KeyError(f'Item with field {id_key} not found for key value {key_value}')
        return data

    return list(data_filter)


def filter_list_by_parent_id(filter_data: dict | list, parent_id, list_key: str | None = None,
                             id_key: str | None = 'organizationId', items_key: str | None = 'items',
                             raise_if_not_found: bool | None = False) -> list:
    """ Фильтрация ответа по ИД родительской сущности """
    if list_key and list_key not in filter_data:
        raise KeyError(f'Invalid response - {list_key} not found.')

    if list_key:
        filter_data = filter_data[list_key]

    data = filter_list_by_key(filter_data, id_key, parent_id, raise_if_not_found=raise_if_not_found)

    if items_key not in data:
        raise KeyError(f'Invalid response - {items_key} not found.')

    return data[items_key]
