create database monitor;

use monitor;

create table machine
(
    name String,
    uuid String
) engine MergeTree primary key uuid;

create table cpu
(
    time    datetime('Asia/Shanghai'),
    uuid    String,
    core    int,
    percent float
) engine MergeTree order by time;

create table memory
(
    time  datetime('Asia/Shanghai'),
    uuid  String,
    total float,
    used  float
) engine MergeTree order by time;

create table swap
(
    time  datetime('Asia/Shanghai'),
    uuid  String,
    total float,
    used  float
) engine MergeTree order by time;

create table disk_parts
(
    time       datetime('Asia/Shanghai'),
    uuid       String,
    device     String,
    mountpoint String,
    total      float,
    used       float
) engine MergeTree order by time;

create table disk_io
(
    time   datetime('Asia/Shanghai'),
    uuid   String,
    device String,
    read   float,
    write  float
) engine MergeTree order by time;

create table net_io
(
    time   datetime('Asia/Shanghai'),
    uuid   String,
    device String,
    send   float,
    recv   float
) engine MergeTree order by time;

create table net_conn
(
    time        datetime('Asia/Shanghai'),
    uuid        String,
    connections int
) engine MergeTree order by time;

create table temperatures
(
    time  datetime('Asia/Shanghai'),
    uuid  String,
    label String,
    temp  float
) engine MergeTree order by time;
