# hodgkinhuxley
# Simulation of a Hodgkin Huxley model the neuron
This is a toy code to simulate the Hodgkin-Huxley model of neuronal firing. Included in the model are Sodium and Potassium channel coductances in addition to a leak conductance. Addition of more channels is rather easy; only requires addition of corresponding differential equations governing activation and inactivation. Here, we utilize governing equations provided by Svirskis, Gytis, et al. from John Rinzel's group. Although limited, you can make custom current injections to the neuron at differnt time points (only square injections supported for now). <br>
### Simple two-pulse injection
![Alt Text](assets\samples\twoimpulses.png)

