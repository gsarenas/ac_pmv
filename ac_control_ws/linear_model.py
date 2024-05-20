import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Data
occupancy = np.array([0, 1, 0.5, 0.25])
temperature = np.array([16.4, 21.76, 19.13, 17.22])
pmv = np.array([-2.156, 1.362, -0.209, -1.044])
ppd = np.array([82.29, 51.53, 12.81, 30.16])

# Reshape for sklearn
occupancy_reshaped = occupancy.reshape(-1, 1)

# Linear regression models
temp_model = LinearRegression().fit(occupancy_reshaped, temperature)
pmv_model = LinearRegression().fit(occupancy_reshaped, pmv)
ppd_model = LinearRegression().fit(occupancy_reshaped, ppd)

# Coefficients
a_T, b_T = temp_model.coef_[0], temp_model.intercept_
a_PMV, b_PMV = pmv_model.coef_[0], pmv_model.intercept_
a_PPD, b_PPD = ppd_model.coef_[0], ppd_model.intercept_

print(f'Temperature model: T(occupancy) = {a_T:.4f} * occupancy + {b_T:.4f}')
print(f'PMV model: PMV(occupancy) = {a_PMV:.4f} * occupancy + {b_PMV:.4f}')
print(f'PPD model: PPD(occupancy) = {a_PPD:.4f} * occupancy + {b_PPD:.4f}')

# Plotting (Optional)
plt.figure(figsize=(14, 5))

plt.subplot(1, 3, 1)
plt.scatter(occupancy, temperature, color='blue')
plt.plot(occupancy, temp_model.predict(occupancy_reshaped), color='red')
plt.title('Temperature vs Occupancy')
plt.xlabel('Occupancy')
plt.ylabel('Temperature (°C)')

plt.subplot(1, 3, 2)
plt.scatter(occupancy, pmv, color='blue')
plt.plot(occupancy, pmv_model.predict(occupancy_reshaped), color='red')
plt.title('PMV vs Occupancy')
plt.xlabel('Occupancy')
plt.ylabel('PMV')

plt.subplot(1, 3, 3)
plt.scatter(occupancy, ppd, color='blue')
plt.plot(occupancy, ppd_model.predict(occupancy_reshaped), color='red')
plt.title('PPD vs Occupancy')
plt.xlabel('Occupancy')
plt.ylabel('PPD (%)')

plt.tight_layout()
plt.show()
