yaruki-client
=============

## Requirement

- [MicroPython TM1637](https://github.com/mcauser/micropython-tm1637)

## 起動方法

1. Raspberry Pi Pico W で MicroPython を使えるようにする
1. const.py.sample を元に const.py を作成し、環境に合わせて編集する
1. 次のファイルを RasPi Pico W へ転送する
    - main.py
    - const.py
    - tm1637.py ([MicroPython TM1637](https://github.com/mcauser/micropython-tm1637) よりコピー）
