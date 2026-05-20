clear all

function [W1, W2] = BackpropCEf(W1, W2, X, D)
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
        delta = e;

        e1 = W2' * delta;
        delta1 = y1 .* (1 - y1) .* e1;

        W1 = W1 + alpha * delta1 * x';
        W2 = W2 + alpha * delta * y1';
    end
end

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

E1 = zeros(1000, 1);
E2 = zeros(1000, 1);

W11 = 2 * rand(4, 3) - 1;
W12 = 2 * rand(1, 4) - 1;

W21 = W11;
W22 = W12;

for epoch = 1:1000
    [W11, W12] = BackpropCEf(W11, W12, X, D);
    [W21, W22] = Backprop(W21, W22, X, D);

    es1 = 0;
    es2 = 0;

    N = 4;
    for k = 1:N
        x = X(k, :)';
        d = D(k);

        v1 = W11 * x;
        y1 = Sigmoid(v1);
        v = W12 * y1;
        y = Sigmoid(v);
        es1 = es1 + (d - y)^2;
        
        v1 = W21 * x;
        y1 = Sigmoid(v1);
        v = W22 * y1;
        y = Sigmoid(v);
        es2 = es2 + (d - y)^2;
    end

    E1(epoch) = es1 / N;
    E2(epoch) = es2 / N;
end

plot(E1, 'r', 'LineWidth', 2)
hold on
plot(E2, 'b:', 'LineWidth', 2)
xlabel('Epoch')
ylabel('Average Training Error')
legend('Cross Entropy', 'Sum of Squared Error')
grid on
