from scripts.helpers import get_account, get_contract, toWei, fund_with_link, _from
from brownie import Lottery, config, network
import time


def _lottery():
    return Lottery[-1]


def deploy_lottery():
    active_network = network.show_active()
    print(f"Running on [{active_network}] network")
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][active_network]["fee"] * toWei,
        config["networks"][active_network]["keyhash"],
        _from(),
        publish_source=config["networks"][active_network].get("verify", False),
    )
    print("Deployed Lottery!")
    return lottery


def start_lottery():
    starting_tx = _lottery().startLottery(_from())
    starting_tx.wait(1)
    print("The lottery has started!")


def enter_lottery():
    value = _lottery().getEntranceFee() + 1000
    tx = _lottery().enter(_from(value))
    tx.wait(1)
    print("You entered the lottery")


def end_lottery():
    # fund the contract, then end the lottery
    tx = fund_with_link(_lottery().address)
    tx.wait(1)
    ending_transaction = _lottery().endLottery(_from())
    ending_transaction.wait(1)
    time.sleep(60)
    print(f"{_lottery().recentWinner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
