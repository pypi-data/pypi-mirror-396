import asyncio
import decimal
import uuid

import pytest
from http_misc import services

from iiko_sdk.gateways.authorization.v1.client import AuthorizationGateway
from iiko_sdk.gateways.iiko_utils import filter_list_by_parent_id, filter_list_by_key
from iiko_sdk.gateways.general.v1 import client as client_v1
from iiko_sdk.gateways.general.v2 import client as client_v2
from iiko_sdk.gateways.orders.enums import PaymentTypeKind
from iiko_sdk.gateways.orders.v1.client import OrdersGateway, OrderItem, ORDER_CREATION_STATUSES, DeliveriesGateway, \
    Payment
from iiko_sdk.gateways.reserves.client import ReservesGateway
from iiko_sdk.gateways.transformers import SetAuthorization, MemoryCache
from tests import settings

api_login = settings.IIKO_DEFAULT_API_LOGIN
base_url = settings.IIKO_BASE_URL
service = services.HttpService(request_preproc=[SetAuthorization(api_login, base_url, cache=MemoryCache())])

# Data from IIKO
RESTAURANT_ID = uuid.UUID('26fb8044-d50f-4a25-875e-868f4087e96a')
TERMINAL_GROUP_ID = uuid.UUID('38a05083-ec33-86f4-0195-cdbd7d080066')
TABLE_ID = uuid.UUID('2f235614-1417-4bb3-bc58-ac60e20ee4b4')
PRODUCT_ID = uuid.UUID('b87b68fc-45fc-440b-86ba-5976f70fe288')


@pytest.mark.integration
async def test_get_token():
    """ Получить api_token """
    gateway = AuthorizationGateway(base_url)
    api_token = await gateway.get_api_token(api_login)
    assert api_token


@pytest.mark.integration
async def test_get_external_menus():
    """ Получить Ids внешних меню из Web """
    gateway = client_v2.GeneralGateway(base_url, service)
    response = await gateway.get_external_menus()
    assert 'externalMenus' in response
    assert 'correlationId' in response
    assert [i['id'] for i in response['externalMenus']]


@pytest.mark.integration
async def test_get_organizations():
    """ Получение списка ресторанов """
    gateway = client_v1.GeneralGateway(base_url, service)
    response = await gateway.get_organizations()
    assert 'organizations' in response
    assert 'correlationId' in response
    assert [i['id'] for i in response['organizations']]


@pytest.mark.integration
async def test_get_menu_by_id():
    """ Получение Web меню по id """
    gateway = client_v2.GeneralGateway(base_url, service)
    response = await gateway.get_menu_by_id(46794, [RESTAURANT_ID])
    assert 'itemCategories' in response
    assert 'correlationId' not in response
    assert [i['id'] for i in response['itemCategories']]


@pytest.mark.integration
async def test_get_order_types():
    """ Получение типов заказов ресторана """
    gateway = client_v1.GeneralGateway(base_url, service)
    response = await gateway.get_order_types([RESTAURANT_ID])
    assert 'orderTypes' in response
    assert 'correlationId' in response
    items = filter_list_by_parent_id(response, RESTAURANT_ID, list_key='orderTypes')
    assert items


@pytest.mark.integration
async def test_get_payment_types():
    """ Получение типов оплат """
    gateway = client_v1.GeneralGateway(base_url, service)
    response = await gateway.get_payment_types([RESTAURANT_ID])
    assert 'paymentTypes' in response
    assert 'correlationId' in response


@pytest.mark.integration
async def test_get_terminal_groups_and_sections():
    """ Получение список групп терминалов """
    gateway = client_v1.GeneralGateway(base_url, service)
    response = await gateway.get_terminal_groups([RESTAURANT_ID])
    assert 'terminalGroups' in response
    assert 'correlationId' in response
    items = filter_list_by_parent_id(response, RESTAURANT_ID, list_key='terminalGroups')
    assert items
    # Получение списка залов и столов ресторана
    terminal_group_ids = [item['id'] for item in items]
    gateway = ReservesGateway(base_url, service)
    response = await gateway.get_restaurant_sections(terminal_group_ids)
    assert 'correlationId' in response
    assert 'restaurantSections' in response

    items = filter_list_by_parent_id(response, terminal_group_ids[0], list_key='restaurantSections',
                                     id_key='terminalGroupId', items_key='tables')
    assert items


@pytest.mark.integration
@pytest.mark.parametrize('gateway_clazz', [OrdersGateway, DeliveriesGateway])
# @pytest.mark.parametrize('gateway_clazz', [DeliveriesGateway])
async def test_create_order(gateway_clazz):
    """ Создание заказа """
    external_number = 'USERID #1'
    gateway = client_v1.GeneralGateway(base_url, service)
    response = await gateway.get_payment_types([RESTAURANT_ID])
    payment_type_id = response['paymentTypes'][0]['id']

    total_sum = decimal.Decimal(1380)

    items = [OrderItem(amount=1, product_id=PRODUCT_ID)]
    gateway = gateway_clazz(base_url, service)
    pay = Payment(payment_type_id=payment_type_id, payment_type_kind=PaymentTypeKind.CASH, amount=decimal.Decimal(total_sum),
                  is_fiscalized_externally=True, is_processed_externally=True)
    if isinstance(gateway, OrdersGateway):
        response = await gateway.create_order(RESTAURANT_ID, TERMINAL_GROUP_ID, items, table_ids=[TABLE_ID],
                                              external_number=external_number, payments=[pay])
    else:
        response = await gateway.create_order(RESTAURANT_ID, '+79263848376', items, terminal_group_id=TERMINAL_GROUP_ID,
                                              external_number=external_number, payments=[pay])
    assert 'orderInfo' in response
    assert 'correlationId' in response
    order_info = response['orderInfo']
    order_id = uuid.UUID(order_info['id'])
    # Получение заказов по id
    await asyncio.sleep(2)
    response = await gateway.get_orders_by_ids(RESTAURANT_ID, order_ids=[order_id])
    assert 'orders' in response
    assert 'correlationId' in response

    order = filter_list_by_key(response['orders'], 'id', order_id)
    assert order
    # Enum: "Success" "InProgress" "Error"
    # Order creation status. In case of asynchronous creation, it allows to track the instance an order was validated/created in iikoFront.
    assert 'creationStatus' in order
    assert 'externalNumber' in order
    assert order['externalNumber'] == external_number
    assert order['creationStatus'] in ORDER_CREATION_STATUSES


# @pytest.mark.integration
# async def test_update_deliveries_status():
#     """ Обновление статуса доставки """
#     items = [OrderItem(amount=1, product_id=PRODUCT_ID)]
#     gateway = DeliveriesGateway(base_url, service)
#     response = await gateway.create_order(RESTAURANT_ID, '+77369283', items, terminal_group_id=TERMINAL_GROUP_ID)
#     assert 'orderInfo' in response
#     order_info = response['orderInfo']
#     order_id = uuid.UUID(order_info['id'])
#     await asyncio.sleep(5)
#     await gateway.update_status(RESTAURANT_ID, order_id, DeliveryStatus.ON_WAY)
#     response = await gateway.get_orders_by_ids(RESTAURANT_ID, order_ids=[order_id])
#     assert response


@pytest.mark.integration
async def test_get_orders_by_tables():
    """ Получение заказов по id столов """
    gateway = OrdersGateway(base_url, service)
    response = await gateway.get_orders_by_tables([RESTAURANT_ID], [TABLE_ID])
    assert 'orders' in response
    assert 'correlationId' in response
