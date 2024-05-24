CREATE DATABASE "cellule_doc"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LOCALE_PROVIDER = 'libc'
    CONNECTION LIMIT = 10
    IS_TEMPLATE = False;

CREATE TABLE public.documents
(
    "ID" character varying(25) NOT NULL,
    "NUMERO_PROJET" character varying(20),
    "NUMERO_COMMANDE" bigint,
    "LIGNE" integer,
    "RELEASE" character varying(5),
    "FOURNISSEUR" character varying(100),
    "DATE_RECEPTION_MATERIEL" date,
    "DATE_OBTENTION_DOC" date,
    "DESCRIPTION" character varying(150),
    "ITEM_CODE" character varying(30),
    "STATUT" character varying(50),
    "COMMENTAIRES" character varying(100),
    "CONSULTANT" character varying(30),
    "ORIGINE_DOC" character varying(10),
    "HOROD_CONTROLE_VALIDE_SYSTEME" date,
    "HOROD_CONTROLE_VALIDE_CELLULE_DOC" date,
    "HOROD_ATTENTE_RETOUR_FOURNISSEUR" date,
    "HOROD_ATTENTE_DOC" date,
    "HOROD_ATTENTE_RETOUR_INTERNE" date,
    "HOROD_LIGNE_INVALIDABLE" date,
    PRIMARY KEY ("ID")
);

ALTER TABLE IF EXISTS public.documents
    OWNER to postgres;


CREATE TABLE public.test
(
    "ID" character varying(25) NOT NULL,
    "CONSULTANT" character varying(30),
    "NUMERO_PROJET" character varying(20),
    "NUMERO_COMMANDE" bigint,
    "LIGNE" integer,
    "RELEASE" character varying(5),
    "ORIGINE_DOC" character varying(10),
    "FOURNISSEUR" character varying(100),
    "DATE_RECEPTION_MATERIEL" date,
    "DATE_OBTENTION_DOC" date,
    CONSTRAINT test_pkey PRIMARY KEY ("ID")
);

ALTER TABLE IF EXISTS public.test
    OWNER to postgres;


CREATE VIEW public.thomas
 AS
select * from public.documents
where "CONSULTANT" = 'thomas';

ALTER TABLE public.thomas
    OWNER TO postgres;


CREATE VIEW public.aurelie
 AS
select * from public.documents
where "CONSULTANT" = 'aurelie';

ALTER TABLE public.aurelie
    OWNER TO postgres;


CREATE VIEW public.karen
 AS
select * from public.documents
where "CONSULTANT" = 'karen';

ALTER TABLE public.karen
    OWNER TO postgres;


CREATE VIEW public.elodie
 AS
select * from public.documents
where "CONSULTANT" = 'elodie';

ALTER TABLE public.elodie
    OWNER TO postgres;


CREATE VIEW public.elise
 AS
select * from public.documents
where "CONSULTANT" = 'elise';

ALTER TABLE public.elise
    OWNER TO postgres;


CREATE VIEW public.raphael
 AS
select * from public.documents
where "CONSULTANT" = 'raphael';

ALTER TABLE public.raphael
    OWNER TO postgres;


CREATE VIEW public.florent
 AS
select * from public.documents
where "CONSULTANT" = 'florent';

ALTER TABLE public.florent
    OWNER TO postgres;


CREATE VIEW public.estelle
 AS
select * from public.documents
where "CONSULTANT" = 'estelle';

ALTER TABLE public.estelle
    OWNER TO postgres;


CREATE VIEW public.null
AS
select * from public.documents
where "CONSULTANT" is null;

ALTER TABLE public.null
    OWNER TO postgres;
