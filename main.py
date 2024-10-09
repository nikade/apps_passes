import datetime
import logging
import time

from AppsWebClient import AppsWebClient
from TgBot import TgBot
from exceptions import TgBotSendException, UnknownResponseException, LoginException

##
# Узнать chatid https://api.telegram.org/bot7230503141:AAGp0HCQ71WIFEE2GauP_fxS9LdOmL8dSa4/getUpdates
#  https://api.telegram.org/bot7230503141/getUpdates
# curl -X POST -H "Content-Type:multipart/form-data" -F chat_id=$CHAT_ID -F text="message" "https://api.telegram.org/bot$TOKEN/sendMessage"
# curl -X POST -H 'Content-Type:multipart/form-data' -F chat_id='-1002427618780'
# -F text='message' 'https://api.telegram.org/bot7230503141:AAGp0HCQ71WIFEE2GauP_fxS9LdOmL8dSa4/sendMessage'

#chat_id = -1002427618780
chat_id = 216992382
bot_token = '7230503141:AAGp0HCQ71WIFEE2GauP_fxS9LdOmL8dSa4'

logging.basicConfig(level=logging.INFO, filename="apps.log",
                    filemode="a", format="%(asctime)s %(levelname)s %(message)s")

tg_bot = TgBot(bot_token, chat_id)
client = AppsWebClient("+79132157888", "4067")

last_date = dict()
error_count = 0

logging.info("Старт")

while True:
    curr_date = datetime.datetime.now()
    try:
        for child in client.childs:
            passes = client.get_passing(child, curr_date, curr_date)
            last_visit = last_date.get(child) or None
            if last_visit is not None:
                not_sended = list(filter(lambda x: x.date > last_visit, passes))
            else:
                not_sended = passes
            not_sended.sort(key=lambda x: x.date)
            for e in not_sended:
                msg = f"{client.childs[child]} {'вошел в школу' if e.direction else 'вышел из школы'} в {e.date.strftime('%d.%m.%Y %H:%M:%S')}"
                logging.info(msg)
                tg_bot.send_message(msg)
            if len(not_sended) > 0:
                last_date[child] = not_sended[-1].date
        error_count = 0
        time.sleep(120)
    except LoginException as e:
        error_count += 1
        msg = f"Проблема с логином, засыпаю на {error_count} часов \"{str(e)}\""
        logging.error(msg)
        tg_bot.send_message(msg)
        time.sleep(3600 * error_count)
    except UnknownResponseException as e:
        error_count += 1
        msg = f"Сломались запросы АППС, засыпаю на {error_count} часов \"{str(e)}\""
        logging.error(msg)
        tg_bot.send_message(msg)
        time.sleep(3600 * error_count)
    except TgBotSendException as e:
        logging.error(str(e))
    except Exception as e:
        logging.error(str(e))
        error_count += 1
        msg = f"Неизвестная ошибка, засыпаю на {error_count} часов \"{str(e)}\""
        time.sleep(3600 * error_count)
