from requests.packages.urllib3 import disable_warnings

from myLogger import logger
from models import *
import siteEvents


def main():
    logger.info('Fetching Summaries...')
    siteEvents.fetch_summaries()

    logger.info('Fetching Details...')
    siteEvents.fetch_details_all()


if __name__ == '__main__':
    disable_warnings()
    setup_all()
    create_all()
    main()