import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Set simulation duration
sim_duration = 40  # ms

# Initialize initial conditions
init = np.zeros(4)
init[0] = -66.8582  # mV
init[1] = 0.1  # m
init[2] = 0.4  # h
init[3] = 0.35  # n

# Set up input current function
def input_current(time):
    if 5 <= time <= 10:
        return 3
    elif 15 <= time <= 25:
        return 19
    else:
        return 0

# Define differential equations
def ydiff(y, time):
    V, m, h, n = y
    
    C = 1  # Capacitance in microfarads
    gNa = 120  # mS
    gK = 36
    gL = 0.3
    ENa = 50  # mV
    EK = -77
    EL = -54.4
    
    x = input_current(time)
    
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

# Time points for simulation
time_points = np.linspace(0, sim_duration, num=1000)

# Solve the differential equations using odeint
y_sim = odeint(ydiff, init, time_points)

# Plot results
plt.figure()

plt.subplot(2, 1, 1)
plt.plot(time_points, y_sim[:, 0], 'm', linewidth=0.9)
plt.xlabel('Time (ms)')
plt.ylabel('Membrane Voltage (mV)')

plt.subplot(2, 1, 2)
plt.plot(time_points, y_sim[:, 1], 'r', linewidth=1.2)
plt.plot(time_points, y_sim[:, 2], 'g', linewidth=1.2)
plt.plot(time_points, y_sim[:, 3], 'b', linewidth=1.2)
plt.xlabel('Time (ms)')
plt.ylabel('Value (unitless)')
plt.legend(['m', 'h', 'n'])

print(f'# steps taken by odeint: {len(time_points)}')

plt.show()
