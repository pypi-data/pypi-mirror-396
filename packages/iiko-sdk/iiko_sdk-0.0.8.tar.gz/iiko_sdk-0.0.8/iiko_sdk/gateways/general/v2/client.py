import uuid

from iiko_sdk.gateways.iiko_utils import BaseIIKOGateway


class GeneralGateway(BaseIIKOGateway):
    """ General API """
    version = 'api/2'

    async def get_external_menus(self):
        """ Получить Ids внешних меню из Web
        POST /api/2/menu """
        return await self.send_and_validate('/menu')

    async def get_menu_by_id(self, menu_id: int, restaurant_ids: list[uuid.UUID]):
        """ Получение Web меню по id
        POST /api/2/menu/by_id """
        return await self.send_and_validate('/menu/by_id', json_request={
            'externalMenuId': menu_id,
            'organizationIds': restaurant_ids
        })
