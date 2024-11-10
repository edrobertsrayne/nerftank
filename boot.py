from machine import Pin
import network
import esp

esp.osdebug(None)

network.hostname("nerftank")


def connect_accesspoint(ssid) -> network.WLAN:
    wifi = network.WLAN(network.AP_IF)
    wifi.config(ssid=ssid)
    print(f"Creating accesspoint {ssid}")
    wifi.active(True)
    while not wifi.active():
        pass

    print("Accesspoint creation successful.")
    print(wifi.ifconfig())

    Pin(2, Pin.OUT).value(1)

    return wifi


def connect_wifi(ssid, password) -> network.WLAN:
    wifi = network.WLAN(network.STA_IF)
    if not wifi.isconnected():
        print(f"Connecting to {ssid}")
        wifi.active(True)
        wifi.connect(ssid, password)
        while not wifi.isconnected():
            pass

    print("Network connection successful.")
    print(wifi.ifconfig())
    print(f"Hostname: {network.hostname()}.local")

    Pin(2, Pin.OUT).value(1)

    return wifi


wifi = connect_accesspoint("nerftank")
