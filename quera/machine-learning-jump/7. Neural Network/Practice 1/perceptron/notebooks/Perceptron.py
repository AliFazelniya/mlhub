import numpy as np
from sklearn.metrics import accuracy_score
class Perceptron:
    def __init__(self):
        self.weights = None

    def weighting(self, sample_features):
        sample_features = np.asarray(sample_features, dtype=float)
        return float(np.dot(self.weights, sample_features))

    def activation(self, weighted_input):
        return 1 if weighted_input >= 0 else -1

    def predict(self, inputs):
        X = np.asarray(inputs, dtype=float)
        is_single = (X.ndim == 1)
        if is_single:
            X = X.reshape(1, -1)

        results = []
        for i in range(X.shape[0]):

            x_with_bias = np.concatenate([[1.0], X[i]])
            w = self.weighting(x_with_bias)
            results.append(self.activation(w))

        preds = np.array(results)
        return int(preds[0]) if is_single else preds

    def fit(self, inputs, outputs, learning_rate, epochs):
        X = np.asarray(inputs, dtype=float)
        y = np.asarray(outputs, dtype=float).reshape(-1)


        ones = np.ones((X.shape[0], 1))
        Xb = np.hstack([ones, X])

        self.weights = np.random.rand(Xb.shape[1])

        for _ in range(epochs):
            for i in range(Xb.shape[0]):
                x_i = Xb[i]
                y_hat = self.activation(self.weighting(x_i))
                diff = y[i] - y_hat
                self.weights = self.weights + learning_rate * diff * x_i

            preds = self.predict(X)
            acc = accuracy_score(y, preds)
            print(f"Accuracy: {acc:.4f}")

