create table users(
user_id integer primary key,
name varchar2(255),
password varchar2(255)
);
create table messages(
message_id integer primary key,
user_id integer,
text varchar2(1023),
foreign key(user_id) references users(user_id)
);
create table modified(
modified_id integer primary key,
message_id integer,
user_id integer,
foreign key(message_id) references messages(message_id),
foreign key(user_id) references users(user_id)
);
insert into users(user_id, name, password) values(1, 'admin', 'admin');
insert into users(user_id, name, password) values(2, 'user1', 'user');
insert into users(user_id, name, password) values(3, 'user2', 'user');
insert into users(user_id, name, password) values(4, 'user3', '123');
insert into users(user_id, name, password) values(5, 'user4', '1234');
insert into users(user_id, name, password) values(6, 'user5', '12345');

insert into messages values(1, 1, 'Tu m�wi admin');
insert into messages values(2, 2, 'Zostawiam sw�j wpis');
insert into messages values(3, 2, 'Kolejny post');
insert into messages values(4, 4, 'Nowy w pracy');

create table messages(
message_id int not null,
user_id int,
text varchar2(1023),
primary key (message_id)
);

create sequence message_id MINVALUE 1 START with 1;

insert into messages values(message_id.nextval, 1,'wiadomosc pierwsza');