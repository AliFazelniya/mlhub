import numpy as np
from sklearn.metrics import accuracy_score
class Adaline:
    def __init__(self):
        self.weights = None

    def weighting(self, inputs_with_bias):
        inputs_with_bias = np.asarray(inputs_with_bias, dtype=float)
        return np.dot(inputs_with_bias, self.weights)

    def activation(self, weighted_input):
        return weighted_input 

    def predict(self, inputs):
        X = np.asarray(inputs, dtype=float)
        is_single = (X.ndim == 1)
        if is_single:
            X = X.reshape(1, -1)

        results = []
        for i in range(X.shape[0]):
            x_with_bias = np.concatenate([[1.0], X[i]])
            w = self.weighting(x_with_bias)
            out = self.activation(w)
            results.append(1 if out >= 0 else -1)

        preds = np.array(results)
        return int(preds[0]) if is_single else preds

    def fit(self, inputs, outputs, learning_rate, epochs):
        X = np.asarray(inputs, dtype=float)
        y = np.asarray(outputs, dtype=float).reshape(-1)

        ones = np.ones((X.shape[0], 1))
        Xb = np.hstack([ones, X])

        self.weights = np.random.rand(Xb.shape[1])

        for _ in range(epochs):
            weighted_input = self.weighting(Xb)           
            output_linear = self.activation(weighted_input)
            diff = y - output_linear                     

            self.weights = self.weights + learning_rate * Xb.T.dot(diff)

            preds = self.predict(X)
            acc = accuracy_score(y, preds)
            print(f"Accuracy: {acc:.4f}")

