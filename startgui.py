'''
Simulation of a Hodgkin-Huxley model of neuronal firing.
'''
__author__ = "Ahmad Abdal Qader"
__version__  = "0.0.1a"
__credits__ = "L.H. Carney, PhD; Svirskis, Gytis, et al."

import sys
import yaml
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QLabel, QSlider, QPushButton, QLineEdit,QVBoxLayout
from PyQt5.QtCore import Qt
from matplotlib.animation import FuncAnimation

class NeuronSimulatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loadConfig()
        self.initUI()
        # self.initSimulation()
    def loadConfig(self):
        with open('scripts/params.yaml', 'r') as config_file:
            config = yaml.safe_load(config_file)
            self.simulation_params = config['simulation_params']
            self.model_params = config['model_params']
    def initUI(self):
        self.setWindowTitle('H-H Model')

        # Create sliders, text boxes, and layout
        sliders_layout = QHBoxLayout()
        self.sliders = []
        for label_text, tick_interval, min_val, max_val, init_val in [('Simulation Duration', 1, 0, 100,40),
                                                            ('V', 1, -100, 100,-67),
                                                            ('m', 0.05, 0, 10, 1),
                                                            ('h', 0.05, 0, 10, 5),
                                                            ('n', 0.05, 0, 10, 3)]:
            label = QLabel(label_text)
            slider = QSlider(Qt.Horizontal)
            text_box = QLineEdit()
            text_box.setReadOnly(False)
            slider.valueChanged.connect(lambda value, tb=text_box: tb.setText(str(value)))
            text_box.editingFinished.connect(lambda tb=text_box, sl=slider: self.updateSliderFromTextBox(tb, sl))
            slider.setTickInterval(int(tick_interval))
            slider.setMinimum(min_val)
            slider.setMaximum(max_val)
            slider.setValue(init_val)
            text_box.setText(str(init_val))
            sliders_layout.addWidget(label)
            sliders_layout.addWidget(slider)
            sliders_layout.addWidget(text_box)
            self.sliders.append((slider, text_box))
        
        # Create start button
        self.start_button = QPushButton('Start Simulation')
        self.start_button.clicked.connect(self.startSimulation)

        # Create matplotlib figures
        self.fig_v = plt.figure()
        self.ax_v = self.fig_v.add_subplot(111)
        self.canvas_v = FigureCanvas(self.fig_v)

        self.fig_mhn = plt.figure()
        self.ax_mhn = self.fig_mhn.add_subplot(111)
        self.canvas_mhn = FigureCanvas(self.fig_mhn)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(sliders_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.canvas_v)
        layout.addWidget(self.canvas_mhn)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # def initSimulation(self, init_values=[40, -66.8582, 0.1, 0.4, 0.35]):
    #     for i, slider in enumerate(self.sliders[1:]):
    #         slider[0].setValue(init_values[i])

    def updateSliderFromTextBox(self, text_box, slider):
        try:
            value = float(text_box.text())
            slider.setValue(int(value))  # Convert value to slider range
        except ValueError:
            pass

    def startSimulation(self):
        sim_duration = self.sliders[0][0].value()
        self.sim_duration = sim_duration
        init_values = [slider.value()/10 for slider, _ in self.sliders[1:]]
        # undo division for membrane voltage
        init_values[0] *= 10

        # Simulate the neuron using the provided code
        time_points = np.linspace(0, sim_duration, num=self.simulation_params['num_points'])
        init_conditions = init_values
        # prepare input current
        input_start = self.simulation_params['input_params']['input_start']
        input_end = self.simulation_params['input_params']['input_end']
        input_height = self.simulation_params['input_params']['input_amp']

        iMatrix = np.zeros((len(input_start), len(time_points)))

        for idx, (start, end, height) in enumerate(zip(input_start, input_end, input_height)):
            tempBegin = time_points >= start
            tempEnd = time_points <= end
            finalTemp = tempBegin & tempEnd
            iMatrix[idx, :] = finalTemp * height

        self.ic = np.sum(iMatrix, axis=0)


        y_sim = odeint(self.ydiff, init_conditions, time_points)

        # Update plots with animated data
        self.ax_v.clear()
        self.ax_mhn.clear()
        self.ax_v.plot(time_points, y_sim[:, 0], 'm', linewidth=0.9)
        self.ax_v.set_xlabel('Time (ms)')
        self.ax_v.set_ylabel('Membrane Voltage (mV)')

        self.ax_mhn.plot(time_points, y_sim[:, 1], 'r', linewidth=1.2, label='m')
        self.ax_mhn.plot(time_points, y_sim[:, 2], 'g', linewidth=1.2, label='h')
        self.ax_mhn.plot(time_points, y_sim[:, 3], 'b', linewidth=1.2, label='n')
        self.ax_mhn.set_xlabel('Time (ms)')
        self.ax_mhn.set_ylabel('Value (unitless)')
        self.ax_mhn.legend()

        self.canvas_v.draw()
        self.canvas_mhn.draw()
    def ydiff(self, y, time):
        V, m, h, n = y
        q = self.model_params

        C = q['C']  # Capacitance in microfarads
        gNa = q['gNa']  # mS (Sodium Conductance)
        gK = q['gK']  # (Potassium Conductance)
        gL =q['gL'] # (Leakage Conductance)
        ENa = q['ENa']  # mV (Sodium Reversal Potential)
        EK = q['EK']  # (Potassium Reversal Potential)
        EL = q['EL']  # (Leakage Reversal Potential)

        # accomodate the ode solver overshooting the simulation duration -> pad input with 0 accordingly
        time2index  = int(time*self.simulation_params['num_points']/self.sim_duration)
        if time2index < self.simulation_params['num_points']:
            x = self.ic[int(time*self.simulation_params['num_points']/self.sim_duration)]
        else:
            x = 0
        

        ## refer to Journal of neurophysiology, 91(6), 2465-2473.
        alphaN = 0.01 * (V + 55) / (1 - np.exp(-(V + 55) / 10))
        betaN = 0.125 * np.exp(-(V + 65) / 80)
        alphaM = 0.1 * (V + 40) / (1 - np.exp(-(V + 40) / 10))
        betaM = 4 * np.exp(-(V + 65) / 18)
        alphaH = 0.07 * np.exp(-(V + 65) / 20)
        betaH = 1 / (1 + np.exp(-(V + 35) / 10))
        
        dydt = np.zeros(4)
        dydt[0] = 1/C * (x - (m**3) * h * gNa * (V - ENa) - (n**4) * gK * (V - EK) - gL * (V - EL))
        dydt[1] = alphaM * (1 - m) - betaM * m
        dydt[2] = alphaH * (1 - h) - betaH * h
        dydt[3] = alphaN * (1 - n) - betaN * n
        
        return dydt

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NeuronSimulatorApp()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec_())
