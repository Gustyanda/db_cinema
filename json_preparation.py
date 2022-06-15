#----- 01. Introduction
# from flask import Flask, flash
# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello World'


#----- 02. Get query
# from flask import Flask, request
# app = Flask(__name__)


# @app.route('/hello', methods=['GET'])
# def hello():
#     name = request.args.get('name')
#     return 'hello ' + name


#----- 03. Get json
# from flask import Flask, request
# app = Flask(__name__)

# @app.route('/hello-json', methods=['GET'])
# def hello():
#     name = request.args.get('name')
#     return {'message':'hello ' + name}


#----- 04. Get json url, specific data, get data headers
# from urllib import response
# from flask import Flask, request
# import requests
# app = Flask(__name__)

# @app.route('/weather', methods=['POST'])
# def data():
#     city = request.headers.get('city')
#     response = requests.get('https://api.openweathermap.org/data/2.5/weather?q='+city+',id&appid=27edaa711aa55803ce95bab5bdaa2129')
#     if response.status_code == 200:    
#         return {
#             'weather': response.json()['weather'][0]['main'],
#             'temp': str(response.json()['main']['temp']) + ' fahrenheit',
#             'coordinate': response.json()['coord']
#         }
#     else:
#         return {
#             'message':'cek kembali'
#         }
        

#----- 05. get data body
# from urllib import response
# from flask import Flask, request
# import requests
# app = Flask(__name__)


# @app.route('/car_manufacturer', methods=['POST'])
# def data():
#     lst_mfr = []
#     data = request.get_json()
#     response = requests.get("https://vpic.nhtsa.dot.gov/api/vehicles/getallmanufacturers?format=json")
#     a = response.json()["Results"]
#     for x in a:
#         if x['Country'] == data['country']:
#             lst_mfr.append(x["Mfr_Name"])
#     return str(lst_mfr)




#----- 06. Authorization user and password
# import string
# from urllib import response
# from flask import Flask, request
# import requests, base64
# app = Flask(__name__)


# @app.route('/car_manufacturer', methods=['GET'])
# def data():
#     decode_var = request.headers.get('Authorization')
#     encode_var = base64.b64decode(decode_var[6:])
#     string_var = encode_var.decode('ascii')
#     lst = string_var.split(':')
#     username = lst[0]
#     password = lst[1]
#     response = requests.get("https://vpic.nhtsa.dot.gov/api/vehicles/getallmanufacturers?format=json")
#     if username == 'admin' and password == '4dm1n123!':
#         lst_mfr = []
#         data = request.get_json()
#         a = response.json()["Results"]
#         for x in a:
#             if x['Country'] == data['country']:
#                 lst_mfr.append(x["Mfr_Name"])
#         return str(lst_mfr)



#----- 07. get auth multi
# from flask import Flask, request
# import requests, base64
# app = Flask(__name__)

# @app.route('/weather', methods=['GET','POST'])

# def handler():
#     decode_var = request.headers.get('Authorization')
#     encode_var = base64.b64decode(decode_var[6:])
#     string_var = encode_var.decode('ascii')
#     lst = string_var.split(':')
#     username = lst[0]
#     password = lst[1]
#     if (username == 'ayamitik') and (password == '80000'):
#         return data()
#     elif (username == 'admin') and (password == '4dm1n123'):
#         return data()
#     elif (username == 'user1') and (password == 'us3r1'):
#         return data()
#     elif (username == 'user2') and (password == 'us3r2'):
#         return data()
#     else:
#         return {
#             'message': '401, balik kanan'
#         }
    

# def data():
#     city = request.headers.get('city')
#     response = requests.get('https://api.openweathermap.org/data/2.5/weather?q='+city+',id&appid=27edaa711aa55803ce95bab5bdaa2129')
#     if response.status_code == 200:
#         return {
#             'weather': response.json()['weather'][0]['main'],
#             'temp': str(response.json()['main']['temp']) + ' fahrenheit',
#             'coordinate': response.json()['coord']
#         }



#----- 07.1. get auth multi
# from flask import Flask, request
# import base64, requests
# app = Flask(__name__)


# def is_authorized(auth):
#     if auth == None:
#         return False
#     encode_var = base64.b64decode(auth[6:])
#     string_var = encode_var.decode('ascii')
#     lst = string_var.split(':')
#     username = lst[0]
#     password = lst[1]
#     username_ = ['admin','user1','user2']
#     password_ = ['4dm1n123','us3r1','us3r2']
#     for x in range(len(username_)):
#         if username_[x] == username and password_[x] == password:
#             return True
#     return False
        

# @app.route('/weather', methods=['GET','POST'])
# def handler():
#     auth_header = request.headers.get('Authorization')
#     allow = is_authorized(auth_header)
#     if allow == True:
#         return data()
#     else:
#         return 'puter balik', 401


# def data():
#     city = request.headers.get('city')
#     response = requests.get('https://api.openweathermap.org/data/2.5/weather?q='+city+',id&appid=27edaa711aa55803ce95bab5bdaa2129')
#     if response.status_code == 200:
#         return {
#             'weather': response.json()['weather'][0]['main'],
#             'temp': str(response.json()['main']['temp']) + ' fahrenheit',
#             'coordinate': response.json()['coord']
#         }



#----- 08. output as postman using API
# from flask import Flask, jsonify, request
# app = Flask(__name__)

# def data(n):
#     shared = 5
#     cumulative = []
#     for x in range(0,int(n)):
#         liked = shared//2
#         shared = liked*3
#         cumulative.append(liked)
#     # return jsonify(sum(cumulative))
#     return {'total': sum(cumulative)}


# @app.route('/viral-advert', methods=['GET'])
# def handler():
#     answer = request.args.get('day')
#     return data(answer)


# def getMovieTitles(substr):
#     import requests  
#     url = "https://jsonmock.hackerrank.com/api/movies/search/?Title="+substr+"&page2"
#     response = requests.get(url)
#     data = response.json()["data"]
#     y = []
#     for i in data:
#         y.append(i["Title"])
#     return y
# print(getMovieTitles("Spiderman"))