SELECT c.cntry_name, c.pop_cntry, ST_Area(c.shape) AS Area
FROM sde.country AS c;
