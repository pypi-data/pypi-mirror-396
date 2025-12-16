import time

from http_misc.services import Transformer

from iiko_sdk.gateways.authorization.v1.client import AuthorizationGateway


class MemoryCache:
    """
    Класс, реализующий хранение access_token памяти
    """
    memory_cache = {}
    _time_dict = {}

    def __init__(self, expired_timeout: float | None = 600):
        """
        expired_timeout - время устаревания кэша по умолчанию, в секундах.
        По умолчанию 600 секунд (10 минут). Вы можете установить expired_timeout в None, тогда кэш никогда не устареет.
        Если указать 0, все ключи будут сразу устаревать (таким образом можно заставить «не кэшировать»).
        """
        self.expired_timeout = expired_timeout

    def set_value(self, cache_key: str, access_token: str) -> None:
        """ Установка значения токена """
        self.memory_cache[cache_key] = access_token
        self._time_dict[cache_key] = time.time() + self.expired_timeout

    def get_value(self, cache_key: str) -> str | None:
        """ Получение значения токена """
        if cache_key in self.memory_cache:
            if self._key_is_expired(cache_key):
                self.delete_key(cache_key)
                return None

            access_token = self.memory_cache.get(cache_key)
            return access_token

        return None

    def delete_key(self, cache_key: str):
        """ Очистка кеша по ключу """
        if cache_key in self.memory_cache:
            self.memory_cache.pop(cache_key)

        if cache_key in self._time_dict:
            self._time_dict.pop(cache_key)

    def _key_is_expired(self, cache_key: str) -> bool:
        """ Проверка срока жизни ключа """
        if self.expired_timeout is None:
            return False

        if self.expired_timeout == 0:
            return True

        if cache_key in self._time_dict:
            return time.time() > self._time_dict[cache_key]

        return True


class SetAuthorization(Transformer):
    """
    Указывает у запроса заголовок Authorization вида 'Bearer {access_token}' предварительно запросив токен пользователя
    """

    def __init__(self, api_login: str, base_url: str, cache=None):
        self.api_login = api_login
        self.base_url = base_url
        self.cache = cache
        self.auth_gateway = AuthorizationGateway(self.base_url)

    async def modify(self, *args, **kwargs):
        access_token = await self._get_access_token()

        headers = kwargs.setdefault('cfg', {}).setdefault('headers', {})
        headers['Content-Type'] = 'application/json; charset=utf-8'
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'

        return args, kwargs

    async def _get_access_token(self):
        access_token = None
        if self.cache:
            access_token = self.cache.get_value(self.api_login)

        if access_token is None:
            access_token = await self._get_remote_access_token()

        return access_token

    async def _get_remote_access_token(self):
        access_token = await self.auth_gateway.get_api_token(self.api_login)

        if self.cache:
            self.cache.set_value(self.api_login, access_token)

        return access_token
