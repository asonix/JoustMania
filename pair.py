import psmove
import os
import time

import dbus
from multiprocessing import Process, Queue, Manager

import jm_dbus

class Pair():
    """
    Manage paring move controllers to the server
    """
    def __init__(self, bus):
        """Use DBus to find bluetooth controllers"""
        self.bus = bus
        self.hci_dict = jm_dbus.get_hci_dict(bus)

        devices = self.hci_dict.values()
        self.bt_devices = {}
        for device in devices:
            self.bt_devices[device] = []

        self.pre_existing_devices()

    def pre_existing_devices(self):
        """
        Enumerate known devices

        For each device on each adapter, add the device's address to it's adapter's
        list of known devices
        """
        for hci, addr in self.hci_dict.items():
            proxy = jm_dbus.get_adapter_proxy(self.bus, hci)
            devices = jm_dbus.get_node_child_names(proxy)

            self.bt_devices[addr] = jm_dbus.get_attached_addresses(self.bus, hci)

    def update_adapters(self):
        """
        Rescan for bluetooth adapters that may not have existed on program launch
        """
        self.hci_dict = jm_dbus.get_hci_dict(self.bus)

        for addr in self.hci_dict.values():
            if addr not in self.bt_devices.keys():
                self.bt_devices[addr] = []

        self.pre_existing_devices()

    def get_all_devices(self):
        """
        Get a list of all devices known by the adapters
        """
        devices = []
        for addr in self.bt_devices.keys():
            devices += self.bt_devices[addr]
        return devices

    def check_if_not_paired(self, addr):
        for devs in self.bt_devices.keys():
            if addr in self.bt_devices[devs]:
                return False
        return True

    def get_lowest_bt_device(self):
        num = 9999999
        print(self.bt_devices)
        for dev in self.bt_devices.keys():
            if len(self.bt_devices[dev]) < num:
                num = len(self.bt_devices[dev])

        for dev in self.bt_devices.keys():
            if len(self.bt_devices[dev]) == num:
                return dev
        return ''

    def pair_move(self, move):
        if move and move.get_serial():
            if move.connection_type == psmove.Conn_USB:
                self.pre_existing_devices()
                if self.check_if_not_paired(move.get_serial().upper()):
                    move.pair_custom(self.get_lowest_bt_device())

    def unpair_all(self):
        for addr in self.bt_devices.keys():
            bt_devices[addr].clear()

        hcis = self.hci_dict.keys()
        for hci in hcis:
            hci_proxy = jm_dbus.get_adapter_proxy(self.bus, hci)
            devices = jm_dbus.get_node_child_names(hci_proxy)

            for dev in devices:
                jm_dbus.remove_device(self.bus, hci, dev)

if __name__ == '__main__':
    from pair_pairing import pair_thread
    from pair_dbus import dbus_thread
    with Manager() as manager:
        device_list = manager.list()
        cmd_queue = Queue()

        dbus_proc = Process(target=dbus_thread, args=(cmd_queue, device_list))
        dbus_proc.start()
        pair_proc = Process(target=pair_thread, args=(cmd_queue, device_list))
        pair_proc.start()

        dbus_proc.join()
        pair_proc.join()
