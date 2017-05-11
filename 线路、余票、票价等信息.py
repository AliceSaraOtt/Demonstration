# -*- coding: utf-8 -*-
import time
import datetime
import json
import requests

def fetch_stations(t, start, end, train_no, code, fd):
    url = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo"

    params = u"train_no=" + train_no + u"&from_station_telecode=" + start + u"&to_station_telecode=" + end + "&depart_date=" + t
    try:
        s = requests.get(url, params=params.encode("utf-8"), verify=False)
    except Exception, e:
        print "fetch stations fail. " + url
        raise e

    stations = json.loads(s.content)

    out = u"---------------------------------\n"
    out += code + u"\n"
    for station in stations["data"]["data"]:
        out += station["station_no"]
        out += u" " + station["station_name"]
        out += u" " + station["arrive_time"]
        out += u" " + station["start_time"]
        out += u" " + station["stopover_time"]
        out += u"\n"

    s = out.encode("utf-8")
    fd.write(s)
    fd.write("\n")

    print s


def fetch_price(t, start, end,
                train_no, seat_types,
                src_name, des_name,
                train_code, fd):
    url = "https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice"

    params = u"train_no=" + train_no + u"&from_station_no=" + start + u"&to_station_no=" + end + u"&seat_types=" + seat_types + u"&train_date=" + t
    try:
        s = requests.get(url, params=params.encode("utf-8"), verify=False)
    except Exception, e:
        print "fetch price fail. " + url
        raise e

    prices = json.loads(s.content)

    price = prices["data"]
    out = u"---------------------------------\n"
    out += train_code + u" " + src_name + u" " + des_name + u"\n"
    if "A9" in price:
        out += price["A9"]
    else:
        out += u" --"
    if "P" in price:
        out += u" " + price["P"]
    else:
        out += u" --"
    if "M" in price:
        out += u" " + price["M"]
    else:
        out += u" --"
    if "O" in price:
        out += u" " + price["O"]
    else:
        out += u" --"
    if "A6" in price:
        out += u" " + price["A6"]
    else:
        out += u" --"
    if "A4" in price:
        out += u" " + price["A4"]
    else:
        out += u" --"
    if "A3" in price:
        out += u" " + price["A3"]
    else:
        out += u" --"
    if "A2" in price:
        out += u" " + price["A2"]
    else:
        out += u" --"
    if "A1" in price:
        out += u" " + price["A1"]
    else:
        out += u" --"
    if "WZ" in price:
        out += u" " + price["WZ"]
    else:
        out += u" --"
    if "MIN" in price:
        out += u" " + price["MIN"]
    else:
        out += u" --"

    s = out.encode("utf-8")
    fd.write(s)
    fd.write("\n")
    print s


def fetch_data(t, start, end, fd1, fd2, existed_codes):
    url = "https://kyfw.12306.cn/otn/leftTicket/query"
    params = u"leftTicketDTO.train_date=" + t + u"&leftTicketDTO.from_station=" + start + u"&leftTicketDTO.to_station=" + end + u'&purpose_codes=ADULT'
    try:
        s = requests.get(url, params=params.encode("utf-8"), verify=False)
    except Exception, e:
        print "requests url fail.", url
        return

    # print s.content
    # print s.url

    datas = json.loads(s.content)

    if len(datas["data"]) == 0:
        print "no train", t, start.encode("utf-8"), end.encode("utf-8")
        return

    for data in datas["data"]:
        time.sleep(0.1)
        code = data["queryLeftNewDTO"]["station_train_code"]
        src_name = data["queryLeftNewDTO"]["from_station_name"]
        des_name = data["queryLeftNewDTO"]["end_station_name"]
        no = data["queryLeftNewDTO"]["train_no"]
        from_station_no = data["queryLeftNewDTO"]["from_station_no"]
        to_station_no = data["queryLeftNewDTO"]["to_station_no"]
        seat_types = data["queryLeftNewDTO"]["seat_types"]

        is_fetch_station = False

        if no in existed_codes:
            
            if (src_name, des_name) in existed_codes[no]:
                continue
            else:
                existed_codes[no].add((src_name, des_name))
        else:
            is_fetch_station = True
            existed_codes[no] = set([(src_name, des_name)])
            # existed_codes[no] = {src_name, des_name}

        time.sleep(0.1)
        fetch_price(t, from_station_no, to_station_no, no, seat_types, src_name, des_name, code, fd2)

        if is_fetch_station:
            time.sleep(0.1)
            fetch_stations(t, start, end, no, code, fd1)


def fetch_stations_code():
    url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8936"

    try:
        s = requests.get(url, verify=False)
    except Exception, e:
        print "fetch stations fail. " + url
        raise e
    station_str = s.content.decode("utf-8")

    stations = station_str.split(u"@")

    results = []
    with open("15.code.txt", "w") as fd:
        for i in range(1, len(stations)):
            station = stations[i].split(u"|")
            results.append((station[1], station[2]))
            fd.write((station[1] + u" " + station[2] + u"\n").encode("utf-8"))

    return results[:6] # 仅前5个站点用于测试


def deal_and_store(existed_codes):
    result = set()
    with open("15.routes.txt", "w") as fd:
        for code in existed_codes: # 便利字典
            routes = existed_codes[code]
            for route in routes: # routes是集合，每一个元素是个列表:['北京'，'哈尔滨'] 只有一个元素
                if route not in result:
                    result.add(route)
                    out = route[0] + u" " + route[1] + u"\n"
                    fd.write(out.encode("utf-8"))


def fetch_trains_static_info(existed_codes):
    stations = fetch_stations_code()

    size = len(stations)
    with open("15.train_code.txt", "w") as fd1:
        with open("15.train_price.txt", "w") as fd2:
            for i in range(0, size - 1): # 这里是组合 是否转换成排列
                for j in range(i + 1, size):
                    t = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
                    src = stations[i][1]
                    des = stations[j][1]

                    # print src,des
                    time.sleep(0.1)
                    fetch_data(t, src, des, fd1, fd2, existed_codes)
    return existed_codes

def get_code_dic():
    res = {}
    with open('15.code.txt', 'r') as fcode:
        for line in fcode:
            res[line.split(' ')[0]] = line.split(' ')[1][:-1]
    return res

def fetch_tickets():
    url = "https://kyfw.12306.cn/otn/leftTicket/query"
    t = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
    code_dic = get_code_dic()

    with open('15.routes.txt','r') as froutes:
        routes = froutes.readlines()
        routes = [(route.split(' ')[0],route.split(' ')[1][:-1]) for route in routes]
        with open('15.tickets.txt', 'w') as f:
            for s,e in routes:
                start = code_dic[s]
                end = code_dic[e]
                params = u"leftTicketDTO.train_date=" + t + u"&leftTicketDTO.from_station=" + start + u"&leftTicketDTO.to_station=" + end + u'&purpose_codes=ADULT'

                try:
                    rep = requests.get(url,params=params,verify=False)
                except Exception,e:
                    raise e

                datas = json.loads(rep.content)
                for data in datas["data"]:
                    out = u"--------------------------------------\n"
                    out += data["queryLeftNewDTO"]["from_station_name"]
                    out += u" " + data["queryLeftNewDTO"]["end_station_name"]
                    out += u" " + data["queryLeftNewDTO"]["station_train_code"]
                    out += u"\n" + data["queryLeftNewDTO"]["swz_num"]
                    out += u" " + data["queryLeftNewDTO"]["tz_num"]
                    out += u" " + data["queryLeftNewDTO"]["zy_num"]
                    out += u" " + data["queryLeftNewDTO"]["ze_num"]
                    out += u" " + data["queryLeftNewDTO"]["gr_num"]
                    out += u" " + data["queryLeftNewDTO"]["rw_num"]
                    out += u" " + data["queryLeftNewDTO"]["yw_num"]
                    out += u" " + data["queryLeftNewDTO"]["rz_num"]
                    out += u" " + data["queryLeftNewDTO"]["yz_num"]
                    out += u" " + data["queryLeftNewDTO"]["wz_num"]
                    out += u" " + data["queryLeftNewDTO"]["qt_num"]

                    content = out.encode("utf-8")
                    f.write(content + '\n')

if __name__ == "__main__":
    # existed_codes = {}
    # fetch_trains_static_info(existed_codes)
    # deal_and_store(existed_codes) # 保存存在的路线
    fetch_tickets()

