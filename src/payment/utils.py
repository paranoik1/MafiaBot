from random import choices
from string import ascii_letters

from aioyoomoney import Quickpay, HistoryMethod, OperationStatus

from src.store.config import YoomoneyConfig


def get_label(id: int, code: str) -> str:
    return str(id) + code


def generate_label(id: int) -> str:
    code = "".join(choices(ascii_letters, k=15))
    label = get_label(id, code)

    return label


async def get_link_pay(label: str, price: int):
    async with Quickpay(
        receiver=YoomoneyConfig.RECEIVER,
        sum=price,
        label=label
    ) as quickpay:
        return quickpay.url


async def check_pay(label: str) -> bool:
    async with HistoryMethod(
        token=YoomoneyConfig.TOKEN,
        label=label,
        details=False
    ) as history:
        if not history.operations:
            return False

        operation = history.operations[0]

    return operation.status == OperationStatus.SUCCESS
