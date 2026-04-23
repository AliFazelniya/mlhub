# data

Datasets required by notebooks in the parent module.

## Files

- `mnist_test.csv` — MNIST test dataset used for prediction.
- `mnist_train.csv.xz` — Compressed MNIST training dataset.
- `restore_mnist_train.sh` — Restores `mnist_train.csv` by decompressing the `.xz` archive.

## How to Use

These datasets are inputs for notebooks in the parent directory. Keep filenames unchanged so notebooks run without edits.

## Notes

Run `restore_mnist_train.sh` to restore `mnist_train.csv` from the `.xz` archive before training.
