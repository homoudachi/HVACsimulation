import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Define Constants
T_SETPOINT = 24  # Target temperature (°C)
RH_SETPOINT = 50  # Target RH (%)
T_COIL_COLD = 8  # Cold water coil temperature (°C)
T_COIL_HOT = 55  # Hot water coil temperature (°C)
RH_HIGH = 60  # High RH threshold (%)
RH_LOW = 35  # Low RH threshold (%)
MAX_FAN_SPEED = 1.0
MIN_FAN_SPEED = 0.1

# Simulation function for dehumidification and heating
def simulate_system(temp_indoor, rh_indoor, temp_outdoor, rh_outdoor, fan_speed, cold_water_valve, hot_water_valve, oa_damper):
    # Simulate cooling or heating response based on outdoor conditions and water valve settings
    cooling_effect = cold_water_valve * (T_COIL_COLD - temp_indoor) * 0.1
    heating_effect = hot_water_valve * (temp_indoor - T_COIL_HOT) * 0.1
    fan_effect = fan_speed * 0.5

    # Adjust indoor temperature
    temp_indoor += cooling_effect - heating_effect + fan_effect

    # Dehumidification (based on cooling)
    if cooling_effect > 0:
        rh_indoor -= (cooling_effect * 0.1)
    # Humidification if heating is dominant
    if heating_effect > 0:
        rh_indoor += (heating_effect * 0.05)

    # Adjust humidity based on OA damper
    if oa_damper > 0:
        if rh_outdoor < rh_indoor:
            rh_indoor -= oa_damper * 0.2  # Dry outdoor air
        elif rh_outdoor > rh_indoor:
            rh_indoor += oa_damper * 0.2  # Humid outdoor air

    # Clamp values to realistic limits
    temp_indoor = np.clip(temp_indoor, 18, 26)  # temperature range 18-26°C
    rh_indoor = np.clip(rh_indoor, 30, 70)  # RH range 30-70%

    return temp_indoor, rh_indoor

# Streamlit interface
st.title("Fan Coil Unit (FCU) Control Simulation")
st.sidebar.header("System Controls")

# Inputs
temp_indoor = st.sidebar.slider("Indoor Temperature (°C)", 18, 26, T_SETPOINT)
rh_indoor = st.sidebar.slider("Indoor Humidity (%)", 30, 70, RH_SETPOINT)
temp_outdoor = st.sidebar.slider("Outdoor Temperature (°C)", -10, 40, 20)
rh_outdoor = st.sidebar.slider("Outdoor Humidity (%)", 30, 80, 50)
fan_speed = st.sidebar.slider("Fan Speed", MIN_FAN_SPEED, MAX_FAN_SPEED, 0.5)
cold_water_valve = st.sidebar.slider("Cold Water Valve (%)", 0, 100, 50)
hot_water_valve = st.sidebar.slider("Hot Water Valve (%)", 0, 100, 50)
oa_damper = st.sidebar.slider("Outdoor Air Damper (%)", 0, 100, 50)

# Simulate the system with the selected values
temp_indoor, rh_indoor = simulate_system(temp_indoor, rh_indoor, temp_outdoor, rh_outdoor, fan_speed, cold_water_valve / 100, hot_water_valve / 100, oa_damper / 100)

# Display Results
st.write(f"### Indoor Conditions")
st.write(f"Indoor Temperature: {temp_indoor:.2f}°C")
st.write(f"Indoor Humidity: {rh_indoor:.2f}%")

# Plot Temperature and Humidity Over Time
time_steps = np.linspace(0, 10, 100)
temperature = [temp_indoor + cooling_effect - heating_effect + fan_effect for _ in time_steps]
humidity = [rh_indoor - cooling_effect * 0.1 + heating_effect * 0.05 for _ in time_steps]

# Plotting
fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.set_xlabel('Time (min)')
ax1.set_ylabel('Temperature (°C)', color='tab:red')
ax1.plot(time_steps, temperature, color='tab:red', label='Temperature')
ax1.tick_params(axis='y', labelcolor='tab:red')

ax2 = ax1.twinx()  
ax2.set_ylabel('Humidity (%)', color='tab:blue')  
ax2.plot(time_steps, humidity, color='tab:blue', label='Humidity')
ax2.tick_params(axis='y', labelcolor='tab:blue')

fig.tight_layout()  
st.pyplot(fig)
