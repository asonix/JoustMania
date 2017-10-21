from gi.repository import GLib

import dbus
import dbus.service
import dbus.mainloop.glib

class JoustParty(dbus.service.Object):
    def __init__(self, bus, path, cmd_queue):
        super().__init__(bus, path)
        self.cmd_queue = cmd_queue

    @dbus.service.method("com.joustmania.party.Party1",
                         in_signature='', out_signature='')
    def ClearAllDevices(self):
        self.cmd_queue.put({'command': 'clear_all_devices'})

    @dbus.service.method("com.joustmania.party.Party1",
                         in_signature='', out_signature='')
    def RequestPairing(self):
        self.cmd_queue.put({'command': 'request_pairing'})

    @dbus.service.method("com.joustmania.party.Party1",
                         in_signature='', out_signature='')
    def PairComplete(self):
        self.cmd_queue.put({'command': 'pair_complete'})

def dbus_thread(cmd_queue):
    print('dbus thread started')

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    system_bus = dbus.SystemBus()
    name = dbus.service.BusName("com.joustmania.party", system_bus)
    jp = JoustParty(system_bus, '/com/joustmania/party', cmd_queue)

    mainloop = GLib.MainLoop()

    print("Running joust party service.")
    mainloop.run()
