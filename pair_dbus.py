from gi.repository import GLib

import dbus
import dbus.service
import dbus.mainloop.glib

class JoustPair(dbus.service.Object):
    def __init__(self, bus, path, cmd_queue, device_list):
        super().__init__(bus, path)
        self.device_list = device_list
        self.cmd_queue = cmd_queue

    @dbus.service.method("com.joustmania.pair.Joust1",
                         in_signature='', out_signature='as')
    def KnownControllers(self):
        return list(self.device_list)

    @dbus.service.method("com.joustmania.pair.Joust1",
                         in_signature='', out_signature='')
    def PausePairing(self):
        self.cmd_queue.put('pause')

    @dbus.service.method("com.joustmania.pair.Joust1",
                         in_signature='', out_signature='')
    def UnpausePairing(self):
        self.cmd_queue.put('go')

    @dbus.service.method("com.joustmania.pair.Joust1",
                         in_signature='', out_signature='')
    def PermitPairing(self):
        self.cmd_queue.put('pairing_permitted')


def dbus_thread(cmd_queue, device_list):
    print('dbus thread started')

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    system_bus = dbus.SystemBus()
    name = dbus.service.BusName("com.joustmania.pair", system_bus)
    jp = JoustPair(system_bus, '/com/joustmania/pair', cmd_queue, device_list)

    mainloop = GLib.MainLoop()

    print("Running joust pairing service.")
    mainloop.run()
