import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import pickle

# Load and prepare the data
def load_data_linear(folder_path):
    all_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.csv')]
    dataframes = []
    for file in all_files:
        df = pd.read_csv(file)
        if 'Distance' in df.columns and 'Time' in df.columns and 'Velocity' in df.columns:
            dataframes.append(df)
    if not dataframes:
        raise ValueError("No valid CSV files found with the required columns.")
    data = pd.concat(dataframes)
    return data

def load_data_angular(folder_path):
    all_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.csv')]
    dataframes = []
    for file in all_files:
        df = pd.read_csv(file)
        if 'Angle' in df.columns and 'Time' in df.columns and 'Angular Velocity' in df.columns:
            dataframes.append(df)
    if not dataframes:
        raise ValueError("No valid CSV files found with the required columns.")
    data = pd.concat(dataframes)
    return data

folder_path = '/home/miguel/Desktop/tests'  # Update this path to your CSV files location
data_linear = load_data_linear(folder_path)
data_angular = load_data_angular(folder_path)

# Preprocessing
data_linear = data_linear.dropna()  # Drop missing values
data_angular = data_angular.dropna()  # Drop missing values

# Ensure there is enough data
if data_linear.shape[0] == 0:
    raise ValueError("No valid data available after preprocessing.")

# Ensure there is enough data
if data_angular.shape[0] == 0:
    raise ValueError("No valid data available after preprocessing.")

# Feature selection
X = data_linear[['Distance', 'Velocity']]
y = data_linear['Time']

W = data_angular[['Angle', 'Angular Velocity']]
z = data_angular['Time']

# Ensure there are enough samples for train-test split
if X.shape[0] < 2:
    raise ValueError("Not enough data samples to split.")

if W.shape[0] < 2:
    raise ValueError("Not enough data samples to split.")

# Split the data into training and testing sets
# Adjust test_size to ensure there is enough training data
test_size_linear = 0.2
test_size_angular = 0.2
if X.shape[0] * test_size_linear < 1:
    test_size_linear = 1 / X.shape[0]

if W.shape[0] * test_size_angular < 1:
    test_size_angular = 1 / X.shape[0]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size_linear, random_state=42)
W_train, W_test, z_train, z_test = train_test_split(W, z, test_size=test_size_angular, random_state=42)

# Normalize the features
scaler_linear = StandardScaler()
scaler_angular = StandardScaler()
X_train = scaler_linear.fit_transform(X_train)
X_test = scaler_linear.transform(X_test)

W_train = scaler_angular.fit_transform(W_train)
W_test = scaler_angular.transform(W_test)

# Build the model
model_linear = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(32, activation='relu'),
    Dense(1)  # Output layer for regression
])

# Build the model
model_angular = Sequential([
    Dense(64, activation='relu', input_shape=(W_train.shape[1],)),
    Dense(32, activation='relu'),
    Dense(1)  # Output layer for regression
])

# Compile the model
model_linear.compile(optimizer='adam', loss='mean_squared_error')
model_angular.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
history = model_linear.fit(X_train, y_train, epochs=50, validation_split=0.2, batch_size=32)
history = model_angular.fit(W_train, z_train, epochs=50, validation_split=0.2, batch_size=32)

# Evaluate the model
loss = model_linear.evaluate(X_test, y_test)
print(f'Test loss: {loss}')
loss = model_angular.evaluate(W_test, z_test)
print(f'Test loss: {loss}')

# Save the model and scaler for future use
model_linear.save('models/travel_time_model_linear.keras')
with open('models/scaler_linear.pkl', 'wb') as f:
    pickle.dump(scaler_linear, f)
model_angular.save('models/travel_time_model_angular.keras')
with open('models/scaler_angular.pkl', 'wb') as f:
    pickle.dump(scaler_angular, f)

print('Model and scaler saved.')
