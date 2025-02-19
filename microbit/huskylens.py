# For Huskylens (PRO inclusive) with Firmware version 0.5.1Norm or 0.5.3Alpha1.
from microbit import i2c, sleep, running_time
import math

_algorithm_names = ["FaceRecognition", 
                    "ObjectTracking", 
                    "ObjectRecognition", 
                    "LineTracking", 
                    "ColorRecognition", 
                    "TagRecognition", 
                    "ObjectClassification",
                    "QRRecognition",
                    "BarcodeRecognition"]

class Request_Command:
    # """Command Codes that can be sent to the Huskylens.""""
    KNOCK = 0x2C
    ALGORITHM = 0x2D
    ALL = 0x20
    BLOCKS = 0x21
    BLOCKS_LEARNED = 0x24
    BLOCKS_OF_ID = 0x27
    ARROWS = 0x22
    ARROWS_LEARNED = 0x25
    ARROWS_OF_ID = 0x28
    LEARNED = 0x23
    ALL_OF_ID = 0x26
    LEARN = 0x36
    FORGET = 0x37
    CUSTOM_LABEL = 0x2F
    CUSTOM_TEXT = 0x34
    CLEAR_TEXT = 0x35
    SAVE_MODEL = 0x32
    LOAD_MODEL = 0x33
    SAVE_PHOTO = 0x30
    SAVE_SCREENSHOT = 0x39
    IS_PRO = 0x3B
    VERSION = 0x3C

class Return_Code:
    # """Return codes that identify answer types, received from the Huskylens."""
    ANY = 0x01 # custom command for "don't care", never returned by Huskylens
    OK = 0x2E
    BUSY = 0x3D
    INFO = 0x29
    BLOCK = 0x2A
    ARROW = 0x2B
    IS_PRO = 0x3B
    NEED_PRO = 0x3E

class Algorithm:
    FACE_RECOGNITION = 0
    OBJECT_TRACKING = 1
    OBJECT_RECOGNITION = 2
    LINE_TRACKING = 3
    COLOR_RECOGNITION = 4
    TAG_RECOGNITION = 5
    OBJECT_CLASSIFICATION = 6
    QR_RECOGNITION = 7
    BARCODE_RECOGNITION = 8

class Block:
    # """Create a new Block with (x,y) as its center and (width,height) as its extent. Id is learned id on Huskylens.
    # Blocks are returned by all Algorithms except for Line_Recognition. """
    def __init__(self, x, y, width, height, id):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.id = id
    
    def __str__(self):
        return "Block: ID_" + str(self.id) + " Pos: (" + str(self.x) + " " + str(self.y) + ") Size: (" + str(self.width) + " " + str(self.height) + ")"
  
class Arrow:
    # """Create a new Arrow from (x,y)_tail to (x,y)_head. Id is learned id on Huskylens.
    # Arrows are returned only for the Line Recognition Algorithm. """
    def __init__(self, x_tail, y_tail, x_head, y_head, id):
        self.x_tail = x_tail
        self.y_tail = y_tail
        self.x_head = x_head
        self.y_head = y_head
        self.id = id
    
    def get_direction(self):
        dx = self.x_head - self.x_tail
        dy = self.y_head - self.y_tail
        deg = 90 - math.degrees(math.atan2(dy, dx))
        if deg < 0: deg = deg + 360
        return int(deg)

    def __str__(self):
        return "Arrow: ID_" + str(self.id) + " (" + str(self.x_tail) + " " + str(self.y_tail) + ")->(" + str(self.x_head) + " " + str(self.y_head) + ")" 

def byte_checksum(byte_list):
    # """Computes the checksum and returns the low byte of the sum."""
    return sum(byte_list) & 0xFF

def hexify(byte_array):
    # """Takes arraylike of bytes and converts it to hex string for pretty-printing."""
    if len(byte_array) == 0: return ""
    return "0x" + "".join("{:02x}".format(i) for i in byte_array)

class Huskylens:

    I2C_ADDR = 0x32

    def __init__(self):
        # """Create a new Huskylens instance.
        # 
        # A Huskylens instance is necessary for further communication.
        # 
        # The Huskylens has its own internal state that can't be known by this instance if 
        # a Huskylens is operated manually or has data stored in advance (names, learned id's).
        # """
        self.learned_slot_count = 0
        self.id_slots = {} # id to learning-slots.
        self.id_names = {} # id to string
        self.algorithm = Algorithm.OBJECT_TRACKING
        self.clear_texts()
        self.pro_enabled = self.is_pro()

    def initialize(self):
        # """Establishes Connection to Huskylens. Then clears custom Texts and activates Algorithm Object Tracking.
        
        #     First, knocks at most 5 times to setup connection.
        #     If successful, clears custom text and changes Algorithm to OBJECT_TRACKING.
        #     Learned ids and labels are kept from previous uses if available.
        #     
        #     Returns:
        #         bool: Wheter initialization was successfull.
        # """
        success = False
        for i in range(5):
            self.knock()
            success, _ = self.get_response(Return_Code.OK)
            if success:
                break
        
        if success > 0:
            s = self.clear_texts()
            s2 = self.set_algorithm(Algorithm.OBJECT_TRACKING)
            if s and s2:
                print("Initialization successful!")
                return True
            else:
                print("Initialization Failed. Couldn't change Algorithm")
                return False
        else:
            print("Initialization Failed. Please check connection to Huskylens.")
            return False

    # Low Level communication commands (deal with byte-data yourself)

    def send_request(self, command, data=None):
        # """Request an action from the Huskylens through a command code and optional Data Bytes.
        # 
        #     Parameters:
        #         command (byte): a Request_Command byte to be sent.
        #         data (list of bytes | None): Optional data to attach to the request or None.
        # """
        buffer = bytearray(b'\x55\xAA\x11\x00\x00')
        buffer[3] = 0 if data is None else len(data)
        buffer[4] = command
        if data:
            for b in data:
                buffer.append(b)
        buffer.append(byte_checksum(buffer))
        # print("request:", hexify(buffer))
        i2c.write(Huskylens.I2C_ADDR, buffer)
        sleep(50)

    def get_response(self, return_code=Return_Code.ANY, timeout=500):
        # """Read a response from I2C. Returns after a timeout when no data available.
        #     If a specific return code is expected and given as a parameter, all other results will set the returned code to 0.
        #     If a timeout occured, the return code is set to -1. Other errors return -2.
        #     This way, the return code is positive upon success, and negative or 0 otherwise.
        # 
        #     Parameters:
        #         return_code (byte): Optional expected return code.
        #         timeout (int): milliseconds to wait for response before giving up
        #     
        #     Returns:
        #         (code | error, data list): A tuple containing the return code or the error code as a signed byte in the first part
        #                               The data as a list of bytes in the second argument or an empty list if nothing was sent along.  
        # """
        response_header = bytearray(b"\x55\0\0\0\0")
        start_time = running_time()

        # bytewise polling, as there seem to be unpredictable 0 bytes between messages!
        #response_header = i2c.read(Huskylens.I2C_ADDR, 5, True)
        while running_time() - start_time < timeout:
            byte = i2c.read(Huskylens.I2C_ADDR, 1)[0]
            if byte == 0x55:
                break
        if byte != 0x55:
            return -1, [] # Timeout error 
        
        # reading rest of header data
        for i in range(4):
            response_header[i+1] = i2c.read(Huskylens.I2C_ADDR, 1)[0]

        if response_header[0:3] != b'\x55\xAA\x11':
            return -2, [] # Wrong header structure error
        
        data_length = response_header[3]
        response_type = response_header[4]
        
        data = []
        if data_length > 0:
            response_body = i2c.read(Huskylens.I2C_ADDR, data_length+1)
            data = response_body[0:-1]
            response_checksum = response_body[-1]
        else:
            response_checksum = ord(i2c.read(Huskylens.I2C_ADDR, 1))
        if response_checksum != byte_checksum(list(response_header) + data):
            return -3, [] # Checksum Error
        
        # print("response: " + hexify([response_type]) + " " + hexify(data))
        if return_code == Return_Code.ANY or response_type == return_code:
            return response_type, data
        else:
            return 0, data # not expected answer Hint

    def knock(self):
        self.send_request(Request_Command.KNOCK)

    # High level commands for students

    def set_algorithm(self, algorithm):
        # """ Change the active algorithm on the Huskylens. Returns True on success."""
        if (algorithm == Algorithm.QR_RECOGNITION or algorithm == Algorithm.BARCODE_RECOGNITION) and (not self.pro_enabled):
            raise RuntimeError("Error: Huskylens PRO version is required for algorithm ", _algorithm_names[algorithm])
            return False
        data = [algorithm, 0x00]
        self.send_request(Request_Command.ALGORITHM, data)
        success, _ = self.get_response(Return_Code.OK)
        if success > 0:
            print("Current Algorithm:", _algorithm_names[algorithm])
            self.algorithm = algorithm
        return True if success > 0 else False

    def get_all(self):
        # """Get All detected objects, Blocks or Arrows as a list."""
        return self._get_results(Request_Command.ALL)

    def get_all_learned(self):
        # """Get all detected objects that are learned as a list."""
        return self._get_results(Request_Command.LEARNED)

    def get_all_with_id(self, id):
        # """Get all detected objects with specific id as a list."""
        if id <= 0 or id > 255:
            raise RuntimeError("Error: ID must be in range from 1 to 255.")
        return self._get_results(Request_Command.ALL_OF_ID, id)

    def get_one(self):
        # """Get one instance of centermost detected object (Block or Arrow) else None."""
        results = self._get_results(Request_Command.ALL)
        return self._get_centermost(results) 

    def get_one_learned(self):
        # """Get one instance of centermost detected object that has an id > 0. else None."""
        results = self._get_results(Request_Command.LEARNED)
        return self._get_centermost(results)

    def get_one_with_id(self, id):
        # """Get one instance of centermost detected object that has given id. else None."""
        if id <= 0 or id > 255:
            raise RuntimeError("Error: ID must be in range from 1 to 255.")
        results = self._get_results(Request_Command.ALL_OF_ID, id)
        return self._get_centermost(results)

    def attach_label(self, id, name):
        # """Attach the label "name" to a learned id of current Algorithm. Returns True on success."""
        if self.algorithm == Algorithm.OBJECT_TRACKING or \
           self.algorithm == Algorithm.LINE_TRACKING: # single learn algorithms
            success = self._set_name(1, name)
        elif self.algorithm == Algorithm.FACE_RECOGNITION or \
             self.algorithm == Algorithm.TAG_RECOGNITION or \
             self.algorithm == Algorithm.OBJECT_CLASSIFICATION or \
             self.algorithm == Algorithm.OBJECT_RECOGNITION: # multi learn algorithms
            # avoid naming unlearned id's to avert bugs.
            slots = self.id_slots.get(id)
            if slots == None:
                raise RuntimeError("Can't attach a name to an unlearned ID number")

            self.id_names[id] = name

            success = True
            for slot in slots:
                s = self._set_name(slot, name)
                success = success and s > 0
        else: # For color recognition (where it works properly!)
            self.id_names[id] = name
            success = self._set_name(id, name)
        return True if success > 0 else False

    def clear_labels(self):
        # """Deletes all learned label names on Huskylens for the current algorithm."""
        self.id_names.clear()
        for i in range(10):
            self._set_name(i, "")

    def add_text(self, text, position_x, position_y):
        # """Add a custom text to the Huskylens screen at a certain screen pixel-position (top left starting point). 
        # Text must be less than 20 bytes long and within pixel-borders. 
        # Multiple texts at the same location get overwritten. Returns True on success."""
        text_bytes = bytes(text, "utf-8")
        if len(text_bytes) > 19:
            raise RuntimeError("Custom Text must be less than 20 bytes long.")
        if position_x > 300 or position_x < 0 or position_y < 35 or position_y > 240:
            raise RuntimeError("Custom Text can't be placed outside of screen pixel size.")
        data = [len(text_bytes)]
        data.append(0xFF if position_x > 255 else 0x00)
        data.append(position_x % 255)
        data.append(240 - position_y) # reverse flipped y axis
        data.extend(list(text_bytes))
        self.send_request(Request_Command.CUSTOM_TEXT, data)
        success, _ = self.get_response(Return_Code.OK)
        return True if success > 0 else False
        
    def clear_texts(self):
        # """Deletes all text on the Huskylens screen."""
        self.send_request(Request_Command.CLEAR_TEXT)
        success, _ = self.get_response(Return_Code.OK)
        return True if success > 0 else False

    def learn(self, id, name=None):
        # """Learn and assign an id to the object currently centered on the huskylens camera. 
        # Optionally attach label to this learned id. Returns True on success."""
        if id <= 0 or id > 255:
            raise RuntimeError("Parameter ID for learned item must be in range [0,255]")
        if self.algorithm == Algorithm.OBJECT_TRACKING or self.algorithm == Algorithm.LINE_TRACKING:
            id = 1
        timeout = 500
        if self.algorithm == Algorithm.OBJECT_CLASSIFICATION:
            timeout = 1000
        self.send_request(Request_Command.LEARN, [id, 0x00])
        success, _ = self.get_response(Return_Code.OK, timeout)
        if success > 0:
            # 1. remember slot for id
            self.learned_slot_count += 1
            if (not (id in self.id_slots)):
                self.id_slots[id] = [self.learned_slot_count]
            else:
                self.id_slots[id].append(self.learned_slot_count)
            # 2. attach, name if available.
            known_by = self.id_names.get(id)
            if known_by != None:
                success = self.attach_label(self.learned_slot_count, known_by)
            elif name != None:
                success = self.attach_label(id, name)
        return True if success > 0 else False
    
    def forget(self):
        # """Forget all learned objects (ids) of the current algorithm. 
        # Labels are unaffected. Returns True on success."""
        self.send_request(Request_Command.FORGET)
        success, _ = self.get_response(Return_Code.OK)
        if success:
            self.learned_slot_count = 0
            self.id_slots.clear()
        return True if success else False
    

    def save_photo(self):
        # """Save a photo to the SD-Card. No Feedback, fails on Huskylens screen if no SD-Card is available."""
        self.send_request(Request_Command.SAVE_PHOTO)
        success, _ = self.get_response(Return_Code.OK, 1000)
        return True if success > 0 else False

    def save_screenshot(self):
        # """Save a screenshot (including texts) to the SD-Card. No Feedback, fails on Huskylens screen if no SD-Card is available."""
        self.send_request(Request_Command.SAVE_SCREENSHOT)
        success, _ = self.get_response(Return_Code.OK, 1000)
        return True if success > 0 else False

    def save_model(self, model_id):
        # """Save the learned ids and labels to the SD-Card. No Feedback, see Huskylens screen for Result.
        # There can be at most 5 models per Algorithm, indexed by model_id."""
        if model_id < 0 or model_id > 4:
            raise RuntimeError("Invalid model_id. Must be number in range [0,4]")
        self.send_request(Request_Command.SAVE_MODEL, [model_id, 0x00])
        success, _ = self.get_response(Return_Code.OK, 1000)
        print("Model saving: Check Huskylens screen for Result!\n\tModel name:", _algorithm_names[self.algorithm] + "_Backup_" + str(model_id) + ".conf")
        return True if success > 0 else False

    def load_model(self, model_id):
        # """Load a previously saved model for the active Algorithm from the SD-Card. No Feedback, see Huskylens screen for Result."""
        if model_id < 0 or model_id > 4:
            raise RuntimeError("Invalid model_id. Must be number in range [0,4]")
        self.send_request(Request_Command.LOAD_MODEL, [model_id, 0x00])
        success, _ = self.get_response(Return_Code.OK, 1000)
        print("Model Loading: Check Huskylens screen for Result!")
        return True if success > 0 else False

    def is_pro(self):
        # """Checks wheter the Huskylens is the PRO version, which supports QR_RECOGNITION and BARCODE_RECOGNITION.
        # Returns True/False on success, else 0."""
        self.send_request(Request_Command.IS_PRO)
        success, data = self.get_response(Return_Code.IS_PRO)
        return bool(data[0]) if success > 0 else False

    # hidden Utility functions

    def _set_name(self, id, name):
        # """Set the name of block "id" to the given "name". Name must be less than 20 characters long."""
        name_bytes = bytes(name, "utf-8")
        if len(name_bytes) > 19: raise RuntimeError("Custom Name must be less than 20 bytes long.")
        data = [id, len(name_bytes)+1]
        data.extend(list(name_bytes))
        data.append(0x00)
        self.send_request(Request_Command.CUSTOM_LABEL, data)
        success, _ = self.get_response(Return_Code.OK)
        return True if success > 0 else False

    def _get_results(self, request_command, id=-1):
        # """Get all detected Blocks or Arrows from the Huskylens, specified by the request and id.
        # Possible Requests: BLOCKS, BLOCKS_LEARNED, BLOCKS_OF_ID, ARROWS, ...
        # Returns a list of all the detected Block or Arrow instances.
        # """
        request_data = None if id < 0 else [id, 0]
        self.send_request(request_command, request_data)

        # 1. get info header
        success, info = self.get_response(Return_Code.INFO)
        if not success:
            raise RuntimeError("Failed to request results. Got answer:" + str(success))
        
        # Ignoring number of detected id's and current frame number.
        n_elements = info[0] + info[1]*255
        #n_ids = info[2] + info[3]*255
        # frame = info[4] + info[5]*255
        #print("result info:", n_elements, n_ids, frame)

        # 2. receive data
        el = 0
        objects = []

        while el < n_elements:
            response_type, el_data = self.get_response(Return_Code.ANY)
            if response_type == Return_Code.BLOCK and self.algorithm != 3:
                x = el_data[0] + el_data[1]*255
                y = 240 - el_data[2] + el_data[3]*255 # flipped y axis
                width = el_data[4] + el_data[5]*255
                height = el_data[6] + el_data[7]*255
                el_id = el_data[8]
                block = Block(x, y, width, height, el_id)
                objects.append(block)
                el += 1
            
            elif response_type == Return_Code.ARROW:
                xtail = el_data[0] + el_data[1]*255
                ytail = 240 - el_data[2] + el_data[3]*255 # flipped y axis
                xhead = el_data[4] + el_data[5]*255
                yhead = 240 - el_data[6] + el_data[7]*255 # flipped y axis
                el_id = el_data[8]
                arrow = Arrow(xtail,ytail,xhead,yhead,el_id)
                objects.append(arrow)
                el += 1
            elif response_type == 0:
                return [] # Error (couldn't read all detected elements) fail silently.
        return objects

    def _get_centermost(self, results):
        # """Select and Return the most centered (L1-distance) instance of all detected Objects in "results". """
        centermost = None
        max_offset = 320+120
        for obj in results:
            center_offset = 0
            if self.algorithm == Algorithm.LINE_TRACKING:
                center_offset = abs((obj.x_tail + (obj.x_tail - obj.x_head) // 2) - 160) \
                                + abs((obj.y_tail + (obj.y_tail - obj.y_head) // 2) - 120)
            else:
                center_offset = abs(obj.x - 160) + abs(obj.y - 120)
            if center_offset < max_offset:
                centermost, max_offset = obj, center_offset
        return centermost 
