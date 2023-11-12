from bot import bot
from time import sleep

print("Bot is ready!")

while True:
    try:
        bot.polling(none_stop=True)
    except Exception:
        pass
