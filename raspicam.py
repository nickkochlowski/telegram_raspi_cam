import os
import telebot
import psutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from gpiozero import CPUTemperature


TELEGRAM_TOKEN = '<insert telebot bot token>'

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

my_chat_id = "insert admin chat id"

motion_detection = False

filepath = "/home/pi/motionvideos/"
done_filepath = "/home/pi/motionvideos/done/"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if(message.chat.id == 989913486):
        bot.send_message(message.chat.id, "Home Menu", reply_markup=gen_markup())


@bot.message_handler(func=lambda message: True)
def message_handler(message):
    global motion_detection

    if(message.chat.id == my_chat_id):
        if(message.text=="Motion Detection"):
            bot.send_message(message.chat.id, "Motion Detection is " + str(motion_detection), reply_markup=gen_markup_motion())

        elif(message.text=="Raspberry Pi W Zero"):
            bot.send_message(message.chat.id, "Raspberry Pi Info", reply_markup=gen_markup_rpi())

        elif(message.text=="Back to HOME"):
            bot.send_message(message.chat.id, "Home Menu", reply_markup=gen_markup())

        elif(message.text=="Turn MD on/off"):
            motion_detection = not motion_detection
            bot.send_message(message.chat.id, "Motion Detection is now " + str(motion_detection))

        elif(message.text=="List motion videos"):
            #for filename in os.listdir(folder_to_track):
                #list = list + str(filename) + "\n"
            bot.send_message(message.chat.id, "The following motion videos are: ", reply_markup=gen_markup_list())

        elif(message.text=="Send photo now"):
            photo = open("/home/pi/motionvideos/snapshot.jpg", 'rb')
            bot.send_photo(message.chat.id, photo)

        elif(message.text=="CPU temperature"):
            cpu = CPUTemperature()
            tempinfo = "CPU Temperature: " + str(cpu.temperature) + " degrees C"
            bot.send_message(message.chat.id, tempinfo)



@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "delete":
        bot.send_message(my_chat_id, "Which video do you want to delete?", reply_markup=gen_markup_delete())

    elif call.data == "back_to_list":
        bot.send_message(my_chat_id, "The following motion videos are: ", reply_markup=gen_markup_list())

    elif call.data[0] == "d":
        del_filepath = call.data[1:]
        if os.path.exists(done_filepath + del_filepath):
            os.remove(done_filepath + del_filepath)
            bot.send_message(my_chat_id, "Video deleted", reply_markup=gen_markup_delete())

    else:
        if os.path.exists(done_filepath + call.data):
            video = open(done_filepath + call.data, 'rb')
            bot.send_video(my_chat_id, video)

    #fullname = folder_to_track + filename



def gen_markup():
    markup = ReplyKeyboardMarkup(row_width=1)
    itembtn1 = KeyboardButton('Motion Detection')
    itembtn2 = KeyboardButton('Raspberry Pi W Zero')

    markup.add(itembtn1, itembtn2)

    return markup


def gen_markup_motion():
    markup = ReplyKeyboardMarkup(row_width=1)
    itembtn1 = KeyboardButton('Turn MD on/off')
    itembtn2 = KeyboardButton('List motion videos')
    itembtn3 = KeyboardButton('Send photo now')
    itembtn4 = KeyboardButton('Back to HOME')

    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)

    return markup


def gen_markup_rpi():
    markup = ReplyKeyboardMarkup()
    itembtn1 = KeyboardButton('CPU temperature')
    itembtn5 = KeyboardButton('Back to HOME')

    markup.row(itembtn1)
    markup.row(itembtn5)

    return markup

def gen_markup_list():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    for filename in os.listdir(done_filepath):
	parsed = filename[3:7] + '/' + filename[7:9] + '/' + filename[9:11] + '-' + filename[11:13] + ':' + filename [13:15] + ':' + filename[15:17]
        markup.add(InlineKeyboardButton(parsed, callback_data=filename))

    markup.add(InlineKeyboardButton('Delete a video', callback_data='delete'))

    return markup

def gen_markup_delete():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    for filename in sorted(os.listdir(done_filepath)):
        delete_file = 'd' + filename
        markup.add(InlineKeyboardButton('Delete ' + filename, callback_data=delete_file))

    markup.add(InlineKeyboardButton('Back to LIST', callback_data='back_to_list'))

    return markup


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if(motion_detection):
            bot.send_message(989913486, "MOTION DETECTED!")


event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, done_filepath, recursive=True)
observer.start()


bot.infinity_polling(True)
