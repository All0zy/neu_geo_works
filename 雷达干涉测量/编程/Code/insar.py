# %%
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio

# 读取 mat 文件
data = sio.loadmat("./S1_Fentale/InSAR_data.mat")
dem = np.asarray(data['dem'])
imm = np.asarray(data['im_m'])
ims = np.asarray(data['im_s'])

scale = 20/9

def showImg(img, title=None, cmap='gray'):
    plt.rcParams['font.family'] = ['SimSun', 'Times New Roman']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(6, 6), dpi=100)
    plt.imshow(img, cmap=cmap, aspect=scale)
    plt.title(title)
    plt.colorbar(shrink=0.75)
    plt.savefig(f'./{title}.png', dpi=300, bbox_inches='tight') # bbobox_inches='tight' 
    plt.show()

# %%
# DEM 图像
showImg(dem, title='研究区域的DEM影像', cmap='jet')

# %%
# imm 图像幅度和相位图
abs_imm = np.abs(imm)
phase_imm = np.angle(imm)

showImg(10 * np.log10(abs_imm), cmap='gray', title='主影像的幅度图')
showImg(phase_imm, cmap='jet', title='主影像的相位图')

# %%
# ims 图像幅度和相位图
abs_ims = np.abs(ims)
phase_ims = np.angle(ims)

showImg(10 * np.log10(abs_ims), cmap='gray', title='辅影像的幅度图')
showImg(phase_ims, cmap='jet', title='辅影像的相位图')

# %%
# 绘制 imm 和 ims 的干涉图
conj_mult = imm * np.conj(ims)
angle_conj_mult = np.angle(conj_mult)
showImg(angle_conj_mult, cmap='jet', title='主影像与辅影像的干涉图')

# %%
# 绘制 imm 和 ims 的相干系数图
from scipy.ndimage import uniform_filter
# uniform_filter 用于计算局部平均值，size 参数控制窗口大小

size = 7
num = uniform_filter(imm * np.conj(ims), size=size)
pwr_imm = uniform_filter(abs(imm) ** 2, size=size)
pwr_ims = uniform_filter(abs(ims) ** 2, size=size)

den = np.sqrt(pwr_imm * pwr_ims)
coherence = np.abs(num) / den
# clip 将相干系数限制在 [0, 1] 范围内
coherence = np.clip(coherence, 0, 1)
showImg(coherence, cmap='jet', title=f'主影像与辅影像的相干系数图 (窗口大小={size}x{size})')

# %%
# 去除平地效应
inc_deg = 36.6569                 # 入射角(度)
B_perp = 95.9                     # 垂直基线(m)
lam = 0.056                       # 波长(m)
R0 = 847587.2953                  # 中心斜距(m)
dr = 2.329541                     # range pixel spacing(m)

ifg_phase = np.angle(conj_mult)

rows, cols = ifg_phase.shape
x = (np.arange(cols) - cols / 2.0) * dr

theta = np.deg2rad(inc_deg)
phi_flat_1d = -4.0 * np.pi / lam * (B_perp / (R0 * np.tan(theta))) * x
phi_flat = np.tile(phi_flat_1d, (rows, 1))

ifg_flat_removed = np.angle(np.exp(1j * (ifg_phase - phi_flat)))

showImg(np.angle(np.exp(1j * phi_flat)), title='平地相位模型图', cmap='jet')
showImg(ifg_flat_removed, title='去平地效应后的相位图', cmap='jet')

# %%
# 去地形相位
# 1) 以中位数高程作为参考面，构造 Δh
h_ref = np.nanmedian(dem)
delta_h = dem - h_ref

# 2) 地形相位模型: phi_topo = -4π B_perp Δh / (λ R sinθ)
phi_topo = -4.0 * np.pi / lam * (B_perp / (R0 * np.sin(theta))) * delta_h

# 3) 去地形相位（相位在复平面相减再取角度）
ifg_topo_removed = np.angle(np.exp(1j * (ifg_flat_removed - phi_topo)))

# 4) 显示
showImg(np.angle(np.exp(1j * phi_topo)), title='地形相位模型图', cmap='jet')
showImg(ifg_topo_removed, title='去平地且去地形后相位图', cmap='jet')

# %%
# 中值滤波 + 中值-自适应滤波 + 复数维纳滤波 + Goldstein滤波 + 
from scipy.ndimage import median_filter, uniform_filter
from scipy.signal import wiener

phase_in = ifg_topo_removed  # 输入：去平地+去地形后的缠绕相位

# 1) 中值滤波
phase_med = median_filter(phase_in, size=5, mode='nearest')
phase_med = np.angle(np.exp(1j * phase_med))  # 重新wrap到[-pi, pi]

# 2) 自适应滤波（基于局部复相位一致性）
z_in = np.exp(1j * phase_in)

win = 7
zr = uniform_filter(np.real(z_in), size=win, mode='nearest')
zi = uniform_filter(np.imag(z_in), size=win, mode='nearest')
z_mean = zr + 1j * zi

# 局部一致性 rho in [0, 1]：越接近1说明相位越稳定
rho = np.abs(z_mean)

# 自适应权重：高一致性保细节，低一致性强平滑
alpha = np.clip((rho - 0.25) / 0.50, 0.0, 1.0)
z_adapt = alpha * z_in + (1.0 - alpha) * z_mean
phase_adapt = np.angle(z_adapt)

# 3) 复杂滤波：复数维纳滤波（对复数实部/虚部分别做Wiener）
z_in = np.exp(1j * phase_in)
zr_w = wiener(np.real(z_in), (7, 7))
zi_w = wiener(np.imag(z_in), (7, 7))
z_wiener = zr_w + 1j * zi_w
phase_wiener = np.angle(z_wiener)

# 4) Goldstein滤波（频域滤波）
def goldstein_filter_phase(phase, alpha=0.7, eps=1e-8):
    z = np.exp(1j * phase)
    spec = np.fft.fft2(z)
    mag = np.abs(spec)

    # 频谱幅度归一化后构建权重，alpha越大抑噪越强
    weight = (mag / (np.max(mag) + eps)) ** alpha
    z_filtered = np.fft.ifft2(spec * weight)
    return np.angle(z_filtered)

phase_goldstein = goldstein_filter_phase(phase_in, alpha=0.7) # alpha=0.7 是一个经验值，可以根据实际情况调整

# 绘图对比
showImg(phase_med, title='中值滤波效果图', cmap='jet')
showImg(phase_adapt, title='自适应滤波效果图', cmap='jet')
showImg(phase_wiener, title='复数维纳滤波效果图', cmap='jet')
showImg(phase_goldstein, title='Goldstein滤波效果图', cmap='jet')

# %%
# 基于深度学习的自监督相位滤波
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
except ImportError as e:
    raise ImportError('当前环境缺少 torch，请先安装 PyTorch 后再运行该单元') from e

phase_in = ifg_topo_removed.astype(np.float32)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def phase_to_2ch(phase):
    return np.stack([np.cos(phase), np.sin(phase)], axis=0).astype(np.float32)


def phase_from_2ch(arr):
    return np.arctan2(arr[1], arr[0])


class PhasePatchDataset(Dataset):
    def __init__(self, phase, patch_size=128, stride=64, mask_ratio=0.1):
        self.phase = phase
        self.patch_size = patch_size
        self.mask_ratio = mask_ratio
        self.patches = []

        h, w = phase.shape
        for i in range(0, h - patch_size + 1, stride):
            for j in range(0, w - patch_size + 1, stride):
                self.patches.append(phase[i:i + patch_size, j:j + patch_size])

    def __len__(self):
        return len(self.patches)

    def __getitem__(self, idx):
        patch = self.patches[idx]
        target = phase_to_2ch(patch)
        mask = (np.random.rand(*patch.shape) < self.mask_ratio).astype(np.float32)

        input_patch = target.copy()
        input_patch[:, mask > 0] = 0.0

        return (
            torch.from_numpy(input_patch),
            torch.from_numpy(target),
            torch.from_numpy(mask[None, ...])
        )


class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.net(x)


class SmallUNet(nn.Module):
    def __init__(self, in_ch=2, out_ch=2, base=32):
        super().__init__()
        self.enc1 = DoubleConv(in_ch, base)
        self.pool1 = nn.MaxPool2d(2)
        self.enc2 = DoubleConv(base, base * 2)
        self.pool2 = nn.MaxPool2d(2)
        self.bottleneck = DoubleConv(base * 2, base * 4)
        self.up2 = nn.ConvTranspose2d(base * 4, base * 2, 2, stride=2)
        self.dec2 = DoubleConv(base * 4, base * 2)
        self.up1 = nn.ConvTranspose2d(base * 2, base, 2, stride=2)
        self.dec1 = DoubleConv(base * 2, base)
        self.out = nn.Conv2d(base, out_ch, 1)

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        b = self.bottleneck(self.pool2(e2))
        d2 = self.up2(b)
        d2 = torch.cat([d2, e2], dim=1)
        d2 = self.dec2(d2)
        d1 = self.up1(d2)
        d1 = torch.cat([d1, e1], dim=1)
        d1 = self.dec1(d1)
        return self.out(d1)


train_dataset = PhasePatchDataset(phase_in, patch_size=128, stride=64, mask_ratio=0.1)
train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=0, drop_last=True)

model = SmallUNet().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)


def masked_loss(pred, target, mask):
    mask2 = mask.repeat(1, 2, 1, 1)
    return F.mse_loss(pred * mask2, target * mask2)


epochs = 10
model.train()
for epoch in range(epochs):
    running = 0.0
    for x_in, x_tgt, mask in train_loader:
        x_in = x_in.to(device)
        x_tgt = x_tgt.to(device)
        mask = mask.to(device)

        pred = model(x_in)
        loss = masked_loss(pred, x_tgt, mask)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running += loss.item()

    print(f'Epoch {epoch + 1}/{epochs}, loss={running / max(len(train_loader), 1):.6f}')

model.eval()
with torch.no_grad():
    full_in = torch.from_numpy(phase_to_2ch(phase_in)[None, ...]).to(device)
    full_out = model(full_in)[0].cpu().numpy()

phase_dl = phase_from_2ch(full_out)
phase_dl = np.angle(np.exp(1j * phase_dl))

showImg(phase_dl, title='深度学习自监督滤波结果', cmap='jet')


