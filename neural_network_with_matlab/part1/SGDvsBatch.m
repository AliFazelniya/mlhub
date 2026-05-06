clear all; clc;

function y = Sigmoid(x)
    y = 1 / (1 + exp(-x));
end

function W = DeltaSGDf(W , X , D)

    alpha = 0.9;
    N = size(X,1);

    for k = 1:N
        
        x = X(k,:)'; 
        d = D(k);

        v = W * x;
        y = Sigmoid(v);

        e = d - y;
        delta = y * (1 - y) * e;

        dW = alpha * delta * x';

        W = W + dW; 

    end
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

N = size(X,1);

E_sgd   = zeros(1000, 1);
E_batch = zeros(1000, 1);

W_sgd   = 2*rand(1,3) - 1;
W_batch = W_sgd;

for epoch = 1:1000

    W_sgd   = DeltaSGDf(W_sgd , X, D);
    W_batch = DeltaBatchf(W_batch, X, D);

    es1 = 0;
    es2 = 0;

    for k = 1:N
        x = X(k,:)';    
        d = D(k);

        y1 = Sigmoid(W_sgd   * x);
        es1 = es1 + (d - y1)^2;

        y2 = Sigmoid(W_batch * x);
        es2 = es2 + (d - y2)^2;
    end

    E_sgd(epoch)   = es1 / N;
    E_batch(epoch) = es2 / N;
end

figure;
plot(E_sgd,   'r', 'LineWidth', 1.5); hold on;
plot(E_batch, 'b', 'LineWidth', 1.5);
grid on;
xlabel('Epoch');
ylabel('Average training error (MSE)');
legend('SGD', 'Batch', 'Location', 'northeast');