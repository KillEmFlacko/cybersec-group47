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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: infect; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.infect (
    nonce character(32) DEFAULT NULL::bpchar,
    id bigint NOT NULL,
    skt character(64) NOT NULL,
    created_date date DEFAULT now(),
    start_date date NOT NULL
);


ALTER TABLE public.infect OWNER TO postgres;

--
-- Name: infect_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.infect_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.infect_id_seq OWNER TO postgres;

--
-- Name: infect_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.infect_id_seq OWNED BY public.infect.id;


--
-- Name: infect id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.infect ALTER COLUMN id SET DEFAULT nextval('public.infect_id_seq'::regclass);


--
-- Name: infect infect_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.infect
    ADD CONSTRAINT infect_pk PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

