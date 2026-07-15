function sat_xyz = sp3_interp(sp3, t_abs, prn)
xyz = squeeze(sp3.pos(:,prn,:));
valid = all(~isnan(xyz),2);
if nnz(valid) < 9
    sat_xyz = [NaN;NaN;NaN];
    return
end
t = sp3.sod(valid);
xyz = xyz(valid,:);
if t_abs < t(1) || t_abs > t(end)
    sat_xyz = [NaN;NaN;NaN];
    return
end
n = find(t <= t_abs, 1, 'last');
st = max(1, n-4);
fn = min(numel(t), st+8);
st = max(1, fn-8);
sel = st:fn;
if numel(sel) < 9
    sat_xyz = [NaN;NaN;NaN];
    return
end
sat_xyz = zeros(3,1);
for j = 1:3
    sat_xyz(j) = lagrange_interp(t(sel), xyz(sel,j), t_abs);
end
end
