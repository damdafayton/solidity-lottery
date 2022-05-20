from scripts.helpers import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    _from,
    fund_with_link,
    get_account,
)
from brownie import network
import pytest
from scripts.deploy import deploy_lottery
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
    lottery = deploy_lottery()
    lottery.startLottery(_from())
    lottery.enter(_from(lottery.getEntranceFee()))
    lottery.enter(_from(lottery.getEntranceFee()))
    fund_with_link(lottery)
    lottery.endLottery(_from())
    time.sleep(60)
    assert lottery.recentWinner() == get_account()
    assert lottery.balance() == 0