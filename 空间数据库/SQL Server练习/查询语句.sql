/*1.查询1：列出City表中所有城市及其所属的国家*/
select name as 城市名,country as 所属国家
from City;
/*2.查询2：列出City表中是首都的城市的属性*/
select *
from City
where capital = 'Y';
/*3.查询3：列出Country表中人均寿命低于70岁的国家的属性*/
select *
from Country
Where life_exp < 70;
/*4.查询4：列出GDP超过1万亿美元的国家的首都和人口数*/
select co.name as 国家,ci.name as 国家首都,co.pop as 国家人口数
from Country co,City ci
Where ci.country = co.name and ci.capital = 'Y';
/*5.查询5：圣劳伦斯河发源地国家的首都的名字是什么？该城市的人口是多少*/
select r.origin as 发源国家, ci.name as 首都, ci.pop as 首都人口数
from River r,Country co,City ci
where r.name = 'St.Lawrence'
and r.origin = co.name 
and co.name = ci.country 
and ci.capital = 'Y';
/*6.查询6：City表中列出的非首都城市的平均人口是多少*/
select avg(pop) as 非首都城市的平均人口
from City
where capital = 'N';
/*7.查询7：求出各个大洲的平均GDP。*/
select cont as 洲, avg(GDP) as 平均GDP
from Country
group by cont;
/*8.查询8：对每一个至少是两条河流发源地的国家，找到发源于它的最短的河流的名字*/
SELECT origin AS 发源地, name AS 最短的河流名字
FROM river r1
WHERE length = (
    SELECT MIN(length)
    FROM river r2
    WHERE r2.origin = r1.origin
)
AND origin IN (
    SELECT origin
    FROM river
    GROUP BY origin
    HAVING COUNT(*) >= 2
);
/*9.查询9：列出GDP超过加拿大的国家。*/
SELECT c1.name
FROM Country c1, Country c2
WHERE c2.name = 'Canada' and c1.gdp > c2.gdp;
/*10.查询10：流进美国的河流的名字*/
select name
from river
where origin = 'USA';
/*11.查询11：找出GDP排名第一的国家*/
SELECT NAME
FROM Country
WHERE GDP >= all (SELECT GDP FROM Country);
/*12.查询12：找出GDP大于5000亿而小于100万亿的国家*/
SELECT NAME
FROM Country
WHERE GDP > 500 and GDP < 100000;
/*13.查询13：列出有河流发源的各国家的居民平均寿命*/
select distinct r.origin as 河流发源的国家, c.life_exp as 居民平均寿命
from River r, Country c
where r.origin = c.name;
/*14.查询14：找出位于南美洲或者人口少于200万的城市*/
select ci.name
from Country co, City ci
where ci.country = co.name and (co.cont = 'SAM' or ci.pop < 2);
/*15.查询15：列出不位于南美洲的城市*/
select ci.name
from Country co, City ci
where ci.country = co.name and co.cont != 'SAM';
/*16.查询16：计算人口少于1亿的国家的个数*/
select count(*) as 人口少于1亿的国家的个数
from Country
where pop < 100;
/*17.查询17：找出北美洲GDP最低的国家，不要使用MIN函数*/
SELECT NAME
FROM Country
WHERE GDP <= all (SELECT GDP FROM Country WHERE cont = 'NAM')
	and cont = 'NAM';
/*18.查询18：列出北美洲所有的国家以及首都人口少于500万的国家*/
select distinct co.name
from City ci, Country co
where ci.country = co.name and (co.cont = 'NAM' or (ci.capital = 'Y' and ci.pop < 5));
/*19.查询19：找出GDP排名第二的国家*/
select name
from Country
order by gdp Desc
offset 1 rows /*跳过前1行*/
fetch next 1 row only; /*取接下来1行*/
