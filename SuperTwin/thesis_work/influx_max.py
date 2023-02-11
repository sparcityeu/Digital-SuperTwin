import time

from influxdb import InfluxDBClient

_dict = {'time': '2022-12-22T17:46:02.564377Z', '_cpu0': 132565498.617, '_cpu1': 96959176.428, '_cpu10': 125295791.391, '_cpu11': 98118715.059, '_cpu12': 69855912.816, '_cpu13': 61997804.048, '_cpu14': 85307598.873, '_cpu15': 104367414.141, '_cpu16': 145976261.376, '_cpu17': 149771257.956, '_cpu18': 101760050.82, '_cpu19': 115583333.5, '_cpu2': 53983335.893, '_cpu20': 496750036.4, '_cpu21': 146431507.628, '_cpu22': 34026397.302, '_cpu23': 43059304.675, '_cpu24': 32809111.706, '_cpu25': 30873943.161, '_cpu26': 32294949.709, '_cpu27': 33624897.034, '_cpu28': 31455074.724, '_cpu29': 32737417.153, '_cpu3': 51818986.511, '_cpu30': 32459466.629, '_cpu31': 32569864.593, '_cpu32': 261703167.477, '_cpu33': 32675206.481, '_cpu34': 117421249.878, '_cpu35': 33511317.831, '_cpu36': 33308689.868, '_cpu37': 36884422.301, '_cpu38': 32580962.031, '_cpu39': 33638407.825, '_cpu4': 42739337.864, '_cpu40': 186831162.977, '_cpu41': 445551790.369, '_cpu42': 33848824.338, '_cpu43': 34887352.232, '_cpu44': 60194797.528, '_cpu45': 48963358.91, '_cpu46': 85773208.584, '_cpu47': 97521786.999, '_cpu48': 39229105.045, '_cpu49': 88748474.701, '_cpu5': 159327551.922, '_cpu50': 76134842.643, '_cpu51': 118690701.807, '_cpu52': 85955588.31, '_cpu53': 105260598.312, '_cpu54': 42884725.466, '_cpu55': 204603986.621, '_cpu56': 35063032.409, '_cpu57': 75412119.024, '_cpu58': 339721042.25, '_cpu59': 30363271.55, '_cpu6': 403959060.747, '_cpu60': 87646515.496, '_cpu61': 197198978.015, '_cpu62': 150293826.801, '_cpu63': 106501572.669, '_cpu64': 54839581.792, '_cpu65': 225680775.145, '_cpu66': 30915692.184, '_cpu67': 30014314.578, '_cpu68': 29162265.122, '_cpu69': 28684207.692, '_cpu7': 125667545.579, '_cpu70': 28957257.712, '_cpu71': 30719091.622, '_cpu72': 28772737.88, '_cpu73': 29192378.19, '_cpu74': 29315588.868, '_cpu75': 29430356.797, '_cpu76': 29698965.05, '_cpu77': 40725059.187, '_cpu78': 29427141.652, '_cpu79': 42573490.607, '_cpu8': 126484890.611, '_cpu80': 52788941.256, '_cpu81': 31010714.492, '_cpu82': 29770679.549, '_cpu83': 30655053.981, '_cpu84': 29412683.47, '_cpu85': 25317172.507, '_cpu86': 45655626.405, '_cpu87': 73315678.621, '_cpu9': 62924380.257, 'tag': '_monitor'}


if __name__ == "__main__":
    
    
    
    client = InfluxDBClient(host='localhost', port=8086)
    client.drop_database("thr_run")
    client.create_database("thr_run")
    client.switch_database("thr_run")
    
    t_end = time.time() + 10
    while time.time() < t_end:
        client.write(record=_dict)