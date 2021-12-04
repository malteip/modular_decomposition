"""Functions for plotting the test data.

This module implements various functions for plotting the data generated with 'test.py'.
"""

import matplotlib.pyplot as plt
import numpy as np
import sys


def plot_prim():  # plot prim_test
    x_10 = []
    y_10 = []

    x_100 = []
    y_100 = []

    x_1000 = []
    y_1000 = []

    cnt = 0
    for line in sys.stdin:
        n, p, p_prim = line.rstrip('\n').split(' ')
        cnt += 1
        if n == '10':
            x_10.append(float(p) / 100)
            y_10.append(float(p_prim))
        if n == '100':
            x_100.append(float(p) / 100)
            y_100.append(float(p_prim))
        if n == '1000':
            x_1000.append(float(p) / 100)
            y_1000.append(float(p_prim))

    plt.plot(x_10, y_10, label='n = 10')
    plt.plot(x_100, y_100, label='n = 100')
    plt.plot(x_1000, y_1000, label='n = 1000')

    # plt.grid(True)
    plt.legend()
    plt.xlabel('p')
    plt.ylabel('p*')
    plt.show()


def plot_m():  # plot m_test
    x_1 = []
    y_1 = []

    x_2 = []
    y_2 = []

    x_3 = []
    y_3 = []

    x_4 = []
    y_4 = []

    x_5 = []
    y_5 = []

    for line in sys.stdin:
        n, p, t = line.rstrip('\n').split(' ')
        if n == '1000':
            x_1.append(float(p) / 100)
            y_1.append(float(t))
        if n == '2000':
            x_2.append(float(p) / 100)
            y_2.append(float(t))
        if n == '3000':
            x_3.append(float(p) / 100)
            y_3.append(float(t))
        if n == '4000':
            x_4.append(float(p) / 100)
            y_4.append(float(t))
        if n == '5000':
            x_5.append(float(p) / 100)
            y_5.append(float(t))

    plt.plot(x_1, y_1, label='n = 1000')
    plt.plot(x_2, y_2, label='n = 2000')
    plt.plot(x_3, y_3, label='n = 3000')
    plt.plot(x_4, y_4, label='n = 4000')
    plt.plot(x_5, y_5, label='n = 5000')

    # plt.grid(True)
    plt.legend()

    plt.xlabel('p')
    plt.ylabel('t')
    plt.show()


def plot_n():  # plot n_test
    x_1 = []
    y_1 = []

    x_2 = []
    y_2 = []

    x_3 = []
    y_3 = []

    x_4 = []
    y_4 = []

    x_5 = []
    y_5 = []

    for line in sys.stdin:
        n, m, t = line.rstrip('\n').split(' ')
        if m == '50000':
            x_1.append(int(n))
            y_1.append(float(t))
        if m == '150000':
            x_2.append(int(n))
            y_2.append(float(t))
        if m == '250000':
            x_3.append(int(n))
            y_3.append(float(t))
        if m == '350000':
            x_4.append(int(n))
            y_4.append(float(t))
        if m == '450000':
            x_5.append(int(n))
            y_5.append(float(t))

    plt.plot(x_1, y_1, label='m ≈ 50000')
    plt.plot(x_2, y_2, label='m ≈ 150000')
    plt.plot(x_3, y_3, label='m ≈ 250000')
    plt.plot(x_4, y_4, label='m ≈ 350000')
    plt.plot(x_5, y_5, label='m ≈ 450000')

    plt.xlabel('n')
    plt.ylabel('t')
    plt.legend()

    plt.show()


def plot_mw():  # plot mw_test
    x_r = []
    y_r = []

    x_d = []
    y_d = []

    x_w = []
    y_w = []

    for line in sys.stdin:
        mode, mw, t = line.rstrip('\n').split(' ')
        if mode == 'r':
            x_r.append(int(mw))
            y_r.append(float(t))
        if mode == 'd':
            x_d.append(int(mw))
            y_d.append(float(t))
        if mode == 'w':
            x_w.append(int(mw))
            y_w.append(float(t))

    plt.plot(x_r, y_r, label='md random')
    plt.plot(x_d, y_d, label='md maximal')
    plt.plot(x_w, y_w, label='md minimal')

    # average
    avg_y = []
    for y1, y2, y3 in zip(y_r, y_d, y_w):
        avg_y.append((y1 + y2 + y3) / 3)

    plt.plot(x_r, avg_y, label='average')

    plt.legend()
    plt.xlabel('mw')
    plt.ylabel('t')
    plt.show()


def plot_mode(mode):
    switcher = {
        'mw': plot_mw,
        'm': plot_m,
        'n': plot_n,
        'p': plot_prim
    }

    plot = switcher.get(mode, lambda: "Invalid arguments")
    plot()


if __name__ == "__main__":
    plot_mode(sys.argv[1])
