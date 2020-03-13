

from maxcube.device import MaxDevice
from maxcube.device import MAX_ROOM


class MaxRoom(MaxDevice):
    def __init__(self):
        super(MaxRoom, self).__init__()
        self.id = None
        self.room_id = None
        self.name = None
        self.rf_address = None
        self.type = MAX_ROOM
        self.comfort_temperature = None
        self.eco_temperature = None
        self.max_temperature = None
        self.min_temperature = None
        self.actual_temperature = None
        self.target_temperature = None
        self.mode = None
        self.typestring = "room"
