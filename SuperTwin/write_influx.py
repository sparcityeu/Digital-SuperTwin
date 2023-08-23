import requests
import time

def return_time():

    _time = "%.0f" % time.time()
    _time = _time + "000000000"
    print("Returning: ", _time)
    return _time
    
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

params = {
    'db': 'dolap',
}


_x = [0, 8, 32, 32]
_y = [2.5, 16, 16, 16]

while(True):
    _time = return_time()
    _datax = 'roofX valueE0=' + str(_x[0]) + ' ' +_time
    print("_datax:", _datax)
    response = requests.post('http://localhost:8086/write', params=params, headers=headers, data=_datax)
    _datay = 'roofY valueE0=' + str(_y[0]) + ' ' +_time
    response = requests.post('http://localhost:8086/write', params=params, headers=headers, data=_datay)
    time.sleep(2)
    for i in range(3):
        _time = return_time()
        _datax = 'roofX valueE0=' + str(_x[i+1]) + ' ' +_time
        print("_datax:", _datax)
        response = requests.post('http://localhost:8086/write', params=params, headers=headers, data=_datax)
        _datay = 'roofY valueE0=' + str(_y[i+1]) + ' ' +_time
        response = requests.post('http://localhost:8086/write', params=params, headers=headers, data=_datay)
        time.sleep(1)


'''
data = 'roofX valueA0=1 ' + _time
response = requests.post('http://localhost:8086/write', params=params, headers=headers, data=data)

data = 'roofX valueA1=8 ' + _time
response = requests.post('http://localhost:8086/write', params=params, headers=headers, data=data)

data = 'roofX valueA2=32 ' + _time
response = requests.post('http://localhost:8086/write', params=params, headers=headers, data=data)

data = 'roofY valueA0=-2.5 ' + _time
response = requests.post('http://localhost:8086/write', params=params, headers=headers, data=data)

data = 'roofY valueA1=16 ' + _time
response = requests.post('http://localhost:8086/write', params=params, headers=headers, data=data)

data = 'roofY valueA2=16 ' + _time
response = requests.post('http://localhost:8086/write', params=params, headers=headers, data=data)
'''
