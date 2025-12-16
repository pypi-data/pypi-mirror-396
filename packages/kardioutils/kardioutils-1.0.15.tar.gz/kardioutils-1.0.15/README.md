DL Utils

# core
is_numeric_str, check_float, check_int, check_str, check, check_list_str, check_dict

# env
config_load

# log
AppLog, BaseLog

# com

# fs

# df

# db

# mq

# auth

# rest (restapp, restutils)

# wsgi

# etl

# ju
em principio para funcionar basta colocar a tabela user_orgs
Alterar a bd update :
———
ALTER TABLE wlists
ADD COLUMN org INT NOT NULL DEFAULT 1;
———
CREATE SEQUENCE orgs_id_seq;
ALTER TABLE orgs
ALTER COLUMN id SET DEFAULT nextval('orgs_id_seq');
SELECT setval('orgs_id_seq', (SELECT MAX(id) FROM orgs));
———
UPDATE users
SET org = 1
WHERE org IS NULL;
ALTER TABLE users
ALTER COLUMN org SET NOT NULL;
————————————————————
ALTER TABLE ecgs
ADD COLUMN org INT;
UPDATE ecgs
SET org = 1;
ALTER TABLE ecgs
ALTER COLUMN org SET NOT NULL;
——————————————————


ALTER TABLE users
ADD CONSTRAINT fk_users_org
FOREIGN KEY (org) REFERENCES orgs(id);

ALTER TABLE wlists
ADD CONSTRAINT fk_wlists_org
FOREIGN KEY (org) REFERENCES orgs(id);

ALTER TABLE ecgs
ADD CONSTRAINT fk_ecgs_org
FOREIGN KEY (org) REFERENCES orgs(id);
—

CREATE TABLE user_orgs (
    user_id INT NOT NULL,
    org_id  INT NOT NULL,
    PRIMARY KEY (user_id, org_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (org_id)  REFERENCES orgs(id)
);
—————————————
ALTER TABLE uploads
  ADD COLUMN IF NOT EXISTS org INTEGER NOT NULL DEFAULT 1;
——————————————
ALTER TABLE orgs
ADD COLUMN logo_url VARCHAR(255);
