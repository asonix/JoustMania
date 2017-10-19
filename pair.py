import psmove
import os
import jm_dbus

class Pair():
    """
    Manage paring move controllers to the server
    """
    def __init__(self):
        """Use DBus to find bluetooth controllers"""
        self.hci_dict = jm_dbus.get_hci_dict()

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
            proxy = jm_dbus.get_adapter_proxy(hci)
            devices = jm_dbus.get_node_child_names(proxy)

            self.bt_devices[addr] = jm_dbus.get_attached_addresses(hci)

    def update_adapters(self):
        """
        Rescan for bluetooth adapters that may not have existed on program launch
        """
        self.hci_dict = jm_dbus.get_hci_dict()

        for addr in self.hci_dict.values():
            if addr not in self.bt_devices.keys():
                self.bt_devices[addr] = []

        self.pre_existing_devices()

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
            hci_proxy = jm_dbus.get_adapter_proxy(hci)
            devices = jm_dbus.get_node_child_names(hci_proxy)

            for dev in devices:
                jm_dbus.remove_device(hci, dev)

class PairManager():
    def __init__():
        self.pair = Pair()
        self.pair_one_move = True
        self.paired_moves = []
        self.tracked_moves = {}
        self.teams = {}

    def pair_usb_move(self, move):
        move_serial = move.get_serial()
        if move_serial not in self.tracked_moves:
            if move.connection_type == psmove.Conn_USB:
                if move_serial not in self.paired_moves:
                    self.pair.pair_move(move)
                    move.set_leds(255,255,255)
                    move.update_leds()
                    self.paired_moves.append(move_serial)
                    self.pair_one_move = False
        
    def pair_move(self, move, move_num):
        move_serial = move.get_serial()
        if move_serial not in self.tracked_moves:
            color = Array('i', [0] * 3)
            opts = Array('i', [0] * 6)
            if move_serial in self.teams:
                opts[Opts.team.value] = self.teams[move_serial]
            else:
                #initialize to team Yellow
                opts[Opts.team.value] = 3 
            if move_serial in self.out_moves:
                opts[Opts.alive.value] = self.out_moves[move_serial]
            opts[Opts.game_mode.value] = self.game_mode.value
            
            #now start tracking the move controller
            proc = Process(target=track_move, args=(move_serial, move_num, opts, color, self.show_battery, self.dead_count))
            proc.start()
            self.move_opts[move_serial] = opts
            self.tracked_moves[move_serial] = proc
            self.force_color[move_serial] = color
            self.exclude_out_moves()

if __name__ == '__main__':

