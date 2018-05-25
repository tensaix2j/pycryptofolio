

import psycopg2
import traceback

import ssl 
import http.client
import json
from pprint import pprint

import os.path
import time



def get_from_binance(plate):

	print("get_from_binance")

	#https://www.binance.com/api/v1/ticker/allPrices
	conn = http.client.HTTPSConnection("www.binance.com", 443)
	conn.request("GET","/api/v1/ticker/allPrices")
	r1 = conn.getresponse()
	print(r1.status, r1.reason)

	rawstr = r1.read()
	data = json.loads( str(rawstr,'utf-8'))

	for obj in data:
		
		try:
			pair 	= obj["symbol"]
			price 	= float(obj["price"])

			if "USDT" in pair:
				quote = "USDT"
			else:
				quote = pair[-3:]

			base = pair[0:len(pair)-len(quote)]
			plate["BINANCE", base, quote ] = price 

		except Exception as ex:
			print("Error : {}".format(ex))		
		



def get_from_hitbtc(plate):

	print("get_from_hitbtc")

	#https://api.hitbtc.com/api/1/public/ticker
	conn = http.client.HTTPSConnection("api.hitbtc.com", 443)
	conn.request("GET","/api/1/public/ticker")
	r1 = conn.getresponse()
	print(r1.status, r1.reason)

	rawstr = r1.read()
	data = json.loads( str(rawstr,'utf-8'))

	for pair in data.keys():
		
		try:
			price 	= float( data[pair]["last"])

			if "USDT" in pair:
				quote = "USDT"
			else:
				quote = pair[-3:]

			base = pair[0:len(pair)-len(quote)]
			if quote == "USD":
				quote = "USDT"
				
			plate["HITBTC", base, quote ] = price 

		except Exception as ex:
			print("Error : {}".format(ex))		
		



def get_from_kucoin(plate):

	print("get_from_kucoin")
	#https://api.kucoin.com/v1/open/tick
	conn = http.client.HTTPSConnection("api.kucoin.com", 443)
	conn.request("GET","/v1/open/tick")

	r1 = conn.getresponse()
	print(r1.status, r1.reason)

	rawstr = r1.read()
	data = json.loads( str(rawstr,'utf-8'))

	for obj in data["data"]:

		try:
			if obj["vol"] > 0:
				base 	= obj["coinType"]
				quote 	= obj["coinTypePair"]	
				price 	= obj["lastDealPrice"]
				plate["KUCOIN", base, quote ] = price 

		except Exception as ex:
			print("Error : {}".format(ex))		
				


def get_from_bittrex(plate):
	
	print("get_from_bittrex")
	#https://bittrex.com/api/v1.1/public/getmarketsummaries ;
	conn = http.client.HTTPSConnection("bittrex.com", 443)
	conn.request("GET","/api/v1.1/public/getmarketsummaries")

	r1 = conn.getresponse()
	print(r1.status, r1.reason)

	rawstr = r1.read()
	data = json.loads( str(rawstr,'utf-8'))

	for obj in data["result"]:

		try:
			if obj["Volume"] > 0:
				pair 	= obj["MarketName"].split("-")
				base 	= pair[1]
				quote 	= pair[0]
				price 	= obj["Last"]
				plate["BITTREX", base, quote ] = price 

		except Exception as ex:
			print("Error : {}".format(ex))		
			


def get_from_huobi(plate, base, quote ):

	try:
		print("get_from_huobi")
		#//http://api.huobi.pro/market/detail/merged?symbol=htusdt
		conn = http.client.HTTPSConnection("api.huobi.pro", 443)
		conn.request("GET","/market/detail/merged?symbol={}{}".format(base.lower(),quote.lower() ) )

		r1 = conn.getresponse()
		print(r1.status, r1.reason)

		rawstr = r1.read()
		data = json.loads( str(rawstr,'utf-8'))

		if data["status"] == "ok":
			price = data["tick"]["bid"][0]
			plate["HUOBI", base, quote ] = price 

	except Exception as ex:
			print("Error : {}".format(ex))		
	


def get_from_bibox(plate, base, quote):

	try:
		print("get_from_bibox")
		#https://api.bibox.com/v1/mdata?cmd=market&pair=BIX_BTC
		conn = http.client.HTTPSConnection("api.bibox.com", 443)
		conn.request("GET","/v1/mdata?cmd=market&pair={}_{}".format(base,quote ) )

		r1 = conn.getresponse()
		print(r1.status, r1.reason)

		rawstr = r1.read()
		data = json.loads( str(rawstr,'utf-8'))
		price = float(data["result"]["last"])
		plate["BIBOX", base, quote ] = price 

	except Exception as ex:
			print("Error : {}".format(ex))		

	

def get_from_cryptopia(plate, base, quote ):
	
	try:

		print("get_from_cryptopia")
		#https://www.cryptopia.co.nz/api/GetMarket/ETN_BTC	
		conn = http.client.HTTPSConnection("www.cryptopia.co.nz", 443)
		conn.request("GET","/api/GetMarket/{}_{}".format(base,quote ) )

		r1 = conn.getresponse()
		print(r1.status, r1.reason)

		rawstr = r1.read()
		data = json.loads( str(rawstr,'utf-8'))

		if data["Success"] == True:
			price = float(data["Data"]["LastPrice"])
			plate["BIBOX", base, quote ] = price 

	except Exception as ex:
			print("Error : {}".format(ex))		



def store(plate):

	print("Storing data")
	
	script_dir = os.path.dirname(sys.argv[0])
	if script_dir == "":
		script_dir = "."
	config_file = "{0}/config.json".format(script_dir) 

	if not os.path.exists(config_file):
		print("{} does not exist".format(config_file) )
		return


	fi = open(config_file, "r") 
	config = json.loads( fi.read() )
	
	dbhost = config["dbhost"]
	dbport = config["dbport"]
	dbname = config["dbname"]
	dbuser = config["dbuser"]
	dbpass = config["dbpass"]
	table_name = "market"

	try:

		conn = psycopg2.connect("dbname='{0}' user='{3}' host='{1}' port='{2}' password='{4}'".format(dbname,dbhost,dbport,dbuser,dbpass) )
		print("Connected to {0}:{1} Db:{2}".format(dbhost,dbport,dbname) )

		cur = conn.cursor()

		# Check for table existence
		cur.execute("SELECT * from information_schema.tables where table_name = '{}'".format(table_name ))
		table_existed = cur.fetchall()

		if len(table_existed) == 0:
			
			print("Table {} does not exist,creating now".format(table_name) )
			cur.execute("CREATE TABLE IF NOT EXISTS market( id SERIAL ,base varchar ,quote varchar ,provider varchar, lastUpdated varchar , price float );" )
			conn.commit()
			
		else:
			print("Table exists")


		

		# Get existinf records	
		cur.execute("SELECT provider,base,quote from market ")
		existing_records = cur.fetchall()
		existing_plate = {}
		for row in existing_records:
			existing_plate[row[0],row[1],row[2]] = 1


		
		for key in plate.keys():
			try:

				if key in existing_plate:
					cur.execute("UPDATE market set price='{0}', lastUpdated = '{1}' where provider='{2}' and base='{3}' and quote='{4}' ".format( plate[key], time.strftime("%Y%m%d.%H%M%S") , key[0],key[1],key[2] ) )
					
				else:
					cur.execute("INSERT INTO market(provider,base,quote,price,lastUpdated) values('{0}','{1}','{2}','{3}','{4}')".format( key[0], key[1], key[2], plate[key], time.strftime("%Y%m%d.%H%M%S") ) )
				
			except Exception as ex:
	 			print("Error INSERT {}".format(ex) )
			
		conn.commit()	

	except Exception as ex:
	    print("Error! {}".format(ex) )







def main():

	plate = {}
	

	get_from_binance( plate )
	get_from_hitbtc( plate )
	get_from_kucoin( plate )
	get_from_bittrex( plate )
	get_from_huobi(plate, "HT", "USDT" )
	get_from_huobi(plate, "HT", "BTC" )
	get_from_huobi(plate, "HT", "ETH" )
	get_from_bibox( plate , "BIX", "USDT")
	get_from_bibox( plate , "BIX", "BTC")
	get_from_bibox( plate , "BIX", "ETH")
	get_from_cryptopia(plate, "ETN", "BTC")
	get_from_cryptopia(plate, "ETN", "ETH")
		
	store(plate)


main()









