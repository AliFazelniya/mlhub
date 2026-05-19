clear all


function [W1, W2] = Backprop(W1, W2, X, D)
    alpha = 0.1;
    
    [N, ~] = size(X);
    for k = 1:N
        x = X(k, :)';
        d = D(k);

        v1 = W1 * x;
        y1 = Sigmoid(v1);

        v = W2 * y1;
        y = Sigmoid(v);

        e = d - y;
        delta = e .* y .* (1 - y);

        e1 = W2' * delta;
        delta1 = e1 .* y1 .* (1 - y1);

        W1 = W1 + alpha * delta1 * x';
        W2 = W2 + alpha * delta * y1';
    end
end

function y = Sigmoid(x)
    y = 1 ./ (1 + exp(-x));
end

X = [0 0 1;
     0 1 1;
     1 0 1;
     1 1 1];

D = [0; 1; 1; 0];

W1 = 2*rand(4, 3) - 1;
W2 = 2*rand(1, 4) - 1;

for epoch = 1:10000
    [W1, W2] = Backprop(W1, W2, X, D);
end

N = 4;

for k = 1:N
    x = X(k, :)';
    v1 = W1 * x;
    y1 = Sigmoid(v1);
    v = W2 * y1;
    y = Sigmoid(v);

    disp(y)
end