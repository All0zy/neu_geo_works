-- Database: sde

-- DROP DATABASE sde;

CREATE DATABASE sde
  WITH OWNER = postgres
       ENCODING = 'UTF8';
ALTER DATABASE sde SET search_path="$user", public, sde;
GRANT ALL ON DATABASE sde TO public;
GRANT ALL ON DATABASE sde TO postgres;
GRANT ALL ON DATABASE sde TO sde;
