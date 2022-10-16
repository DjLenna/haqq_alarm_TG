import requests
import json
from sys import exit

LOCAL_RPC = "tcp://localhost:26657"
TRUSTED_API = "https://haqq.api.t.stavr.tech"
VALOPER = ""
ADDRESS = ""
HEX_ADDRESS = ""
CRITICAL_BLOCKS_GAP = 20
CRITICAL_PEERS_COUNT = 10
UPTIME_WINDOW = 500
TELEGRAM_TOKEN = ""
TELEGRAM_CHAT_ID = ""


def request_handler(host: str, api: str):
    try:
        response = requests.get(f"{host}/{api}").text
        return response if response is not None else exit(f"[ERROR] API request failed: {api}")
    except Exception:
        exit(f"[ERROR] API request failed: {api}")


def telegram_alert(msg: str):
    try:
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            tgMSG = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}" \
                    f"/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg}"
            requests.post(f"{tgMSG}")
    except Exception as err:
        exit(f"[ERROR] Telegram connection failed: {err}")


def main():
    TG_message = ""

    try:
        # 1 NODE STATUS

        local_block = json.loads(
            request_handler(host=LOCAL_RPC, api="status")
        )["result"]["sync_info"]["latest_block_height"]
        local_block = int(local_block)

        trusted_block = json.loads(
            request_handler(host=TRUSTED_API, api="blocks/latest")
        )["block"]["header"]["height"]
        trusted_block = int(trusted_block)

        TG_message = f"Height: {local_block}/{trusted_block}\n"
        if (trusted_block - local_block) > CRITICAL_BLOCKS_GAP:
            TG_message += "[WARN] The node has lagged behind the main network!!\n"

        # 2 UPTIME

        signed_blocks = 0

        for i in range(trusted_block - UPTIME_WINDOW, trusted_block):
            signatures = json.loads(
                request_handler(host=TRUSTED_API, api=f"blocks/{i}")
            )["block"]["last_commit"]["signatures"]

            addresses = [s["validator_address"] for s in signatures]

            if HEX_ADDRESS in addresses:
                signed_blocks += 1

        uptime = (signed_blocks * 100) / UPTIME_WINDOW

        TG_message += f"Uptime: {uptime:.2f}% ({signed_blocks}/{UPTIME_WINDOW} blocks signed)\n"

        # 3 PEERS COUNT

        peers_count = json.loads(
            request_handler(host=LOCAL_RPC, api="net_info")
        )["result"]["n_peers"]
        peers_count = int(peers_count)

        TG_message += f"Peers count: {peers_count}\n"
        if peers_count < CRITICAL_PEERS_COUNT:
            TG_message += f"[WARN] Critical number of peers!!\n"

        # 4 VALIDATOR STATUS

        validator = json.loads(
            request_handler(host=TRUSTED_API, api=f"/cosmos/staking/v1beta1/validators/{VALOPER}")
        )

        jailed_status = validator['validator']['jailed']
        if jailed_status:
            TG_message += "[WARN] Your validator in jail!!!\n"
        else:
            TG_message += f"Jailed: false\n"

        bond_status = validator['validator']['status']
        TG_message += f"Bond status: {bond_status}\n"
        if "BOND_STATUS_BONDED" not in bond_status:
            TG_message += "[WARN] You are not in active set now!!!\n"

        # 5 PROPOSALS

        active_proposals = json.loads(
            request_handler(host=TRUSTED_API, api="gov/proposals?status=voting_period")
        )

        voted_proposals = json.loads(
            request_handler(host=TRUSTED_API, api=f"/gov/proposals?status=voting_period&voter={ADDRESS}")
        )

        if len(active_proposals) > len(voted_proposals):
            TG_message += "[WARN] There are active proposals now. Don't forget to vote!\n"
        else:
            TG_message += "There are no active proposals now.\n"

        telegram_alert(TG_message)

    except Exception as err:
        exit(f"[ERROR]: Someting went wrong: {err}")


if __name__ == "__main__":
    print("Start.....")
    main()
    print("End!")
