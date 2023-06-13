create database monitor;

use monitor;

create table machine
(
    name String,
    uuid UUID
) engine MergeTree primary key uuid;

create table cpu
(
    time    datetime('Asia/Shanghai'),
    uuid    UUID,
    core    int,
    percent float
) engine MergeTree order by time;

create table memory
(
    time    datetime('Asia/Shanghai'),
    uuid    UUID,
    total   float,
    used    float,
    percent float
) engine MergeTree order by time;

create table swap
(
    time    datetime('Asia/Shanghai'),
    uuid    UUID,
    total   float,
    used    float,
    percent float
) engine MergeTree order by time;

create table disk_parts
(
    time       datetime('Asia/Shanghai'),
    uuid       UUID,
    device     String,
    mountpoint String,
    total      float,
    used       float,
    percent    float
) engine MergeTree order by time;

create table disk_io
(
    time   datetime('Asia/Shanghai'),
    uuid   UUID,
    device String,
    read   float,
    write  float
) engine MergeTree order by time;

create table net_io
(
    time   datetime('Asia/Shanghai'),
    uuid   UUID,
    device String,
    send   float,
    recv   float
) engine MergeTree order by time;

create table net_conn
(
    time        datetime('Asia/Shanghai'),
    uuid        UUID,
    count int
) engine MergeTree order by time;

create table temperatures
(
    time  datetime('Asia/Shanghai'),
    uuid  UUID,
    label String,
    temp  float
) engine MergeTree order by time;

create table processes
(
    time        datetime('Asia/Shanghai'),
    uuid        UUID,
    count int
) engine MergeTree order by time;