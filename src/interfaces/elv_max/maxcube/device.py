MAX_CUBE = 0
MAX_THERMOSTAT = 1
MAX_THERMOSTAT_PLUS = 2
MAX_WALL_THERMOSTAT = 3
MAX_WINDOW_SHUTTER = 4
MAX_PUSH_BUTTON = 5

MAX_DEVICE_MODE_AUTOMATIC = 0
MAX_DEVICE_MODE_MANUAL = 1
MAX_DEVICE_MODE_VACATION = 2
MAX_DEVICE_MODE_BOOST = 3
MAX_DEVICE_MODE_UNKNOWN = 10

MAX_DEVICE_BATTERY_OK = 0
MAX_DEVICE_BATTERY_LOW = 1

MAX_ROOM = 1000

modestrings = {MAX_DEVICE_MODE_AUTOMATIC:"automatic",
               MAX_DEVICE_MODE_MANUAL:"manual",
               MAX_DEVICE_MODE_VACATION:"Vacation",
               MAX_DEVICE_MODE_BOOST:"Boost",
               MAX_DEVICE_MODE_UNKNOWN:"Unknown"}


class MaxDevice:
    def __init__(self):
        self.type = None
        self.rf_address = None
        self.room_id = None
        self.name = None
        self.serial = None
        self.battery = None
        self.programme = None
        self.id = None
        self.typestring ="unknown"
        self.set_current_mode(MAX_DEVICE_MODE_UNKNOWN)
        self.mode = "unknown"
        self.current_mode = "unknown"

    def is_thermostat(self):
        return self.type in (MAX_THERMOSTAT, MAX_THERMOSTAT_PLUS)

    def is_wallthermostat(self):
        return self.type == MAX_WALL_THERMOSTAT

    def is_windowshutter(self):
        return self.type == MAX_WINDOW_SHUTTER

    def is_room(self):
        return self.type == MAX_ROOM

    def to_dict(self):
        data = {}
        keys = ['type', 'rf_address', 'room_id', 'name', 'serial', 'battery',
                'comfort_temperature', 'eco_temperature', 'max_temperature',
                'min_temperature', 'valve_position', 'target_temperature',
                'actual_temperature', 'mode', 'programme']
        for key in keys:
            data[key] = getattr(self, key, None)
        data['rf_address'] = self.rf_address
        return data
    def set_current_mode(self,mode):
        global modestrings
        self.mode=mode
        self.current_mode = modestrings.get(mode,"unknown")
