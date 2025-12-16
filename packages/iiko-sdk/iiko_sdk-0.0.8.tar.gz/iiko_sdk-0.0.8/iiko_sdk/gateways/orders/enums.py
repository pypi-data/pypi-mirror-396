import enum


class PaymentTypeKind(str, enum.Enum):
    """ Тип оплаты """
    CASH = 'Cash'
    CARD = 'Card'
    LOYALTY_CARD = 'LoyaltyCard'
    EXTERNAL = 'External'


class DeliveryStatus(str, enum.Enum):
    """ Статус доставки """
    WAITING = 'Waiting'
    ON_WAY = 'OnWay'
    DELIVERED = 'Delivered'


class DeliveryType(str, enum.Enum):
    """ Тип доставки """
    DELIVERY_BY_COURIER = 'DeliveryByCourier'
    DELIVERY_BY_CLIENT = 'DeliveryByClient'
