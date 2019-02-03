# coding: utf-8
from resource import Resource, open_league_fetch, ResourcePlanner, Schedule
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import urllib3
import pandas as pd
import time
import threading

TOKEN = "774150692:AAGoyMjFOWUlt7MsGu5Rez-VmjVxJcVPF1M"
N_COMMANDS = 15

LOGS_FILE="logs.txt"


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
openLeagueResults = Resource("open_league_res.xls", open_league_fetch)


def logging(handler):
    def z(func):
        def f(*args, **kwargs):
            with open(LOGS_FILE, "a") as logs_file:
                logs_file.write("{}\t{}'n".format(time.time(), handler))
            return func(*args, **kwargs)
        return f
    return z


@logging("start")
def start(bot, update):
    options = ['Текущие результаты','Финальные результаты', 'Выбрать команду']
    keyboard = [[InlineKeyboardButton(name, callback_data=str(idx))] for idx, name in enumerate(options)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Привет! Я умею показывать результаты ЧГК. Выбери:', reply_markup=reply_markup)


@logging("help")
def help(bot, update):
    commands = {"/results": "Результаты по всем играм",
                "/final_results": "Результаты за вычетом 2 худших игр",
                "/choose_tema": "Выбрать свою команду"}
    update.message.reply_text("\n".join([k + " " + v for k, v in commands.iteritems()]))


def getCommands(sheetX):
    commands = list(map(str, sheetX['Команда']))
    maxN = 0
    while commands[maxN] != "nan":
        maxN += 1
    for i in range(maxN):
        if commands[i] == "Высокий пинг":
            commands[i] = "<b>Высокий пинг</b>"
            break
    return commands, maxN


def parse_matrix(sheetX):
    commands, maxN = getCommands(sheetX)
    points = list(map(str, sheetX[u'сум']))[:maxN]
    position = map(str, range(1, maxN + 1))
    matrix_res = "Матрица:\n" + u'\n'.join(list(map(lambda x: x[0] + ") " + x[1] + " - " + x[2], zip(position, commands[:maxN], points)))[:N_COMMANDS])
    return matrix_res


@logging("results")
def results(bot, update):
    xls = pd.ExcelFile(openLeagueResults.file)
    sheetX = xls.parse(0)
    commands, maxN = getCommands(sheetX)
    points = list(map(str, sheetX[u'сум']))[:maxN]
    position = list(map(str, range(1, maxN + 1)))
    chgk_res = "ЧГК:\n" + u'\n'.join(list(map(lambda x: x[0] + ") " + x[1] + " - " + x[2], zip(position, commands, points)))[:N_COMMANDS])

    matrix_res = parse_matrix(xls.parse(1))

    update.message.reply_html(chgk_res + u"\n\n" + matrix_res)


def cast_x(x):
	if x == u"nan":
		return "0"
	return x


@logging("final_results")
def final_results(bot, update):
    xls = pd.ExcelFile(openLeagueResults.file)
    sheetX = xls.parse(0)
    commands, maxN = getCommands(sheetX)

    points = [[] for i in range(maxN)]
    columns = sheetX.columns.values
    for column in columns[2:]:
   		points_col = map(str, sheetX[column])
   		points_col = list(map(float, map(cast_x, points_col)))
   		for j in range(maxN):
   			points[j].append(points_col[j])
    for i in range(maxN):
   		points[i].sort()
   		points[i] = points[i][2:]
   		points[i] = sum(points[i])
    command_points = list(zip(commands[:maxN], points))
    command_points.sort(key=lambda x: -x[1])
    command_points = list(map(lambda x: x[0] + " - " + str(x[1]), command_points))

    position = map(str, range(1, maxN + 1))
    chgk_res = u"ЧГК:\n" + u'\n'.join(list(map(lambda x: x[0] + ") " + x[1], zip(position, command_points)))[:N_COMMANDS])

    matrix_res = parse_matrix(xls.parse(1))

    update.message.reply_html(chgk_res + u"\n\n" + matrix_res)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    resourcePlanner = ResourcePlanner(openLeagueResults, Schedule(), 60*60*12)
    t1 = threading.Thread(target = resourcePlanner.run)
    t1.start()

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
