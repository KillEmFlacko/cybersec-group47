--
-- PostgreSQL database dump
--

-- Dumped from database version 12.3
-- Dumped by pg_dump version 12.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: DELETE_FAKE(character, character); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public."DELETE_FAKE"(ephid character, hash character) RETURNS integer
    LANGUAGE plpgsql
    AS $$DECLARE
out integer;
BEGIN
create temp table to_delete(contact_id CHAR(64));
if(hash is not null) then 
insert into "to_delete"
SELECT contact_id FROM "Share" WHERE contact_id IN (SELECT id FROM "ContactEvent" WHERE ephid1 = ephid OR ephid2 = ephid) AND x != hash GROUP BY contact_id;
else
insert into "to_delete"
SELECT contact_id FROM "Share" WHERE contact_id IN (SELECT id FROM "ContactEvent" WHERE ephid1 = ephid OR ephid2 = ephid) group by contact_id;
end if;
out := (select count(*) from "to_delete");
DELETE FROM "ContactEvent" WHERE id IN (select * from to_delete);
DELETE FROM "Share" WHERE contact_id IN (select * from to_delete);
DROP TABLE "to_delete";
RETURN out;
END$$;


ALTER FUNCTION public."DELETE_FAKE"(ephid character, hash character) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ContactEvent; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."ContactEvent" (
    id character(64) NOT NULL,
    ephid1 character(32) NOT NULL,
    ephid2 character(32) NOT NULL,
    created_timestamp timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public."ContactEvent" OWNER TO postgres;

--
-- Name: Share; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Share" (
    id bigint NOT NULL,
    contact_id character(64) NOT NULL,
    x character(64) NOT NULL,
    y character(132) NOT NULL
);


ALTER TABLE public."Share" OWNER TO postgres;

--
-- Name: Share_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Share_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Share_id_seq" OWNER TO postgres;

--
-- Name: Share_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Share_id_seq" OWNED BY public."Share".id;


--
-- Name: Share id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Share" ALTER COLUMN id SET DEFAULT nextval('public."Share_id_seq"'::regclass);


--
-- Name: ContactEvent ContactEvent_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ContactEvent"
    ADD CONSTRAINT "ContactEvent_pkey" PRIMARY KEY (id);


--
-- Name: Share Share_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Share"
    ADD CONSTRAINT "Share_pkey" PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

