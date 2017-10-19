from gi.repository import GLib
from multiprocessing import Queue

import dbus
import dbus.service
import dbus.mainloop.glib

class JMDBusServer(dbus.service.Object):
    def __init__(self, bus, path, command_queue):
        super().__init__(bus, path)
        self.command_queue = command_queue

    @dbus.service.method("com.joustmania.Joust1",
                         in_signature='', out_signature='')
    def UnpairAll(self):
        self.command_queue.put({'command': 'unpairall'})

    @dbus.service.method("com.joustmania.Joust1",
                         in_signature='', out_signature='')
    def Exit(self):
        mainloop.quit()


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    session_bus = dbus.SystemBus()
    name = dbus.service.BusName("com.joustmania", session_bus)
    object = JMDBusServer(session_bus, '/com/joustmania', Queue())

    mainloop = GLib.MainLoop()
    print("Running joustmania service.")
    mainloop.run()
