function clk = read_clk_whu(filepath, ~)
fid = fopen(filepath, 'r');
if fid < 0
    error('无法打开 CLK 文件: %s', filepath);
end
cleanup = onCleanup(@() fclose(fid));

records_t = [];
records_c = [];
base_day = NaN;
while true
    line = fgetl(fid);
    if ~ischar(line)
        break
    end
    if numel(line) < 40
        continue
    end
    if startsWith(line, 'AS G')
        prn = str2double(line(5:7));
        yy = str2double(strtrim(line(9:12)));
        mo = str2double(strtrim(line(14:15)));
        dd = str2double(strtrim(line(17:18)));
        hh = str2double(strtrim(line(20:21)));
        mi = str2double(strtrim(line(23:24)));
        ss = str2double(strtrim(line(26:35)));
        val = sscanf(line(41:end), '%f');
        if isempty(val)
            continue
        end
        if isnan(base_day)
            base_day = datenum(yy,mo,dd);
        end
        day_offset = (datenum(yy,mo,dd) - base_day) * 86400;
        sod = day_offset + hh*3600 + mi*60 + ss;
        records_t(end+1,1) = sod; %#ok<AGROW>
        records_c(end+1,1) = prn; %#ok<AGROW>
        records_c(end,2) = val(1); %#ok<AGROW>
    end
end

t = unique(records_t);
clk.sod = t;
clk.bias = nan(numel(t),32);
for i = 1:size(records_c,1)
    it = find(abs(t-records_t(i))<1e-6,1);
    clk.bias(it, records_c(i,1)) = records_c(i,2);
end
clk.interval = median(diff(t));
end
