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

def updateCD(chat_id, num, numattempts, games, user):
    cb = ChatData.get_or_insert(str(chat_id))
    cb.num = num
    cb.numattempts = numattempts
    cb.games = games
    cb.user = user
    cb.put()

def getCD(chat_id, name):
    cb = ChatData.get_by_id(str(chat_id))
    if cb:
        return cb
    else:
        cb = ChatData.get_or_insert(str(chat_id))
        digits = '123456789'
        size = 4
        cb.num = ''.join(random.sample(digits,size))
        cb.numattempts = 0
	cb.games = 1
	cb.user = name
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

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg,
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()

            logging.info('send response:')
            logging.info(resp)


        cd = getCD(chat_id, str(chat))
        digits = '123456789'
        size = 4
        num = cd.num
        numattempts = cd.numattempts
	games = cd.games

        if text.startswith('/'):
            if "start" in text:
                if numattempts > 0:
                    reply("Finish the current game!!")
                else:
                    reply("Guess the 4 digit number I guessed!!")
		    numattempts = 1
		    updateCD(chat_id, num, numattempts, games, str(chat))
            else:
                reply('Oopsie!!')
        else:
            if numattempts > 0:
                if len(text) == size and all(char in digits for char in text) and len(set(text)) == size:
                    if text == num:
                      reply("You won in "+str(numattempts)+" tries!")
                      numattempts = 0
                      num = ''.join(random.sample(digits,size))
                      updateCD(chat_id, num, numattempts, games+1, str(chat))
                      return
                    numattempts += 1
                    bulls = cows = 0
                    for i in range(size):
                      if text[i] == num[i]:
                          bulls += 1
                      elif text[i] in num:
                          cows += 1
                    reply("Attempt: "+str(numattempts-1)+"\nBulls: "+str(bulls)+"\nCows: "+str(cows))
                    updateCD(chat_id, num, numattempts, games, str(chat))
                    return
                reply("4 digits. Non repeating!!!!")
            else:
                reply("Click /start")


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
    ('/test', MeTester),
], debug=True)
