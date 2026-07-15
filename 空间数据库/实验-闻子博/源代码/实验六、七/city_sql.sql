SELECT f_table_name, srid
FROM sde_geometry_columns
WHERE f_table_name = 'city';


SELECT registration_id
FROM sde_table_registry
WHERE table_name = 'city';


CREATE TABLE sde.city
(
  objectid integer NOT NULL,
  gid smallint,
  area numeric(38,8),
  perimeter numeric(38,8),
  cities_ numeric(38,8),
  cities_id numeric(38,8),
  city_name character varying(50),
  gmi_admin character varying(50),
  admin_name character varying(50),
  fips_cntry character varying(50),
  cntry_name character varying(50),
  status character varying(50),
  pop_rank smallint,
  pop_class character varying(50),
  port_id smallint,
  shape st_point
)

delete from sde.city

insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'0','0.000','0.000','20.000000000','53.000000000','Bismarck','USA-NDA','North Dakota','US','United States','Provincial capital','7','Less than 50000','0',sde.st_geometry('POINT (-100.7833025517 46.79999918311)',2));
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'1','0.000','0.000','24.000000000','54.000000000','Pierre','USA-SDA','South Dakota','US','United States','Provincial capital','7','Less than 50000','0',sde.st_geometry('POINT (-100.3499985517 44.36669918311)',2));
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'2','0.000','0.000','374.000000000','428.000000000','Winnipeg','CAN-MNT','Manitoba','CA','Canada','Provincial capital','3','500000 to 1000000','0',sde.st_geometry('POINT (-97.1240005517 49.92100118311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'3','0.000','0.000','556.000000000','1998.000000000','Saint Paul','USA-MNN','Minnesota','US','United States','Provincial capital','4','250000 to 500000','0',sde.st_geometry('POINT (-93.0650025517 45.02100018311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'4','0.000','0.000','561.000000000','208.000000000','Minneapolis','USA-MNN','Minnesota','US','United States','Other','2','1000000 to 5000000','0',sde.st_geometry('POINT (-93.3077925517 44.92418718311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'5','0.000','0.000','608.000000000','224.000000000','Milwaukee','USA-WIS','Wisconsin','US','United States','Other','2','1000000 to 5000000','4860',sde.st_geometry('POINT (-87.9907375517 43.06794718311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'6','0.000','0.000','609.000000000','2020.000000000','Madison','USA-WIS','Wisconsin','US','United States','Provincial capital','5','100000 to 250000','0',sde.st_geometry('POINT (-89.4000015517 43.06666518311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'7','0.000','0.000','642.000000000','232.000000000','Chicago','USA-ILL','Illinois','US','United States','Other','1','5000000 and greater','4800',sde.st_geometry('POINT (-87.6413035517 41.82654618311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'8','0.000','0.000','658.000000000','1992.000000000','Des Moines','USA-IOW','Iowa','US','United States','Provincial capital','5','100000 to 250000','0',sde.st_geometry('POINT (-93.6220015517 41.59799918311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'9','0.000','0.000','694.000000000','2004.000000000','Lincoln','USA-NEB','Nebraska','US','United States','Provincial capital','5','100000 to 250000','0',sde.st_geometry('POINT (-96.6819995517 40.80699918311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'10','0.000','0.000','748.000000000','1991.000000000','Indianapolis','USA-IND','Indiana','US','United States','Provincial capital','3','500000 to 1000000','0',sde.st_geometry('POINT (-86.1350025517 39.81399918311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'11','0.000','0.000','750.000000000','1990.000000000','Springfield','USA-ILL','Illinois','US','United States','Provincial capital','5','100000 to 250000','0',sde.st_geometry('POINT (-89.6539995517 39.79399918311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'12','0.000','0.000','782.000000000','1993.000000000','Topeka','USA-KAN','Kansas','US','United States','Provincial capital','5','100000 to 250000','0',sde.st_geometry('POINT (-95.6949995517 39.04600118311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'13','0.000','0.000','785.000000000','266.000000000','Kansas sde.city','USA-KAN','Kansas','US','United States','Other','2','1000000 to 5000000','0',sde.st_geometry('POINT (-94.6265635517 38.99411818311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'14','0.000','0.000','799.000000000','269.000000000','St. Louis','USA-MOS','Missouri','US','United States','Other','2','1000000 to 5000000','0',sde.st_geometry('POINT (-90.3419795517 38.63888518311)',2) );
insert into sde.city values ((SELECT o_base_id FROM sde.i8_get_ids(2,1)),'15','0.000','0.000','803.000000000','2000.000000000','Jefferson sde.city','USA-MOS','Missouri','US','United States','Provincial capital','7','Less than 50000','0',sde.st_geometry('POINT (-92.1689985517 38.58000218311)',2) );
