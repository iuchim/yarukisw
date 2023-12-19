import const
import network
import requests
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

def send_state(state):
    tm.show('CONN')
    print('send_state: connecting...')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(const.WIFI_SSID, const.WIFI_PASS)
    max_wait = 10
    while max_wait > 0:
        print('send_state: status={}'.format(wlan.status()))
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        sleep_ms(1000)
    if wlan.status() != 3:
        tm.show('E-00')
        raise RuntimeError('wlan status={}'.format(wlan.status()))
    tm.show('SEND')
    url = const.API_URL + '/states/now'
    data = { 'state': 'on' if state else 'off' }
    auth = (const.API_USER, const.API_PASS)
    res = None
    try:
        print('send_state: url={}, data={}'.format(url, data))
        res = requests.post(url, json=data, auth=auth)
        if not res.json()['ok']:
            raise RuntimeError('text=' + res.text)
        res.close()
        wlan.disconnect()
    except:
        tm.show('E-01')
        raise

def wait_state_off():
    if pin_state.value():
        tm.show('off ')
        while pin_state.value():
            sleep_ms(100)

def draw_first():
    tm.show('----')

def draw_time(ms, blink):
    if ms < 3600000:
        a = ms // 60000
        b = (ms % 60000) // 1000
    else:
        a = ms // 3600000
        b = (ms % 3600000) // 60000
    colon = (ms // 500 & 1) == 0 if blink else True
    tm.numbers(a, b, colon=colon)

def draw_result(ms):
    if ticks_ms() // 1000 & 1:
        tm.show('    ')
    else:
        draw_time(ms, False)

def main():
    wait_state_off()
    prev_state = False
    curr_state = False
    curr_ms = 0
    work_ms = 0
    start_ms = 0
    end_ms = 0
    while True:
        prev_state = curr_state
        curr_state = pin_state.value() != 0
        curr_ms = ticks_ms()
        work_ms = ticks_diff(curr_ms, start_ms)
        if curr_state != prev_state:
            send_state(curr_state)
            if curr_state:
                start_ms = curr_ms
                work_ms = 0
            else:
                end_ms = work_ms
        if curr_state:
            draw_time(work_ms, True)
        elif end_ms != 0:
            draw_result(end_ms)
        else:
            draw_first()
        sleep_ms(50)

main()
