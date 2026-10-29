"""Met à jour la section <!--CHAIN:START--> ... <!--CHAIN:END--> du README
avec le dernier bloc Ethereum, le gas et le prix de l'ETH."""

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

RPC = "https://ethereum-rpc.publicnode.com"
PRICE_URL = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd,eur"
HEADERS = {"Content-Type": "application/json", "User-Agent": "profile-readme-bot"}


def rpc(method: str) -> str:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": []}).encode()
    req = urllib.request.Request(RPC, data=payload, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["result"]


def main() -> int:
    try:
        block = int(rpc("eth_blockNumber"), 16)
        gas_gwei = int(rpc("eth_gasPrice"), 16) / 1e9
        req = urllib.request.Request(PRICE_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            price = json.load(r)["ethereum"]
    except Exception as exc:  # on ne casse pas le workflow si une API est KO
        print(f"Scan failed, README unchanged: {exc}")
        return 0

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    section = (
        "<!--CHAIN:START-->\n"
        "| ⛓️ Block | ⛽ Gas | 💎 ETH |\n"
        "|:-:|:-:|:-:|\n"
        f"| `#{block}` | `{gas_gwei:.2f} gwei` | `${price['usd']:,.0f}` · `{price['eur']:,.0f}€` |\n\n"
        f"<sub>⏱️ Dernier scan : {now}</sub>\n"
        "<!--CHAIN:END-->"
    )

    with open("README.md", encoding="utf-8") as f:
        content = f.read()

    new_content, n = re.subn(
        r"<!--CHAIN:START-->.*?<!--CHAIN:END-->", section, content, flags=re.DOTALL
    )
    if n == 0:
        print("Markers not found in README.md")
        return 1

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated: block {block}, gas {gas_gwei:.2f} gwei, ETH ${price['usd']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
