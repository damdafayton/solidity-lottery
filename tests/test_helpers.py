from brownie import network
from scripts.helpers import get_account


def test_get_account():
    account = get_account()
    if network.show_active() == "rinkeby":
        result = "0x1eda434e8f97f7214641d550A4e9918eBA2E5e6a"
    assert account == result
