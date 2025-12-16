import uuid

from iiko_sdk.gateways.iiko_utils import BaseIIKOGateway


class GeneralGateway(BaseIIKOGateway):
    """ General API """
    version = 'api/1'

    async def get_terminal_groups(self, restaurant_ids: list[uuid.UUID], include_disabled: bool | None = True,
                                  external_data: list[str] | None = None):
        """ Получение список групп терминалов
        POST /api/1/terminal_groups """
        json_request = {
            'organizationIds': restaurant_ids,
            'includeDisabled': include_disabled
        }

        if external_data:
            json_request['returnExternalData'] = external_data

        return await self.send_and_validate('/terminal_groups', json_request=json_request)

    async def get_organizations(self):
        """ Получение списка организаций
        POST /api/1/organizations """
        return await self.send_and_validate('/organizations')

    async def get_order_types(self, restaurant_ids: list[uuid.UUID]):
        """ Получение типов заказов
         POST /api/1/deliveries/order_types """
        return await self.send_and_validate('/deliveries/order_types', json_request={
            'organizationIds': restaurant_ids
        })

    async def get_payment_types(self, restaurant_ids: list[uuid.UUID]):
        """ Получение типов оплат
         POST /api/1/payment_types """
        return await self.send_and_validate('/payment_types', json_request={
            'organizationIds': restaurant_ids
        })
