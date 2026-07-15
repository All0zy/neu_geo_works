function obs = hatch_smooth_obs(obs, window)
f = gps_frequencies();
lam1 = f.c / f.f1;
lam2 = f.c / f.f2;

state = containers.Map('KeyType','char','ValueType','any');

for i = 1:numel(obs.epochs)
    ns = numel(obs.epochs(i).sat);

    if ~isfield(obs.epochs, 'P_if_sm')
        [obs.epochs.P_if_sm] = deal([]);
    end

    obs.epochs(i).P_if_sm = nan(ns,1);

    ep = obs.epochs(i);

    for k = 1:ns
        prn = ep.sat(k);
        key = sprintf('G%02d', prn);

        if isfield(ep, 'slip') && numel(ep.slip) >= k && ep.slip(k)
            if isKey(state, key)
                remove(state, key);
            end
        end

        if isnan(ep.C1(k)) || isnan(ep.P2(k)) || isnan(ep.L1(k)) || isnan(ep.L2(k))
            continue
        end

        Pif = iono_free_comb(ep.C1(k), ep.P2(k), f);
        Lif = iono_free_comb(ep.L1(k)*lam1, ep.L2(k)*lam2, f);

        if isKey(state, key)
            st = state(key);
            n = min(st.n + 1, window);
            Psm = (Pif + (n-1) * (st.Psm + (Lif - st.Lif_prev))) / n;
            st.n = n;
            st.Psm = Psm;
            st.Lif_prev = Lif;
            state(key) = st;
        else
            st = struct('n', 1, 'Psm', Pif, 'Lif_prev', Lif);
            state(key) = st;
        end

        obs.epochs(i).P_if_sm(k,1) = state(key).Psm;
    end
end
end