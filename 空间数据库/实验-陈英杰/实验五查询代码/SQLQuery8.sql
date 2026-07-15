-- ?1?City????
USE cyj_world;
-- City???NAME?COUNTRY
SELECT NAME AS , COUNTRY AS 
FROM City;

-- ?2?City????
USE cyj_world;
-- ??CityCAPITAL???'Y'???¼??
SELECT *
FROM City
WHERE CAPITAL = 'Y';

-- ?3?Country?70???
USE cyj_world;
-- ??Country[LIFE-EXP]????70?¼??
SELECT *
FROM Country
WHERE [LIFE-EXP] < 70;

-- ?4?GDP1?????
USE cyj_world;
-- ??CountryGDP10000City???
SELECT City.NAME,Country.POP
FROM Country,City
WHERE Country.NAME=City.COUNTRY AND City.CAPITAL='Y' AND Country.GDP>100;

--?5????????ôó????
USE cyj_world;
-- ?River????'St.Lawrence'?????ORIGIN?City?ù???
SELECT City.NAME,City.POP
FROM River
JOIN City on  City.COUNTRY=River.ORIGIN AND City.CAPITAL = 'Y'
WHERE River.NAME='St.Lawrence';

--?6City????????
USE cyj_world;
--CityCAPITAL?'N'???POP????
SELECT AVG(City.POP) As  ???
FROM City
WHERE City.CAPITAL='N';

--?7??GDP
USE cyj_world;
-- ?CONT???ÿGDP??
SELECT   Country.CONT AS  ,AVG(Country.GDP) AS ?GDP
FROM Country
Group by Country.CONT;

--?8ÿ??????????
USE cyj_world;
-- ???????????2 
-- ?River????????
SELECT River.ORIGIN,River.NAME AS ?
FROM River
WHERE River.ORIGIN IN
(
    SELECT ORIGIN
    FROM River
    GROUP BY ORIGIN
    HAVING COUNT(*) >= 2
) AND River.LENGTH=
(
    SELECT MIN(River.LENGTH)
    FROM River
);

--?9?GDPô??
USE cyj_world;
-- ?ôGDP???GDP???¼
SELECT   Country.NAME 
FROM Country
WHERE Country.GDP>(SELECT Country.GDP FROM Country WHERE Country.NAME='Canada')

--?10?
USE cyj_world;
--??ORIGIN ?USA?????
SELECT NAME AS 
FROM River
WHERE ORIGIN = 'USA';

--?11?GDP??
USE cyj_world;
-- ?GDP????¼
SELECT   Country.NAME 
FROM Country
WHERE Country.GDP>=ALL(SELECT Country.GDP FROM Country);

--?12?GDP5000??100??
USE cyj_world;
-- ??GDP??50001000000???¼
SELECT NAME AS , GDP
FROM Country
WHERE GDP > 5000 AND GDP < 1000000;

--?13???????
USE cyj_world;
-- 
SELECT Country.NAME,Country.[LIFE-EXP] AS ?
FROM Country,River 
WHERE River.ORIGIN=Country.NAME;

--?14????200?
USE cyj_world;
-- CityCountry???
-- ????CONT = 'SAM' ???City.POP ?200??¼
SELECT City.NAME AS , City.POP AS ?, Country.CONT AS ?
FROM City,Country 
WHERE City.COUNTRY = Country.NAME AND (Country.CONT = 'SAM' OR City.POP < 200);

--?15????
USE cyj_world;
-- CityCountry????CONT 'SAM' ??¼
SELECT City.NAME AS , Country.CONT AS ?
FROM City,Country 
WHERE City.COUNTRY = Country.NAME AND Country.CONT != 'SAM';

--?16?1????
USE cyj_world;
-- ??CountryPOP???100???1?100 ?¼?
SELECT COUNT(*) AS ?1???
FROM Country
WHERE POP < 100;

--?17?GDP?????MIN
USE cyj_world;
SELECT Country.NAME AS GDP??
FROM Country
WHERE Country.CONT='NAM' AND GDP<=ALL(SELECT GDP FROM Country );

--?18??????500?
USE cyj_world;
-- CountryCity
-- ??????500?
SELECT Country.NAME AS 
FROM Country ,City
WHERE Country.NAME = City.COUNTRY AND City.CAPITAL = 'Y'AND Country.CONT = 'NAM'AND City.POP < 500;

--?19?GDP??
USE cyj_world;
SELECT TOP 1 NAME, GDP
FROM Country
-- ? GDP ?????
WHERE GDP NOT IN (
    SELECT TOP 1 GDP 
    FROM Country 
    ORDER BY GDP DESC
)
ORDER BY GDP DESC;