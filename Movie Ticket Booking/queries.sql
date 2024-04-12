create database cinema_mitra_db;

select * from movies join show_times_table on movies.id=show_times_table.movie_id;

insert into confirmed_bookings values(
"varad@gmail.com",
2,
"Normal"
,"left",
"Uri",
"10 50 pm",
"12:34",
"ddss",
2
);


select max(ticket_id) from confirmed_bookings;

create database chatbot_db;

use chatbot_db;


create table bookings(
ticket_id int primary key,
user_gmail varchar(200),
movie_name varchar(300),
section varchar(30),
position varchar(30),
seats int,
seat_numbers varchar(100),
show_time varchar(30),
ticket_url text
);






