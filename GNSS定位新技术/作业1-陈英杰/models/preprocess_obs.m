function obs = preprocess_obs(obs, cfg)
if cfg.proc.enable_cycle_slip
    obs = detect_cycle_slip_basic(obs);
end
if cfg.proc.enable_hatch
    obs = hatch_smooth_obs(obs, cfg.proc.hatch_window);
end
end
