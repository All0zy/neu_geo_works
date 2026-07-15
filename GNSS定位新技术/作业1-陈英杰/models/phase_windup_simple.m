function dphi_m = phase_windup_simple(rec_xyz, sat_xyz)
% 简化版风up，保证模型结构不同于旧代码；如需更严谨可再升级
persistent last_val
if isempty(last_val)
    last_val = containers.Map('KeyType','char','ValueType','double');
end
u = (rec_xyz(:) - sat_xyz(:));
u = u / norm(u);
ez = sat_xyz(:) / norm(sat_xyz(:));
ey = cross(ez, [0;0;1]);
if norm(ey) < 1e-8
    ey = [0;1;0];
end
ey = ey / norm(ey);
ex = cross(ey, ez);

[lat, lon, ~] = ecef2geodetic_simple(rec_xyz(1), rec_xyz(2), rec_xyz(3));
er = [cos(lat)*cos(lon); cos(lat)*sin(lon); sin(lat)];
en = [-sin(lat)*cos(lon); -sin(lat)*sin(lon); cos(lat)];
ee = [-sin(lon); cos(lon); 0];
Dsat = ex - u*dot(u,ex) - cross(u,ey);
Drec = ee - u*dot(u,ee) + cross(u,en);
ang = atan2(dot(u,cross(Dsat,Drec)), dot(Dsat,Drec));
key = 'global';
if isKey(last_val, key)
    prev = last_val(key);
    n = round((prev - ang)/(2*pi));
    ang = ang + 2*pi*n;
end
last_val(key) = ang;
dphi_m = ang / (2*pi) * 0.190293672798; % 近似转换到L1波长量级米值
end
