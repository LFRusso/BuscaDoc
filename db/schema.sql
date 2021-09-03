--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.21
-- Dumped by pg_dump version 13.3

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

--
-- Name: corpus; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.corpus (
    code character varying,
    name character varying,
    txt_ementa character varying,
    text character varying,
    text_preprocessed character varying
);


ALTER TABLE public.corpus OWNER TO admin;

--
-- Name: feedback; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.feedback (
    id integer NOT NULL,
    query character varying,
    user_feedback character varying,
    date_created timestamp without time zone
);


ALTER TABLE public.feedback OWNER TO admin;

--
-- Name: feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.feedback_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feedback_id_seq OWNER TO admin;

--
-- Name: feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.feedback_id_seq OWNED BY public.feedback.id;


--
-- Name: feedback id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.feedback ALTER COLUMN id SET DEFAULT nextval('public.feedback_id_seq'::regclass);


--
-- Data for Name: corpus; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.corpus (code, name, txt_ementa, text, text_preprocessed) FROM stdin;
\.


--
-- Data for Name: feedback; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.feedback (id, query, user_feedback, date_created) FROM stdin;
\.


--
-- Name: feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.feedback_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

