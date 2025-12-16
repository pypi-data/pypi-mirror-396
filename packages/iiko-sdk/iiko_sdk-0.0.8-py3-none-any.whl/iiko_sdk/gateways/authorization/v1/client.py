from http_misc import http_utils, services, retry_policy

policy = retry_policy.AsyncRetryPolicy()


class AuthorizationGateway:
    """ Authorization API """
    version = 'api/1'

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_api_token(self, api_login: str) -> str:
        """ Получить api_token
        POST /api/1/access_token """
        url = http_utils.join_str(self.base_url, self.version, '/access_token')
        request = {
            'method': 'POST',
            'url': url,
            'cfg': {
                'json': {
                    'apiLogin': api_login
                }
            }
        }

        response_data = await http_utils.send_and_validate(services.HttpService(), request, policy=policy)
        if 'token' not in response_data:
            raise KeyError('Invalid response. Token is absent.')

        return response_data['token']
