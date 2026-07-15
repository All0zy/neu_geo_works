function [az, el] = sat_az_el(rec_xyz, sat_xyz)
[lat, lon, ~] = ecef2geodetic_simple(rec_xyz(1), rec_xyz(2), rec_xyz(3));
d = sat_xyz(:) - rec_xyz(:);
R = [-sin(lon) cos(lon) 0; ...
     -sin(lat)*cos(lon) -sin(lat)*sin(lon) cos(lat); ...
      cos(lat)*cos(lon)  cos(lat)*sin(lon) sin(lat)];
enu = R * d;
az = atan2(enu(1), enu(2));
if az < 0, az = az + 2*pi; end
el = atan2(enu(3), hypot(enu(1), enu(2)));
end
