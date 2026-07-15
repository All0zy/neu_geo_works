% ========================================================================
% 文件名: run_ppp_suwn.m
% 功能: PPP 主程序入口。
% 说明:
%   1) 读取配置文件 ppp_config_suwn.m；
%   2) 读取观测文件(.o)、精密轨道(SP3)、精密钟差(CLK)、天线文件(ATX)、偏差文件(BIA)；
%   3) 调用观测预处理模块进行周跳探测、Hatch 平滑等；
%   4) 调用静态 PPP 滤波器得到最终解算坐标；
%   5) 输出 PPP 结果、与标准坐标的差值、ENU 误差和 3D 误差；
%   6) 保存 ppp_result.mat 结果文件。
%
% 使用方法:
%   直接在 MATLAB 当前路径位于本工程根目录时运行:
%       run_ppp_suwn
% ========================================================================
clc; clear; close all;
addpath(genpath(fileparts(mfilename('fullpath'))));

% 读取统一配置，包括数据路径、滤波参数、标准坐标等
cfg = ppp_config_suwn();

fprintf('============================================================\n');
fprintf('开始 SUWN + WHU GPS 双频静态 PPP\n');
fprintf('OBS : %s\n', cfg.files.obs);
fprintf('SP3 : %s\n', strjoin(cfg.files.sp3, ', '));
fprintf('CLK : %s\n', cfg.files.clk);
fprintf('ATX : %s\n', cfg.files.atx);
if isfield(cfg.files,'bia')
    fprintf('BIA : %s\n', cfg.files.bia);
end
fprintf('============================================================\n');

% 读取 RINEX 观测文件，解析每个历元的 GPS 双频观测值
obs = read_rinex2_obs_gps(cfg.files.obs, cfg);
cfg.sta.ant_delta_hen = obs.header.ant_delta_hen;

% 读取并拼接 SP3 精密轨道文件
sp3 = read_sp3_multi(cfg.files.sp3, cfg);
% 读取 WHU 精密钟差文件
clk = read_clk_whu(cfg.files.clk, cfg);
% 读取天线文件，并提取当前接收机天线的 PCO 信息
atx = read_atx_igs(cfg.files.atx, obs.header.antenna_type, cfg);

if isfield(cfg.files,'bia') && cfg.output.use_bia && exist(cfg.files.bia,'file')
    % 读取 Bias-SINEX(OSB) 文件，为码偏差/相位偏差改正做准备
    bia = read_bia_osb(cfg.files.bia);
    % 将 BIA 偏差逐历元逐卫星作用到观测值上
    obs = apply_bia_osb(obs, bia);
end

fprintf('观测历元数: %d\n', numel(obs.epochs));
fprintf('GPS 卫星数: %d\n', numel(obs.gps_prns));
fprintf('测站: %s\n', obs.header.marker_name);
fprintf('天线: %s\n', obs.header.antenna_type);

% 预处理观测值：目前包括周跳探测与 Hatch 平滑
obs = preprocess_obs(obs, cfg);
% 调用静态 PPP 主滤波器，获得最终坐标解和历元序列结果
result = run_static_ppp_filter(obs, sp3, clk, atx, cfg);

fprintf('\n============================================================\n');
fprintf('PPP 结束\n');
fprintf('有效历元数: %d\n', result.num_valid_epochs);
fprintf('ZWD (m): %.4f\n', result.zwd);
fprintf('坐标 STD (m): %.4f %.4f %.4f\n', result.xyz_std(1), result.xyz_std(2), result.xyz_std(3));
fprintf('最终解算坐标 XYZ (m): %.4f %.4f %.4f\n', result.xyz(1), result.xyz(2), result.xyz(3));

 % 将最终解算坐标与标准坐标进行比较，输出 dXYZ / ENU / 3D 误差
[enu, dxyz, err3d] = evaluate_solution(result.xyz, cfg.eval.ref_xyz);
fprintf('标准坐标 XYZ (m): %.4f %.4f %.4f\n', cfg.eval.ref_xyz(1), cfg.eval.ref_xyz(2), cfg.eval.ref_xyz(3));
fprintf('解算坐标-标准坐标 dXYZ (mm): %.1f %.1f %.1f\n', dxyz(1)*1000, dxyz(2)*1000, dxyz(3)*1000);
fprintf('ENU 误差 (mm): %.1f %.1f %.1f\n', enu(1)*1000, enu(2)*1000, enu(3)*1000);
fprintf('3D误差 (mm): %.1f\n', err3d*1000);
fprintf('============================================================\n');


save(fullfile(fileparts(mfilename('fullpath')), 'ppp_result.mat'), 'result');