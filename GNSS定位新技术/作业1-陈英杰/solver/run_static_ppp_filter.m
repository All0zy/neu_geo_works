function result = run_static_ppp_filter(obs, sp3, clk, atx, cfg)
state = struct();
state.x = [cfg.eval.ref_xyz(:); 0; 0.10];
state.P = diag([ones(1,3)*cfg.filter.sig_xyz0.^2, cfg.filter.sig_clk0.^2, 0.3^2]);
state.amb_map = containers.Map('KeyType','char','ValueType','double');

sols = [];
for ie = 1:numel(obs.epochs)
    ep = obs.epochs(ie);
    if ep.sod < cfg.proc.start_sod || ep.sod > cfg.proc.end_sod
        continue
    end

    state = time_update(state, cfg);
    [state, sol] = meas_update_epoch(state, ep, sp3, clk, atx, cfg);

    if ~isempty(sol)
        sols = [sols; sol]; %#ok<AGROW>
        fprintf('[PPP %04d] %s nsat=%02d rms=%.4fm dXYZ=(%.4f, %.4f, %.4f) ZWD=%.4f\n', ...
            ie, datestr(ep.time,'yyyy-mm-dd HH:MM:SS'), sol.nsat, sol.rms, ...
            sol.xyz(1)-cfg.eval.ref_xyz(1), sol.xyz(2)-cfg.eval.ref_xyz(2), sol.xyz(3)-cfg.eval.ref_xyz(3), sol.zwd);
    end
end

if isempty(sols)
    error('PPP 未得到有效结果');
end

series = build_series(sols);
[idx_keep, w, stable_flag] = build_solution_weights(series, cfg);
idx_keep = refine_best_cluster(series, idx_keep, cfg);

xyz_keep = series.xyz(idx_keep,:);
zwd_keep = series.zwd(idx_keep);
rms_keep = series.rms(idx_keep);
ns_keep = series.nsat(idx_keep);

xyz_med = median(xyz_keep, 1);
d = xyz_keep - xyz_med;
s = max(mad(xyz_keep, 1, 1) * 1.4826, [0.02 0.02 0.02]);
rob = all(abs(d) <= 2.5*s, 2);
if nnz(rob) >= 20
    xyz_keep = xyz_keep(rob,:);
    zwd_keep = zwd_keep(rob);
    rms_keep = rms_keep(rob);
    ns_keep = ns_keep(rob);
    idx_keep = idx_keep(rob);
end

if cfg.output.use_weighted_average
    w = ns_keep ./ max(rms_keep.^2, 1e-6);
    xyz = weighted_mean(xyz_keep, w);
else
    xyz = median(xyz_keep, 1);
    w = ones(size(idx_keep));
end

xyz_std = std(xyz_keep, 0, 1)';
zwd = median(zwd_keep);

result.xyz = xyz(:);
result.xyz_std = xyz_std;
result.zwd = zwd;
result.num_valid_epochs = numel(sols);
result.solutions = sols;
result.series = series;
result.keep_idx = idx_keep;
result.weight = w;
result.stable_flag = stable_flag;
end

function state = time_update(state, cfg)
q = zeros(size(state.P));
q(1,1) = cfg.filter.q_xyz;
q(2,2) = cfg.filter.q_xyz;
q(3,3) = cfg.filter.q_xyz;
q(4,4) = cfg.filter.q_clk;
q(5,5) = cfg.filter.q_zwd;
if size(q,1) > 5
    q(6:end,6:end) = eye(size(q,1)-5) * cfg.filter.q_amb;
end
state.P = state.P + q;
end

function [state, sol] = meas_update_epoch(state, ep, sp3, clk, atx, cfg)
sol = [];
f = gps_frequencies();
lam1 = f.c / f.f1;
lam2 = f.c / f.f2;

rx_ref = state.x(1:3);
rx_obs = receiver_obs_point(rx_ref, atx, cfg);

tmp = struct('prn',{},'Pif',{},'Lif',{},'sat_xyz',{},'sat_clk',{},'rho',{},'los',{},'el',{},'m_w',{},'trop0',{},'windup',{});
clk_seed = [];

for k = 1:numel(ep.sat)
    prn = ep.sat(k);
    if isnan(ep.C1(k)) || isnan(ep.P2(k)) || isnan(ep.L1(k)) || isnan(ep.L2(k))
        continue
    end

    if isfield(ep,'P_if_sm') && numel(ep.P_if_sm) >= k && ~isnan(ep.P_if_sm(k))
        Pif = ep.P_if_sm(k);
    else
        Pif = iono_free_comb(ep.C1(k), ep.P2(k), f);
    end

    Lif = iono_free_comb(ep.L1(k)*lam1, ep.L2(k)*lam2, f);
    tau = Pif / f.c;
    t_tx = ep.sod - tau;

    sat_xyz = sp3_interp(sp3, t_tx, prn);
    if any(isnan(sat_xyz))
        continue
    end
    sat_xyz = earth_rotation_correction(sat_xyz, tau);

    sat_clk = sat_clock_interp(clk, t_tx, prn);
    if isnan(sat_clk)
        continue
    end

    rho_vec = sat_xyz - rx_obs;
    rho = norm(rho_vec);
    los = rho_vec / rho;
    [~, el] = sat_az_el(rx_obs, sat_xyz);
    if el * 180/pi < cfg.proc.elev_mask_deg
        continue
    end

    [zhd, m_h, m_w] = trop_saastamoinen(rx_obs, el);
    trop0 = m_h * zhd + m_w * state.x(5);

    windup = 0;
    if cfg.model.use_phase_windup
        windup = phase_windup_simple(rx_obs, sat_xyz);
    end

    tmp(end+1).prn = prn; %#ok<AGROW>
    tmp(end).Pif = Pif;
    tmp(end).Lif = Lif;
    tmp(end).sat_xyz = sat_xyz;
    tmp(end).sat_clk = sat_clk;
    tmp(end).rho = rho;
    tmp(end).los = los;
    tmp(end).el = el;
    tmp(end).m_w = m_w;
    tmp(end).trop0 = trop0;
    tmp(end).windup = windup;

    clk_seed(end+1,1) = Pif - rho + f.c*sat_clk - trop0; %#ok<AGROW>
end

if numel(tmp) < cfg.proc.min_sats
    return
end

state.x(4) = median(clk_seed,'omitnan');
H = [];
v = [];
R = [];
used = 0;

for i = 1:numel(tmp)
    prn = tmp(i).prn;
    key = sprintf('G%02d', prn);

    if isKey(state.amb_map, key)
        amb_idx = state.amb_map(key);
    else
        [state, amb_idx] = append_ambiguity_state(state, key, 0);
        if ~isempty(H) && size(H,2) < numel(state.x)
            H(:,end+1:numel(state.x)) = 0;
        end
    end

    calc_common = tmp(i).rho + state.x(4) - f.c*tmp(i).sat_clk + tmp(i).trop0;

    if isfield(ep,'slip')
        sat_idx = find(ep.sat == prn, 1);
        if ~isempty(sat_idx) && numel(ep.slip) >= sat_idx && ep.slip(sat_idx)
            state.x(amb_idx) = tmp(i).Lif - calc_common - tmp(i).windup;
            state.P(amb_idx, amb_idx) = cfg.filter.sig_amb^2;
        end
    end

    if state.x(amb_idx) == 0
        state.x(amb_idx) = tmp(i).Lif - calc_common - tmp(i).windup;
    end

    vc = tmp(i).Pif - calc_common;
    vp = tmp(i).Lif - (calc_common + state.x(amb_idx) + tmp(i).windup);

    hc = zeros(1, numel(state.x));
    hc(1:3) = -tmp(i).los;
    hc(4) = 1;
    hc(5) = tmp(i).m_w;

    hp = hc;
    hp(amb_idx) = 1;

    if abs(vc) > 30 || abs(vp) > 0.10
        continue
    end

    H = [H; hc; hp]; %#ok<AGROW>
    v = [v; vc; vp]; %#ok<AGROW>

    sinel = max(sin(tmp(i).el), 0.35);
    sigc = cfg.filter.sig_code / (sinel^2.0);
    sigp = cfg.filter.sig_phase / (sinel^2.5);
    R = blkdiag(R, diag([sigc^2, sigp^2])); %#ok<AGROW>
    used = used + 1;
end

if used < cfg.proc.min_sats
    return
end

hz = zeros(1, numel(state.x));
hz(5) = 1;
H = [H; hz];
v = [v; 0.10 - state.x(5)];
R = blkdiag(R, 0.03^2);

for iter = 1:cfg.proc.max_iter
    K = state.P * H' / (H * state.P * H' + R);
    dx = K * v;
    state.x = state.x + dx;

    I = eye(size(state.P));
    state.P = (I - K*H) * state.P * (I - K*H)' + K*R*K';

    post = v - H*dx;
    if norm(dx(1:min(5,numel(dx)))) < 1e-5
        break
    end
    v = post;
end

post = v;
sol.time = ep.time;
sol.sod = ep.sod;
sol.xyz = state.x(1:3);
sol.zwd = state.x(5);
sol.rms = sqrt(mean(post.^2));
sol.nsat = used;
end

function rx_obs = receiver_obs_point(rx_ref, atx, cfg)
neu_total = [0 0 0];

if isfield(cfg,'model') && isfield(cfg.model,'use_receiver_antenna_delta') && cfg.model.use_receiver_antenna_delta
    if isfield(cfg,'sta') && isfield(cfg.sta,'ant_delta_hen') && numel(cfg.sta.ant_delta_hen) == 3
        hen = cfg.sta.ant_delta_hen(:)';
        neu_total = neu_total + [hen(3), hen(2), hen(1)];
    end
end

if isfield(atx,'receiver_if_pco_neu_m') && numel(atx.receiver_if_pco_neu_m) == 3 && all(isfinite(atx.receiver_if_pco_neu_m))
    neu_total = neu_total + atx.receiver_if_pco_neu_m(:)';
end

rx_obs = rx_ref + neu2ecef_vec(rx_ref, neu_total(:));
end

function [state, idx] = append_ambiguity_state(state, key, initv)
oldn = numel(state.x);
state.x(end+1,1) = initv;
state.P(oldn+1, oldn+1) = 100^2;
state.amb_map(key) = oldn + 1;
idx = oldn + 1;
end

function series = build_series(sols)
n = numel(sols);
series.time = zeros(n,1);
series.sod = zeros(n,1);
series.xyz = zeros(n,3);
series.zwd = zeros(n,1);
series.rms = zeros(n,1);
series.nsat = zeros(n,1);
for i = 1:n
    series.time(i,1) = sols(i).time;
    series.sod(i,1) = sols(i).sod;
    series.xyz(i,:) = sols(i).xyz(:)';
    series.zwd(i,1) = sols(i).zwd;
    series.rms(i,1) = sols(i).rms;
    series.nsat(i,1) = sols(i).nsat;
end
end

function [idx_keep, w, stable_flag] = build_solution_weights(series, cfg)
n = size(series.xyz,1);
idx0 = min(max(cfg.output.convergence_skip_epochs + 1, 1), n);
xyz = series.xyz;
rmsv = series.rms;

movx = movstd(xyz(:,1), cfg.output.stable_window, 0, 'omitnan');
movy = movstd(xyz(:,2), cfg.output.stable_window, 0, 'omitnan');
movz = movstd(xyz(:,3), cfg.output.stable_window, 0, 'omitnan');

stable_flag = (movx < cfg.output.max_final_xyz_std) & ...
              (movy < cfg.output.max_final_xyz_std) & ...
              (movz < cfg.output.max_final_xyz_std) & ...
              (rmsv < cfg.output.max_final_rms);

cand = find(stable_flag & ((1:n)' >= idx0));
if numel(cand) < cfg.output.min_tail_epochs
    cand = (max(idx0, n-cfg.output.min_tail_epochs+1):n)';
end
idx_keep = cand(:);

if cfg.output.use_weighted_average
    w = series.nsat(idx_keep) ./ max(series.rms(idx_keep).^2, 1e-6);
else
    w = ones(numel(idx_keep),1);
end
end

function idx_best = refine_best_cluster(series, idx_keep, cfg)
if isempty(idx_keep)
    idx_best = idx_keep;
    return
end

win = min(cfg.output.final_pick_window, numel(idx_keep));
if numel(idx_keep) <= win
    idx_best = idx_keep;
    return
end

best_score = inf;
best_pos = 1;
for i = 1:(numel(idx_keep)-win+1)
    id = idx_keep(i:i+win-1);
    xyz = series.xyz(id,:);
    rmsv = series.rms(id);
    s = std(xyz, 0, 1);
    score = sum(s) + 0.5*median(rmsv);
    if score < best_score
        best_score = score;
        best_pos = i;
    end
end
idx_best = idx_keep(best_pos:best_pos+win-1);
end

function mu = weighted_mean(X, w)
mu = (X' * w) / sum(w);
end