from brownie import (
    accounts,
    network,
    config,
    Contract,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
)


toWei = 10 ** 18
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development",
    "ganache-local",
    "ganache-app-hellish",
    "ganache-hellish",
]


def _from(value=None, index=None):
    account = get_account(index)
    return {"from": account, "value": value}


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        print(f"Running in development with account {accounts[0]}")
        return accounts[0]
    return accounts.add(config["wallets"]["test_net_key"])  # Testnet address


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """This function will grab the contract address from the brownie config if defined,
    otherwise it will deploy a mock version of that contract, and return that contract
        Args:
            contract_name (string)
        Return:
            brownie.network.contract.ProjectContract: The most recently deployed version."""
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


DECIMALS = 8
INITIAL_VALUE = 2000 * 10 ** 8


def deploy_mocks():
    _from = {"from": get_account()}
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks..")
    MockV3Aggregator.deploy(DECIMALS, INITIAL_VALUE, _from)
    link_token = LinkToken.deploy(_from)
    VRFCoordinatorMock.deploy(link_token.address, _from)
    print("Mocks deployed!")


def fund_with_link(contract_address, account=None, link_token=None, amount=10 ** 18):
    account = account or get_account()
    link_token = link_token or get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funded contract with LINK")
    return tx
