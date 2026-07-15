-- Database: template_postgis

-- DROP DATABASE template_postgis;

CREATE DATABASE template_postgis
  WITH OWNER = postgres
       ENCODING = 'UTF8';
ALTER DATABASE template_postgis SET search_path="$user", public, sde;
