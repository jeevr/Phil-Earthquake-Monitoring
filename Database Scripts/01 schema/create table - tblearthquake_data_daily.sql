
SELECT name AS schema_name
FROM sys.schemas
ORDER BY name;

-- raw table





-- drop table if exists tblearthquake_data_daily
create table raw.tblearthquake_data_daily (
    date_time varchar,
    date varchar,
    time varchar,
    latitude varchar,
    longitude varchar,
    depth_km varchar,
    depth_km_symbol varchar,
    magnitude varchar,
    location varchar,
    hlink varchar,
    details varchar
);


select *
from raw.tblearthquake_data_daily



-- drop table if exists tblearthquake_data_daily
create table fnl.tblearthquake_data_daily (
    date date,
    time time,
    geo_lat double precision,
    geo_long double precision,
    geo_point varchar,
    location varchar,
    depth_km double precision,
    depth_km_symbol varchar,
    magnitude double precision,
    info_no int,
    depth_of_focus_km int,
    origin varchar,
    expecting_damage varchar,
    expecting_aftershocks varchar,
    page_link varchar
)

select *
from fnl.tblearthquake_data_daily
