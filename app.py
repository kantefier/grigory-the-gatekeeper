import requests
import time
import logging
import telegram
import os
import sys

tg_channel_link = "@wex_usdt_status"
withdraw_status_url_template = "https://api.waves.exchange/v1/withdraw/currencies/{token}/{network}"

delay_seconds = int(os.environ.get('BOT_DELAY_SECONDS', 60))
bot_token = os.environ.get('BOT_TOKEN')
logging_level = os.environ.get('LOG_LEVEL', 'INFO')

initial_status = 'initial'


class GatewayPosition:
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
    GatewayPosition('USDT', 'BSC'),
    GatewayPosition('USDT', 'ETH')
]


if __name__ == '__main__':
    logging.basicConfig(level=logging.getLevelName(logging_level),
                        format='%(asctime)s %(levelname)s [%(module)s] %(message)s')

    logger = logging.getLogger('GrigoryBot')

    logging.info("Starting Grigory...")

    if bot_token is None:
        logger.fatal('BOT_TOKEN env variable is not set, terminating...')
        sys.exit(1)

    bot = telegram.Bot(bot_token)

    while True:
        for p in positions:
            token = p.token
            network = p.network
            last_status = p.last_status
            try:
                logger.debug("Going to send a request to Waves Exchange")

                request_url = withdraw_status_url_template.format(token=token, network=network)
                gateway_response = requests.get(request_url).json()

                logger.debug("Got a response from Waves Exchange")
                current_status = gateway_response['status']

                logger.debug("Found 'status' field")
                if current_status != last_status:
                    if last_status == initial_status:
                        logger.debug("First run, just updating the status")
                        p.update_status(current_status)
                        continue

                    logger.info("Status has changed! Old status: '{}', new status: '{}'"
                                .format(last_status, current_status))

                    # status has changed, signal to telegram channel
                    message = """
                    {} gateway (Waves -> {}) status changed to: {}
                    """.format(token, network, current_status)
                    status = bot.send_message(chat_id=tg_channel_link, text=message)

                    # change last saved status
                    logger.debug("Updating status for {}".format(p))
                    p.update_status(current_status)
                    logger.debug("Status updated: {}".format(p))
                else:
                    logger.debug("Status didn't change, old status: '{}'".format(last_status))
            except Exception as err:
                logger.error('Encountered an error: {0}'.format(err))
                pass

        # sleep after each try
        time.sleep(delay_seconds)

