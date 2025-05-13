
SELECT name AS schema_name
FROM sys.schemas
ORDER BY name;

-- raw table





drop table if exists raw.tblearthquake_data_daily;
create table raw.tblearthquake_data_daily (
    date_time varchar(max),
    date varchar(max),
    time varchar(max),
    latitude varchar(max),
    longitude varchar(max),
    depth_km varchar(max),
    depth_km_symbol varchar(max),
    magnitude varchar(max),
    location varchar(max),
    hlink varchar(max),
    details varchar(max)
);


select *
from raw.tblearthquake_data_daily

truncate table raw.tblearthquake_data_daily


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
