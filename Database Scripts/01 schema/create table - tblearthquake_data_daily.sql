
-- drop table if exists tblearthquake_data_daily
create table tblearthquake_data_daily (
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