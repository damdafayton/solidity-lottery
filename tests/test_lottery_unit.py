# get 0.019 eth

from tracemalloc import start
from brownie import network, exceptions
from scripts.helpers import (
    fund_with_link,
    toWei,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    _from,
    get_account,
    get_contract,
)
from scripts.deploy import deploy_lottery
import pytest
from dotenv import load_dotenv

load_dotenv()


def skip_if_not_local():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()


def test_get_entrance_fee():
    skip_if_not_local()
    lottery = deploy_lottery()
    entrance_fee = lottery.getEntranceFee()
    # eth/usd = 2000
    # entrance fee = 50usd == 0.025eth
    expected_entrance_fee = 50 * toWei / 2000

    assert entrance_fee == expected_entrance_fee


def test_cant_enter_unless_lottery_started():
    skip_if_not_local()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter(_from(lottery.getEntranceFee()))


def start_lottery():
    skip_if_not_local()
    lottery = deploy_lottery()
    lottery.startLottery(_from())
    return lottery


def test_can_start_and_enter_lottery():
    lottery = start_lottery()
    # Act
    lottery.enter(_from(lottery.getEntranceFee()))
    # Assert
    assert lottery.players(0) == get_account()


def test_can_end_lottery():
    lottery = start_lottery()
    lottery.enter(_from(lottery.getEntranceFee()))
    fund_with_link(lottery)
    lottery.endLottery(_from())
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    lottery = start_lottery()
    fee = lottery.getEntranceFee()
    lottery.enter(_from(fee))
    lottery.enter(_from(fee, 1))
    lottery.enter(_from(fee, 2))
    fund_with_link(lottery)

    account = get_account()
    starting_balance = account.balance()
    balance_of_lottery = lottery.balance()

    transaction = lottery.endLottery(_from())
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, _from()
    )

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance + balance_of_lottery
