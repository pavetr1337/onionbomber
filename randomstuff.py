import random
import datetime
import requests as req

import os
from dotenv import load_dotenv

load_dotenv()

names = {
	"male" : [
		"Алексей",
		"Дмитрий",
		"Виталий",
		"Виктор",
		"Геннадий",
		"Александр",
		"Кирилл",
		"Валерий"
	],
	"female" : [
		"Мария",
		"Анна",
		"Виктория",
		"Анастасия",
		"София"
	]
}
def get_random_name(gender="male"):
	return random.choice(names[gender])

surnames = {
	"male" : [
		"Алексеев",
		"Лукьянов",
		"Громов",
		"Захаров",
		"Сухоруков",
		"Дмитриев",
	],
	"female" : [
		"Алексеева",
		"Лукьянова",
		"Громова",
		"Захарова",
		"Сухорукова",
		"Дмитриева",
	]
}

def get_random_surname(gender="male"):
	return random.choice(surnames[gender])

nicks = [
	"DeathCrazy",
	"DarkLively",
	"OmegaGx",
	"OneReality",
	"FreezThe",
	"FlammeGodzilla",
	"DoctorHyper",
	"StrongCraby",
	"LuckMaster",
	"GalacticPhantom",
	"DuckFrench",
	"NeverHeal"
]

def get_random_nick():
	return f"{random.choice(nicks)}{random.randint(1000,10000)}"

mails = [
	"mail.ru",
	"rambler.ru",
	"bk.ru",
	"yandex.ru",
	"gmail.com",
	"hotmail.com",
	"protonmail.com"
]

def get_random_mail():
	return f"{get_random_nick()}@{random.choice(mails)}"

def get_today():
	return (datetime.datetime.today()).strftime('%Y-%m-%d')

proxies = []
api_url = "https://proxyleet.com/proxy/type=socks5&speed=1000&key="

def get_proxy():
		if not proxies:
			res = req.get(f"{api_url}{os.getenv("PROXYLEET_KEY")}",timeout=5,verify=False)
			for line in res.content.splitlines():
				proxies.append(str(line,'utf-8'))
		addr = random.choice(proxies)
		proxy = {
			"http": f"socks5://{addr}",
			"https": f"socks5://{addr}"
		}
		return proxy

# print(get_random_name())
# print(get_random_nick())
# print(get_random_mail())

# print(get_today())