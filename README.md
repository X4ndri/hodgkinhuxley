# hodgkinhuxley
# Simulation of a Hodgkin Huxley model the neuron
This is a toy code to simulate the Hodgkin-Huxley model of neuronal firing. Included in the model are Sodium and Potassium channel coductances in addition to a leak conductance. Addition of more channels is rather easy; only requires addition of corresponding differential equations governing activation and inactivation. Here, we utilize governing equations provided by Svirskis, Gytis, et al. from John Rinzel's group. Although limited, you can make custom current injections to the neuron at differnt time points (only square injections supported for now). <br>
### Simple two-pulse injection
![Alt Text](https://github.com/X4ndri/hodgkinhuxley/blob/main/assets/samples/twoimpulses.png)

## Model variables:
The model parameters such as individual channel conductances and membrane capacitance can easily be adjusted from a yml file. Source code includes the governinig equations for activation and inactivation subunits, but these are straight forwards and modular, so you can try your own! Initial conditions are set from the gui for easy trial-and-error attempts.
```yaml
simulation_params:
  num_points : 1000 # number of points in the simulation
  # use the following to build your current injection to the neuron
  input_params:
    # inputs start times
    input_start : [2, 8, 19]
    # input end times
    input_end : [4, 11, 23]
    # input amplitudes
    input_amp : [5, 13, 21]
    # e.g. this means from time 2 to 4, input is square with amplitude 5

model_params:
  C: 1 # membrane capacitance in microfarads
  gNa: 120 # Sodium Conductance
  gK: 36 # Potassium Conductance
  gL: 0.3 # Leakage Conductance
  ENa: 50 # mV Sodium Reversal Potential
  EK: -77 # mV Potassium Reversal Potential
  EL: -54.4 # mV Leakage Reversal Potential
```