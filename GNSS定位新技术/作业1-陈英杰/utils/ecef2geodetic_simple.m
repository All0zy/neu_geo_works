function [lat, lon, h] = ecef2geodetic_simple(x, y, z)
a = 6378137.0;
f = 1/298.257223563;
e2 = f*(2-f);
lon = atan2(y, x);
p = hypot(x, y);
lat = atan2(z, p*(1-e2));
for i = 1:5
    N = a / sqrt(1 - e2*sin(lat)^2);
    h = p/cos(lat) - N;
    lat = atan2(z, p*(1 - e2*N/(N+h)));
end
N = a / sqrt(1 - e2*sin(lat)^2);
h = p/cos(lat) - N;
end
