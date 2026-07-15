function dt = sat_clock_interp(clk, t_abs, prn)
col = clk.bias(:,prn);
idx = find(~isnan(col));
if numel(idx) < 2
    dt = NaN;
    return
end
t = clk.sod(idx);
y = col(idx);
if t_abs < t(1) || t_abs > t(end)
    dt = NaN;
    return
end
dt = interp1(t, y, t_abs, 'linear');
end
