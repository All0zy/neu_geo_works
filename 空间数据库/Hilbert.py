import numpy as np

def tdimh(a, b):
    a_bin = format(a, '03b')
    b_bin = format(b, '03b')
    c = a_bin[0] + b_bin[0] + a_bin[1] + b_bin[1] + a_bin[2] + b_bin[2]
    
    d1 = binh(a_bin[0] + b_bin[0])
    d2 = binh(a_bin[1] + b_bin[1])
    d3 = binh(a_bin[2] + b_bin[2])
    
    s = [d1, d2, d3]
    
    if d1 == 0:
        if d2 == 3:
            d2 = 1
        elif d2 == 1:
            d2 = 3
            
        if d3 == 3:
            d3 = 1
        elif d3 == 1:
            d3 = 3
    
    if d1 == 3:
        if d2 == 0:
            d2 = 2
        elif d2 == 2:
            d2 = 0
            
        if d3 == 0:
            d3 = 2
        elif d3 == 2:
            d3 = 0
    
    if d2 == 0:
        if d3 == 1:
            d3 = 3
        elif d3 == 3:
            d3 = 1
    
    if d2 == 3:
        if d3 == 0:
            d3 = 2
        elif d3 == 2:
            d3 = 0
    
    s = [d1, d2, d3]
    o = d1 * 4**2 + d2 * 4 + d3
    return c, s, o

def binh(y):
    if y == '00':
        return 0
    elif y == '01':
        return 1
    elif y == '10':
        return 3
    elif y == '11':
        return 2
    else:
        return None

x = np.array([0, 1, 2, 3, 4, 5, 6, 7])
y = np.array([0, 1, 2, 3, 4, 5, 6, 7])

s = np.zeros((8, 8), dtype=int)
c_matrix = np.empty((8, 8), dtype=object)
m_matrix = np.empty((8, 8), dtype=object)

for i in range(8):
    for j in range(8):
        c, m, o = tdimh(x[i], y[j])
        s[j, i] = o
        c_matrix[j, i] = c
        m_matrix[j, i] = ''.join(map(str, m))

op = np.zeros((8, 8), dtype=int)
for k in range(8):
    opp = s[8 - k - 1, :]
    op[k, :] = opp

c_matrix_flipped = np.empty((8, 8), dtype=object)
for k in range(8):
    c_matrix_flipped[k, :] = c_matrix[8 - k - 1, :]

m_matrix_flipped = np.empty((8, 8), dtype=object)
for k in range(8):
    m_matrix_flipped[k, :] = m_matrix[8 - k - 1, :]

# 打印结果
print("\n转换后的六位二进制矩阵:")
print(c_matrix_flipped)
print("\n转换的3bit数据矩阵:")
print(m_matrix_flipped)
print("\n最终输出矩阵:")
print(op)

def transformMatrix(s):
    transformed_s = s.copy()
    for i in range(len(s)):
        if s[i] == 0:
            transformed_s[i+1:] = 4 - transformed_s[i+1:]
        elif s[i] == 3:
            transformed_s[i+1:] = 2 - transformed_s[i+1:]
    return transformed_s