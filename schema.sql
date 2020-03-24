create table if not exists apps (
	app_name text,
	developer_name text,
	mail text,
	gp_link text,
	created_at datetime
);

create unique index app_name_developer_name on apps (app_name, developer_name);
