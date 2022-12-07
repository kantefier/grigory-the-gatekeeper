import aiohttp
import logging
import telegram
from telegram.parsemode import ParseMode
import os
import sys
import asyncio

tg_channel_link = os.environ.get('TG_CHANNEL_LINK', "@wex_usdt_status")
withdraw_status_url_template = "https://api.waves.exchange/v1/withdraw/currencies/{token}/{network}"
message_template = """
{emoji} *{network}* {token} gateway status changed to: _{status}_
"""

delay_seconds = int(os.environ.get('BOT_DELAY_SECONDS', 60))
bot_token = os.environ.get('BOT_TOKEN')
logging_level = os.environ.get('LOG_LEVEL', 'INFO')

initial_status = 'initial'


class GatewayPositionWithState:
    def __init__(self, token, network):
        self.token = token
        self.network = network
        self.last_status = initial_status

    def __str__(self):
        return "GatewayPosition(token={}, network={}, last_status={})"\
            .format(self.token, self.network, self.last_status)

    def update_status(self, new_status):
        self.last_status = new_status


positions = [
    GatewayPositionWithState('USDT', 'BSC'),
    GatewayPositionWithState('USDT', 'ETH'),
    GatewayPositionWithState('USDT', 'POLYGON')
]

status_to_emoji = {
    'inactive': '⛔️',
    'insufficient_funds': '🚫',
    'active': '✅'
}


async def watch_position(session, p):
    token = p.token
    network = p.network
    last_status = p.last_status
    try:
        logger.debug("Going to send a request to Waves Exchange")

        request_url = withdraw_status_url_template.format(token=token, network=network)
        async with session.get(request_url) as gateway_response_raw:
            match gateway_response_raw.status:
                case 200:
                    gateway_response = await gateway_response_raw.json()

                    logger.debug("Got a response from Waves Exchange")
                    current_status = gateway_response['status']

                    logger.debug("Found 'status' field")
                    if current_status != last_status:
                        if last_status == initial_status:
                            logger.debug("First run, just updating the status")
                            p.update_status(current_status)
                            return

                        logger.info("Status has changed! Old status: '{}', new status: '{}'"
                                    .format(last_status, current_status))

                        status_emoji = status_to_emoji.get(current_status, '❓')

                        # status has changed, signal to telegram channel
                        message = message_template.format(
                            emoji=status_emoji, network=network, token=token, status=current_status.replace('_', ' '))

                        status = bot.send_message(chat_id=tg_channel_link, text=message, parse_mode=ParseMode.MARKDOWN)

                        # change last saved status
                        logger.debug("Updating status for {}".format(p))
                        p.update_status(current_status)
                        logger.debug("Status updated: {}".format(p))
                    else:
                        logger.debug("Status didn't change, old status: '{}'".format(last_status))

                case other_code:
                    logger.error("Gateway responded with {}: {}".format(other_code, gateway_response_raw))
                    # TODO: write me a private message about the problem

    except Exception as err:
        logger.error('Encountered an error: {}'.format(err))
        pass


async def crawl_gates():
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = []
            for p in positions:
                task = asyncio.create_task(watch_position(session, p))
                tasks.append(task)

            await asyncio.gather(*tasks)

            # sleep after each try
            await asyncio.sleep(delay_seconds)


# Entry point
if __name__ == '__main__':
    logging.basicConfig(level=logging.getLevelName(logging_level),
                        format='%(asctime)s %(levelname)s [%(module)s] %(message)s')

    logger = logging.getLogger('GrigoryBot')

    logging.info("Starting Grigory...")

    if bot_token is None:
        logger.fatal('BOT_TOKEN env variable is not set, terminating...')
        sys.exit(1)

    bot = telegram.Bot(bot_token)

    asyncio.run(crawl_gates())

