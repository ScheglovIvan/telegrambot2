import telebot
from telebot import types
import requests
import json
import uuid
import os
import datetime
import shutil
import base64, codecs

from db import UserDB
from AccesRigths import AccesRigths
from python_bitrix24 import Bitrix24Connection

# bot = telebot.TeleBot("2143139509:AAFkBQusRowSMeN0BDElifUdRftArljum_U")
bot = telebot.TeleBot("5097809043:AAF20-jYn_Q155v8uQ9Tbp74HSL-hXRKGpE")

# path = "/home/altair_kyiv/telegrambot/altairtelebot/"
path = ""

def getBitrixData(request): # Запросы в Bitrix
    r = requests.get('https://altair.bitrix24.ua/rest/1/oqi0o4hegmmdh20f/%s'%(request))
    return r.json()["result"]

def SaveFile(b): # Сохранить файл для отправки в телеграм
    file_id = str(uuid.uuid4())
    f = open(path+'temporary_files/%s.png'%(file_id), 'wb')
    f.write(b)
    f.close()
    return file_id

def DeleteSavedFiles(arrID):
    for id in arrID:
        print("temporary_files/%s.png"%(id))
        # os.remove("temporary_files/%s.png"%(id))

############################ Функции не требующие Авторизации #######################################
def Login(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить телефон", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id, 'Вы не прошли авторизацию, для того чтобы авторизирываться отправьте ваш номер телефона...', reply_markup=keyboard)


def CreateUser(message):
    user = UserDB()
    bitrix_contant = getBitrixData("user.get.json?&select[]=UF_DEPARTMENT&filter[PERSONAL_MOBILE]=%s"%(message.contact.phone_number.replace("+", "")))

    if bitrix_contant:
        bitrix_id = bitrix_contant[0].get("ID")
        name = bitrix_contant[0].get("NAME")
        lastname = bitrix_contant[0].get("LAST_NAME")
        departmentId = bitrix_contant[0].get("UF_DEPARTMENT")[0]

        departmentData = getBitrixData("/department.get.json?ID=%s"%(departmentId))[0]
        departmentName = departmentData.get("NAME")

        if user.CreateUser(message.from_user.id, bitrix_id, departmentId, departmentName):
            bot.send_message(message.chat.id, 'ID пользователя: %s\nИмя: %s %s\nДепортамент: %s\n'%(bitrix_id, name, lastname, departmentName))
        else:
            bot.send_message(message.chat.id, "Произошла ошибка")

    else:
        bot.send_message(message.chat.id, 'Этот номер не зарегистрирован в СРМ')

def Auth(user_id): # Функция авторизации
    user = UserDB()
    data = user.identification(user_id)

    if data:
        return data
    else:
        return False



def changeDealStage(id):
    stages = getBitrixData("crm.dealcategory.stage.list.json?ID=9")
    for i in range(len(stages)):
        print(stages[i])


def GetTask(request):
    deals = getBitrixData('crm.deal.list.json?&%s&select[]=*&select[]=UF_*'%(request))

    data = []
    if deals:
        for deal in deals:
            try:
                maket_2d = deal["UF_CRM_1631010986406"][0]["showUrl"][1:]
                maket_3d_1 = deal["UF_CRM_1633274176243"]['showUrl'][1:]
                maket_3d_2 = deal["UF_CRM_1633274210788"]['showUrl'][1:]
                lekala = deal["UF_CRM_1633274245866"]['showUrl'][1:]
                backlight = deal["UF_CRM_1631011487404"]
            except:
                maket_2d = None
                maket_3d_1 = None
                maket_3d_2 = None
                lekala = None
                backlight = None

            d = {
                "dealID": deal["ID"],
                "ASSIGNED_BY_ID": deal["ASSIGNED_BY_ID"],
                "STAGE_ID": deal["STAGE_ID"],
                "title": deal['TITLE'],
                "size": deal["UF_CRM_1633275532889"],
                "closedate": deal['CLOSEDATE'].split("T")[0],
                "maket_2d": maket_2d,
                "maket_3d_1": maket_3d_1,
                "maket_3d_2": maket_3d_2,
                "lekala": lekala,
                "photo_for_client":  deal["UF_CRM_1638104801724"],
                "photo_ypakovki":  deal["UF_CRM_1638104867920"],
                "backlight": backlight
            }

            data.append(d)

        return data
    else:
        return None

def TakeTask(user_data, deal_id): # Взять задачу в работу
    
    if user_data:
        bitrix_user_id = user_data[0][2]

        data = GetTask("filter[CATEGORY_ID]=25&filter[ASSIGNED_BY_ID]=%s"%(bitrix_user_id))
        # print(data)
        if data == None:
            getBitrixData("/crm.deal.update.json?ID=%s&fields[ASSIGNED_BY_ID]=%s"%(deal_id, bitrix_user_id))
            return True
        else:
            return False


def GetStageName(STAGE_ID):
    stages = getBitrixData("crm.dealcategory.stage.list.json?ID=25")

    for stage in stages:
        if stage['STATUS_ID'] == STAGE_ID:
            stage_name = stage['NAME']
            return stage_name

def SendMedia(message, user_data):
    if user_data:
        data = GetTask('filter[ASSIGNED_BY_ID]=%s&filter[CATEGORY_ID]=25'%(user_data[0][2]))
        if data:
            task = data[0]
            if task["photo_for_client"] == []:
                print("Отправить фото для клиента")
                f = open("1598571191/file_5.jpg", "rb")
                data = f.read()
                f.close()
                print(base64.b64encode(data))

                # deal_id = task["dealID"]
                # getBitrixData("/crm.deal.update.json?ID=%s&fields[UF_CRM_1638104801724]=%s"%(deal_id, bitrix_user_id))


            elif task["photo_ypakovki"] == []:
                print("Отправить фото в упаковки")

def showTask(message, task, user_data):
    if task:
        b24 = Bitrix24Connection("altair.kyiv@gmail.com", "pipirka123", "https://altair.bitrix24.ua/")

        files = [b24.GetFile(task['maket_2d']), b24.GetFile(task['maket_3d_1']), b24.GetFile(task['maket_3d_2']), b24.GetFile(task['lekala'])]

        file_id = []
        for url in files:
            file_id.append(SaveFile(url))

        stage_name = GetStageName(task["STAGE_ID"])

        if task["backlight"] == "1":
            backlight = "Есть"
        else:
            backlight = "Нет"
        
        mesasge_text = "Задача: %s\nНазвание: %s\nРазмер: %sм\nПодсветка: %s"%(stage_name, task['title'], task['size'], backlight)

        if int(user_data[0][2]) == int(task["ASSIGNED_BY_ID"]):

            if stage_name == "Проверить и отфоткать":
                photo_for_client = task["photo_for_client"]
                if photo_for_client == []:
                    mesasge_text = "Задача: %s\nНазвание: %s\nРазмер: %sм"%(stage_name, task['title'], task['size'])
                    button_text = 'Загрузить фото и Видео'
                    callback_data = '{"name":"DownloadMedia"}'
                else:
                    mesasge_text = "Задача: %s\nНазвание: %s\nРазмер: %sм"%(stage_name, task['title'], task['size'])
                    button_text = 'Выполнено'
                    callback_data = '{"name":"completed", "deal_id":"%s", "user_id":"%s"}'%(task['dealID'], message.from_user.id)

            elif stage_name == "Упаковать":

                photo_for_client = task["photo_for_client"]
                photo_ypakovki = task["photo_ypakovki"]

                print(photo_for_client)
                print(photo_ypakovki)

                mesasge_text = "Задача: %s\nНазвание: %s\nРазмер: %sм"%(stage_name, task['title'], task['size'])
                button_text = 'Загрузить фото'
                callback_data = '{"name":"DownloadMedia"}'

            else:
                button_text = 'Выполнено'
                callback_data = '{"name":"completed", "deal_id":"%s", "user_id":"%s"}'%(task['dealID'], message.from_user.id)
        
        else:
            button_text = 'Взять задачу'
            callback_data = '{"name":"TakeTask", "deal_id":"%s", "user_id":"%s"}'%(task['dealID'], message.from_user.id)


        try:
            photo_arr = [telebot.types.InputMediaPhoto(open(path+"temporary_files/%s.png"%(id), 'rb')) for id in file_id]
            bot.send_media_group(message.chat.id, photo_arr)
        except:
            pass

        
        keyboard  = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data)
        keyboard.row(button)

        bot.send_message(message.chat.id, mesasge_text, reply_markup=keyboard)
        DeleteSavedFiles(file_id)
    else:
        bot.send_message(message.chat.id, "У вас пока нет задач")

def TasksInWork(message, user_data):
    stages = list(reversed(AccesRigths["departamentsId"][str(user_data[0][3])]["stages"]))

    task = None
    for stage in stages:
        deal = GetTask('filter[STAGE_ID]=%s&filter[ASSIGNED_BY_ID]=%s&filter[CATEGORY_ID]=25'%(stage, user_data[0][2]))
        if deal:
            task = deal[0]
            break

    showTask(message, task, user_data)



def GetNextTask(message, user_data): # Вывести следующую задачу
    stages = list(reversed(AccesRigths["departamentsId"][str(user_data[0][3])]["stages"]))

    task = None

    for stage in stages:
        deals = GetTask('filter[ASSIGNED_BY_ID]=1&filter[CATEGORY_ID]=25&filter[STAGE_ID]=%s'%(stage))
        if deals:
            deals = sorted(deals, key=lambda x: x['closedate'])

            task = deals[0]
            break

    showTask(message, task, user_data)

def TaskCompleted(message, user_data):
    if user_data:
        bitrix_user_id = user_data[0][2]
        data = GetTask("filter[CATEGORY_ID]=25&filter[ASSIGNED_BY_ID]=%s"%(bitrix_user_id))
        if data:
            STAGE_ID = data[0]["STAGE_ID"]
            stages = getBitrixData("crm.dealcategory.stage.list.json?ID=25")


            for i in range(len(stages)):
                if stages[i]['STATUS_ID'] == STAGE_ID:
                    next_stage = stages[i+1]
                    if next_stage["NAME"] == "Проблемы":
                        next_stage = stages[i+2]

                    next_stage_id = next_stage['STATUS_ID']
                    break

            stages = AccesRigths["departamentsId"][str(user_data[0][3])]["stages"]
            
            task = data[0]
            task_id = task["dealID"]

            # if next_stage["NAME"] == "Упаковать" and task["photo_for_client"] == []:
            #     print("Нет фото для клиента")
            # elif next_stage["NAME"] == "Ждет отправки" and task["photo_for_client"] == [] and task["photo_ypakovki"] == []:
            #     print("Нет фото для клиента")
            #     print("Нет фото Упаовки")
            # else:

            change_user = True
            for stage in stages:
                if stage == next_stage_id:
                    change_user = False
                    break
            
            if change_user:
                user_id = 1
            else:
                user_id = bitrix_user_id                
                

            getBitrixData("/crm.deal.update.json?ID=%s&fields[STAGE_ID]=%s&fields[ASSIGNED_BY_ID]=%s"%(task_id, next_stage_id, user_id))
            
            task = GetTask("filter[CATEGORY_ID]=25&filter[ASSIGNED_BY_ID]=%s"%(bitrix_user_id))
            if task: 
                showTask(message, task[0], user_data)


@bot.message_handler(commands=['start'])
def start(message):
    user_data = Auth(message.from_user.id)
    if user_data:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        item1 = types.KeyboardButton("Задача в работе")
        item2 = types.KeyboardButton("Следующая задача")

        markup.add(item1, item2)

        bot.send_message(message.chat.id, "Выбрать чат", reply_markup = markup)
    else:
        Login(message)

@bot.message_handler(commands=["number"])
def phone(message):
    Login(message)
    print(message.text)
 
@bot.message_handler(content_types=['contact']) # Авторизация после отправки контакта
def contact(message):
    if message.contact is not None:
        user_data = Auth(message.from_user.id)
        if user_data:
            bot.send_message(message.chat.id, "Вы авторизировались")
        else:
            CreateUser(message)
            

@bot.callback_query_handler(func=lambda call: True) # Отслеживание нажатий на кнопки
def callback_inline(call):
    user_data = Auth(call.from_user.id)

    if user_data:
        if call.message:
            data = json.loads(call.data)
            deal_id = data.get('deal_id')

            if data.get('name') == "TakeTask":    
                if TakeTask(user_data, deal_id):
                    bot.send_message(call.message.chat.id, "Вы взяли задачу в работу")
                else:
                    bot.send_message(call.message.chat.id, "Чтобы взять эту задачу в работу завершите преведущую...")
                    TasksInWork(call.message, user_data)
            elif data.get('name') == "completed":
                TaskCompleted(call.message, user_data)
            elif data.get('name') == "DownloadMedia":
                if os.path.exists("ready_orders/" + str(user_data[0][1])) == False:
                    bot.send_message(call.message.chat.id, "Отправьте фотографии и нажмите еще раз...")
                else:
                    photo_arr = [telebot.types.InputMediaPhoto(open("ready_orders/" + str(user_data[0][1]) + "/%s"%(id), 'rb')) for id in os.listdir("ready_orders/" + str(user_data[0][1]))]
                    bot.send_media_group(call.message.chat.id, photo_arr)
        
                    keyboard  = telebot.types.InlineKeyboardMarkup()
                    # button_yes = telebot.types.InlineKeyboardButton("Готово", callback_data='{"name": "SendMedia"}')

                    task = GetTask("filter[CATEGORY_ID]=25&filter[ASSIGNED_BY_ID]=%s"%(user_data[0][2]))[0]
                    # print(task)
                    button_yes = telebot.types.InlineKeyboardButton("Готово", callback_data='{"name":"completed", "deal_id":"%s", "user_id":"%s"}'%(task['dealID'], call.from_user.id))
                    
                    button_no = telebot.types.InlineKeyboardButton("Заменить", callback_data='{"name": "ChangeMedia"}')
                    keyboard.row(button_yes, button_no)

                    bot.send_message(call.message.chat.id, "Вы точно хотите добавить эти файлы", reply_markup=keyboard)
            elif data.get('name') == "ChangeMedia":
                if os.path.exists("ready_orders/" + str(user_data[0][1])):
                    shutil.rmtree("ready_orders/" + str(user_data[0][1]))

                bot.send_message(call.message.chat.id, "Отправьте фотографии и нажмите еще раз...")
            elif data.get('name') == "SendMedia":
                SendMedia(call.message, user_data)
    else:
        Login(call.message)


@bot.message_handler(content_types=["photo", "video"])
def photo(message):
    user_data = Auth(message.from_user.id)
    if user_data:
        deal = GetTask('filter[ASSIGNED_BY_ID]=%s&filter[CATEGORY_ID]=25'%(user_data[0][2]))
        if deal:
            if os.path.exists("ready_orders/" + str(user_data[0][1])) == False:
                os.mkdir("ready_orders/" + str(user_data[0][1])+"/")


            if message.content_type == "video":
                file_info = bot.get_file(message.video.file_id)
            elif message.content_type == "photo":
                file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)

            downloaded_file = bot.download_file(file_info.file_path)

            # src = "ready_orders/" + str(user_data[0][1]) + '/' + file_info.file_path.split('/')[-1]
            src = "ready_orders/" + str(user_data[0][1]) + '/' + file_info.file_path.split('/')[-1]
            f = open(src, 'wb')
            f.write(downloaded_file)
            f.close()
        else:
            bot.send_message(message.chat.id, "у вас нету задач")


@bot.message_handler(content_types=['text']) # Обработка текстовых команд
def main(message):    
    user_data = Auth(message.from_user.id)
    print(user_data)
    if user_data:
        if message.text == "Задача в работе":

            TasksInWork(message, user_data)

        elif message.text == "Следующая задача":

            bot.send_message(message.chat.id, "Подождите подбираеться следующая задача...")
            GetNextTask(message, user_data)

        else:

            bot.send_message(message.chat.id, "Не правильный запрос, такой команды не существует")
    else:
        Login(message)

        

bot.infinity_polling()
