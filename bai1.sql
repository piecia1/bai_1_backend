
"""Kod do utworzenia bazy danych oraz wpisania przykładowych danych
"""
create table messages(
message_id int not null,
user_id int,
text varchar2(1023),
primary key (message_id)
);

create table users(
user_id int primary key,
name varchar2(255),
password varchar2(255)
);

create table allowed_messages(
user_id int,
message_id int 
);

create sequence user_id MINVALUE 1 START with 1;
create sequence message_id MINVALUE 1 START with 1;

insert into users values(user_id.nextval, 'user1','haslo1');
insert into users values(user_id.nextval, 'user2','haslo2');
insert into users values(user_id.nextval, 'user3','haslo3');

insert into messages values(message_id.nextval, 1,'wiadomosc pierwsza');
insert into messages values(message_id.nextval, 2,'kolejna widomosc');
insert into messages values(message_id.nextval, 3,'Trzecia widomosc');





