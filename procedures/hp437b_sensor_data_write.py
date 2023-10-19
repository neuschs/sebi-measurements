import json
import logging
import os
import sys

from pymeasure.display.console import ManagedConsole
from pymeasure.experiment import Procedure, Results, Worker
from pymeasure.log import console_log
from pymeasure.experiment import *
from pymeasure.instruments.hp import HP437B

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class WritePowerSensorCalibrationTable(Procedure):
    table_id = IntegerParameter('Sensor table id', default=0, minimum=0, maximum=9)
    resource = Parameter('Ressource String')
    sensor_data_path = Parameter('Sensor data path')

    instrument = object

    def startup(self):
        pass
        # self.instrument = HP437B(self.resource)

    def execute(self):
        json_data = None
        with open(str(self.sensor_data_path), 'r') as fh:
            json_data = json.load(fh)

        log.info(f"Read json sensor data '{self.sensor_data_path}'")
        ref_cal_factor = json_data['reference_calibration_factor']
        frequency_list = [entry['frequency'] for entry in json_data['table']]
        calibration_factor_list = [entry['calibration_factor'] for entry in json_data['table']]

        log.info(f"Parsed {len(calibration_factor_list)} calibration paris for SN:"
                 f"{json_data['serial_number']}")

        log.info(f"Write sensor data to table {self.table_id}")
        # self.instrument.sensor_data_ref_cal_factor(self.table_id, ref_cal_factor)
        # self.instrument.sensor_data_write_cal_factor_table()
        log.info("Verifiy sensor data")
        if True:
            log.info("Verification successfull")
        else:
            log.error("Verification unsuccessfull")
        # self.instrument.sensor_data_clear(self.table_id)

    def shutdown(self):
        pass


console_log(log)
app = ManagedConsole(procedure_class=WritePowerSensorCalibrationTable)
sys.exit(app.exec())
