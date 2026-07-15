function atx = read_atx_igs(filepath, antenna_type, ~)
fid = fopen(filepath, 'r');
if fid < 0
    error('无法打开 ATX 文件: %s', filepath);
end
cleanup = onCleanup(@() fclose(fid));

anttype = strtrim(antenna_type);
rcv_pco = nan(2,3); % G01/G02 -> N E U (mm)
sat_pco = nan(32,2,3); % prn, freq, neu(mm)
in_block = false;
cur_type = '';
cur_sat = 0;
cur_is_rcv = false;
cur_freq = 0;

while true
    line = fgetl(fid);
    if ~ischar(line)
        break
    end
    line = pad_line(line, 80);
    label = strtrim(line(61:80));
    switch label
        case 'START OF ANTENNA'
            in_block = true;
            cur_type = '';
            cur_sat = 0;
            cur_is_rcv = false;
            cur_freq = 0;
        case 'TYPE / SERIAL NO'
            if ~in_block, continue; end
            lhs = strtrim(line(1:20));
            syschar = strtrim(line(21));
            if startsWith(lhs, 'G') && numel(lhs) >= 3 && all(isstrprop(lhs(2:3),'digit'))
                cur_is_rcv = false;
                cur_sat = str2double(lhs(2:3));
                cur_type = lhs;
            elseif strcmp(strtrim(line(1:20)), anttype)
                cur_is_rcv = true;
                cur_sat = 0;
                cur_type = anttype;
            elseif strcmp(syschar, 'G') && all(isstrprop(strtrim(line(22:23)),'digit'))
                cur_is_rcv = false;
                cur_sat = str2double(strtrim(line(22:23)));
            end
        case 'START OF FREQUENCY'
            freq_code = strtrim(line(4:6));
            if strcmp(freq_code, 'G01')
                cur_freq = 1;
            elseif strcmp(freq_code, 'G02')
                cur_freq = 2;
            else
                cur_freq = 0;
            end
        case 'NORTH / EAST / UP'
            if cur_freq == 0
                continue
            end
            vals = sscanf(line(1:60), '%f');
            if numel(vals) >= 3
                if cur_is_rcv
                    rcv_pco(cur_freq,:) = vals(1:3)';
                elseif cur_sat >= 1 && cur_sat <= 32
                    sat_pco(cur_sat,cur_freq,:) = vals(1:3);
                end
            end
        case 'END OF ANTENNA'
            in_block = false;
    end
end

atx.receiver_pco_neu_mm = rcv_pco;
atx.sat_pco_neu_mm = sat_pco;
atx.antenna_type = anttype;
atx.receiver_if_pco_neu_m = iono_free_pco(rcv_pco) ./ 1000;
end

function ifpco = iono_free_pco(pco)
f = gps_frequencies();
a1 = f.f1^2 / (f.f1^2 - f.f2^2);
a2 = -f.f2^2 / (f.f1^2 - f.f2^2);
ifpco = a1 * pco(1,:) + a2 * pco(2,:);
end

function s = pad_line(s,n)
if numel(s) < n
    s = [s repmat(' ',1,n-numel(s))];
end
end
