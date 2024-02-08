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

# doesn't work to good due to the VNA having issues to lock in case connected with the frequency counter

class MeasureFrequencyError(Procedure):
    step = FloatParameter('Frequency Step', units='Hz', default=100e6, maximum=20e9)
    start_frequency = FloatParameter('Start Frequency', units='Hz', default=130e6, maximum=20e9)
    stop_frequency = FloatParameter('Stop Frequency', units='Hz', default=20e9, maximum=20e9)

    DATA_COLUMNS = ['Frequency', 'Frequency Error in Hz']

    frequency_counter = object
    vna = object

    def startup(self):
        self.frequency_counter = VISAAdapter("USB0::0x03EB::0x2065::HP_5347A__2929::INSTR", read_termination="\n")
        self.vna = VISAAdapter("GPIB0::16::INSTR")
        self.vna.write("POWE %d" % -10)
        self.frequency_counter.write("AUTO\r\n")

    def execute(self):
        counter = 0
        frequencies = np.arange(self.start_frequency, self.stop_frequency, self.step)
        for frequency in frequencies:
            # switch to other port because the frequency counter blocks phase lockins of the HP8720A
            self.frequency_counter.connection.clear()
            self.vna.write("S11")
            sleep(1)
            self.vna.write("CWFREQ %.2e" % frequency)
            sleep(0.1)
            self.vna.write("S22")
            self.frequency_counter.write("SAMPLE,HOLD\r\n")
            sleep(3)
            self.frequency_counter.write("TRIGGER\r\n")
            sleep(2)
            data = {
                'Frequency': frequency,
                'Frequency Error in Hz': abs(float(self.frequency_counter.connection.read_raw(24)) - frequency)
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
            procedure_class=MeasureFrequencyError,
            inputs=['step', 'start_frequency', 'stop_frequency'],
            displays=['step', 'start_frequency', 'stop_frequency'],
            x_axis='Frequency',
            y_axis='Frequency Error in Hz'
        )
        self.setWindowTitle('HP 8720A Frequency Verification')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
