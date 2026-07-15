function obs = read_rinex2_obs_gps(filepath, cfg)
fid = fopen(filepath, 'r');
if fid < 0
    error('无法打开 OBS 文件: %s', filepath);
end
cleanup = onCleanup(@() fclose(fid));

header = struct();
obs_types = {};

while true
    line = fgetl(fid);
    if ~ischar(line)
        error('OBS 文件头未找到 END OF HEADER');
    end
    line80 = pad_line(line,80);
    tag = strtrim(line80(61:80));

    switch tag
        case 'RINEX VERSION / TYPE'
            header.version = str2double(strtrim(line80(1:9)));
            header.file_type = strtrim(line80(21));
            header.sys = strtrim(line80(41));

        case 'MARKER NAME'
            header.marker_name = strtrim(line80(1:60));

        case 'REC # / TYPE / VERS'
            header.receiver = strtrim(line80(21:40));

        case 'ANT # / TYPE'
            header.antenna_type = strtrim(line80(21:40));

        case 'APPROX POSITION XYZ'
            header.approx_xyz = sscanf(line80(1:60), '%f', [3,1])';

        case 'ANTENNA: DELTA H/E/N'
            header.ant_delta_hen = sscanf(line80(1:60), '%f', [3,1])';

        case '# / TYPES OF OBSERV'
            nobs = sscanf(line80(1:6), '%d', 1);
            vals = cell(1,nobs);
            idx = 1;
            cur = line80;
            while idx <= nobs
                for k = 1:9
                    c1 = 10 + (k-1)*6 + 1;
                    c2 = c1 + 1;
                    if c2 <= numel(cur)
                        token = strtrim(cur(c1:c2));
                        if ~isempty(token)
                            vals{idx} = token;
                            idx = idx + 1;
                            if idx > nobs
                                break;
                            end
                        end
                    end
                end
                if idx <= nobs
                    nxt = fgetl(fid);
                    if ~ischar(nxt)
                        error('OBS 文件头在读取观测类型时意外结束');
                    end
                    cur = pad_line(nxt,80);
                end
            end
            obs_types = vals;

        case 'INTERVAL'
            header.interval = sscanf(line80(1:10), '%f', 1);

        case 'TIME OF FIRST OBS'
            vals = sscanf(line80(1:43), '%f');
            header.first = vals(:)';

        case 'TIME OF LAST OBS'
            vals = sscanf(line80(1:43), '%f');
            header.last = vals(:)';

        case 'LEAP SECONDS'
            header.leap_seconds = sscanf(line80(1:6), '%f', 1);

        case 'END OF HEADER'
            break
    end
end

map = make_obs_type_map(obs_types);
epochs = struct('time', {}, 'sod', {}, 'sat', {}, 'C1', {}, 'P2', {}, 'L1', {}, 'L2', {}, 'lliL1', {}, 'lliL2', {});
gps_seen = false(1,32);

while true
    line = fgetl(fid);
    if ~ischar(line)
        break
    end
    if isempty(strtrim(line))
        continue
    end

    line80 = pad_line(line, 80);

    yr = sscanf(line80(1:3), '%d', 1);
    if isempty(yr)
        continue
    end
    mo = sscanf(line80(4:6), '%d', 1);
    dy = sscanf(line80(7:9), '%d', 1);
    hr = sscanf(line80(10:12), '%d', 1);
    mi = sscanf(line80(13:15), '%d', 1);
    se = sscanf(line80(16:26), '%f', 1);
    flag = sscanf(line80(27:29), '%d', 1);
    nsat = sscanf(line80(30:32), '%d', 1);

    if isempty(flag) || isempty(nsat)
        continue
    end

    if yr < 80
        yr = yr + 2000;
    else
        yr = yr + 1900;
    end

    if flag ~= 0
        extra_sat_lines = max(0, ceil((nsat - 12) / 12));
        for ii = 1:extra_sat_lines
            fgetl(fid);
        end
        continue
    end

    epoch_dt = datenum(yr,mo,dy,hr,mi,se);
    sod = hr*3600 + mi*60 + se;

    sat_ids = cell(1, nsat);
    cols = line80(33:68);

    extra_sat_lines = max(0, ceil((nsat - 12) / 12));
    for ii = 1:extra_sat_lines
        nxt = fgetl(fid);
        if ~ischar(nxt)
            break
        end
        nxt80 = pad_line(nxt,80);
        cols = [cols nxt80(33:68)]; %#ok<AGROW>
    end

    for k = 1:nsat
        i1 = (k-1)*3 + 1;
        i2 = k*3;
        if i2 <= numel(cols)
            sat_ids{k} = strtrim(cols(i1:i2));
        else
            sat_ids{k} = '';
        end
    end

    sat = [];
    C1 = [];
    P2 = [];
    L1 = [];
    L2 = [];
    lli1 = [];
    lli2 = [];
    nlines_obs = ceil(numel(obs_types)/5);

    for k = 1:nsat
        sid = sat_ids{k};

        blocks = cell(nlines_obs,1);
        for b = 1:nlines_obs
            raw = fgetl(fid);
            if ~ischar(raw)
                raw = '';
            end
            blocks{b} = pad_line(raw,80);
        end

        if numel(sid) < 3
            continue
        end
        if sid(1) ~= 'G'
            continue
        end

        prn = str2double(sid(2:3));
        if isnan(prn) || prn < 1 || prn > 32
            continue
        end
        gps_seen(prn) = true;

        vals = nan(1, numel(obs_types));
        llis = nan(1, numel(obs_types));
        idx = 1;

        for b = 1:nlines_obs
            cur = blocks{b};
            for j = 1:5
                if idx > numel(obs_types)
                    break
                end
                p1 = (j-1)*16 + 1;
                p2 = p1 + 13;

                if p2 <= numel(cur)
                    token = strtrim(cur(p1:p2));
                    if ~isempty(token)
                        vals(idx) = str2double(token);
                    end

                    lli_col = p1 + 14;
                    if lli_col <= numel(cur)
                        lli_token = strtrim(cur(lli_col));
                        if ~isempty(lli_token)
                            llis(idx) = str2double(lli_token);
                        end
                    end
                end
                idx = idx + 1;
            end
        end

        c1 = get_obs_value(vals, map, {'C1','P1'});
        p2 = get_obs_value(vals, map, {'P2','C2'});
        l1 = get_obs_value(vals, map, {'L1'});
        l2 = get_obs_value(vals, map, {'L2'});
        i1 = get_obs_lli(llis, map, {'L1'});
        i2 = get_obs_lli(llis, map, {'L2'});

        sat(end+1,1) = prn; %#ok<AGROW>
        C1(end+1,1) = c1; %#ok<AGROW>
        P2(end+1,1) = p2; %#ok<AGROW>
        L1(end+1,1) = l1; %#ok<AGROW>
        L2(end+1,1) = l2; %#ok<AGROW>
        lli1(end+1,1) = i1; %#ok<AGROW>
        lli2(end+1,1) = i2; %#ok<AGROW>
    end

    epochs(end+1).time = epoch_dt; %#ok<AGROW>
    epochs(end).sod = sod;
    epochs(end).sat = sat;
    epochs(end).C1 = C1;
    epochs(end).P2 = P2;
    epochs(end).L1 = L1;
    epochs(end).L2 = L2;
    epochs(end).lliL1 = lli1;
    epochs(end).lliL2 = lli2;
end

obs.header = header;
obs.obs_types = obs_types;
obs.epochs = epochs;
obs.gps_prns = find(gps_seen);
obs.freq = gps_frequencies();
obs.cfg = cfg;
end

function s = pad_line(s, n)
if ~ischar(s)
    s = char(s);
end
if numel(s) < n
    s = [s repmat(' ',1,n-numel(s))];
end
end

function map = make_obs_type_map(obs_types)
map = containers.Map();
for i = 1:numel(obs_types)
    map(obs_types{i}) = i;
end
end

function v = get_obs_value(vals, map, names)
v = NaN;
for i = 1:numel(names)
    if isKey(map, names{i})
        idx = map(names{i});
        if idx <= numel(vals)
            v = vals(idx);
            if ~isnan(v) && v ~= 0
                return
            end
        end
    end
end
end

function v = get_obs_lli(vals, map, names)
v = NaN;
for i = 1:numel(names)
    if isKey(map, names{i})
        idx = map(names{i});
        if idx <= numel(vals)
            v = vals(idx);
            return
        end
    end
end
end