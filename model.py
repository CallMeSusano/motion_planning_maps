import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Load and prepare the data
def load_data_from_folder(folder_path):
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

folder_path = '/home/miguel/Desktop/tests'  # Update this path to your CSV files location
data = load_data_from_folder(folder_path)

# Preprocessing
data = data.dropna()  # Drop missing values

# Ensure there is enough data
if data.shape[0] == 0:
    raise ValueError("No valid data available after preprocessing.")

# Feature selection
X = data[['Distance', 'Velocity']]
y = data['Time']

# Ensure there are enough samples for train-test split
if X.shape[0] < 2:
    raise ValueError("Not enough data samples to split.")

# Split the data into training and testing sets
# Adjust test_size to ensure there is enough training data
test_size = 0.2
if X.shape[0] * test_size < 1:
    test_size = 1 / X.shape[0]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

# Normalize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Build the model
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(32, activation='relu'),
    Dense(1)  # Output layer for regression
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
history = model.fit(X_train, y_train, epochs=50, validation_split=0.2, batch_size=32)

# Evaluate the model
loss = model.evaluate(X_test, y_test)
print(f'Test loss: {loss}')

# Predict function
def predict_time(distance, velocity):
    input_data = np.array([[distance, velocity]])
    input_data = scaler.transform(input_data)
    predicted_time = model.predict(input_data)
    return predicted_time[0][0]

# Save the model and scaler for future use
model.save('travel_time_model.h5')
with open('scaler.pkl', 'wb') as f:
    import pickle
    pickle.dump(scaler, f)

print('Model and scaler saved.')
