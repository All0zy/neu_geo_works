import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re


def read_coordinates(file_path):
    coordinates = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(r'Position \(X, Y, Z\): (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)', line)
            if match:
                x, y, z = map(float, match.groups())
                coordinates.append((x, y, z))
    return coordinates


def plot_3d(coordinates):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x_vals = [coord[0] for coord in coordinates]
    y_vals = [coord[1] for coord in coordinates]
    z_vals = [coord[2] for coord in coordinates]

    ax.scatter(x_vals, y_vals, z_vals, c='r', marker='o')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()


if __name__ == "__main__":
    file_path = '新建 文本文档 (2).txt'
    coordinates = read_coordinates(file_path)
    plot_3d(coordinates)