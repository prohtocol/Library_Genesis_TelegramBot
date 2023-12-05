import os
import subprocess
import telebot
from book import book_get
import config

bot = telebot.TeleBot(config.YOUR_BOT_TOKEN)
bot.files_enabled = True


@bot.message_handler(commands=["start"])
def starting(message):
    """
    Responds to the /start command with a welcome message.
    """
    text = (
        "Hey. Send me book name in any format and I"
        " will respond with libgen.is book file."
    )
    bot.reply_to(message, text)


@bot.message_handler(commands=["toggle_files"])
def toggle_files(message):
    """
    Toggles the bot's file sending feature.
    """
    bot.files_enabled = not bot.files_enabled
    bot.reply_to(
        message,
        f'File downloads are now '
        f'{"disabled" if not bot.files_enabled else "enabled"}',
    )


# Handles any other message
@bot.message_handler(func=lambda message: True)
def echo(msg):
    """
    This function will get the book name from the
    user and will send the book to the user
    This will respond to any message
    """
    wait_message_id = bot.reply_to(msg, "Please wait...").message_id
    chat_id = msg.chat.id
    books = book_get(msg.text, config.mainres, config.results)

    if books == "Error: emoji":
        bot.reply_to(msg, "Error: emoji\nPlease do not use Emojis😂")
    elif books == "Error: no results found":
        bot.reply_to(
            msg, "Error: no results found\nPlease try for another book."
        )
    elif books == "Error: enter name":
        bot.reply_to(
            msg,
            "Error: enter name\nPlease provide the"
            " name of the book you are looking for",
        )
    elif books == "Error: Title Too Short":
        bot.reply_to(
            msg,
            "Error: Title Too Short\nPlease provide "
            "the full title for better results",
        )
    else:
        bot.delete_message(chat_id, wait_message_id)

        def send_book(book_obj, with_file=False):
            """
            Sends the book details and optionally the file to the user.
            """
            dn = f"[DOWNLOAD NOW]({book_obj[5]})"
            caption_all = f"*Name* : {book_obj[0]}\n*Author* : \
            {book_obj[1]}\n"\
                f"*Size* : {book_obj[3]}\n*Format* : {book_obj[4]}\n{dn}"
            bot.send_photo(
                msg.from_user.id,
                book_obj[6],
                caption=caption_all,
                parse_mode="Markdown",
            )
            if bot.files_enabled and with_file:
                # Download the file
                file_name = book_obj[0] + "." + book_obj[4]
                subprocess.run(["wget", "-O", file_name, book_obj[5]])
                # Send the file to the chat
                with open(file_name, "rb") as file:
                    bot.send_document(chat_id, file)
                # Delete the file
                os.remove(file_name)

        good_fmt_books = [b[4] == "pdf" or b[4] == "epub" for b in books]
        if any(good_fmt_books):
            best_match_best_format_index = good_fmt_books.index(True)
            send_book(books[best_match_best_format_index], with_file=True)
        else:
            send_book(books[0], with_file=True)


def main():
    """
    Runs the bot and starts polling for messages.
    """
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("Polling stopped by user")


if __name__ == "__main__":
    main()
