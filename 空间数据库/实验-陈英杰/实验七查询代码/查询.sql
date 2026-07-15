select * from city
select * from country
select * from river
select * from street
select * from water
/*1.查询：列出COUNTRY表中所有与美国相邻的国家的名字*/

SELECT C1.cntry_name AS "Neighbors of USA"
FROM country C1, country C2
WHERE st_touches(C1.shape, C2.shape) =true AND C2.cntry_name = 'United States' 

/*2.查询：找出RIVER表中所列出的河流流经的国家*/

SELECT DISTINCT R.NAME, C.cntry_name
FROM river R, country C
WHERE st_crosses(R.shape, C.shape) = true AND R.NAME IS NOT NULL



/*3.查询：对于RIVER表中列出的河流，在CITY表中找到距离其最近的城市*/
select distinct R.name,C1.city_name
from river R, city C1
where ST_DISTANCE(C1.shape, R.shape) <= ALL (select ST_DISTANCE(C2.shape, R.shape) from city C2) and R.name is not null


/*4.查询：假设Mississippi河流能为方圆10公里以内的城市供水，列出能从该河获得供水的城市*/
select distinct C.city_name
from river R, city C
where R.name='Mississippi' and st_distance(C.shape, R.shape)<10

/*5.查询：列出COUNTRY表中每个国家的名字、人口和国土面积*/

SELECT C.cntry_name, C.pop_cntry, C.area
FROM country C

/*6.查询：求出河流在流经的各国境内的长度*/

SELECT R.NAME, C.cntry_name, st_Length(st_Intersection(R.shape, C.shape)) AS "Length"
FROM river R, country C
WHERE st_crosses(R.shape, C.shape) = true

/*7.查询：列出每个洲的首府以及其首府到赤道的距离*/
select DISTINCT ci.admin_name,ci.city_name, st_distance(st_point(0,st_y(ci.shape)),st_point(st_x(ci.shape),st_y(ci.shape))) as "distance"
from city ci
where ci.status='Provincial capital' 

/*8.查询：按其邻国数目的多少列出所有国家*/
select DISTINCT C1.cntry_name,count(C2.cntry_name)
from  country C1,country C2
where st_touches(C1.shape,C2.shape)= true
group by C1.cntry_name
order by count(C2.cntry_name)

/*9.查询：列出只有一个邻国的国家。*/

select DISTINCT C1.cntry_name
from  country C1,country C2
where st_touches(C1.shape,C2.shape)= true
group by C1.cntry_name
having count(C2.cntry_name)=1





/*10.查询：哪一个国家的邻国最多*/
select  C1.cntry_name
from  country C1,country C2
where st_touches(C1.shape,C2.shape)= true
group by C1.cntry_name
having count(C2.cntry_name)>= all(select  count(C2.cntry_name) from  country C1,country C2 where st_touches(C1.shape,C2.shape)= true group by C1.cntry_name)


/*11.查询：用SQL语句写出下面的查询，请使用OGIS扩展的数据类型和函数

a)列出City表中距离各个洲首府100公里以内的城市*/
select c1.admin_name,c1.city_name,c2.city_name as "距离首府少于100公里的城市"
from city c1,city c2
where c1.status='Provincial capital'  and st_distance(c1.shape,c2.shape)<100


/*b)位于美国和加拿大的Rainy河的长度是多少？*/
SELECT  C.cntry_name, st_Length(st_Intersection(R.shape, C.shape)) AS "国内Rainy的长度"
FROM river R, country C
WHERE st_crosses(R.shape, C.shape) = true and R.name='Rainy' 

/*c)美国和加拿大接壤吗？*/

SELECT bool(st_touches(C1.shape, C2.shape)) as "美国和加拿大是否接壤"
FROM country C1,country C2
where C1.sovereign='United States' and C2.sovereign='Canada'



/*d)列出完全在赤道以北的国家*/
select ci.city_name
from city ci
where  st_distance(st_point(0,st_y(ci.shape)),st_point(st_x(ci.shape),st_y(ci.shape))) >0




















