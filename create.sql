create database monitor;

use monitor;

create table cpu
(
    time    datetime('Asia/Shanghai'),
    core    int,
    percent float
) engine MergeTree order by time;

create table memory
(
    time  datetime('Asia/Shanghai'),
    total float,
    used  float
) engine MergeTree order by time;

create table swap
(
    time  datetime('Asia/Shanghai'),
    total float,
    used  float
) engine MergeTree order by time;

create table disk_parts
(
    time       datetime('Asia/Shanghai'),
    device     String,
    mountpoint String,
    total      float,
    used       float
) engine MergeTree order by time;

create table disk_io
(
    time   datetime('Asia/Shanghai'),
    device String,
    read   float,
    write  float
) engine MergeTree order by time;

create table net_io
(
    time   datetime('Asia/Shanghai'),
    device String,
    send   float,
    recv   float
) engine MergeTree order by time;

create table net_conn
(
    time        datetime('Asia/Shanghai'),
    connections int
) engine MergeTree order by time;

create table temperatures
(
    time  datetime('Asia/Shanghai'),
    label String,
    temp  float
) engine MergeTree order by time;
