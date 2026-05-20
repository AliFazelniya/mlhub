function runMnistConv()
clc; clear; close all;
data = readmatrix('mnist_train.csv');
data = data(randperm(size(data, 1)), :);
splitIdx = floor(0.8 * size(data, 1));
trainData = data(1:splitIdx, :);
testData = data(splitIdx+1:end, :);
Labels = trainData(:, 1);
Labels(Labels == 0) = 10;
Images = reshape(trainData(:, 2:end)', 28, 28, []);
Images = Images / 255;
LabelsTe = testData(:, 1);
LabelsTe(LabelsTe == 0) = 10;
ImagesTe = reshape(testData(:, 2:end)', 28, 28, []);
ImagesTe = ImagesTe / 255;
rng(1);
W1 = 1e-2 * randn([9 9 20]);
W5 = (2*rand(100, 2000) - 1) * sqrt(6) / sqrt(360 + 2000);
Wo = (2*rand(10, 100) - 1) * sqrt(6) / sqrt(10 + 100);
for epoch = 1:3
    [W1, W5, Wo] = MnistConvf(W1, W5, Wo, Images, Labels);
end
X = ImagesTe;
save('MnistConv.mat', 'W1', 'W5', 'Wo', 'X');
acc = 0;
N = size(ImagesTe, 3);
for k = 1:N
    x = ImagesTe(:, :, k);
    y1 = Conv(x, W1);
    y2 = ReLU(y1);
    y3 = Pool(y2);
    y4 = reshape(y3, [], 1);
    v5 = W5 * y4;
    y5 = ReLU(v5);
    v = Wo * y5;
    y = Softmax(v);
    [~, i] = max(y);
    if i == LabelsTe(k)
        acc = acc + 1;
    end
end
fprintf('Accuracy on test set: %f%%\n', (acc / N) * 100);
end
function [W1, W5, Wo] = MnistConvf(W1, W5, Wo, X, D)
alpha = 0.01; beta = 0.95;
momentum1 = zeros(size(W1)); momentum5 = zeros(size(W5)); momentumo = zeros(size(Wo));
N = length(D); bsize = 100; blist = 1:bsize:(N-bsize+1);
for batch = 1:length(blist)
    dW1 = zeros(size(W1)); dW5 = zeros(size(W5)); dWo = zeros(size(Wo));
    begin = blist(batch);
    for k = begin:begin+bsize-1
        x = X(:, :, k);
        y1 = Conv(x, W1); y2 = ReLU(y1); y3 = Pool(y2); y4 = reshape(y3, [], 1);
        v5 = W5 * y4; y5 = ReLU(v5); v = Wo * y5; y = Softmax(v);
        d = zeros(10, 1); d(D(k)) = 1;
        delta = (y - d); e5 = Wo' * delta; delta5 = (y5 > 0) .* e5;
        e4 = W5' * delta5; e3 = reshape(e4, size(y3));
        e2 = zeros(size(y2));
        for c = 1:20, e2(:, :, c) = kron(e3(:, :, c), ones(2)) * (1/4); end
        delta2 = (y2 > 0) .* e2; delta1_x = zeros(size(W1));
        for c = 1:20, delta1_x(:, :, c) = conv2(x, rot90(delta2(:, :, c), 2), 'valid'); end
        dW1 = dW1 + delta1_x; dW5 = dW5 + delta5 * y4'; dWo = dWo + delta * y5';
    end
    dW1 = dW1 / bsize; dW5 = dW5 / bsize; dWo = dWo / bsize;
    momentum1 = beta*momentum1 - alpha*dW1; momentum5 = beta*momentum5 - alpha*dW5; momentumo = beta*momentumo - alpha*dWo;
    W1 = W1 + momentum1; W5 = W5 + momentum5; Wo = Wo + momentumo;
end
end
function y = Conv(x, W)
[wrow, wcol, numFilters] = size(W);
y = zeros(size(x,1)-wrow+1, size(x,2)-wcol+1, numFilters);
for k = 1:numFilters, y(:, :, k) = conv2(x, rot90(W(:, :, k), 2), 'valid'); end
end
function y = Pool(x)
y = zeros(size(x,1)/2, size(x,2)/2, size(x,3));
for k = 1:size(x,3)
    image = conv2(x(:, :, k), ones(2)/4, 'valid');
    y(:, :, k) = image(1:2:end, 1:2:end);
end
end
function y = ReLU(x), y = max(0, x); end
function y = Softmax(x), x = x - max(x); ex = exp(x); y = ex / sum(ex); end
