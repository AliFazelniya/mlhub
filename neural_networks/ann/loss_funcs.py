from ternsorflow import keras

# ----- Regression Loss Functions -----
loss_func_1 = keras.losses.MeanSquaredError()
loss_func_2 = keras.losses.MeanAbsoluteError()

# ---- Classification Loss Functions -----
loss_func_3 = keras.losses.CategoricalCrossentropy()
loss_func_4 = keras.losses.BinaryCrossentropy()