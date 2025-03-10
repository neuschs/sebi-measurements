import logging
import sys
from time import time

from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure
from pymeasure.experiment import FloatParameter, ListParameter, Metadata
from pymeasure.instruments.hp import HP4145x
import numpy as np

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LeakageCurrent(Procedure):
    vce_min = FloatParameter('VCE Minimum', units='V', default=0, maximum=100, minimum=-100)
    vce_max = FloatParameter('VCE Maximum', units='V', default=40, maximum=100, minimum=-100)
    vce_step = FloatParameter('VCE Step', units='V', default=1)
    vce_current_compliance = FloatParameter('VCE Current Compliance', units='A', default=10e-3, minimum=-100e-3,
                                            maximum=100e-3)

    parameter = ListParameter('Parameter', choices=["ICBO", "ICEO"], default="ICBO")

    assignments = ListParameter('Assignments', choices=["E=1,B=2,C=3"], default="E=1,B=2,C=3")
    integration_time = ListParameter('Integration Time', choices=['SHORT', 'MEDIUM', 'LONG'], default='MEDIUM', description="None, 16 or 256 averages")

    DATA_COLUMNS = ['VC', 'IC']

    hp4145a = object

    def startup(self):
        self.hp4145a = HP4145x("GPIB::17", timeout=200000)
        self.hp4145a.clear()
        self.hp4145a.reset()

        self.hp4145a.disable_all()

        self.hp4145a.manual_flush = True

        parameter_map = {"ICBO": ("B", "smu2"), "ICEO": ("E", "smu1")}

        # fix assignments for now
        name, smu = parameter_map[self.parameter]
        smu_to_gnd = getattr(self.hp4145a, smu)

        smu_to_gnd.voltage_name = f"V{name}"
        smu_to_gnd.current_name = f"I{name}"
        smu_to_gnd.channel_function = "CONST"
        smu_to_gnd.channel_mode = "COM"

        self.hp4145a.smu3.voltage_name = "VC"
        self.hp4145a.smu3.current_name = "IC"
        self.hp4145a.smu3.channel_function = "VAR1"
        self.hp4145a.smu3.channel_mode = "V"

        self.hp4145a.flush_channel_definition()

        # voltage sweep across VCE
        self.hp4145a.var1.channel_mode = 'V'
        self.hp4145a.var1.sweep_mode = 'LINEAR'
        self.hp4145a.var1.start = self.vce_min
        self.hp4145a.var1.stop = self.vce_max
        self.hp4145a.var1.step = self.vce_step
        self.hp4145a.var1.compliance = self.vce_current_compliance

        self.hp4145a.flush_source_setup()
        self.hp4145a.integration_time = self.integration_time

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
                'VC': x[i],
                'IC': y[i]
            }
            self.emit('results', data)


class MainWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class=LeakageCurrent,
            inputs=['parameter', 'vce_min', 'vce_max', 'vce_step', 'vce_current_compliance', "assignments", "integration_time"],
            displays=['parameter', 'vce_min', 'vce_max', 'vce_step', 'vce_current_compliance', "assignments", "integration_time"],
            x_axis='VC',
            y_axis='IC'
        )
        self.setWindowTitle('Leakage Current')

        self.directory = 'data'
        self.filename = 'Transistor_{Parameter}'


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
