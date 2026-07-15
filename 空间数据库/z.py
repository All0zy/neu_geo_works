def z_index(x, y):
    print("====计算坐标({},{})====".format(x,y))
    x_bin = bin(x)[2:].zfill(4)
    y_bin = bin(y)[2:].zfill(4)
    index = ''.join([a + b for a, b in zip(x_bin, y_bin)])
    index_ten = int(index, 2)
    print("x->{}, y->{}, 合并->{}, Z索引值->{}".format(x_bin,y_bin,index,index_ten))

coordinates = [(1,0), (3, 8), (4, 6), (7, 9)]
for x, y in coordinates:
    index = z_index(x, y)