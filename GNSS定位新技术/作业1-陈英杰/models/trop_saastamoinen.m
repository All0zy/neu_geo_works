function [zhd, m_h, m_w] = trop_saastamoinen(rec_xyz, elev_rad)
[lat, ~, h] = ecef2geodetic_simple(rec_xyz(1), rec_xyz(2), rec_xyz(3));
lat_deg = abs(lat * 180/pi);

P = 1013.25 * (1 - 2.2557e-5 * max(h,0))^5.2568;
T = 15.0 - 6.5e-3 * max(h,0) + 273.15;
RH = 0.50;

zhd = 0.0022768 * P / (1 - 0.00266*cos(2*lat) - 0.00028*h/1e3);
e = RH * 6.108 * exp((17.15*(T-273.15)) / (234.7 + (T-273.15)));
zwd0 = 0.002277 * (1255/T + 0.05) * e;
if isnan(zwd0)
    zwd0 = 0.10;
end

[aht, bht, cht, awt, bwt, cwt] = niell_coeff(lat_deg);
sinE = max(sin(elev_rad), 0.05);

m_h = mapf(sinE, aht, bht, cht) + ...
      (1/sinE - mapf(sinE, 2.53e-5, 5.49e-3, 1.14e-3)) * (h/1000);
m_w = mapf(sinE, awt, bwt, cwt);

if ~isfinite(m_h), m_h = 1/sinE; end
if ~isfinite(m_w), m_w = 1/sinE; end
if ~isfinite(zhd), zhd = 2.3; end
if ~isfinite(zwd0), zwd0 = 0.10; end %#ok<NASGU>
end

function m = mapf(sinE, a, b, c)
m = (1 + a/(1 + b/(1 + c))) / (sinE + a/(sinE + b/(sinE + c)));
end

function [ah,bh,ch,aw,bw,cw] = niell_coeff(lat_deg)
lat_tab = [15 30 45 60 75];
ah_tab = [1.2769934e-3 1.2683230e-3 1.2465397e-3 1.2196049e-3 1.2045996e-3];
bh_tab = [2.9153695e-3 2.9152299e-3 2.9288445e-3 2.9022565e-3 2.9024912e-3];
ch_tab = [62.610505e-3 62.837393e-3 63.721774e-3 63.824265e-3 64.258455e-3];
aw_tab = [5.8021897e-4 5.6794847e-4 5.8118019e-4 5.9727542e-4 6.1641693e-4];
bw_tab = [1.4275268e-3 1.5138625e-3 1.4572752e-3 1.5007428e-3 1.7599082e-3];
cw_tab = [4.3472961e-2 4.6729510e-2 4.3908931e-2 4.4626982e-2 5.4736038e-2];

lat_use = min(max(lat_deg,15),75);
ah = interp1(lat_tab, ah_tab, lat_use, 'linear');
bh = interp1(lat_tab, bh_tab, lat_use, 'linear');
ch = interp1(lat_tab, ch_tab, lat_use, 'linear');
aw = interp1(lat_tab, aw_tab, lat_use, 'linear');
bw = interp1(lat_tab, bw_tab, lat_use, 'linear');
cw = interp1(lat_tab, cw_tab, lat_use, 'linear');
end