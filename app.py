import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

F = 96485  # Faraday's constant, C/mol e-
MOLAR_MASS_HOCL = 52.46  # g/mol
ELECTRONS_PER_HOCL = 2

st.title("HOCl Generation Time Estimator")

st.markdown("Estimate how long to run electrolysis to generate a desired HOCl concentration.")

# --- Input sliders ---
volume_liters = st.slider("Water Volume (L)", 0.01, 1.0, 0.1, 0.01)
target_ppm = st.slider("Target HOCl Concentration (ppm)", 10, 500, 100, 10)
faradaic_efficiency = st.slider("Faradaic Efficiency (%)", 10, 100, 75, 5) / 100
voltage = st.slider("Voltage (V)", 3.0, 12.0, 7.2, 0.1)
resistance = st.slider("Electrode Resistance (Ω)", 0.1, 10.0, 1.4, 0.1)

# --- Derived values ---
current = voltage / resistance
grams_needed = (target_ppm * volume_liters) / 1000
mol_needed = grams_needed / MOLAR_MASS_HOCL
charge_c = (mol_needed * ELECTRONS_PER_HOCL * F) / faradaic_efficiency
time_sec = charge_c / current

# --- Output ---
st.metric("Required Charge (C)", f"{charge_c:.2f}")
st.metric("Current (A)", f"{current:.2f}")
st.metric("Time Required (s)", f"{time_sec:.1f}")
st.metric("Time Required (min)", f"{time_sec/60:.1f}")

# --- Chart for multiple concentrations ---
st.markdown("### Time vs Concentration Plot")

ppms = np.linspace(10, 500, 50)
times = []
for ppm in ppms:
    g = (ppm * volume_liters) / 1000
    m = g / MOLAR_MASS_HOCL
    q = (m * ELECTRONS_PER_HOCL * F) / faradaic_efficiency
    t = q / current
    times.append(t)

fig, ax = plt.subplots()
ax.plot(ppms, times)
ax.set_xlabel("HOCl Concentration (ppm)")
ax.set_ylabel("Time Required (s)")
ax.grid(True)
st.pyplot(fig)

