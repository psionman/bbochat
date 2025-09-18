"""Main procedure for BBOChat."""

from bbochat import logger
from bbochat.root import Root

from psiutils.icecream_init import ic_init
ic_init()


def main():
    """Call the GUI loop."""
    logger.info('Application started')
    Root()


if __name__ == '__main__':
    main()
