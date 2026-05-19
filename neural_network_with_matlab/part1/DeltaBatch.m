clear all; clc;

function y = Sigmoid(x)
    y = 1 / (1 + exp(-x));
end

function W = DeltaBatchf(W , X, D)
    alpha = 0.9;
    dWsum = zeros(1, 3);

    N = size(X, 1);
    for k = 1:N
        x = X(k, :)';     
        d = D(k);          

        v = W * x;         
        y = Sigmoid(v);

        e = d - y;
        delta = y * (1 - y) * e;

        dW = alpha * delta * x';  

        dWsum = dWsum + dW;
    end

    dWavg = dWsum / N;
    W = W + dWavg;          
end

X = [0 0 1;
     0 1 1;
     1 0 1;
     1 1 1];

D = [0; 0; 1; 1];

W = 2 * rand(1, 3) - 1;

for epoch = 1:40000
    W = DeltaBatchf(W , X , D);
end

N = size(X, 1);
for k = 1:N
    x = X(k, :)';
    v = W * x;
    y = Sigmoid(v);
    fprintf('Input: [%d %d %d] --> Output: %.4f\n', X(k, 1), X(k, 2), X(k, 3), y);
end
