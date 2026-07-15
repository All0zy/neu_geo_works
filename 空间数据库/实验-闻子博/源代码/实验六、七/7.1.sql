SELECT R.name, C.cntry_name
FROM sde.river R
JOIN sde.country C ON ST_Intersects(R.shape, C.shape);
