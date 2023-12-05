from unittest import result
from bs4 import BeautifulSoup as bs
import requests
import telebot
# import os
import time
from book import book_get
import secrets
import requests
import time
import requests
import os
import telebot
# import pycurl

import subprocess

bot = telebot.TeleBot(secrets.YOUR_BOT_TOKEN)
results = 5
mainres = 25
bot.files_enabled = True



@bot.message_handler(commands=["start"])
def starting(message):
    text = f"I am a simple book bot.\nI will help you to download books of your own choice\nOur syntax is easy just send\n/book<space><book name>\nWithout without bracket sign.\nEXAMPLE : /book abc\n\nSend /help to get help"
    bot.reply_to(message , text)


@bot.message_handler(commands=["help"])
def help(message):
    text = f"Commands:\n1.  /book <book_name>"
    bot.reply_to(message , text)


@bot.message_handler(commands=["toggle_files"])
def toggle_files(message):
    bot.files_enabled = not bot.files_enabled
    bot.reply_to(message, f'Files are now {"disabled" if not bot.files_enabled else "enabled"}')




@bot.message_handler(func=lambda message: True)
def echo(message):
    """
    This function will get the book name from the user and will send the book to the user
    This will respond to any message
    """
    id = message.from_user.id
    given_name = message.text
    messageId = bot.reply_to(message, "Please wait...").message_id
    chatId = message.chat.id
    data = book_get(given_name, mainres, results)

    if data == "Error: emoji":
        bot.reply_to(message, "Error: emoji\nPlease do not use Emojis😂")
    elif data == "Error: no results found":
        bot.reply_to(message, "Error: no results found\nPlease try for another book.")
    elif data == "Error: enter name":
        bot.reply_to(message, "Error: enter name\nPlease provide the name of the book you are looking for")
    elif data == "Error: Title Too Short":
        bot.reply_to(message, "Error: Title Too Short\nPlease provide the full title for better results")
    else:
        counter = 0
        bot.delete_message(chatId, messageId)


    def send_book(book_obj, with_file=False):
        dn = f"[DOWNLOAD NOW]({book_obj[5]})"
        caption_all = f"*Name* : {book_obj[0]}\n*Author* : {book_obj[1]}\n*Size* : {book_obj[3]}\n*Format* : {book_obj[4]}\n{dn}"
        bot.send_photo(id, book_obj[6], caption=caption_all, parse_mode="Markdown")
        if bot.files_enabled and with_file:
            # Download the file
            file_name = book_obj[0] + "." + book_obj[4]

            # response = requests.get(book_obj[5])
            # with open(file_name, "wb") as file:
            #     file.write(response.content)


            # c = pycurl.Curl()
            # c.setopt(pycurl.URL, book_obj[5])
            # c.setopt(pycurl.WRITEDATA, open(file_name, 'wb'))
            # c.perform()
            # c.close()



            subprocess.run(['wget', '-O', file_name, book_obj[5]])


            # Send the file to the chat
            with open(file_name, "rb") as file:
                bot.send_document(chatId, file)
            # Delete the file
            os.remove(file_name)

    # for i in data:
    #     if counter <= results:
    #         send_book(i)
    #         counter += 1

    llist = []
    try:
        lllst = [i[4] == "pdf" or i[4] == 'epub' for i in data]
    except IndexError:
        print(data)
    if any(lllst):
        best_match_best_format_index = lllst.index(True)
        i = data[best_match_best_format_index]
        send_book(i, with_file=True)
    else:
        i = data[0]
        send_book(i, with_file=True)



def run_bot():
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print('Polling stopped by user')



if __name__ == "__main__":
    run_bot()


