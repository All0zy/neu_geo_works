function v_ecef = neu2ecef_vec(rec_xyz, v_neu)
[lat, lon, ~] = ecef2geodetic_simple(rec_xyz(1), rec_xyz(2), rec_xyz(3));
R = [-sin(lat)*cos(lon) -sin(lon) cos(lat)*cos(lon); ...
     -sin(lat)*sin(lon)  cos(lon) cos(lat)*sin(lon); ...
      cos(lat)           0        sin(lat)];
v_ecef = R * v_neu(:);
end
