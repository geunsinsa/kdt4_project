# 크롤링한 리뷰 데이터베이스 및 테이블 생성 코드
create database musinsareview;
use musinsareview;

create table tbl_review(
idx int not null,
review varchar(16000) not null
);

TRUNCATE table tbl_review;

select * from tbl_review;