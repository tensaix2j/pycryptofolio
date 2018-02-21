import os
import tornado.ioloop
import tornado.web as web
from pprint import pprint


import ssl 
import http.client
import json

import psycopg2
import traceback



public_root = os.path.join(os.path.dirname(__file__), 'public')
conn = None
cur = None
table_name = "market"


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class CryptoTickersHandler(tornado.web.RequestHandler):
    def get(self):

        profile = self.get_arguments("profile")[0]
        
        #https://jsonblob.com/api/jsonBlob/cee8ea07-e160-11e7-b884-1b54ec7f20bc
        conn = http.client.HTTPSConnection("jsonblob.com", 443)
        conn.request("GET","/api/jsonBlob/{}".format(profile ) )
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        rawstr = r1.read()
        holdings = json.loads( str(rawstr,'utf-8'))
        
        # Check for table existence
        cur.execute("SELECT provider,base,quote,price from {} where base in ({}) order by provider".format(table_name , ",".join( map( lambda x:"'" + x + "'", holdings.keys()) )  ) ) 
        recs = cur.fetchall()

        market = {}
        for rec in recs:
          
          provider = rec[0]
          base     = rec[1]
          quote    = rec[2]
          price    = rec[3]

          if base not in market:
            market[base] = {}

          if quote not in market[base]:
            market[base][quote] = price
            if quote == "USDT" and "USDT" not in market:
              market["USDT"] = {}
            if base == "BTC" and quote == "USDT": 
              market["USDT"]["BTC"] = 1.0 / price
            if base == "ETH" and quote == "USDT":
              market["USDT"]["ETH"] = 1.0 / price  

        response = {}
        portfolio = []

        sum_total_btc = 0.0
        sum_total_eth = 0.0
        sum_total_usd = 0.0
        sum_total_sgd = 0.0

        for base in holdings.keys():

          obj = {}
          obj["base"] = base

          if base in market:
            
            if base == "BTC":
              obj["btc"]        = 1.0
            elif "BTC" in market[base]:
              obj["btc"]        = market[base]["BTC"]
            elif "ETH" in market[base]:
              obj["btc"]        = market[base]["ETH"] * market["ETH"]["BTC"]
            elif base == "USDT":
              obj["btc"]        = 1.0 / market["BTC"]["USDT"]
            

            if base == "ETH":
              obj["eth"]        = 1.0
            elif "ETH" in market[base]: 
              obj["eth"]        = market[base]["ETH"]
            elif "BTC" in market[base]:
              obj["eth"]        = market[base]["BTC"] / market["ETH"]["BTC"]
            elif base == "BTC":
              obj["eth"]        = 1.0 / market["ETH"]["BTC"]
            elif base == "USDT":
              obj["eth"]        = 1.0 / market["ETH"]["USDT"]
            

            if "USDT" in market[base]:
              obj["usd"]        = market[base]["USDT"]
            elif "BTC" in market[base]:
              obj["usd"]        = market[base]["BTC"] * market["BTC"]["USDT"]
            elif "ETH" in market[base]:
              obj["usd"]        = market[base]["ETH"] * market["ETH"]["USDT"]
            elif base == "USDT":
              obj["usd"]        = 1.0


            obj["sgd"]        = obj["usd"] * 1.32
            obj["own"]        = holdings[base]

            obj["total_btc"]  = obj["btc"] * obj["own"]
            obj["total_eth"]  = obj["eth"] * obj["own"]
            obj["total_usd"]  = obj["usd"] * obj["own"]
            obj["total_sgd"]  = obj["sgd"] * obj["own"]

            sum_total_btc += obj["total_btc"]
            sum_total_eth += obj["total_eth"]
            sum_total_usd += obj["total_usd"]
            sum_total_sgd += obj["total_sgd"]

            portfolio.append( obj )


        portfolio.sort(key=lambda x: x["total_usd"], reverse=True)
        
        response["portfolio"] = portfolio
        response["sum_total_btc"] = sum_total_btc
        response["sum_total_eth"] = sum_total_eth
        response["sum_total_usd"] = sum_total_usd
        response["sum_total_sgd"] = sum_total_sgd

        self.write( json.dumps(response ) )




handlers = [
  (r'/', MainHandler),
  (r'/index', MainHandler),
  (r'/cryptotickers', CryptoTickersHandler),
  (r'/(.*)', web.StaticFileHandler, {'path': public_root}),
]

settings = dict(
  debug=True,
  static_path=public_root,
  template_path=public_root
)

application = web.Application(handlers, **settings)

if __name__ == "__main__":
    
    try:

      if not os.path.exists("config.json"):
        print("Need config.json")
        exit()  

      fi = open("config.json", "r") 
      config = json.loads( fi.read() )
      dbhost = config["dbhost"]
      dbport = config["dbport"]
      dbname = config["dbname"]
      dbuser = config["dbuser"]
      dbpass = config["dbpass"]
      

      conn = psycopg2.connect("dbname='{0}' user='{3}' host='{1}' port='{2}' password='{4}'".format(dbname,dbhost,dbport,dbuser,dbpass) )
      print("Connected to {0}:{1} Db:{2}".format(dbhost,dbport,dbname) )
      cur = conn.cursor()

      application.listen(10000)
      tornado.ioloop.IOLoop.instance().start()
    except Exception as ex:
      print("Error! {}".format(ex) )
  