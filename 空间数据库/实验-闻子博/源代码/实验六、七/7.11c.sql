SELECT ST_Touches(
  (SELECT shape FROM sde.country WHERE cntry_name = 'Argentina'),
  (SELECT shape FROM sde.country WHERE cntry_name = 'Brazil')
) AS touching;
