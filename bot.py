# *-* coding: utf-8 *-*
#importing modules
import telebot,sqlite3, os
#defining variables and creating bot with bot's token
global username
bot=telebot.TeleBot(os.environ["BOT_API_TOKEN"])
username="Gric_bot"
#defining bot's answers on different content types
@bot.message_handler(commands=["start","help"])
def start(message):
    global username,data,inv_usrs
    rating=None
    connection=sqlite3.connect("base.db")
    cursor=connection.cursor()
    if message.text.split(" ")[0] == "/start" and message.text.split("/start ")[-1] != "/start":
        try:
            usr_id=int(message.text.split("/start ")[-1])
            if message.from_user.id != usr_id:
                data,inv_usrs=get_data()
                r=0
                for i in inv_usrs:
                    if i[0] == usr_id:
                        r=1
                        inv=i
                try:
                    if str(message.from_user.id) not in inv[1].split(", "):
                            r=0
                            for i in data:
                                if i[0] == usr_id:
                                    r=1
                                    usr=i
                            
                            if r == 0:
                                new_user(usr_id,1,bot.get_chat(usr_id).first_name)
                            if r == 1:
                                sql="UPDATE users SET rating = {0} WHERE user_id = {1}".format(usr[1]+1,usr_id)
                                cursor.execute(sql)
                                connection.commit()
                            sql="SELECT * FROM users"
                            data=cursor.execute(sql).fetchall()
                            sql="SELECT * FROM invited_users"
                            data=cursor.execute(sql).fetchall()
                            for i in data:
                                if i[0] == usr_id:
                                    usr=i
                except NameError:
                    r=0
                    for i in data:
                        if i[0] == usr_id:
                            r=1
                            usr=i
                    
                    if r == 0:
                        new_user(usr_id,1,bot.get_chat(usr_id).first_name)
                    if r == 1:
                        sql="UPDATE users SET rating = {0} WHERE user_id = {1}".format(usr[1]+1,usr_id)
                        cursor.execute(sql)
                        connection.commit()
                    sql="SELECT * FROM users"
                    data=cursor.execute(sql).fetchall()
                    sql="SELECT * FROM invited_users"
                    inv_usrs=cursor.execute(sql).fetchall()
                r=0
                for i in inv_usrs:
                    if i[0] == usr_id:
                        r=1
                        inv=i
                if r == 0:
                    sql='''INSERT into invited_users(main_usr_id,invited_users,name_main_usr)
                    VALUES(?,?,?)'''
                    lst=[message.from_user.id]
                    cursor.execute(sql,(usr_id,str(lst).strip("[]"),bot.get_chat(usr_id).first_name))
                    connection.commit()
                if r == 1:
                    aa=inv[1].split(", ")
                    if str(message.from_user.id) not in aa:
                        aa.append(str(message.from_user.id))
                        sql="UPDATE invited_users SET invited_users = \"{0}\" WHERE main_usr_id = {1}".format(str(aa).strip("[]"),usr_id)
                        cursor.execute(sql)
                data,inv_usrs=get_data()
                for i in inv_usrs:
                    if i[0] == usr_id:
                        r=1
                        inv=i
            else:
                bot.send_message(message.chat.id,"Don't cheat! You can't invite yourself!")
        except ValueError:
            pass
    if rating is None:
        data,inv_usrs=get_data()
        r=0
        usr=0
        for i in data:
            if i[0] == message.from_user.id:
                r=1
                usr=i
        if r == 0:
            new_user(message.from_user.id,0,message.from_user.first_name)
            rating=0
        if r == 1:
            rating=usr[1]
    connection.close()
    data,inv_usrs=get_data()
    for i in data:
        if i[0] == message.from_user.id:
            usr=i
    if usr[3] == None:
        bot.send_message(message.chat.id,"Hello, "+message.from_user.first_name+'''! I'm referral bot! Invite users to get more points!
    /help, /start to display this message
    To get your invite link, you should do some steps:
    1. Join this group:
    https://t.me/griccoin1
    2. Send /done when you're done
    3. Send your email
    Your rating: '''+str(rating))
    else:
        bot.send_message(message.chat.id,"Hello, "+message.from_user.first_name+'''! I'm referral bot! Invite users to get more points!
/help, /start to display this message
Your rating: '''+str(rating)+'''
Your invite link:
t.me/'''+username+"?start="+str(message.from_user.id))
@bot.message_handler(commands=["done"])
def done(message):
    if bot.get_chat_member(-1001397863358,message.from_user.id).status == "left":
        bot.send_message(message.chat.id,"You are not in this group! Please, join to continue.")
    else:
        sent=bot.send_message(message.chat.id,"You're in this group! Good! Now, enter your email to continue:")
        bot.register_next_step_handler(sent,email)
def email(message):
    email=message.text
    data,inv_usrs=get_data()
    connection=sqlite3.connect("base.db")
    cursor=connection.cursor()
    r=0
    for i in data:
        if i[0] == message.from_user.id:
            r=1
    if r == 0:
        new_user(message.from_user.id,0,message.from_user.first_name)
    if r == 1:
        sql="UPDATE users SET email = \"{0}\" WHERE user_id = {1}".format(email,message.from_user.id)
        cursor.execute(sql)
        connection.commit()
    connection.close()
    bot.send_message(message.chat.id,"Congratulations! You can now get your invite link! Type /help or /start to get it!")
def get_data():
    connection=sqlite3.connect("base.db")
    cursor=connection.cursor()
    sql="SELECT * FROM users"
    data=cursor.execute(sql).fetchall()
    sql="SELECT * FROM invited_users"
    inv_usrs=cursor.execute(sql).fetchall()
    connection.close()
    return data,inv_usrs
def new_user(usr_id,rating,name):
    connection=sqlite3.connect("base.db")
    cursor=connection.cursor()
    sql='''INSERT INTO users(user_id,rating,name,email)
    VALUES(?,?,?,?)'''
    cursor.execute(sql,(usr_id,rating,name,None))
    connection.commit()
    connection.close()
global data,inv_usrs
data,inv_usrs=get_data()
#and here we run long polling, it means that bot will check for new messages, none_stop=True means that it will not stop if error occurs
if __name__ == "__main__":
    while True:
        bot.infinity_polling(none_stop=True)
