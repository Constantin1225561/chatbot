
# coding: utf-8

# In[1]:

import json 
import requests
import time
import urllib
import sys, random, collections, os


# In[2]:

# Since we split on whitespace, this can never be a word
NONWORD = "\n"

class Markov():

	def __init__(self, order=2):
		self.output = ""
		self.order = order
		self.table = collections.defaultdict(list)
		self.seen = collections.deque([NONWORD] * self.order, self.order)

	# Generate table
	def generate_table(self, filename):
		for line in open(filename): 
			for word in line.split():
				self.table[tuple(self.seen)].append(word)
				self.seen.append(word)
		self.table[tuple(self.seen)].append(NONWORD) # Mark the end of the file

	#table, seen = generate_table("gk_papers.txt")

	# Generate output
	def generate_output(self, max_words=100):
		self.output = ""
		self.seen.extend([NONWORD] * self.order) # clear it all
		for i in range(max_words):
			word = random.choice(self.table[tuple(self.seen)])
			if word == NONWORD:
				exit()
			self.output = self.output + word + " "
			self.seen.append(word)


	def walk_directory(self, rootDir):
		for dirName, subdirList, fileList in os.walk(rootDir):
			print('Found directory: %s' % dirName)
			for fname in fileList:
				self.generate_table(os.path.join(dirName,fname))
				#print('\t%s' % fname)


# In[3]:

people = ["trump", "clinton", "bojack"]
markovChains = [Markov(order=1), Markov(order=1), Markov(order=1)]
i = 0
while i < len(people):
    markovChains[i] = Markov(order=3)
    markovChains[i].walk_directory('./data/'+people[i])
    i = i + 1

def getReply(text):
    person = "null"
    i = 0
    while i < len(people):
        if people[i] in text.lower():
            person = people[i]
            m = markovChains[i]
        i = i + 1
    if person == "null":
        message = "Whom should I imitate? I can imitate:"
        i = 0
        while i < len(people):
            message += " " + people[i]
            i = i + 1
        return message
    m.generate_output(max_words=50)
    return m.output


# In[4]:

TOKEN = "321534474:AAFZTRNsQ6bb9hEd0_vMAFFLfX18lMVC4yU" # don't put this in your repo! (put in config, then import config)
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        send_message(getReply(text), chat)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text) # urllib.parse.quote_plus(text) # (python3)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()

