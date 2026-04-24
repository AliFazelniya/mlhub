# coding: utf-8
import numpy as np
def calc_no_loop(new_points, points):
    return np.sum((new_points[:, np.newaxis, :] - points[np.newaxis, :, :]) ** 2, axis=2)
