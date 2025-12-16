import decimal
import uuid
from dataclasses import dataclass
from datetime import datetime

from iiko_sdk.gateways.iiko_utils import BaseIIKOGateway
from iiko_sdk.gateways.orders.enums import DeliveryType, PaymentTypeKind


@dataclass
class Payment:
    payment_type_id: uuid.UUID
    payment_type_kind: PaymentTypeKind
    amount: decimal.Decimal
    is_processed_externally: bool | None = None
    is_fiscalized_externally: bool | None = None
    payment_additional_data: dict | None = None

    def to_json(self):
        data = {
            'sum': self.amount,
            'paymentTypeKind': self.payment_type_kind,
            'paymentTypeId': str(self.payment_type_id)
        }
        if self.is_processed_externally is not None:
            data['isProcessedExternally'] = self.is_processed_externally

        if self.is_fiscalized_externally is not None:
            data['isFiscalizedExternally'] = self.is_fiscalized_externally

        if self.payment_additional_data is not None:
            data['paymentAdditionalData'] = self.payment_additional_data

        return data


@dataclass
class OrderItem:
    product_id: uuid.UUID
    amount: int
    item_type: str | None = 'Product'


ORDER_STATUSES = {'New', 'Bill', 'Closed', 'Deleted'}
ORDER_CREATION_STATUSES = {'Success', 'InProgress', 'Error'}


class OrdersGateway(BaseIIKOGateway):
    """ Orders API """
    version = 'api/1'

    async def get_orders_by_tables(self, restaurant_ids: list[uuid.UUID], table_ids: list[uuid.UUID],
                                   statuses: list[str] | None = None, date_from: datetime | None = None,
                                   date_to: datetime | None = None):
        """ Получение заказов по id столов
        POST /api/1/order/by_table """
        json_request = {
            'organizationIds': restaurant_ids,
            'tableIds': table_ids
        }
        if statuses:
            statuses = set(statuses)
            diff = statuses - ORDER_STATUSES
            if diff:
                raise ValueError(f'Invalid statuses {','.join(diff)}')
            json_request['statuses'] = list(statuses)

        if date_from:
            # yyyy-MM-dd HH:mm:ss.fff
            json_request['dateFrom'] = date_from.strftime('%Y-%m-%d %H:%M:%S.%f')

        if date_to:
            json_request['dateTo'] = date_to.strftime('%Y-%m-%d %H:%M:%S.%f')

        return await self.send_and_validate('/order/by_table', json_request=json_request)

    async def get_orders_by_ids(self, restaurant_ids: list[uuid.UUID] | uuid.UUID,
                                order_ids: list[uuid.UUID] | None = None, pos_order_ids: list[uuid.UUID] | None = None):
        """ Получение заказов по id
        POST /api/1/order/by_id """
        if not order_ids and not pos_order_ids:
            raise ValueError('order_ids and pos_order_ids are none or empty')
        if isinstance(restaurant_ids, uuid.UUID):
            restaurant_ids = [restaurant_ids]
        json_request = {
            'organizationIds': restaurant_ids,
        }
        if order_ids:
            json_request['orderIds'] = order_ids

        if pos_order_ids:
            json_request['posOrderIds'] = pos_order_ids

        return await self.send_and_validate('/order/by_id', json_request=json_request)

    async def create_order(self, restaurant_id: uuid.UUID, terminal_group_id: uuid.UUID, order_items: list[OrderItem],
                           table_ids: list[uuid.UUID] | None = None,
                           payments: list[Payment] | None = None,
                           external_number: str | None = None):
        """ Создание заказа
        POST /api/1/order/create """
        if not order_items:
            raise ValueError('Order items is none or empty')

        json_request = {
            'organizationId': restaurant_id,
            'terminalGroupId': terminal_group_id,
            'order': {
                'items': [
                    {
                        'productId': i.product_id,
                        'amount': i.amount,
                        'type': i.item_type
                    } for i in order_items
                ]
            }
        }
        if external_number:
            json_request['order']['externalNumber'] = external_number

        if table_ids:
            json_request['order']['tableIds'] = table_ids

        if payments:
            json_request['order']['payments'] = [p.to_json() for p in payments]

        return await self.send_and_validate('/order/create', json_request=json_request)


class DeliveriesGateway(BaseIIKOGateway):
    """ Deliveries API """
    version = 'api/1'

    async def get_orders_by_ids(self, restaurant_id: uuid.UUID,
                                order_ids: list[uuid.UUID] | None = None,
                                pos_order_ids: list[uuid.UUID] | None = None):
        """ Получение заказов по id
        POST /api/1/order/by_id """
        if not order_ids and not pos_order_ids:
            raise ValueError('order_ids and pos_order_ids are none or empty')

        json_request = {
            'organizationId': restaurant_id
        }
        if order_ids:
            json_request['orderIds'] = order_ids

        if pos_order_ids:
            json_request['posOrderIds'] = pos_order_ids

        return await self.send_and_validate('/deliveries/by_id', json_request=json_request)

    async def create_order(self, restaurant_id: uuid.UUID, phone: str, order_items: list[OrderItem],
                           terminal_group_id: uuid.UUID | None = None,
                           delivery_type: DeliveryType | None = DeliveryType.DELIVERY_BY_CLIENT,
                           payments: list[Payment] | None = None,
                           external_number: str | None = None):
        """ Создание заказа
        POST /api/1/order/create """
        if not order_items:
            raise ValueError('Order items is none or empty')

        json_request = {
            'organizationId': restaurant_id,
            'order': {
                'phone': phone,
                'orderServiceType': delivery_type,
                'items': [
                    {
                        'productId': i.product_id,
                        'amount': i.amount,
                        'type': i.item_type
                    } for i in order_items
                ]
            }
        }

        if external_number:
            json_request['order']['externalNumber'] = external_number

        if terminal_group_id:
            json_request['terminalGroupId'] = terminal_group_id

        if payments:
            json_request['order']['payments'] = [p.to_json() for p in payments]

        return await self.send_and_validate('/deliveries/create', json_request=json_request)
