import const
import network
import urequests
from time import ticks_ms, ticks_diff, sleep_ms
from machine import Pin
from tm1637 import TM1637

# setup pins
pin_led = Pin('LED', Pin.OUT)
pin_7seg_clk = Pin(const.PIN_7SEG_CLK)
pin_7seg_dio = Pin(const.PIN_7SEG_DIO)
pin_state = Pin(const.PIN_STATE, mode=Pin.IN, pull=Pin.PULL_DOWN)

# global
tm = TM1637(clk=pin_7seg_clk, dio=pin_7seg_dio, brightness=1)
wlan = None

def init_wifi():
    global tm
    global wlan
    tm.show('CONN')
    print('init_wifi: start')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    sleep_ms(500)
    wlan.active(True)
    wlan.connect(const.WIFI_SSID, const.WIFI_PASS)
    max_wait = 10
    while max_wait > 0:
        print('init_wifi: status=' + str(wlan.status()))
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        sleep_ms(1000)
    if wlan.status() != 3:
        tm.show('E-00')
        raise RuntimeError('wlan status=' + str(wlan.status))
    print('init_wifi: end')

def send_state(state):
    global tm
    global wlan
    tm.show('SEND')
    print('send_state: start')
    if wlan.status() != 3:
        tm.show('E-01')
        raise RuntimeError('wlan status=' + str(wlan.status))
    url = const.API_URL + '/states/now'
    headers = {'content-type': 'application/json'}
    data = '{"state":"on"}' if state else '{"state":"off"}'
    auth = (const.API_USER, const.API_PASS)
    try:
        print('send url=' + url)
        print('send data=' + data)
        res = urequests.post(url, headers=headers, data=data, auth=auth)
    except:
        tm.show('E-02')
        raise
    try:
        if not res.json()['ok']:
            raise RuntimeError('text=' + res.text)
    except:
        tm.show('E-03')
        raise
    finally:
        res.close()
    print('send_state: end')

def wait_state_off():
    global tm
    if pin_state.value():
        tm.show('off ')
        while pin_state.value():
            sleep_ms(100)

def draw_first():
    global tm
    tm.show('----')

def draw_time(ms, blink):
    global tm
    if ms < 3600000:
        a = ms // 60000
        b = (ms % 60000) // 1000
    else:
        a = ms // 3600000
        b = (ms % 3600000) // 60000
    colon = (ms // 500 & 1) == 0 if blink else True
    tm.numbers(a, b, colon=colon)

def draw_result(ms):
    global tm
    if ticks_ms() // 1000 & 1:
        tm.show('    ')
    else:
        draw_time(ms, False)

def main():
    init_wifi()
    wait_state_off()
    prev_state = False
    curr_state = False
    curr_ms = 0
    start_ms = 0
    end_ms = 0
    while True:
        prev_state = curr_state
        curr_state = pin_state.value() != 0
        curr_ms = ticks_ms()
        work_ms = ticks_diff(curr_ms, start_ms)
        if curr_state != prev_state:
            if curr_state:
                send_state(curr_state)
                start_ms = curr_ms
                work_ms = 0
            else:
                end_ms = work_ms
                send_state(curr_state)
        if curr_state:
            draw_time(work_ms, True)
        elif end_ms != 0:
            draw_result(end_ms)
        else:
            draw_first()
        sleep_ms(50)

main()
