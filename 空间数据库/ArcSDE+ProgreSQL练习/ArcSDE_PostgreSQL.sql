--1.查询：列出COUNTRY表中所有与美国相邻的国家的名字
select c1.cntry_name AS 与美国相邻的国家
from country c1, country c2
where st_touches(c1.shape, c2.shape) and c2.gmi_cntry = 'USA';
--2.查询：找出RIVER表中所列出的河流流经的国家
select r.name, c.cntry_name
from river r, country c
where r.name is not null and st_crosses(r.shape, c.shape);
--3.查询：对于RIVER表中列出的河流，在CITY表中找到距离其最近的城市
select r.name, c1.city_name
from city c1, river r 
where st_distance(c1.shape, r.shape) < all (
  select st_distance(c2.shape, r.shape)
  from city c2
  where c1.city_name != c2.city_name
);
--4.查询：假设圣劳伦斯河能为方圆300公里以内的城市供水，列出能从该河获得供水的城市
select c.city_name
from city c,river r
where st_intersects(c.shape, st_buffer(r.shape, 300)) and r.name='Saint Louis';
--5.查询：列出COUNTRY表中每个国家的名字、人口和国土面积
select c.cntry_name, c.pop_cntry, c.area
from country c;
--6.查询：求出河流在流经的各国境内的长度
select r.name, c.cntry_name, st_length(st_intersection(r.shape, c.shape))
from river r, country c 
where st_crosses(r.shape, c.shape);
--7.查询：列出每个州的首府以及其到赤道的距离
SELECT ci.admin_name, ci.city_name, st_distance(st_point(st_x(ci.shape),0),st_point(st_x(ci.shape),st_y(ci.shape))) as "distance"
FROM city ci
WHERE ci.status='Provincial capital'
--8.查询：按其邻国数目的多少列出所有国家
select c1.cntry_name, count(c2.cntry_name)
from country c1, country c2
where st_touches(c1.shape, c2.shape)
GROUP BY c1.cntry_name
ORDER BY count(c2.cntry_name);
--9.查询：列出只有一个邻国的国家。
select c1.cntry_name
from country c1, country c2
where st_touches(c1.shape, c2.shape)
GROUP BY c1.cntry_name
HAVING count(c2.cntry_name) = 1;
--10.查询：哪一个国家的邻国最多SELECT c1.cntry_name
SELECT c1.cntry_name
FROM country c1, country c2 
WHERE ST_Touches(c1.shape, c2.shape)
GROUP BY c1.cntry_name
HAVING COUNT(c2.cntry_name) >= ALL (
        SELECT COUNT(c4.cntry_name)
        FROM country c3
        JOIN country c4 
        ON ST_Touches(c3.shape, c4.shape)
        GROUP BY c3.cntry_name
    );       
--11.查询：用SQL语句写出下面的查询，请使用OGIS扩展的数据类型和函数
/*a)列出City表中距离各个洲首府100公里以内的城市*/
SELECT DISTINCT c1.city_name, c2.city_name as "100km以内的城市"
FROM sde.city c1,sde.city c2  
WHERE c1.status = 'Provincial capital' AND ST_Distance(c1.shape,c2.shape)<100 AND c1.city_name!=c2.city_name
ORDER BY c1.city_name
/*b)位于美国和加拿大的Rainy河的长度是多少？*/
SELECT c1.cntry_name,ST_Length(ST_Intersection(r1.shape,c1.shape)) as "Rainy河的长度"
FROM sde.river r1,sde.country c1
WHERE ST_Crosses(r1.shape,c1.shape) AND c1.cntry_name IN ('Canada','United States') AND r1.name='Rainy'
/*c)美国和加拿大接壤吗？*/
SELECT ST_Touches(c1.shape, c2.shape) as "美国和加拿大接壤吗"  
FROM sde.country c1,sde.country c2
WHERE c2.gmi_cntry = 'USA' AND c1.gmi_cntry ='CAN';
/*d)列出完全在赤道以北的国家*/
SELECT c1.cntry_name as "完全在赤道以北的国家"
FROM sde.country c1
WHERE ST_MinY(c1.shape) >0;
