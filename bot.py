# coding: utf-8
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import urllib3
import pandas as pd
from bs4 import BeautifulSoup
import time

TOKEN = "774150692:AAGoyMjFOWUlt7MsGu5Rez-VmjVxJcVPF1M"
URL = "http://old1.club60sec.ru/calendar/6662/"
FILE = "chgk_res.xls"
args = {"LAST_UPDATE_TIME" : 0}
update_interval = 5 * 60
N_COMMANDS = 15
LOGS_FILE="logs.txt"
options = ['Текущие результаты','Финальные результаты']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def track_metrica(handler):
    def z(func):
        def f(*args, **kwargs):
            with open(LOGS_FILE, "a") as ggg:
                ggg.write(str(time.time()) + " " + handler + "\n")
            return func(*args, **kwargs)
        return f
    return z

def get_doc():
    #cache results
    if time.time() - args["LAST_UPDATE_TIME"] < update_interval:
        print("Cached")
        return

    http = urllib3.PoolManager()
    response = http.request('GET', URL)
    soup = BeautifulSoup(response.read())

    dropbox_href = None
    for link in soup.findAll('a'):
        link_text = link.get('href')
        if "dropbox" in link_text:
            dropbox_href = link_text
            break

    dropbox_href = "=".join(dropbox_href.split("=")[:-1] + ["1"])

    response = http.request('GET', dropbox_href)
    with open(FILE, "w") as f:
        args["LAST_UPDATE_TIME"] = time.time()
        f.write(response.read())

@track_metrica("start")
def start(bot, update):
    keyboard = [[InlineKeyboardButton(name, callback_data=str(idx))] for idx, name in enumerate(options)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Привет! Я умею показывать результаты ЧГК. Выбери:', reply_markup=reply_markup)

@track_metrica("help")
def help(bot, update):
    commands = {"/results": "результаты по всем играм",
                "/final_results": "результаты за вычетом 2 худших игр"}
    update.message.reply_text("\n".join([k + " " + v for k, v in commands.iteritems()]))

@track_metrica("button")
def button(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="Выбрано: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

    if query == '0':
        results(bot, update)
    if query == '1':
        final_results(bot, update)

def getCommands(sheetX):
    commands = map(unicode, sheetX[u'Команда'])
    maxN = 0
    while commands[maxN] != "nan":
        maxN += 1
    for i in xrange(maxN):
        if commands[i] == u"Высокий пинг":
            commands[i] = u"<b>Высокий пинг</b>"
            break
    return commands, maxN


def parse_matrix(sheetX):
    commands, maxN = getCommands(sheetX)
    points = map(unicode, sheetX[u'сум'])[:maxN]
    position = map(unicode, range(1, maxN + 1))
    matrix_res = u"Матрица:\n" + u'\n'.join(map(lambda x: x[0] + ") " + x[1] + " - " + x[2], zip(position, commands[:maxN], points))[:N_COMMANDS])
    return matrix_res

@track_metrica("results")
def results(bot, update):
    get_doc()
    xls = pd.ExcelFile(FILE)
    sheetX = xls.parse(0)
    commands, maxN = getCommands(sheetX)
    points = map(unicode, sheetX[u'сум'])[:maxN]
    position = map(unicode, range(1, maxN + 1))
    chgk_res = u"ЧГК:\n" + u'\n'.join(map(lambda x: x[0] + ") " + x[1] + " - " + x[2], zip(position, commands, points))[:N_COMMANDS])

    matrix_res = parse_matrix(xls.parse(1))

    update.message.reply_html(chgk_res + u"\n\n" + matrix_res)


def cast_x(x):
	if x == u"nan":
		return "0"
	return x

@track_metrica("final_results")
def final_results(bot, update):
    get_doc()
    xls = pd.ExcelFile(FILE)
    sheetX = xls.parse(0)
    commands, maxN = getCommands(sheetX)

    points = [[] for i in xrange(maxN)]
    columns = sheetX.columns.values
    for column in columns[2:]:
   		points_col = map(unicode, sheetX[column])
   		points_col = map(float, map(cast_x, points_col))
   		for j in xrange(maxN):
   			points[j].append(points_col[j])
    for i in xrange(maxN):
   		points[i].sort()
   		points[i] = points[i][2:]
   		points[i] = sum(points[i])
    command_points = zip(commands[:maxN], points)
    command_points.sort(key=lambda x: -x[1])
    command_points = map(lambda x: x[0] + " - " + unicode(x[1]), command_points)

    position = map(unicode, range(1, maxN + 1))
    chgk_res = u"ЧГК:\n" + u'\n'.join(map(lambda x: x[0] + ") " + x[1], zip(position, command_points))[:N_COMMANDS])

    matrix_res = parse_matrix(xls.parse(1))

    update.message.reply_html(chgk_res + u"\n\n" + matrix_res)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("results", results))
    dp.add_handler(CommandHandler("final_results", final_results))
    dp.add_handler(MessageHandler(Filters.text, start))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
