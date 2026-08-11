clear all

function [W1, W2, W3, W4] = DeepDropoutf(W1, W2, W3, W4, X, D)
    alpha = 0.01;
    [~, ~, N] = size(X);

    for k = 1:N
        x = reshape(X(:, :, k), 25, 1);

        v1 = W1*x;
        y1 = Sigmoid(v1);
        m1 = DropoutMask(size(y1), 0.2);
        y1 = y1 .* m1;

        v2 = W2*y1;
        y2 = Sigmoid(v2);
        m2 = DropoutMask(size(y2), 0.2);
        y2 = y2 .* m2;

        v3 = W3*y2;
        y3 = Sigmoid(v3);
        m3 = DropoutMask(size(y3), 0.2);
        y3 = y3 .* m3;

        v = W4*y3;
        y = Softmax(v);

        d = D(k, :)';

        e = d - y;
        delta = e;

        e3 = W4' * delta;
        delta3 = y3 .* (1 - y3) .* e3;
        delta3 = delta3 .* m3;

        e2 = W3' * delta3;
        delta2 = y2 .* (1 - y2) .* e2;
        delta2 = delta2 .* m2;

        e1 = W2' * delta2;
        delta1 = y1 .* (1 - y1) .* e1;
        delta1 = delta1 .* m1;

        W4 = W4 + alpha * delta * y3';
        W3 = W3 + alpha * delta3 * y2';
        W2 = W2 + alpha * delta2 * y1';
        W1 = W1 + alpha * delta1 * x';
    end
end

function m = DropoutMask(sz, ratio)
    m = (rand(sz) > ratio) / (1 - ratio);
end

function y = Softmax(x)
    ex = exp(x - max(x));
    y = ex ./ sum(ex);
end

function y = Sigmoid(x)
    y = 1 ./ (1 + exp(-x));
end

X(:, :, 1) = [ 0 1 1 0 0; 0 0 1 0 0; 0 0 1 0 0; 0 0 1 0 0; 0 1 1 1 0 ];
X(:, :, 2) = [ 1 1 1 1 0; 0 0 0 0 1; 0 1 1 1 0; 1 0 0 0 0; 1 1 1 1 1 ];
X(:, :, 3) = [ 1 1 1 1 0; 0 0 0 0 1; 0 1 1 1 0; 0 0 0 0 1; 1 1 1 1 0 ];
X(:, :, 4) = [ 0 0 0 1 0; 0 0 1 1 0; 0 1 0 1 0; 1 1 1 1 1; 0 0 0 1 0 ];
X(:, :, 5) = [ 1 1 1 1 1; 1 0 0 0 0; 1 1 1 1 0; 0 0 0 0 1; 1 1 1 1 0 ];

D = [ 1 0 0 0 0; 0 1 0 0 0; 0 0 1 0 0; 0 0 0 1 0; 0 0 0 0 1 ];

W1 = 2*rand(20, 25) - 1;
W2 = 2*rand(20, 20) - 1;
W3 = 2*rand(20, 20) - 1;
W4 = 2*rand(5,  20) - 1;

for epoch = 1:10000
    [W1, W2, W3, W4] = DeepDropoutf(W1, W2, W3, W4, X, D);
end

for k = 1:5
    x = reshape(X(:, :, k), 25, 1);
    v1 = W1 * x; y1 = Sigmoid(v1);
    v2 = W2 * y1; y2 = Sigmoid(v2);
    v3 = W3 * y2; y3 = Sigmoid(v3);
    v  = W4 * y3; y  = Softmax(v);
    disp(y')
end