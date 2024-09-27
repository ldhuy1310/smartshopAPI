from pymongo import MongoClient

# Kết nối tới MongoDB
client = MongoClient('mongodb://db:27017/')

# Kết nối tới database 'mydatabase'
db = client['mydatabase']

# Tạo collection 'smart_shop' nếu chưa tồn tại
if 'smart_shop' not in db.list_collection_names():
    db.create_collection('smart_shop')
    print("Collection 'smart_shop' created.")
else:
    print("Collection 'smart_shop' already exists.")
