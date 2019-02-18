import pymongo
 
myclient = pymongo.MongoClient('mongodb://localhost:27899/')
mydb = myclient['scrap']
mycol = mydb["test"]
mydict = { "name": "Google", "alexa": "1", "url": "https://www.google.com" }
x = mycol.insert_one(mydict)
print(x.inserted_id)
