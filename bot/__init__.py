from telebot import TeleBot, types
from .dataClasses import Question, Form
from uuid import uuid4, UUID
from random import shuffle

bot = TeleBot(open("./bot/token", "r", encoding="utf-8").read())

tests = {}
"""
{
    id: list(Form, ...)
}
"""
option = {}
"""
{
    UUID: {
        type: Learning | Testing
        time_limit: int
    }
}
"""
question = {}


@bot.message_handler(commands=["start"])
def start(mess: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Создать тест", callback_data="CreateTest"), types.InlineKeyboardButton("Пройти тесты", callback_data="CompleteTest"))
    bot.send_photo(mess.chat.id, open("./bot/pic/start.png", "rb"), reply_markup=markup)


def selectType(mess: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Учебный режим", callback_data="LearningType"), types.InlineKeyboardButton("Тестовый режим", callback_data="TestingType"))
    bot.send_photo(mess.message.chat.id, open("./bot/pic/start.png", "rb"), reply_markup=markup)


def timeLimit(mess: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Ограничить время", callback_data="LimitTime"), types.InlineKeyboardButton("Неограниченное время", callback_data="WithoutLimit"))
    bot.send_photo(mess.message.chat.id, open("./bot/pic/start.png", "rb"), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callbackInline(call: types.CallbackQuery):
    if call.data == 'CreateTest':
        selectType(mess=call)
    elif call.data == 'CompleteTest':
        askId(call.message)
    elif call.data == 'LearningType':
        option[call.message.chat.id] = {"type": None, "limit_time": None}
        option[call.message.chat.id]["type"] = "Learning"
        timeLimit(call)
    elif call.data == 'TestingType':
        option[call.message.chat.id] = {"type": None, "limit_time": None}
        option[call.message.chat.id]["type"] = "Testing"
        timeLimit(call)
    elif call.data == 'WithoutLimit':
        option[call.message.chat.id]["time_limit"] = None
        zeroStep(chat_id=call.message.chat.id)
    elif call.data == 'LimitTime':
        limitTime(call.message)


def limitTime(mess: types.Message):
    s = bot.send_message(mess.chat.id, "Введите время в минутах")
    bot.register_next_step_handler(s, setLimit)


def setLimit(mess: types.Message):
    option[mess.chat.id]["time_limit"] = int(mess.text)
    zeroStep(chat_id=mess.chat.id)


def zeroStep(chat_id: int):
    s = bot.send_message(chat_id, "Введите вопрос")
    bot.register_next_step_handler(s, nextStep)


def nextStep(mess: types.Message):
    s = bot.send_message(mess.chat.id, "Введите правильный ответ")
    bot.register_next_step_handler(s, nextStepTwo, name_of_qu=mess.text)


def nextStepTwo(mess: types.Message, name_of_qu: str=""):
    add_other_ans(name_of_qu=name_of_qu, corr_ans=mess.text, mess=mess)


def add_other_ans(mess: types.Message, corr_ans: str, name_of_qu: str, list_of_an: list=()):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Следующий вопрос"), types.KeyboardButton("Закончить тест"))
    if "Следующий вопрос" in mess.text:
        nextQuest(mess, corr_ans, name_of_qu, list_of_an)
        return
    elif "Закончить тест" in mess.text:
        endTest(mess, corr_ans, name_of_qu, list_of_an)
        return
    if isinstance(list_of_an, tuple):
        list_of_an = []
    list_of_an.append(mess.text)
    n = bot.send_message(mess.chat.id, "Добавьте вариант ответа", reply_markup=markup)
    bot.register_next_step_handler(n, add_other_ans, name_of_qu=name_of_qu, corr_ans=mess.text, list_of_an=list_of_an)

def nextQuest(mess: types.Message, corr_ans, name_of_qu, list_of_an):
    list_of_an.append(corr_ans)
    q = Question(name=name_of_qu, corr_ans=corr_ans, other_ans=list_of_an)
    user = mess.from_user.id
    if user not in question.keys():
        question[user] = [q]
    else:
        question[user].append(q)
    zeroStep(mess.chat.id)

def endTest(mess: types.Message, corr_ans: str, name_of_qu: str, list_of_an: list):
    user = mess.from_user.id
    id = uuid4()
    list_of_an.append(corr_ans)
    q = Question(name=name_of_qu, corr_ans=corr_ans, other_ans=list_of_an)
    if user not in question.keys():
        question[user] = [q]
    else:
        question[user].append(q)
    if user not in tests:
        tests[user] = [Form(id=id, question=question[user], type=option[mess.from_user.id]["type"], time_limit=option[mess.from_user.id]["limit_time"])]
    else:
        tests[user].append(Form(id=id, question=question[user], time_limit=option[mess.from_user.id]["limit_time"]))
    question.pop(user)
    print(tests)
    bot.send_message(mess.chat.id, f"Ура! Вы создали тест. Ваш код для теста:\n <code>{id}</code>", reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML")

def askId(mess: types.Message):
    s = bot.send_message(mess.chat.id, "Введите уникальный код для получения доступа к тесту")
    bot.register_next_step_handler(s, findId)

def findId(mess: types.Message):
    test = None
    for t in tests.values():
        for form in t:
            if form.id == UUID(mess.text):
                test = tuple(tests[key][tests[key].index(form)] for key in tests if tests[key] == form)
    viewTest(mess, test)

def viewTest(mess: types.Message, form: Form, question_id: int=0):
    if question_id != 0 and mess.text == form.question[question_id - 1]:
        pass
    question_ = form.question[question_id]
    s = bot.send_message(mess.chat.id, f"Вопрос {question_.name}")
    shuffle(question_.other_ans)
    for ans in question_.other_ans:
        bot.send_message(mess.chat.id, ans)
    bot.register_next_step_handler(s, viewTest, form=form, question_id = question_id + 1)