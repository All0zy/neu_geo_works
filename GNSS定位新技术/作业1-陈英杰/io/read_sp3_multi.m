function sp3 = read_sp3_multi(file_list, ~)
nfile = numel(file_list);
all_t = [];
all_pos = nan(0,32,3);
day_dn = nan(nfile,1);
tmp = cell(nfile,1);

for i = 1:nfile
    tmp{i} = read_sp3_one(file_list{i});
    day_dn(i) = tmp{i}.day_dn;
end

if nfile >= 2
    base_dn = day_dn(ceil(nfile/2));
else
    base_dn = day_dn(1);
end

for i = 1:nfile
    one = tmp{i};
    offset = (one.day_dn - base_dn) * 86400;
    all_t = [all_t; one.sod(:) + offset]; %#ok<AGROW>
    all_pos = cat(1, all_pos, one.pos);
end

[all_t, ia] = unique(all_t, 'stable');
all_pos = all_pos(ia,:,:);

sp3.sod = all_t;
sp3.pos = all_pos;
sp3.interval = median(diff(all_t));
end

function sp3 = read_sp3_one(filepath)
fid = fopen(filepath, 'r');
if fid < 0
    error('无法打开 SP3 文件: %s', filepath);
end
cleanup = onCleanup(@() fclose(fid));

pos = nan(288,32,3);
sod = nan(288,1);
current_idx = 0;
base_day = NaN;

while true
    line = fgetl(fid);
    if ~ischar(line)
        break
    end

    if startsWith(line, '*')
        vals = sscanf(line(2:end), '%f');
        yy = vals(1);
        mm = vals(2);
        dd = vals(3);
        hh = vals(4);
        mi = vals(5);
        ss = vals(6);

        if isnan(base_day)
            base_day = datenum(yy,mm,dd);
        end

        current_idx = current_idx + 1;
        sod(current_idx) = hh*3600 + mi*60 + ss;

    elseif startsWith(line, 'PG')
        prn = str2double(line(3:4));
        vals = sscanf(line(5:end), '%f');
        if prn >= 1 && prn <= 32 && current_idx >= 1 && numel(vals) >= 3
            pos(current_idx,prn,1:3) = vals(1:3) * 1000;
        end
    end
end

pos = pos(1:current_idx,:,:);
sod = sod(1:current_idx);

sp3.sod = sod;
sp3.pos = pos;
sp3.day_dn = base_day;
end