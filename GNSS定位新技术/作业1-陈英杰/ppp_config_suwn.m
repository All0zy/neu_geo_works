% ========================================================================
% 文件名: ppp_config_suwn.m
% 功能: PPP 工程统一配置文件。
% 说明:
%   该文件集中设置所有输入文件路径、解算控制参数、滤波参数、误差模型开关、
%   以及标准坐标与输出控制参数。后续换数据时，优先修改本文件。
%
% 主要配置内容:
%   files.*    : 输入文件路径
%   proc.*     : 解算时间范围、截止高度角、预处理控制参数
%   filter.*   : 卡尔曼滤波初始方差与过程噪声参数
%   model.*    : 各种模型改正开关
%   eval.*     : 标准坐标(参考坐标)
%   output.*   : 最终结果筛选、加权、作图与保存控制
% ========================================================================
function cfg = ppp_config_suwn()
root = fileparts(mfilename('fullpath'));
data_dir = fullfile(root, 'data');

% 观测文件路径
cfg.files.obs = fullfile(data_dir, 'suwn0020.26o');
cfg.files.sp3 = {
    fullfile(data_dir, 'WUM0MGXFIN_20260010000_01D_05M_ORB.SP3')
    fullfile(data_dir, 'WUM0MGXFIN_20260020000_01D_05M_ORB.SP3')
    fullfile(data_dir, 'WUM0MGXFIN_20260030000_01D_05M_ORB.SP3')
    };
% 精密钟差文件路径
cfg.files.clk = fullfile(data_dir, 'WUM0MGXFIN_20260020000_01D_30S_CLK.CLK');
% 天线文件路径
cfg.files.atx = fullfile(data_dir, 'I20.ATX');
% 偏差文件路径(OSB/BIA)
cfg.files.bia = fullfile(data_dir, 'WUM0MGXFIN_20260020000_01D_01D_OSB.BIA');


% 当前解算系统：仅使用 GPS
cfg.proc.use_system = 'G';
cfg.proc.sample_interval = 30;
cfg.proc.start_sod = 0;
cfg.proc.end_sod = 86400 - cfg.proc.sample_interval;
cfg.proc.elev_mask_deg = 20;
cfg.proc.min_sats = 5;
cfg.proc.max_iter = 4;
cfg.proc.outlier_code_m = 8.0;
cfg.proc.outlier_phase_m = 0.05;
cfg.proc.hatch_window = 100;
cfg.proc.enable_hatch = true;
cfg.proc.enable_cycle_slip = true;

cfg.filter.sig_code = 0.60;
cfg.filter.sig_phase = 0.006;
cfg.filter.sig_zwd = 0.02;
cfg.filter.sig_amb = 100.0;
cfg.filter.sig_xyz0 = 100.0;
cfg.filter.sig_clk0 = 1e5;
cfg.filter.q_xyz = 1e-7;
cfg.filter.q_clk = 1e2;
cfg.filter.q_zwd = 1e-4;
cfg.filter.q_amb = 0.0;

cfg.model.use_receiver_apc = true;
cfg.model.use_receiver_antenna_delta = false;
cfg.model.use_phase_windup = true;
cfg.model.use_relativistic = false;
cfg.model.use_solid_earth_tide = false;

% 标准坐标，用于误差评估，不直接参与 PPP 观测方程
cfg.eval.ref_xyz = [-3062022.7737, 4055453.7317, 3841815.7127];

% 最终结果提取阶段是否采用加权平均
cfg.output.use_weighted_average = true;
cfg.output.convergence_skip_epochs = 900;
cfg.output.min_tail_epochs = 240;
cfg.output.plot_result = true;
cfg.output.save_plot = false;
cfg.output.use_bia = true;
cfg.output.stable_window = 240;
cfg.output.max_final_rms = 0.70;
cfg.output.max_final_xyz_std = 0.25;
cfg.output.final_pick_window = 180;
end