function obs = detect_cycle_slip_basic(obs)
f = gps_frequencies();
lam1 = f.c / f.f1;
lam2 = f.c / f.f2;
prev = containers.Map('KeyType','char','ValueType','any');

for i = 1:numel(obs.epochs)
    ep = obs.epochs(i);
    slip = false(size(ep.sat));
    for k = 1:numel(ep.sat)
        prn = ep.sat(k);
        key = sprintf('G%02d', prn);
        if isnan(ep.L1(k)) || isnan(ep.L2(k)) || isnan(ep.C1(k)) || isnan(ep.P2(k))
            slip(k) = true;
            continue
        end
        gf = ep.L1(k)*lam1 - ep.L2(k)*lam2;
        mw = melbourne_wubbena(ep.C1(k), ep.P2(k), ep.L1(k), ep.L2(k), f);
        lli_hit = (~isnan(ep.lliL1(k)) && ep.lliL1(k) > 0) || (~isnan(ep.lliL2(k)) && ep.lliL2(k) > 0);
        if isKey(prev, key)
            old = prev(key);
            if abs(gf - old.gf) > 0.08 || abs(mw - old.mw) > 4 || lli_hit
                slip(k) = true;
            end
        else
            slip(k) = true;
        end
        prev(key) = struct('gf',gf,'mw',mw);
    end
    obs.epochs(i).slip = slip;
end
end

function mw = melbourne_wubbena(C1, P2, L1, L2, f)
phi_wl = (f.c/f.f1)*L1 - (f.c/f.f2)*L2;
code_nw = (f.f1*C1 + f.f2*P2) / (f.f1 + f.f2);
lam_wl = f.c/(f.f1-f.f2);
mw = (phi_wl - code_nw)/lam_wl;
end
