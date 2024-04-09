create database cinema_mitra_db;

select * from movies join show_times_table on movies.id=show_times_table.movie_id;