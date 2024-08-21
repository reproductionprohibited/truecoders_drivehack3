import logging
from typing import (
    Dict,
    List,
    Tuple
)

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    filters
)

from settings import get_config, setup_logger

info_logger = setup_logger(name='info_logger', log_filename='info.log', level=logging.INFO)
error_logger = setup_logger(name='error_logger', log_filename='error.log', level=logging.ERROR)
config = get_config()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f'Привет, @{user.username}',
        parse_mode=ParseMode.MARKDOWN
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Help placeholder message...')


def main() -> None:
    app = ApplicationBuilder().token(config['TOKEN']).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))

    info_logger.info('Starting bot...')
    app.run_polling()


if __name__ == '__main__':
    main()
