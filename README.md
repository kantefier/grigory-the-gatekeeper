# Grigory the Gatekeeper

Is a Telegram bot which purpose is to monitor Waves Exchange's Gateways.

It's first implementation is written in Python 3 and can be found at `py-implementation/`.

## How does it work?
The bot is polling Waves Exchange's Gateway API and parses the answer, which contains current gateway status.

Currently the bot supports USDT token and polls for ETH and BSC networks.

The bot is using a [public telegram channel](https://t.me/wex_usdt_status) to write status changes.