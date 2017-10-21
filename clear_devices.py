#!/usr/bin/env python

import dbus
import jm_dbus

if __name__ == '__main__':
    bus = dbus.SystemBus()
    jm_dbus.clear_all_devices(bus)
