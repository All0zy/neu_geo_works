function xyz_rot = earth_rotation_correction(xyz, tau)
omega = 7.2921151467e-5;
ang = omega * tau;
R = [cos(ang) sin(ang) 0; -sin(ang) cos(ang) 0; 0 0 1];
xyz_rot = R * xyz(:);
end
