import logging
import sys
from time import time

from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, Metadata
from pymeasure.experiment import FloatParameter, ListParameter
from pymeasure.instruments.hp import HP4145x
import numpy as np

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class StaticCollectorCharacteristics(Procedure):
    ib = FloatParameter('IB', units='A', default=10e-6, maximum=100e-6, minimum=-100e-6)
    ib_voltage_compliance = FloatParameter('IB Voltage Compliance', units='V', default=2, maximum=100, minimum=-100)
    vce_min = FloatParameter('VCE Minimum', units='V', default=0, maximum=100, minimum=-100)
    vce_max = FloatParameter('VCE Maximum', units='V', default=1, maximum=100, minimum=-100)
    vce_step = FloatParameter('VCE Step', units='V', default=0.01)
    vce_current_compliance = FloatParameter('VCE Current Compliance', units='A', default=100e-3, minimum=-100e-3,
                                            maximum=100e-3)

    assignments = ListParameter('Assignments', choices=["E=1,B=2,C=3"], default="E=1,B=2,C=3")

    starttime = Metadata('Start time', fget=time)

    DATA_COLUMNS = ['VCE', 'IC']

    hp4145a = object

    def startup(self):
        self.hp4145a = HP4145x("GPIB::17")
        self.hp4145a.clear()
        self.hp4145a.reset()


        self.hp4145a.manual_flush = True

        self.hp4145a.smu1.voltage_name = "VE"
        self.hp4145a.smu1.current_name = "IE"
        self.hp4145a.smu1.channel_function = "CONST"
        self.hp4145a.smu1.channel_mode = "COM"

        self.hp4145a.smu2.voltage_name = "VB"
        self.hp4145a.smu2.current_name = "IB"
        self.hp4145a.smu2.channel_function = "CONST"
        self.hp4145a.smu2.channel_mode = "I"
        self.hp4145a.smu2.compliance = self.ib_voltage_compliance
        self.hp4145a.smu2.constant_value = self.ib

        self.hp4145a.smu3.voltage_name = "VCE"
        self.hp4145a.smu3.current_name = "IC"
        self.hp4145a.smu3.channel_function = "VAR1"
        self.hp4145a.smu3.channel_mode = "V"

        self.hp4145a.smu4.disabled = True
        self.hp4145a.vmu1.disabled = True
        self.hp4145a.vmu2.disabled = True
        self.hp4145a.vsu1.disabled = True
        self.hp4145a.vsu2.disabled = True
        self.hp4145a.flush_channel_definition()

        # voltage sweep across VCE
        self.hp4145a.var1.channel_mode = 'V'
        self.hp4145a.var1.sweep_mode = 'LINEAR'
        self.hp4145a.var1.start = self.vce_min
        self.hp4145a.var1.stop = self.vce_max
        self.hp4145a.var1.step = self.vce_step
        self.hp4145a.var1.compliance = self.vce_current_compliance

        self.hp4145a.flush_source_setup()

        self.hp4145a.select_graphics_mode("MATRIX", channel_name="IC")

    def execute(self):
        self.hp4145a.data_ready_srq = True
        self.hp4145a.measure()
        self.hp4145a.adapter.connection.wait_for_srq()

        trace = self.hp4145a.get_data("IC")
        x = np.arange(self.hp4145a.var1._start, self.hp4145a.var1._stop + self.hp4145a.var1._step,
                      self.hp4145a.var1._step)

        y = trace[0].to_list()

        for i in range(len(y)):
            data = {
                'VCE': x[i],
                'IC': y[i]
            }
            self.emit('results', data)


class MainWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class=StaticCollectorCharacteristics,
            inputs=['ib', 'ib_voltage_compliance', 'vce_min', 'vce_max', 'vce_step', 'vce_current_compliance', "assignments"],
            displays=['ib', 'ib_voltage_compliance', 'vce_min', 'vce_max', 'vce_step', 'vce_current_compliance', "assignments"],
            x_axis='VCE',
            y_axis='IC',
            sequencer=True,
            sequencer_inputs=['ib']
        )
        self.setWindowTitle('Static Collector Characteristic')

        self.directory = 'data'


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
