import StringIO
import json
import logging
import random
import urllib
import urllib2
import re

import random
# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '117344370:AAHHCNDsY6DGWdFBDNnk4e-KSVwXGOH09xU'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

DIGITS = '0123456789'
SIZE = 4

# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)

# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return True
    #return False


# ================================


class ChatData(ndb.Model):
    num = ndb.StringProperty()
    numattempts = ndb.IntegerProperty()
    user = ndb.StringProperty()
    games = ndb.IntegerProperty()
    best = ndb.IntegerProperty()
    guesshistory = ndb.StringProperty()

def updateCD(chat_id, num, numattempts, games, user, best, history):
    cb = ChatData.get_or_insert(str(chat_id))
    cb.num = num
    cb.numattempts = numattempts
    cb.games = games
    cb.user = user
    cb.best = best
    cb.guesshistory = history
    cb.put()

def getCD(chat_id, name):
    cb = ChatData.get_by_id(str(chat_id))
    if cb:
        return cb
    else:
        cb = ChatData.get_or_insert(str(chat_id))
        cb.num = ''.join([random.choice(DIGITS) for _ in range(SIZE)])
        cb.numattempts = 0
        cb.games = 1
        cb.user = name
        cb.best = 0
        cb.guesshistory = ""
        cb.put()
        return cb



class MeTester(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write('yolo')

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        qb = body.get('callback_query')
        if(qb):
            text = qb.get('message').get('text')
            if "left" in qb.get('data'):
                x = -1
            else:
                x = 1
            try:
                newtext = str(int(text)+x)
            except:
                newtext = 0
            inline_keyboard = {'inline_keyboard': [[{'text':'Left', 'callback_data': 'left'},{'text':'Right', 'callback_data': 'right'}]]}
            inline_keyboard = json.dumps(inline_keyboard)
            params = urllib.urlencode({
                'chat_id': str(qb.get('message').get('chat').get('id')),
                'text': newtext,
                'message_id': str(qb.get('message').get('message_id')),
                'reply_markup': inline_keyboard,
                'disable_web_page_preview': 'true'
            })
            a = urllib.urlopen(BASE_URL+'editMessageText?'+params)
            logging.info(a.read())
            return

        try:
            update_id = body['update_id']
            message = body['message']
            message_id = message.get('message_id')
            date = message.get('date')
            text = message.get('text')
            fr = message.get('from')
            chat = message['chat']
            chat_id = chat['id']

            if not text:
                logging.info('no text')
                return
        except Exception as e:
            logging.error(e)






        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg,
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()

            logging.info('send response:')
            #logging.info(resp)





        cd = getCD(chat_id, str(chat))

        num = cd.num
        numattempts = cd.numattempts
        best = cd.best
        games = cd.games
        if cd.guesshistory:
            history = cd.guesshistory
        else:
            history = ""
        if text.startswith('/'):
            if "start" in text:
                if numattempts > 0:
                    reply("Finish the current game!!")
                else:
                    reply("Guess the 4 digit number I guessed!!")
                    numattempts = 1
                    updateCD(chat_id, num, numattempts, games, str(chat), best, history)
            elif "showbest" in text.lower():
                if best == 0:
                    reply("Start playing first :|")
                else:
                    reply("Your best was "+str(best))
            elif "history" in text:
                reply (history)
            elif "rcg" in text:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(urllib.urlopen('http://explosm.net/rcg').read())
                url = soup.find_all(id='rcg-comic')[0].find('img')['src']
                params = urllib.urlencode({'chat_id': str(16795984),'text': url})
                a = urllib.urlopen(BASE_URL+'sendMessage?'+params)
            else:
                reply('Oopsie!!')
        else:
            if numattempts > 0:
                if len(text) == SIZE and all(char in DIGITS for char in text): # and len(set(text)) == SIZE:
                    if text == num:
                      reply("You won in "+str(numattempts)+" tries!")
                      num = ''.join([random.choice(DIGITS) for _ in range(SIZE)])
                      if best == 0 or best > numattempts:
                          best = numattempts
                      numattempts = 0
                      history = ""
                      updateCD(chat_id, num, numattempts, games+1, str(chat), best, history)
                      return
                    numattempts += 1
                    bulls = cows = 0
                    for i in range(SIZE):
                      if text[i] == num[i]:
                          bulls += 1
                    for i in range(len(set(text))):
                      if "".join(set(text))[i] in num:
                         cows += 1
                    cows = cows - bulls
                    try:
                        history+="#"+str(numattempts-1)+". "+text+"\nBulls: "+str(bulls)+"\nCows: "+str(cows)+"\n\n"
                    except:
                        history = ""
                    reply("Attempt: "+str(numattempts-1)+"\nBulls: "+str(bulls)+"\nCows: "+str(cows))
                    updateCD(chat_id, num, numattempts, games, str(chat), best, history)
                    return
                reply("4 DIGITS!!!")
            else:
                reply("Click /start")


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
    ('/test', MeTester),
], debug=True)
