clear all;
load('MnistConv.mat');

k = 2;
x = X(:, :, k);
y1 = Conv(x, W1);
y2 = ReLU(y1);
y3 = Pool(y2);
y4 = reshape(y3, [], 1);
v5 = W5 * y4;
y5 = ReLU(v5);
v = Wo * y5;
y = Softmax(v);

figure;
imshow(x, []);
title('Input Image');

figure;
for i = 1:20
    subplot(4,5,i);
    imagesc(W1(:,:,i));
    axis off; colormap gray;
    title(['Filter ' num2str(i)]);
end
sgtitle('Convolution Filters');

figure;
for i = 1:20
    subplot(4,5,i);
    imagesc(y1(:,:,i));
    axis off; colormap gray;
    title(['Conv Feature ' num2str(i)]);
end
sgtitle('Features [Convolution]');

figure;
for i = 1:20
    subplot(4,5,i);
    imagesc(y2(:,:,i));
    axis off; colormap gray;
    title(['ReLU Feature ' num2str(i)]);
end
sgtitle('Features [Convolution + ReLU]');

figure;
for i = 1:20
    subplot(4,5,i);
    imagesc(y3(:,:,i));
    axis off; colormap gray;
    title(['Pooled Feature ' num2str(i)]);
end
sgtitle('Features [Convolution + ReLU + MeanPool]');

function y = Conv(x, W)
[wrow, wcol, numFilters] = size(W);
y = zeros(size(x,1)-wrow+1, size(x,2)-wcol+1, numFilters);
for k = 1:numFilters, y(:,:,k) = conv2(x, rot90(W(:,:,k),2), 'valid'); end
end

function y = Pool(x)
y = zeros(size(x,1)/2, size(x,2)/2, size(x,3));
for k = 1:size(x,3)
    image = conv2(x(:,:,k), ones(2)/4, 'valid');
    y(:,:,k) = image(1:2:end, 1:2:end);
end
end

function y = ReLU(x), y = max(0, x); end
function y = Softmax(x), x = x - max(x); ex = exp(x); y = ex / sum(ex); end
