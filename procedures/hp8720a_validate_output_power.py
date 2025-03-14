import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import tempfile
import random
from time import sleep
from pymeasure.log import console_log
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from pymeasure.instruments.hp import HP437B
from pymeasure.adapters import VISAAdapter
import numpy as np

class MeasureVNAPower(Procedure):

    step = FloatParameter('Frequency Step', units='Hz', default=100e6, maximum=20e9)
    start_frequency = FloatParameter('Start Frequency', units='Hz', default=130e6, maximum=20e9)
    stop_frequency = FloatParameter('Stop Frequency', units='Hz', default=18e9, maximum=20e9)
    port = IntegerParameter('VNA Port', default=1)
    vna_power = FloatParameter('VNA Power', default=-10, units='dBm')
    attenuator = FloatParameter('Attenuator', default=0, units='dB')
    settling_time = FloatParameter('Power Sensor Settling Time', units='s', default=0.5)

    DATA_COLUMNS = ['Frequency', 'Power']

    power_meter = object
    vna = object
    def startup(self):
        self.power_meter = HP437B("GPIB0::30::INSTR")
        self.vna = VISAAdapter("GPIB0::16::INSTR")
        if self.port == 1:
            self.vna.write("S11")
        elif self.port == 2:
            self.vna.write("S22")
        self.vna.write("POWE %d" % self.vna_power)

    def execute(self):
        counter = 0
        frequencies = np.arange(self.start_frequency, self.stop_frequency, self.step)
        for frequency in frequencies:

            self.vna.write("CWFREQ %.2e" % frequency)
            self.power_meter.frequency = frequency
            sleep(self.settling_time)
            data = {
                'Frequency': frequency,
                'Power': self.power_meter.power + self.attenuator
            }
            self.emit('results', data)
            log.debug("Emitting results: %s" % data)
            self.emit('progress', 100 * counter / len(frequencies))
            counter += 1
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break


class MainWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class=MeasureVNAPower,
            inputs=['step', 'start_frequency', 'stop_frequency', 'port', 'vna_power', 'attenuator', 'settling_time'],
            displays=['step', 'start_frequency', 'stop_frequency', 'port', 'vna_power', 'attenuator', 'settling_time'],
            x_axis='Frequency',
            y_axis='Power'
        )
        self.setWindowTitle('HP 8720A Power Verification')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())