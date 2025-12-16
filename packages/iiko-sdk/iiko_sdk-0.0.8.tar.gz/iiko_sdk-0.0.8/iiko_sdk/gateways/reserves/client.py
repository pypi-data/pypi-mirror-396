import uuid

from iiko_sdk.gateways.iiko_utils import BaseIIKOGateway


class ReservesGateway(BaseIIKOGateway):
    """ Reserves API """
    version = 'api/1'

    async def get_restaurant_sections(self, terminal_group_ids: list[uuid.UUID], return_schema: bool | None = True,
                                      revision: int | None = 0):
        """ Получение списка залов и столов ресторана
        POST /api/1/reserve/available_restaurant_sections """
        return await self.send_and_validate('/reserve/available_restaurant_sections', json_request={
            'terminalGroupIds': terminal_group_ids,
            'returnSchema': return_schema,
            'revision': revision
        })
