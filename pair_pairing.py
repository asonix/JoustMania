from pair import Pair

import psmoveapi, psmove
import time
import dbus
import jm_dbus

def psmove_update(x):
    pass

def psmove_connect(move, cmd_queue, device_list, p):
    p.update_adapters()
    connected_move = move.serial.upper()
    print('connect', connected_move)

    if connected_move not in p.get_all_devices():
        moves = [psmove.PSMove(x) for x in range(psmove.count_connected())]

        bus = dbus.SystemBus()

        for m in moves:
            if m.get_serial().upper() == connected_move:
                pair(m, p)

    p.update_adapters()

    for device in p.get_all_devices():
        if device not in device_list:
            print('adding to device list')
            device_list.append(device)

    print('connect complete')

def pair(m, p):
    print('pairing')
    try:
        jm_dbus.request_pairing(bus)
        while True:
            if cmd_queue.get() == 'pairing_permitted':
                break
    except dbus.exceptions.DBusException as e:
        if 'ServiceUnknown' not in str(e):
            raise e
    p.pair_move(m)
    m.set_leds(255,255,255)
    m.update_leds()
    try:
        jm_dbus.pair_complete(bus)
    except dbus.exceptions.DBusException as e:
        if 'ServiceUnknown' not in str(e):
            raise e

def psmove_disconnect(move, device_list, p):
    p.update_adapters()
    disconnected_move = move.serial.upper()
    print('disconnect', disconnected_move)

    if disconnected_move not in p.get_all_devices():
        if disconnected_move in device_list:
            print('deleting form device remove')
            device_list.remove(disconnected_move)

    print('disconnect complete')

def pair_thread(cmd_queue, device_list):
    print('pair thread started')
    p = Pair(dbus.SystemBus())
    p.update_adapters()

    for dev in p.get_all_devices():
        if dev not in device_list:
            device_list.append(dev)

    api = psmoveapi.PSMoveAPI()
    api.on_update = psmove_update
    api.on_connect = lambda x: psmove_connect(x, cmd_queue, device_list, p)
    api.on_disconnect = lambda x: psmove_disconnect(x, device_list, p)

    prev_running = False
    running = True
    while True:
        time.sleep(0.1)
        p.pre_existing_devices()
        if len(p.get_all_devices()) != len(device_list):
            print('device list', device_list)
            print('all devices', p.get_all_devices())
            removed = set(device_list) - set(p.get_all_devices())
            for dev in removed:
                print('removing', dev, 'from list')
                device_list.remove(dev)

        while not cmd_queue.empty():
            if running and cmd_queue.get() == 'pause':
                running = False
            elif not running and cmd_queue.get() == 'go':
                running = True

        if running != prev_running:
            prev_running = running
            if running:
                print('Unpaused')
            else:
                print('Paused')

        if running:
            api.update()
