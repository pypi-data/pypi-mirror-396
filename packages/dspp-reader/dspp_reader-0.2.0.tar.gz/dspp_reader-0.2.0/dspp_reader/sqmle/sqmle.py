import astropy.units as u
import datetime
import os
import re
import socket
import logging
import sys

from astropy.units import Quantity
from pathlib import Path
from time import sleep
from zoneinfo import ZoneInfo

from dspp_reader.tools import Device, Site
from dspp_reader.tools.generics import augment_data, get_filename

logger = logging.getLogger()

READ = b'rx\r\n'
READ_WITH_SERIAL_NUMBER = b'Rx\r\n'
REQUEST_CALIBRATION_INFORMATION = b'cx\r\n'
UNIT_INFORMATION_REQUEST = b'ix\r\n'


class SQMLE(object):
    def __init__(self,
                 site_id: str = '',
                 site_name: str = '',
                 site_timezone: str = '',
                 site_latitude: str = '',
                 site_longitude: str = '',
                 site_elevation: str = '',
                 sun_altitude: float = -10,
                 device_type:str = 'sqm-le',
                 device_id:str = None,
                 device_altitude:float = None,
                 device_azimuth:float = None,
                 device_ip:str = None,
                 device_port=10001,
                 device_window_correction:float = 0,
                 number_of_reads=3,
                 reads_spacing=1,
                 reads_frequency=30,
                 read_all_the_time:bool = False,
                 save_to_file=True,
                 save_to_database=False,
                 post_to_api=False,
                 save_files_to: Path = os.getcwd(),
                 file_format: str = "tsv",):
        self.site_id = site_id
        self.site_name = site_name
        self.site_timezone = site_timezone
        self.site_latitude = site_latitude
        self.site_longitude = site_longitude
        self.site_elevation = site_elevation
        self.sun_altitude = sun_altitude
        self.device_type = device_type
        self.device_id = device_id
        self.device_port = device_port
        self.device_altitude = device_altitude
        self.device_azimuth = device_azimuth
        self.device_ip = device_ip
        self.device_window_correction = device_window_correction

        self.number_of_reads = number_of_reads
        self.reads_spacing = reads_spacing
        self.reads_frequency = reads_frequency
        self.read_all_the_time = read_all_the_time
        self.save_to_file = save_to_file
        self.save_to_database = save_to_database
        self.post_to_api = post_to_api
        self.save_files_to = Path(save_files_to)
        self.file_format = file_format
        self.separator = ''
        if self.file_format == "tsv":
            self.separator = "\t"
        elif self.file_format == "csv":
            self.separator = ","
        elif self.file_format == "txt":
            self.separator = " "
        else:
            self.separator = " "

        self.site = None
        if all([self.site_id, self.site_name, self.site_timezone, self.site_latitude, self.site_longitude, isinstance(float(self.site_elevation), float)]):
            self.site = Site(
                id=self.site_id,
                name=self.site_name,
                latitude=self.site_latitude,
                longitude=self.site_longitude,
                elevation=self.site_elevation,
                timezone=self.site_timezone)
        else:
            logger.error(f"Not enough site info provided: Please provide: site_id, site_name, site_timezone, site_latitude, site_longitude, site_elevation")

        self.device = None
        if all([self.device_type,
                self.device_id,
                self.device_port,
                isinstance(float(self.device_altitude), float),
                isinstance(float(self.device_azimuth), float),
                self.device_ip,
                self.device_port]):
            self.device = Device(
                serial_id=self.device_id,
                type=self.device_type,
                altitude=self.device_altitude,
                azimuth=self.device_azimuth,
                window_correction=self.device_window_correction,
                site=self.site,
                ip=self.device_ip,
                port=self.device_port,
            )
        else:
            logger.error("Not enough information to define device")

        self.socket = None
        if self.device:
            while not self.socket:
                try:
                    logger.debug(f"Creating socket connection for {self.device.type} {self.device.serial_id}")
                    self.socket = socket.create_connection((self.device.ip, self.device.port), timeout=5)
                    logger.info(f"Created socket connection for {self.device.type} {self.device.serial_id}")
                except OSError as e:
                    timeout = 20
                    print(
                        f"\r{datetime.datetime.now().astimezone()}: Unable to connect to {self.device.serial_id} at {self.device.ip}:{self.device.port}: {e}")
                    for i in range(1, timeout + 1, 1):
                        print(f"\rAttempting again in {timeout - i} seconds...", end="", flush=True)
                        sleep(1)
        else:
            logger.error(f"A device is needed to be able to continue")
            logger.info(f"Use the argument  --help for more information")
            sys.exit(1)

        if self.save_to_file:
            if not os.path.exists(self.save_files_to):
                try:
                    os.makedirs(self.save_files_to)
                    logger.info(f"Created directory {self.save_files_to}")
                except OSError:
                    logger.error(f"Could not create directory {self.save_files_to}")
                    sys.exit(1)
            logger.info(f"Data will be saved to {self.save_files_to}")

    def __call__(self):
        try:
            while True:
                if self.device and self.socket:
                    if self.device.site:
                        next_period_start, next_period_end, time_to_next_start, time_to_next_end = self.device.site.get_time_range(sun_altitude=self.sun_altitude)
                        if time_to_next_end > time_to_next_start and not self.read_all_the_time:
                            logger.debug(
                                f"Next Sunset is at {next_period_start.strftime('%Y-%m-%d %H:%M:%S %Z (UTC%z)')}")
                            hours = int(time_to_next_start.sec // 3600)
                            minutes = int((time_to_next_start.sec % 3600) // 60)
                            seconds = int(time_to_next_start.sec % 60)

                            try:
                                self._send_command(command=UNIT_INFORMATION_REQUEST, sock=self.socket)
                                message = f"Waiting for {hours:02d} hours {minutes:02d} minutes {seconds:02d} seconds until next sunset {next_period_start.to_datetime(timezone=ZoneInfo(self.device.site.timezone)).strftime('%Y-%m-%d %H:%M:%S')} {self.device.site.timezone} "
                                if logger.getEffectiveLevel() == logging.DEBUG:
                                    logger.debug(message)
                                else:
                                    print(f"\r{message}", end="", flush=True)
                            except OSError as e:
                                error_message = f"Socket error: {e}. The device may be unavailable."
                                if logger.getEffectiveLevel() == logging.DEBUG:
                                    logger.debug(error_message)
                                else:
                                    print(f"\033[2K\r{error_message}", end="", flush=True)

                            continue
                    else:
                        logger.warning(f"No device has been defined, this program will continue reading continuously.")

                    self.timestamp = datetime.datetime.now(datetime.UTC)
                    data = {}
                    measurements = []
                    try:
                        for read in range(1, self.number_of_reads + 1, 1):
                            logger.debug(f"Reading {read} of {self.number_of_reads}...")
                            data = self._send_command(command=READ_WITH_SERIAL_NUMBER, sock=self.socket)
                            logger.debug(f"Response: {data}")

                            parsed_data = self._parse_data(data=data, command=READ_WITH_SERIAL_NUMBER)

                            measurements.append(parsed_data)
                            if self.device.serial_id:
                                if self.device.serial_id != parsed_data['serial_number']:
                                    logger.warning(
                                        f"Serial number mismatch: {self.device.serial_id} != {parsed_data['serial_number']}")
                            sleep(self.reads_spacing)

                    except IndexError as e:
                        logger.error(f"Error parsing data: Key error: {e}", exc_info=logger.getEffectiveLevel() == logging.DEBUG)
                        sleep(self.reads_spacing)
                        continue
                    if len(measurements) == 0:
                        logger.warning(f"No data has been read, this program will continue.")
                        continue
                    if len(measurements) == 1:
                        data = measurements[0]
                    elif len(measurements) > 1:
                        raise NotImplementedError("Averaging data is not yet implemented. Use --number-of-reads 1")

                    corrected_data = self.__apply_window_correction(data=data)

                    augmented_data = augment_data(data=corrected_data, timestamp=self.timestamp, device=self.device)

                    if self.save_to_file:
                        self._write_to_txt(data=augmented_data)
                    if self.save_to_database:
                        self._write_to_database()
                    if self.post_to_api:
                        self._post_to_api()

                    last_datapoint = datetime.datetime.now(datetime.UTC)

                    for i in range(self.reads_frequency):
                        print(f"\rLast Datapoint recorded at {last_datapoint.strftime('%Y-%m-%d %H:%M:%S %Z')} or localtime {last_datapoint.astimezone(ZoneInfo(self.device.site.timezone)).strftime('%Y-%m-%d %H:%M:%S %Z')}. Next read in {self.reads_frequency - i} seconds...", end="", flush=True)
                        sleep(1)
                else:
                    if not self.device:
                        logger.error(f"A device is needed to be able to continue")
                    if not self.socket:
                        logger.error(f"It seems that the connection to the device is unavailable")
        except KeyboardInterrupt:
            logger.info("SQM-LE stopped by user")
        except ConnectionRefusedError:
            logger.info("SQM-LE connection refused")
        finally:
            if self.socket:
                self.socket.close()

    def _send_command(self, command, sock):
        sock.sendall(command)
        data = sock.recv(1024)
        return data.decode()

    def __apply_window_correction(self, data):
        data['magnitude'] = data['magnitude'] + self.device_window_correction * u.mag
        return data

    def _parse_data(self, data, command):
        data = data.split(',')
        if command == READ:
            return {
                'type': data[0],
                'magnitude' : float(re.sub('m', '', data[1])) * u.mag,
                'frequency' : float(re.sub('Hz', '', data[2])) * u.Hz,
                'period_count' : int(re.sub('c', '', data[3])) * u.count,
                'period_seconds' : float(re.sub('s', '', data[4])) * u.second,
                'temperature' : float(re.sub('C', '', data[5])) * u.C,
            }
        elif command == READ_WITH_SERIAL_NUMBER:
            return {
                'type': data[0],
                'magnitude' : float(re.sub('m', '', data[1])) * u.mag,
                'frequency' : float(re.sub('Hz', '', data[2])) * u.Hz,
                'period_count' : int(re.sub('c', '', data[3])) * u.count,
                'period_seconds' : float(re.sub('s', '', data[4])) * u.second,
                'temperature' : float(re.sub('C', '', data[5])) * u.C,
                'serial_number' : str(int(data[6])),
            }
        elif command == REQUEST_CALIBRATION_INFORMATION:
            return {
                'type': data[0],
                'magnitude_offset_calibration': float(data[1]),
                'dark_period': float(data[2]),
                'temperature_light_calibration': float(data[3]),
                'magnitude_offset_manufacturer': float(data[4]),
                'temperature_dark_calibration': float(data[5]),
            }
        elif command == UNIT_INFORMATION_REQUEST:
            return {
                'type': data[0],
                'protocol_number': data[1],
                'model_number': data[2],
                'feature_number': data[3],
                'serial_number': data[4],
            }
        else:
            logger.error(f"Unknown command: {command}")
            return data



    def __get_header(self, data, filename):
        columns = []
        units = []
        for key in data.keys():
            columns.append(key)
            if isinstance(data[key], Quantity):
                units.append(f"# {key}: {data[key].unit}\n")
        return f"# Filename {filename}\n{''.join(units)}# {self.separator.join(columns)}\n"

    def __get_line_for_plain_text(self, data):
        fields = []
        for key in data.keys():
            if isinstance(data[key], Quantity):
                fields.append(str(data[key].value))
            else:
                fields.append(str(data[key]))
        return f"{self.separator.join(fields)}\n"


    def _write_to_txt(self, data):
        filename = get_filename(
            save_files_to=self.save_files_to,
            device_name=self.device.serial_id,
            device_type='sqmle',
            file_format=self.file_format)
        if not os.path.exists(filename):
            header = self.__get_header(data=data, filename=filename)
            with open(filename, 'w') as f:
                f.write(header)
        data_line = self.__get_line_for_plain_text(data=data)
        with open(filename, "a") as f:
            f.write(data_line)
            logger.debug(f"Data written to {filename}")

    def _write_to_database(self):
        pass

    def _post_to_api(self):
        pass
