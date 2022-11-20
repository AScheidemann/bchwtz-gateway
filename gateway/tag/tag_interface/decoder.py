from ast import Bytes
from binascii import hexlify # built-in
import logging
import time
from xmlrpc.client import DateTime
from attr import dataclass
from bleak.backends.scanner import AdvertisementData
from ruuvitag_sensor.decoder import Df3Decoder, get_decoder
from gateway.sensor.acceleration import AccelerationSensor
from copy import copy
import crcmod

from gateway.tag.tagconfig import TagConfig

logger = logging.getLogger("Decoder")
logger.setLevel(logging.WARNING)
class Decoder():
    def __init__(self) -> None:
        self.resolution = 0


    def __process_data_8(self, bytes, scale, rate):
        """Parse acceleration data with an resolution of 8 Bit.
        :param bytes: Samples from bytearray
        :type bytes: bytes
        :param scale: Sensor specific scale
        :type scale: int
        :param rate: Sensor specific sampling rate.
        :type rate: int
        :return: x_vector, y_vector, z_vector, timestamp_list
        :rtype: list
        """
        j = 0
        pos = 0
        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate
        if (scale == 2):
            # logger.info("Scale: 2G")
            factor = 16 / (256 * 1000)
        elif (scale == 4):
            # logger.info("Scale: 4G")
            factor = 32 / (256 * 1000)
        elif (scale == 8):
            # logger.info("Scale: 8G")
            factor = 64 / (256 * 1000)
        elif (scale == 16):
            # logger.info("Scale: 16G")
            factor = 192 / (256 * 1000)
        while (pos < len(bytes)):
            """Read and store timestamp. This is little endian again"""
            t = bytes[pos:pos + 8]
            inv_t = t[::-1]
            timestamp = int(hexlify(inv_t), 16) / 1000
            pos += 8
            """Read values"""
            for i in range(96):
                value = bytes[pos] << 8
                pos += 1
                if (value & 0x8000 == 0x8000):
                    # negative number
                    # calculate 16Bit pair complement
                    value = value ^ 0xffff
                    value += 1
                    # negate
                    value = -value
                value *= factor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    z_vector.append(value)
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                j += 1
        return x_vector, y_vector, z_vector, timestamp_list


    def __process_data_10(self, bytes, scale, rate):
        """Parse acceleration data with an resolution of 10 Bit.
        :param bytes: Samples from bytearray
        :type bytes: bytes
        :param scale: Sensor specific scale
        :type scale: int
        :param rate: Sensor specific sampling rate.
        :type rate: int
        :return: x_vector, y_vector, z_vector, timestamp_list
        :rtype: list
        """
        j = 0
        pos = 0
        koords = ["\nx", "y", "z"]
        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate
        if (scale == 2):
            factor = 4 / (64 * 1000)
        elif (scale == 4):
            factor = 8 / (64 * 1000)
        elif (scale == 8):
            factor = 16 / (64 * 1000)
        elif (scale == 16):
            factor = 48 / (64 * 1000)
        while (pos < len(bytes)):
            t = bytes[pos:pos + 8]
            inv_t = t[::-1]
            timestamp = int(hexlify(inv_t), 16) / 1000
            pos += 8
            for i in range(24):
                value = bytes[pos] & 0xc0
                value |= (bytes[pos] & 0x3f) << 10
                pos += 1
                value |= (bytes[pos] & 0xc0) << 2
                if (value & 0x8000 == 0x8000):
                    # negative number
                    # calculate calculate 16Bit pair complement
                    value = value ^ 0xffff
                    value += 1
                    # negate
                    value = -value
                value *= factor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                j += 1
                value = (bytes[pos] & 0x30) << 2
                value |= (bytes[pos] & 0x0f) << 12
                pos += 1
                value |= (bytes[pos] & 0xf0) << 4
                if (value & 0x8000 == 0x8000):
                    # negative number
                    # calculate calculate 16Bit pair complement
                    value = value ^ 0xffff
                    value += 1
                    # negate
                    value = -value
                value *= factor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                j += 1
                value = (bytes[pos] & 0x0c) << 4
                value |= (bytes[pos] & 0x03) << 14
                pos += 1
                value |= (bytes[pos] & 0xfc) << 6
                if (value & 0x8000 == 0x8000):
                    # negative number
                    # calculate 16Bit pair complement
                    value = value ^ 0xffff
                    value += 1
                    # negate
                    value = -value
                value *= factor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                j += 1
                value = (bytes[pos] & 0x03) << 6
                pos += 1
                value |= (bytes[pos]) << 8
                pos += 1
                if (value & 0x8000 == 0x8000):
                    # negative number
                    # calculate 16Bit pair complement
                    value = value ^ 0xffff
                    value += 1
                    # negate
                    value = -value
                value *= factor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                j += 1
        return x_vector, y_vector, z_vector, timestamp_list


    def __process_data_12(self, bytes, scale, rate):
        """Parse acceleration data with an resolution of 12 Bit.
        :param bytes: Samples from bytearray
        :type bytes: bytes
        :param scale: Sensor specific scale
        :type scale: int
        :param rate: Sensor specific sampling rate.
        :type rate: int
        :return: x_vector, y_vector, z_vector, timestamp_list
        :rtype: list
        """
        j = 0
        pos = 0
        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate
        if (scale == 2):
            # logger.info("Scale: 2G")
            factor = 1 / (16 * 1000)
        elif (scale == 4):
            # logger.info("Scale: 4G")
            factor = 2 / (16 * 1000)
        elif (scale == 8):
            # logger.info("Scale: 8G")
            factor = 4 / (16 * 1000)
        elif (scale == 16):
            # logger.info("Scale: 16G")
            factor = 12 / (16 * 1000)
        while (pos < len(bytes)):
            t = bytes[pos:pos + 8]
            inv_t = t[::-1]
            timestamp = int(hexlify(inv_t), 16) / 1000
            pos += 8
            for i in range(48):
                value = bytes[pos] & 0xf0
                value |= (bytes[pos] & 0x0f) << 12
                pos += 1
                value |= (bytes[pos] & 0xf0) << 4
                if (value & 0x8000 == 0x8000):
                    # negative number
                    # calculate calculate 16Bit pair complement
                    value = value ^ 0xffff
                    value += 1
                    # negate
                    value = -value
                value *= factor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                j += 1
                value = (bytes[pos] & 0x0f) << 4
                pos += 1
                value |= bytes[pos] << 8
                pos += 1
                if (value & 0x8000 == 0x8000):
                    # negative number
                    # calculate calculate 16Bit pair complement
                    value = value ^ 0xffff
                    value += 1
                    # negate
                    value = -value
                value *= factor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                j += 1
        return x_vector, y_vector, z_vector, timestamp_list



    def __unpack8(self, bytes, samplingrate, scale) -> list:
        """unpacks the 8 byte sequences of the sensor to hex-strings
        :param bytes: the bytes from your sensor
        :type bytes: bytes
        :param samplingrate: current samplingrate of the sensor
        :type samplingrate: int
        :param scale: current scale of the sensor
        :type scale: int
        """
        j = 0
        pos = 0
        # res = []
        measurements: list[AccelerationSensor.AccelerationMeasurement] = []
        accvalues = [0, 0, 0]
        timestamp = 0
        timeBetweenSamples = 1000/samplingrate
        if(scale == 2):
            factor = 16/(256*1000)
        elif(scale == 4):
            factor = 32/(256*1000)
        elif(scale == 8):
            factor = 64/(256*1000)
        elif(scale == 16):
            factor = 192/(256*1000)
        while(pos < len(bytes)):
            # Ein Datenblock bei 8 Bit Auflösung ist 104 Bytes lang
            # Jeder Datenblock beginnt mit einem Zeitstempel
            if pos % 104 == 0:
                timestamp = int.from_bytes(
                    bytes[pos:pos+7], byteorder='little', signed=False)
                pos += 8
                j = 0
            value = bytes[pos] << 8
            pos += 1
            if(value & 0x8000 == 0x8000):
                # negative number
                # calculate 16Bit pair complement
                value = value ^ 0xffff
                value += 1
                # negate
                value = -value
            # save value
            accvalues[j] = value * factor
            # Write to CSV
            if(j % 3 == 2):
                timestamp += timeBetweenSamples
                j = 0
                # res.append(f"{timestamp, accvalues[0], accvalues[1], accvalues[2]}")
                measurements.append(AccelerationSensor.AccelerationMeasurement(acc_x = accvalues[0], acc_y = accvalues[1], acc_z = accvalues[2], recorded_time = timestamp, gathering_type = "logging_data"))
            else:
                j += 1
        return measurements



    def __unpack10(self, bytes, samplingrate, scale) -> list:
        """unpacks the 10 byte sequences of the sensor to hex-strings
        :param bytes: the bytes from your sensor
        :type bytes: bytes
        :param samplingrate: current samplingrate of the sensor
        :type samplingrate: int
        :param scale: current scale of the sensor
        :type scale: int
        """
        i = 0
        j = 0
        pos = 0
        accvalues = [0, 0, 0]
        timestamp = 0
        timeBetweenSamples = 1000/samplingrate
        measurements: list[AccelerationSensor.AccelerationMeasurement] = []
        if(scale == 2):
            factor = 4/(64*1000)
        elif(scale == 4):
            factor = 8/(64*1000)
        elif(scale == 8):
            factor = 16/(64*1000)
        elif(scale == 16):
            factor = 48/(64*1000)
        while(pos < len(bytes)-1):
            # Ein Datenblock bei 10 Bit Auflösung ist 128 Bytes lang
            # Jeder Datenblock beginnt mit einem Zeitstempel
            if pos % 128 == 0:
                timestamp = int.from_bytes(
                    bytes[pos:pos+7], byteorder='little', signed=False)
                pos += 8
                i = 0
                j = 0
            else:
                if i == 0:
                    value = bytes[pos] & 0xc0
                    value |= (bytes[pos] & 0x3f) << 10
                    pos += 1
                    value |= (bytes[pos] & 0xc0) << 2
                    i += 1
                elif i == 1:
                    value = (bytes[pos] & 0x30) << 2
                    value |= (bytes[pos] & 0x0f) << 12
                    pos += 1
                    value |= (bytes[pos] & 0xf0) << 4
                    i += 1
                elif i == 2:
                    value = (bytes[pos] & 0x0c) << 4
                    value |= (bytes[pos] & 0x03) << 14
                    pos += 1
                    value |= (bytes[pos] & 0xfc) << 6
                    i += 1
                elif i == 3:
                    value = (bytes[pos] & 0x03) << 6
                    pos += 1
                    value |= (bytes[pos]) << 8
                    pos += 1
                    i = 0
                if(value & 0x8000 == 0x8000):
                    # negative number
                    # calculate 16Bit pair complement
                    value = value ^ 0xffff
                    value += 1
                    # negate
                    value = -value
                # save value
                accvalues[j] = value * factor
                j += 1
                # Write to CSV
                if(j == 3):

                    timestamp += timeBetweenSamples
                    j = 0
                    measurements.append(AccelerationSensor.AccelerationMeasurement(acc_x = accvalues[0], acc_y = accvalues[1], acc_z = accvalues[2], recorded_time = timestamp, gathering_type = "logging_data"))

        return measurements

    def __unpack12(self, bytes, samplingrate, scale) -> list:
        """unpacks the 12 byte sequences of the sensor to hex-strings
        :param bytes: the bytes from your sensor
        :type bytes: bytes
        :param samplingrate: current samplingrate of the sensor
        :type samplingrate: int
        :param scale: current scale of the sensor
        :type scale: int
        """
        i = 0
        j = 0
        pos = 0
        accvalues = [0, 0, 0]
        timestamp = 0
        timeBetweenSamples = 1000/samplingrate
        measurements: list[AccelerationSensor.AccelerationMeasurement] = []
        logger.warn("scale: %d" % scale)
        if(scale == 2):
            factor = 1/(16*1000)
        elif(scale == 4):
            factor = 2/(16*1000)
        elif(scale == 8):
            factor = 4/(16*1000)
        elif(scale == 16):
            factor = 12/(16*1000)
        while(pos < len(bytes)-1):
            # Ein Datenblock bei 12 Bit Auflösung ist 152 Bytes lang
            # Jeder Datenblock beginnt mit einem Zeitstempel
            if pos % 152 == 0:
                timestamp = int.from_bytes(
                    bytes[pos:pos+7], byteorder='little', signed=False)
                pos += 8
                i = 0
                j = 0
            else:
                if i == 0:
                    value = bytes[pos] & 0xf0
                    value |= (bytes[pos] & 0x0f) << 12
                    pos += 1
                    value |= (bytes[pos] & 0xf0) << 4
                    i += 1
                elif i == 1:
                    value = (bytes[pos] & 0x0f) << 4
                    pos += 1
                    value |= bytes[pos] << 8
                    pos += 1
                    i = 0
                if(value & 0x8000 == 0x8000):
                    # negative number
                    # calculate 16Bit pair complement
                    value = value ^ 0xffff
                    value += 1
                    # negate
                    value = -value
                # save value
                accvalues[j] = value * factor
                j += 1
                # Write to CSV
                if(j == 3):
                    j = 0
                    measurements.append(AccelerationSensor.AccelerationMeasurement(acc_x = accvalues[0], acc_y = accvalues[1], acc_z = accvalues[2], recorded_time = timestamp, gathering_type = "logging_data"))

        return measurements

    def decode_data(self, bytearr: Bytes = None, resolution: int = 12, samplerate: int = 10, scale: float = 2):
        self.resolution = resolution
        if bytearr is None:
            logger.warning("no input data - returning None")
            return None
        if resolution == 8:
            return self.__process_data_8(bytearr, scale, samplerate)
        elif resolution == 10:
            return self.__process_data_10(bytearr, scale, samplerate)
        elif resolution == 12:
            return self.__process_data_12(bytearr, scale, samplerate)
        logger.warning(f"Did not find resolution: {resolution}")
        return None

    def decode_config_rx(self, bytearr: Bytes =  None) -> TagConfig:
        config = TagConfig()
        if len(bytearr) < 11:
            logger.error("invalid bytearr - resuming with empty config")
            return TagConfig()
        if bytearr[4] == 201:
            logger.info("Samplerate 400Hz")
            config.samplerate = 400
        else:
            config.samplerate = int(bytearr[4])
        logger.info(f"Samplerate {config.samplerate} Hz")
        config.resolution = int(bytearr[5])
        config.scale = int(bytearr[6])
        config.dsp_function = int(bytearr[7])
        config.dsp_parameter = int(bytearr[8])
        config.mode = "%x" % bytearr[9]
        config.divider = int(bytearr[10])
        return config

    def decode_time_rx(self, bytearr: Bytes =  None) -> float:
        logger.info("Received time: %s" % hexlify(bytearr[:-9:-1]))
        received_time = time.mktime(time.localtime(int(hexlify(bytearr[:-9:-1]), 16) / 1000))
        return received_time

    def decode_advertisement(self, advertisement_data: AdvertisementData) -> dict:
        data = advertisement_data.hex()
        return get_decoder(advertisement_data).decode_data(data)

    def decode_heartbeat_rx(self, bytearr: Bytes = None) -> int:
        heartbeat = int.from_bytes(bytearr[4:6], byteorder='big', signed=False)
        logger.info("Received heartbeat: %s" % heartbeat)
        return heartbeat

    def build_acc_log_crc(self, rx_bt: bytearray, acceleration_sensor: AccelerationSensor) -> None:
        datablock = rx_bt[1:]
        acceleration_sensor.crc.extend(datablock)
        # self.start_time = time.time()
        logger.info("Received data block: %s" % hexlify(datablock))

    def decode_acc_log_crc(self, rx_bt: bytearray, acceleration_sensor: AccelerationSensor) -> None:
        crc = rx_bt[12:14]
        # Redundancy check
        crcfn = crcmod.mkCrcFun(0x11021, rev=False, 
                                        initCrc=0xffff, xorOut=0)

        logger.warn(hexlify(acceleration_sensor.crc))
        # CRC validation
        crcdata = crcfn(acceleration_sensor.crc)

        logger.info("Status: %s" % str(self.ri_error_to_string(rx_bt[3])))

        if hexlify(crc) == bytearray():
            logger.error("No crc received")
            return None

        if int(hexlify(crc), 16) != crcdata:
            logger.error("CRC are unequal: %s - %s" % (int(hexlify(crc), 16), crcdata))
            return None

        enc_mode = rx_bt[5]
        scale = rx_bt[6]
        rate = rx_bt[4]

        logger.warn("scale: %d" % rx_bt[6])
        # Start data
        # Timestamp hier wird genutzt um zu den acceleration daten die Zeit zu haben 
        # Timestamp wird vom Sensor nicht jede Nachricht mitgeschickt. 
        # Time für acceleration data ergibt sich aus letztem timestamp + sampling frequenz * anzahl samples seit letztem timestamp
        # Hier gibt noch Fehler, die beim Sensor liegen könnten -> Abweichungen zwischen Interpolierten Zeitstempel und geschickten nächsten TimeStamp
        if (enc_mode == 12):
            # 12 Bit
            logger.info("Start processing received data with process_sensor_data_12")
            data = self.__unpack12(acceleration_sensor.crc, rate, scale)
        elif (enc_mode == 10):
            # 10 Bit
            logger.info("Start processing received data with process_sensor_data_10")
            data = self.__unpack10(acceleration_sensor.crc, rate, scale)
        elif (enc_mode == 8):
            # 8 Bit
            logger.info("Start processing received data with process_sensor_data_8")
            data = self.__unpack8(acceleration_sensor.crc, rate, scale)
        else:
            logger.error('Cannot process bytearray! Unknwon sensor resolution!')
        if data != None:
            logger.info("got data:")
            logger.info(data)
            # dataList=message_return_value.from_get_accelorationdata(accelorationdata=AccelerationData,mac=self.mac)
            # self.data.append(dataList.return_value.__dict__)
            acceleration_sensor.measurements.extend(data)

        return

    def ri_error_to_string(self, error):
        """Decodes the Tag error, if it was raised.

        :param error: Error value in hex.
        :type error: byte
        :return: Result with decoded error code
        :rtype: set
        """
        result = set()
        if (error == 0):
            result.add("RD_SUCCESS")
        elif(error == 1):
            result.add("RD_ERROR_INTERNAL")
        elif(error == 2):
            result.add("RD_ERROR_NO_MEM")
        elif(error == 3):
            result.add("RD_ERROR_NOT_FOUND")
        elif(error == 4):
            result.add("RD_ERROR_NOT_SUPPORTED")
        elif(error == 5):
            result.add("RD_ERROR_INVALID_PARAM")
        elif(error == 6):
            result.add("RD_ERROR_INVALID_STATE")
        elif(error == 7):
            result.add("RD_ERROR_INVALID_LENGTH")
        elif(error == 8):
            result.add("RD_ERROR_INVALID_FLAGS")
        elif(error == 9):
            result.add("RD_ERROR_INVALID_DATA")
        elif(error == 10):
            result.add("RD_ERROR_DATA_SIZE")
        elif(error == 11):
            result.add("RD_ERROR_TIMEOUT")
        elif(error == 12):
            result.add("RD_ERROR_NULL")
        elif(error == 13):
            result.add("RD_ERROR_FORBIDDEN")
        elif(error == 14):
            result.add("RD_ERROR_INVALID_ADDR")
        elif(error == 15):
            result.add("RD_ERROR_BUSY")
        elif(error == 16):
            result.add("RD_ERROR_RESOURCES")
        elif(error == 17):
            result.add("RD_ERROR_NOT_IMPLEMENTED")
        elif(error == 18):
            result.add("RD_ERROR_SELFTEST")
        elif(error == 19):
            result.add("RD_STATUS_MORE_AVAILABLE")
        elif(error == 20):
            result.add("RD_ERROR_NOT_INITIALIZED")
        elif(error == 21):
            result.add("RD_ERROR_NOT_ACKNOWLEDGED")
        elif(error == 22):
            result.add("RD_ERROR_NOT_ENABLED")
        elif(error == 31):
            result.add("RD_ERROR_FATAL")
        return result