from flask import Flask,render_template,request
from flask_pymongo import PyMongo
import json
import urllib.request as urllib

app=Flask(__name__)

app.config["MONGO_DBNAME"]="user_data"
app.config["MONGO_URI"]="mongodb://admin:admin123@ds141168.mlab.com:41168/company_pricing"
mongo=PyMongo(app)

@app.route('/register-stock',methods=['GET','POST'])
def registerStock():
    buyingValue=request.json.get('BuyingValue')
    investedMoney=request.json.get('InvestedMoney')
    companyName=request.json.get('CompanyName')
    saveToDatabase({'buyingValue': buyingValue, 'investedMoney': investedMoney, 'companyName': companyName,
                 'currentValue': buyingValue})


def getCurrentValue(investedStocks):

    for doc in investedStocks:
        data=json.loads(urllib.urlopen("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=NSE:"+doc["companyName"]+"&interval=1min&outputsize=compact&apikey=MCAF9B429I44328U").read())
        doc['currentValue']=float(data['Time Series (1min)'][list(data['Time Series (1min)'].keys())[0]]['1. open'])
    return investedStocks
   # dxpmbg7n70vw3anb

@app.route('/check-investment',methods=['GET','POST'])
def checkInvestment():
    StockRecords=retrieveFromDatabase()
    investedStocks=[document for document in StockRecords]
    investedStocks=getCurrentValue(investedStocks)
    for doc in investedStocks:
        print(doc)
        doc['profitMargin']=float(doc['currentValue'])-float(doc['buyingValue'])
        saveToDatabase(doc,modify=True)
    return str(investedStocks)

def saveToDatabase(document,modify=False):
    conn = mongo.db.value_holding
    if modify is not True:
        conn.insert(document)
    else:
        conn.update({"_id":document['_id']},{"$set": {"currentValue":document['currentValue']}},upsert=False)

def retrieveFromDatabase():
    conn = mongo.db.value_holding
    return conn.find({})

if __name__=='__main__':
    app.run(debug=True)