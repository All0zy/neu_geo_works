function bia = read_bia_osb(filepath)
fid = fopen(filepath, 'r');
if fid < 0
    error('无法打开 BIA 文件: %s', filepath);
end
cleanup = onCleanup(@() fclose(fid));

c = 299792458.0;
bia.file = filepath;
bia.code = nan(32,3);   % [C1C C2W C2L] in m
bia.phase = nan(32,3);  % [L1C/L1W L2W L2L] in m

while true
    line = fgetl(fid);
    if ~ischar(line)
        break
    end
    if numel(line) < 80
        continue
    end
    if ~startsWith(line, ' OSB  G')
        continue
    end

    prn = str2double(strtrim(line(11:13)));
    obs1 = strtrim(line(24:26));
    val = sscanf(line(71:end), '%f', 1);
    if isnan(prn) || prn < 1 || prn > 32 || isempty(val)
        continue
    end
    val_m = val * 1e-9 * c;

    switch obs1
        case 'C1C'
            bia.code(prn,1) = val_m;
        case 'C2W'
            bia.code(prn,2) = val_m;
        case 'C2L'
            bia.code(prn,3) = val_m;
        case {'L1C','L1W'}
            bia.phase(prn,1) = val_m;
        case 'L2W'
            bia.phase(prn,2) = val_m;
        case 'L2L'
            bia.phase(prn,3) = val_m;
    end
end
end