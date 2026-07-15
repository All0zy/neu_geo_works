function obs = apply_bia_osb(obs, bia)
f = gps_frequencies();
lam1 = f.c / f.f1;
lam2 = f.c / f.f2;

for i = 1:numel(obs.epochs)
    ep = obs.epochs(i);
    ns = numel(ep.sat);

    for k = 1:ns
        prn = ep.sat(k);
        if prn < 1 || prn > 32
            continue
        end

        if ~isnan(ep.C1(k)) && ~isnan(bia.code(prn,1))
            ep.C1(k) = ep.C1(k) - bia.code(prn,1);
        end

        if ~isnan(ep.P2(k))
            if ~isnan(bia.code(prn,2))
                ep.P2(k) = ep.P2(k) - bia.code(prn,2);
            elseif ~isnan(bia.code(prn,3))
                ep.P2(k) = ep.P2(k) - bia.code(prn,3);
            end
        end

        if ~isnan(ep.L1(k)) && ~isnan(bia.phase(prn,1))
            ep.L1(k) = ep.L1(k) - bia.phase(prn,1) / lam1;
        end

        if ~isnan(ep.L2(k))
            if ~isnan(bia.phase(prn,2))
                ep.L2(k) = ep.L2(k) - bia.phase(prn,2) / lam2;
            elseif ~isnan(bia.phase(prn,3))
                ep.L2(k) = ep.L2(k) - bia.phase(prn,3) / lam2;
            end
        end
    end

    obs.epochs(i) = ep;
end
end