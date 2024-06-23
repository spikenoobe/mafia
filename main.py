from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message
from time import sleep
import db
from random import choice

TOKEN = "6881967983:AAHXrg2vlAxClLS43-5i9cGwvW40hfRN5vk"
bot = TeleBot(TOKEN)

game = False
night = False

def get_killed(night: bool) -> str:
    if not night:
        username_killed = db.citizen_kill()
        return f'горожане выгнали: {username_killed}'
    username_killed = db.mafia_kill()
    return f'мафия убила: {username_killed}'

def auto_play_citizen(message: Message):
    players_roles = db.get_player_roles()
    for player_id in players_roles:
        usernames = db.get_all_alive()
        name = f"robot{player_id}"
        if player_id < 5 and name in usernames:
            usernames.remove(name)
            vote_username = choice(usernames)
            db.vote("citizen_vote", vote_username, player_id)
            bot.send_message(message.chat.id, f"{name} проголосвал за {vote_username}")

def autoplay_mafia():
    players_roles = db.get_players_roles()
    for player_id, role in players_roles:
        usernames = db.get_all_alive()
        name = f"robot{player_id}"
        if player_id < 5 and name in usernames and role == "mafia":
            usernames.remove(name)
            vote_username = choice(usernames)
            db.vote("mafia_vote", vote_username, player_id)


def game_loop(message: Message):
    global night, game
    bot.send_message(message.chat.id, "добро пожаловать в игру! Вам дается 1 минута чтобы познакомиться")
    sleep(10)
    while True:
        msg = get_killed(night)
        bot.send_message(message.chat.id, msg)
        if not night:
            bot.send_message(message.chat.id, "Настала ночь. Город засыпает, просыпается мафия.")
        else:
            bot.send_message(message.chat.id, "Наступил день. Город просыпается.")
        winner = db.check_winner()
        if winner == "Мафия" or winner == "Горожане":
            game = False
            bot.send_message(message.chat.id, f"Игра закончена! победили {winner}")
            return
        db.clear(dead=False)
        night = not night
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id, f'В игре:\n{alive}')
        sleep(10)
        autoplay_mafia() if night else auto_play_citizen()

@bot.message_handler(func=lambda message: message.text.lower() == 'готов играть' and message.chat.type == 'private')
def send_text(message: Message):
    bot.send_message(message.chat.id, f"{message.from_user.first_name} играет")
    bot.send_message(message.chat.id, 'Вы добавлены в игру')
    db.insert_player(message.from_user.id, message.from_user.first_name)


@bot.message_handler(commands=['start'])
def game_on(message: Message):
    if not game:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton('готов играть'))
        bot.send_message(message.chat.id, "если хотите играть нажмите на кнопку ниже", reply_markup=keyboard)

@bot.message_handler(commands=['play'])
def game_start(message: Message):
    global game
    players = db.player_amount()
    if players >= 5 and not game:
        db.set_roles(players)
        players_roles = db.get_player_roles( )
        mafia_usernames = db.get_mafia_usernames( )
        for player_id, role, in players_roles:
            try:
                bot.send_message(player_id, role)
            except Exception:
                continue

        if role == 'mafia':
            bot.send_message(player_id, f'Все члены мафии:\n{mafia_usernames}')
        db.clear(dead=True)
        game = True
        bot.send_message(message.chat.id, 'Игра началась!')
        game_loop(message)
        return
    bot.send_message(message.chat.id, 'Недостаточно людей!')
    for i in range(5 - players):
        bot_name = f'robot{i}'
        db.insert_player(i, bot_name)
        bot.send_message(message.chat.id, f'{bot_name} добавлен!')
        sleep(0.2)
    game_start(message)

@bot.message_handler(commands=['kick'])
def kick(message: Message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id, 'такого имени нет!')
            return
        voted = db.vote("citizen_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'ваш голос учтен')
            return
        bot.send_message('сейчас ночь вы не можете никого выгнать')

@bot.message_handler(commands=['kill'])
def kill(message: Message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    mafia_usernames = db.get_mafia_usernames()
    if night and message.from_user.first_name in mafia_usernames:
        if not username in usernames:
            bot.send_message(message.chat.id, 'такого имени нет')
            return
        voted = db.vote("mafia_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'ваш голос учтенн')
            return
        bot.send_message(message.chat.id, 'у вас больше нет права голосовать')
    bot.send_message(message.chat.id, 'сейчас нельзя убивать')




bot.polling(non_stop=True, interval=1) 