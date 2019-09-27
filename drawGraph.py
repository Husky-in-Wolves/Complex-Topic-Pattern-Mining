import matplotlib.pyplot as plt
import numpy as np, re


markers = [".", "+", "x", "."]
linestyles = ["-", "--", "--", "--"]
baseColor = ["red", "green", "royalblue", "khaki", "y", "g", "b", "r"]
color=[["y", "g", "b", "r"], ["orange", "c", "royalblue", "tomato"]]


def plot_scatter(X, L, P, labels, xlabel, ylabel, title):
    for i, y in enumerate(L):
        plt.plot(range(len(X)), y, c=baseColor[i], marker=markers[i], label=labels[i], ms=11, ls=linestyles[i], linewidth=2)
    plt.scatter(len(X)-1, P, c="black", marker="*", label=labels[-1], s=120)
    ''' add Legend and title'''
    plt.legend(labels=labels, loc='best', fontsize=13); plt.title(title)
    ''' add the lables of x, y axes '''
    plt.xlabel(xlabel, fontsize=15); plt.ylabel(ylabel, fontsize=15); plt.tick_params(labelsize=12)
    ''' limit the range of x, y axes '''
    plt.xticks(range(len(X)), X); plt.ylim(0.7, 1.0)
    ''' add the background '''
    plt.grid(linestyle=":", color="gray", axis="y")
    plt.show()
