USE jty_world;

-- 如果存在表，则删除它
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[City]') AND type in (N'U'))
DROP TABLE [dbo].[City];

-- 创建表
CREATE TABLE [dbo].[City] (
    NAME varchar(35) PRIMARY KEY,
    COUNTRY varchar(35),
    POP float,
    CAPITAL char(1),
    SHAPE char(13)
);
USE jty_world;

-- 如果存在表，则删除它
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Country]') AND type = N'U')
DROP TABLE [dbo].[Country];

-- 创建表
CREATE TABLE [dbo].[Country] (
    NAME varchar(35) PRIMARY KEY,
    CONT varchar(35),
    POP int,
    GDP int,
    [LIFE-EXP] float,
    SHAPE char(15)
);

USE jty_world;

-- 如果存在表，则删除它
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[River]') AND type = N'U')
DROP TABLE [dbo].[River];

-- 创建表
CREATE TABLE [dbo].[River] (
    NAME varchar(35) PRIMARY KEY,
    ORIGIN varchar(35),
    LENGTH int,
    SHAPE char(15)
);
INSERT INTO City values('Havana', 'Cuba', 2.1, 'Y', 'Pointid-1');
INSERT INTO City values('Washington, D.C.', 'USA', 3.2, 'Y', 'Pointid-2');
INSERT INTO City values('Monterrey', 'Mexico', 2.0, 'N', 'Pointid-3');
INSERT INTO City values('Toronto', 'Canada', 3.4, 'N', 'Pointid-4');
INSERT INTO City values('Brasilia', 'Brazil', 1.5, 'Y', 'Pointid-5');
INSERT INTO City values('Rosario', 'Argentina', 1.1, 'N', 'Pointid-6');
INSERT INTO City values('Ottawa', 'Canada', 0.8, 'Y', 'Pointid-7');
INSERT INTO City values('Mexico', 'Mexico', 14.1, 'Y', 'Pointid-8');
INSERT INTO City values('Buenos Aires', 'Argentina', 10.75, 'Y', 'Pointid-9');

INSERT INTO Country values('Canada', 'NAM', 30.1, 658.0, 77.08, 'Pointid-1');
INSERT INTO Country values('Mexico', 'NAM', 107.5, 694.3, 69.36, 'Pointid-2');
INSERT INTO Country values('Brazil', 'SAM', 183.3, 1004.0, 65.60, 'Pointid-3');
INSERT INTO Country values('Cuba', 'NAM', 11.7, 16.9, 75.95, 'Pointid-4');
INSERT INTO Country values('USA', 'NAM', 270.0, 8003.0, 75.75, 'Pointid-5');
INSERT INTO Country values('Argentina', 'SAM', 36.3, 348.2, 70.75, 'Pointid-6');

INSERT INTO River values ('Rio Parana','Brazil',2600,'LineStringid-1'); 
INSERT INTO River values ('St.Lawrence','USA',1200,'LineStringid-2');
INSERT INTO River values ('Rio Grande','USA',3000,'LineStringid-3');
INSERT INTO River values ('Mississippi','USA',6000,'LineStringid-4')

select name as 城市,country as 国家 from city

select *  from city
where capital= 'Y'

select name as 国家,cont as 大洲,pop as 人口 from country
where [life-exp]<70

select co.name as 首都,co.cont as 大洲,co.pop as [人口数（百万） ] from city ci,country co
where ci.country=co.name and   /*首先在country表与city表间建立联系*/
co.GDP>1000 and
ci.capital= 'Y'         /*多个条件之间用and进行连接*/

select co.name+'('+co.cont+')' as [首都（大洲）],co.pop/100 as [人口数（亿）] from city ci,country co
where ci.country=co.name and co.GDP>1000 and ci.capital='Y'

select ci.name as 河流发源地首都,ci.pop as 该城市人口数 from city ci,river ri
where ci.country=ri.origin and  ri.name= 'St.Lawrence' and ci.capital= 'Y'

select AVG (ci.Pop) as 非首都城市平均人口 from city ci
where ci.capital= 'N'

select co.cont as 大洲,AVG (co.GDP) as [continent-GDP]
from country co  group by co.cont

select MIN (ri.Length)as [min-length],ri.origin
from river ri
group by ri.origin having count (*)>1

select name from river where length =
( select MIN (ri2.Length)as [min-length]
from river ri2
group by ri2 .origin having count (*)>1
)

select co.name  from country co
where co.GDP > any( select co1.GDP
from country co1
where co1.name = 'Canada')

select co.name  from country co
where co.GDP > any( select co1.GDP
from country co1
where co1.name = 'Canada')

select ri.name from river ri
where ri.origin = 'USA'

select TOP 1 name from country
order by GDP DESC

--查询12：找出GDP大于5000亿而小于100万亿的国家
select co.name  from country co
where co.GDP > 50 and co.GDP < 1000

--查询13：列出有河流发源的各国家的居民平均寿命
select co.name,co. [LIFE-EXP] as 居民平均寿命 from country co,river ri
where ri.origin = co.name

--查询14：找出位于南美洲或者人口少于200万的城市
select ci.name
from city ci,country co
where ci.country = co.name and (co.cont = 'SAM' or ci.pop < 2)

--查询15：列出不位于南美洲的城市
select ci.name
from city ci,country co
where co.cont <> 'SAM' and co.name = ci.country

--查询16：计算人口少于1亿的国家的个数
select count (*) as 人口少于亿的国家的个数 from country co
where co.pop < 100

--查询17：找出北美洲GDP最低的国家，不要使用MIN函数
select co.name  from country co
where co.cont = 'NAM' and co.GDP < all (select co1.GDP
from country co1
where co1.name <> co.name )

select distinct co.name from country co,city ci
where co.cont = 'NAM' or ( co.name = ci.country and ci.pop < 500 and
ci.capital = 'Y')

select TOP 1 name from country
where GDP not in (select top 1 GDP
from country
order by GDP DESC
)
order by GDP DESC