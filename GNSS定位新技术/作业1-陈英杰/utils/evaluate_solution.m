function [enu, dxyz, err3d] = evaluate_solution(xyz, ref_xyz)
dxyz = xyz(:) - ref_xyz(:);
[lat, lon, ~] = ecef2geodetic_simple(ref_xyz(1), ref_xyz(2), ref_xyz(3));
R = [-sin(lon) cos(lon) 0; ...
     -sin(lat)*cos(lon) -sin(lat)*sin(lon) cos(lat); ...
      cos(lat)*cos(lon)  cos(lat)*sin(lon) sin(lat)];
enu = R * dxyz;
err3d = norm(dxyz);
end
