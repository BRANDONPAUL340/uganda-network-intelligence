--
-- PostgreSQL database dump
--

\restrict w04AfHKejhK5qGGXZ4QXkvZLatja60qdaoDV6YDU3FIaMBXYsS8IX0eTOuUyrrV

-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

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
-- Name: data_quality_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_quality_results (
    quality_result_id bigint NOT NULL,
    run_id bigint NOT NULL,
    check_name character varying(150) NOT NULL,
    status character varying(20) NOT NULL,
    failed_records integer DEFAULT 0,
    severity character varying(20) DEFAULT 'INFO'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_quality_severity CHECK (((severity)::text = ANY ((ARRAY['INFO'::character varying, 'WARNING'::character varying, 'CRITICAL'::character varying])::text[])))
);


ALTER TABLE public.data_quality_results OWNER TO postgres;

--
-- Name: data_quality_results_quality_result_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.data_quality_results_quality_result_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.data_quality_results_quality_result_id_seq OWNER TO postgres;

--
-- Name: data_quality_results_quality_result_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.data_quality_results_quality_result_id_seq OWNED BY public.data_quality_results.quality_result_id;


--
-- Name: equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment (
    equipment_id integer NOT NULL,
    site_id integer,
    equipment_type character varying(50) NOT NULL,
    manufacturer character varying(100) NOT NULL,
    model character varying(100) NOT NULL,
    installation_date date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.equipment OWNER TO postgres;

--
-- Name: gold_equipment_health; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gold_equipment_health (
    equipment_id integer NOT NULL,
    equipment_type character varying(50),
    manufacturer character varying(100),
    model character varying(100),
    measurement_count integer DEFAULT 0,
    avg_latency_ms numeric(10,2),
    avg_packet_loss_pct numeric(5,2),
    avg_availability_pct numeric(5,2),
    health_status character varying(20)
);


ALTER TABLE public.gold_equipment_health OWNER TO postgres;

--
-- Name: gold_site_daily_performance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gold_site_daily_performance (
    site_id integer NOT NULL,
    site_name character varying(100) NOT NULL,
    measurement_date date NOT NULL,
    measurement_count integer DEFAULT 0,
    avg_traffic_mb numeric(12,2),
    avg_latency_ms numeric(10,2),
    avg_packet_loss_pct numeric(5,2),
    avg_signal_strength_dbm numeric(6,2),
    avg_availability_pct numeric(5,2)
);


ALTER TABLE public.gold_site_daily_performance OWNER TO postgres;

--
-- Name: incidents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.incidents (
    incident_id bigint NOT NULL,
    site_id integer,
    equipment_id integer,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone,
    incident_type character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT incidents_check CHECK ((end_time >= start_time)),
    CONSTRAINT incidents_severity_check CHECK (((severity)::text = ANY ((ARRAY['INFO'::character varying, 'WARNING'::character varying, 'CRITICAL'::character varying])::text[])))
);


ALTER TABLE public.incidents OWNER TO postgres;

--
-- Name: ingestion_batches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ingestion_batches (
    batch_id bigint NOT NULL,
    pipeline_run_id bigint,
    source_type character varying(20) NOT NULL,
    source_name character varying(255) NOT NULL,
    started_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at timestamp with time zone,
    records_received integer DEFAULT 0 NOT NULL,
    records_loaded integer DEFAULT 0 NOT NULL,
    status character varying(20) DEFAULT 'RUNNING'::character varying NOT NULL,
    error_message text,
    CONSTRAINT chk_ingestion_source_type CHECK (((source_type)::text = ANY ((ARRAY['CSV'::character varying, 'API'::character varying])::text[]))),
    CONSTRAINT chk_ingestion_status CHECK (((status)::text = ANY ((ARRAY['RUNNING'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying])::text[]))),
    CONSTRAINT chk_records_loaded CHECK ((records_loaded >= 0)),
    CONSTRAINT chk_records_received CHECK ((records_received >= 0))
);


ALTER TABLE public.ingestion_batches OWNER TO postgres;

--
-- Name: ingestion_batches_batch_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ingestion_batches_batch_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ingestion_batches_batch_id_seq OWNER TO postgres;

--
-- Name: ingestion_batches_batch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ingestion_batches_batch_id_seq OWNED BY public.ingestion_batches.batch_id;


--
-- Name: measurements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.measurements (
    measurement_id bigint NOT NULL,
    measured_at timestamp with time zone NOT NULL,
    site_id integer,
    equipment_id integer,
    traffic_mb numeric(12,2),
    latency_ms numeric(10,2),
    packet_loss_pct numeric(5,2),
    signal_strength_dbm numeric(6,2),
    availability_pct numeric(5,2),
    CONSTRAINT measurements_availability_pct_check CHECK (((availability_pct >= (0)::numeric) AND (availability_pct <= (100)::numeric))),
    CONSTRAINT measurements_latency_ms_check CHECK ((latency_ms >= (0)::numeric)),
    CONSTRAINT measurements_packet_loss_pct_check CHECK (((packet_loss_pct >= (0)::numeric) AND (packet_loss_pct <= (100)::numeric))),
    CONSTRAINT measurements_traffic_mb_check CHECK ((traffic_mb >= (0)::numeric))
);


ALTER TABLE public.measurements OWNER TO postgres;

--
-- Name: pipeline_lineage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pipeline_lineage (
    lineage_id bigint NOT NULL,
    run_id bigint NOT NULL,
    stage_run_id bigint,
    source_table character varying(100) NOT NULL,
    target_table character varying(100) NOT NULL,
    records_processed integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT pipeline_lineage_records_processed_check CHECK ((records_processed >= 0))
);


ALTER TABLE public.pipeline_lineage OWNER TO postgres;

--
-- Name: pipeline_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pipeline_runs (
    run_id bigint NOT NULL,
    pipeline_name character varying(100) NOT NULL,
    started_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at timestamp with time zone,
    status character varying(20) DEFAULT 'RUNNING'::character varying NOT NULL,
    current_stage character varying(50) NOT NULL,
    records_processed integer DEFAULT 0,
    error_message text,
    duration_seconds numeric(10,3) DEFAULT 0.000,
    CONSTRAINT pipeline_runs_duration_seconds_check CHECK ((duration_seconds >= (0)::numeric)),
    CONSTRAINT pipeline_runs_records_processed_check CHECK ((records_processed >= 0)),
    CONSTRAINT pipeline_runs_status_check CHECK (((status)::text = ANY ((ARRAY['RUNNING'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying])::text[])))
);


ALTER TABLE public.pipeline_runs OWNER TO postgres;

--
-- Name: pipeline_stage_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pipeline_stage_runs (
    stage_run_id bigint NOT NULL,
    run_id bigint NOT NULL,
    stage_name character varying(50) NOT NULL,
    started_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at timestamp with time zone,
    status character varying(20) DEFAULT 'RUNNING'::character varying NOT NULL,
    records_processed integer DEFAULT 0,
    error_message text,
    CONSTRAINT pipeline_stage_runs_records_processed_check CHECK ((records_processed >= 0)),
    CONSTRAINT pipeline_stage_runs_stage_name_check CHECK (((stage_name)::text = ANY ((ARRAY['SILVER'::character varying, 'QUALITY'::character varying, 'GOLD'::character varying])::text[]))),
    CONSTRAINT pipeline_stage_runs_status_check CHECK (((status)::text = ANY ((ARRAY['RUNNING'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying])::text[])))
);


ALTER TABLE public.pipeline_stage_runs OWNER TO postgres;

--
-- Name: pipeline_audit_report; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.pipeline_audit_report AS
 SELECT pr.run_id,
    pr.pipeline_name,
    pr.started_at AS pipeline_started_at,
    pr.completed_at AS pipeline_completed_at,
        CASE
            WHEN (pr.completed_at IS NOT NULL) THEN (pr.completed_at - pr.started_at)
            ELSE NULL::interval
        END AS pipeline_duration,
    pr.status AS pipeline_status,
    psr.stage_run_id,
    psr.stage_name,
    psr.started_at AS stage_started_at,
    psr.completed_at AS stage_completed_at,
        CASE
            WHEN (psr.completed_at IS NOT NULL) THEN (psr.completed_at - psr.started_at)
            ELSE NULL::interval
        END AS stage_duration,
    psr.status AS stage_status,
    pl.source_table,
    pl.target_table,
    COALESCE(pl.records_processed, pr.records_processed) AS lineage_records_processed,
    pl.created_at AS lineage_created_at
   FROM ((public.pipeline_runs pr
     LEFT JOIN public.pipeline_stage_runs psr ON ((pr.run_id = psr.run_id)))
     LEFT JOIN public.pipeline_lineage pl ON ((psr.stage_run_id = pl.stage_run_id)));


ALTER VIEW public.pipeline_audit_report OWNER TO postgres;

--
-- Name: pipeline_lineage_lineage_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pipeline_lineage_lineage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pipeline_lineage_lineage_id_seq OWNER TO postgres;

--
-- Name: pipeline_lineage_lineage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pipeline_lineage_lineage_id_seq OWNED BY public.pipeline_lineage.lineage_id;


--
-- Name: pipeline_operational_metrics; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.pipeline_operational_metrics AS
 SELECT r.run_id,
    r.pipeline_name,
    r.pipeline_started_at,
    r.pipeline_completed_at,
    r.pipeline_status,
    r.pipeline_duration,
    EXTRACT(epoch FROM r.pipeline_duration) AS pipeline_duration_seconds,
        CASE
            WHEN (r.pipeline_duration IS NULL) THEN 'UNKNOWN'::text
            WHEN (EXTRACT(epoch FROM r.pipeline_duration) <= (60)::numeric) THEN 'PASS'::text
            ELSE 'BREACH'::text
        END AS pipeline_sla_status,
    m.latest_measurement,
    (CURRENT_DATE - (m.latest_measurement)::date) AS freshness_days,
        CASE
            WHEN (m.latest_measurement IS NULL) THEN 'UNKNOWN'::text
            WHEN ((CURRENT_DATE - (m.latest_measurement)::date) <= 1) THEN 'PASS'::text
            ELSE 'BREACH'::text
        END AS freshness_status
   FROM (( SELECT DISTINCT pipeline_audit_report.run_id,
            pipeline_audit_report.pipeline_name,
            pipeline_audit_report.pipeline_started_at,
            pipeline_audit_report.pipeline_completed_at,
            pipeline_audit_report.pipeline_status,
            pipeline_audit_report.pipeline_duration
           FROM public.pipeline_audit_report) r
     CROSS JOIN ( SELECT max(measurements.measured_at) AS latest_measurement
           FROM public.measurements) m);


ALTER VIEW public.pipeline_operational_metrics OWNER TO postgres;

--
-- Name: pipeline_runs_run_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pipeline_runs_run_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pipeline_runs_run_id_seq OWNER TO postgres;

--
-- Name: pipeline_runs_run_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pipeline_runs_run_id_seq OWNED BY public.pipeline_runs.run_id;


--
-- Name: pipeline_stage_runs_stage_run_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pipeline_stage_runs_stage_run_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pipeline_stage_runs_stage_run_id_seq OWNER TO postgres;

--
-- Name: pipeline_stage_runs_stage_run_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pipeline_stage_runs_stage_run_id_seq OWNED BY public.pipeline_stage_runs.stage_run_id;


--
-- Name: raw_measurements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.raw_measurements (
    raw_measurement_id bigint NOT NULL,
    measurement_id bigint NOT NULL,
    site_id integer NOT NULL,
    equipment_id integer NOT NULL,
    measurement_date date NOT NULL,
    traffic_mb numeric(12,2),
    latency_ms numeric(10,2),
    packet_loss_pct numeric(5,2),
    signal_strength_dbm numeric(6,2),
    availability_pct numeric(5,2),
    source_file character varying(255) NOT NULL,
    ingestion_run_id bigint,
    ingested_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.raw_measurements OWNER TO postgres;

--
-- Name: raw_measurements_raw_measurement_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.raw_measurements_raw_measurement_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.raw_measurements_raw_measurement_id_seq OWNER TO postgres;

--
-- Name: raw_measurements_raw_measurement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.raw_measurements_raw_measurement_id_seq OWNED BY public.raw_measurements.raw_measurement_id;


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schema_migrations (
    version character varying(50) NOT NULL,
    description character varying(255) NOT NULL,
    applied_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.schema_migrations OWNER TO postgres;

--
-- Name: silver_measurements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.silver_measurements (
    measurement_id bigint NOT NULL,
    measured_at timestamp with time zone NOT NULL,
    site_id integer NOT NULL,
    site_name character varying(100),
    region character varying(50),
    district character varying(100),
    site_type character varying(30),
    equipment_id integer NOT NULL,
    equipment_type character varying(50),
    manufacturer character varying(100),
    model character varying(100),
    traffic_mb numeric(12,2),
    latency_ms numeric(10,2),
    packet_loss_pct numeric(5,2),
    signal_strength_dbm numeric(6,2),
    availability_pct numeric(5,2),
    ingested_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.silver_measurements OWNER TO postgres;

--
-- Name: silver_network_health; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.silver_network_health (
    measurement_id bigint NOT NULL,
    measured_at timestamp with time zone NOT NULL,
    site_id integer NOT NULL,
    site_name character varying(100),
    region character varying(50),
    district character varying(100),
    site_type character varying(30),
    equipment_id integer NOT NULL,
    equipment_type character varying(50),
    manufacturer character varying(100),
    model character varying(100),
    traffic_mb numeric(12,2),
    latency_ms numeric(10,2),
    packet_loss_pct numeric(5,2),
    signal_strength_dbm numeric(6,2),
    availability_pct numeric(5,2),
    health_status character varying(20) NOT NULL,
    ingested_at timestamp with time zone,
    batch_id integer,
    run_id bigint,
    inserted_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT silver_network_health_health_status_check CHECK (((health_status)::text = ANY ((ARRAY['Healthy'::character varying, 'Warning'::character varying, 'Critical'::character varying])::text[])))
);


ALTER TABLE public.silver_network_health OWNER TO postgres;

--
-- Name: sites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sites (
    site_id integer NOT NULL,
    site_name character varying(100) NOT NULL,
    region character varying(50) NOT NULL,
    district character varying(100) NOT NULL,
    site_type character varying(30) NOT NULL,
    latitude numeric(9,6),
    longitude numeric(9,6),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.sites OWNER TO postgres;

--
-- Name: data_quality_results quality_result_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_quality_results ALTER COLUMN quality_result_id SET DEFAULT nextval('public.data_quality_results_quality_result_id_seq'::regclass);


--
-- Name: ingestion_batches batch_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingestion_batches ALTER COLUMN batch_id SET DEFAULT nextval('public.ingestion_batches_batch_id_seq'::regclass);


--
-- Name: pipeline_lineage lineage_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_lineage ALTER COLUMN lineage_id SET DEFAULT nextval('public.pipeline_lineage_lineage_id_seq'::regclass);


--
-- Name: pipeline_runs run_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_runs ALTER COLUMN run_id SET DEFAULT nextval('public.pipeline_runs_run_id_seq'::regclass);


--
-- Name: pipeline_stage_runs stage_run_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_stage_runs ALTER COLUMN stage_run_id SET DEFAULT nextval('public.pipeline_stage_runs_stage_run_id_seq'::regclass);


--
-- Name: raw_measurements raw_measurement_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.raw_measurements ALTER COLUMN raw_measurement_id SET DEFAULT nextval('public.raw_measurements_raw_measurement_id_seq'::regclass);


--
-- Data for Name: data_quality_results; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_quality_results (quality_result_id, run_id, check_name, status, failed_records, severity, created_at) FROM stdin;
\.


--
-- Data for Name: equipment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment (equipment_id, site_id, equipment_type, manufacturer, model, installation_date, created_at) FROM stdin;
\.


--
-- Data for Name: gold_equipment_health; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gold_equipment_health (equipment_id, equipment_type, manufacturer, model, measurement_count, avg_latency_ms, avg_packet_loss_pct, avg_availability_pct, health_status) FROM stdin;
\.


--
-- Data for Name: gold_site_daily_performance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gold_site_daily_performance (site_id, site_name, measurement_date, measurement_count, avg_traffic_mb, avg_latency_ms, avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct) FROM stdin;
\.


--
-- Data for Name: incidents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.incidents (incident_id, site_id, equipment_id, start_time, end_time, incident_type, severity, description, created_at) FROM stdin;
\.


--
-- Data for Name: ingestion_batches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ingestion_batches (batch_id, pipeline_run_id, source_type, source_name, started_at, completed_at, records_received, records_loaded, status, error_message) FROM stdin;
\.


--
-- Data for Name: measurements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.measurements (measurement_id, measured_at, site_id, equipment_id, traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct) FROM stdin;
\.


--
-- Data for Name: pipeline_lineage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pipeline_lineage (lineage_id, run_id, stage_run_id, source_table, target_table, records_processed, created_at) FROM stdin;
\.


--
-- Data for Name: pipeline_runs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pipeline_runs (run_id, pipeline_name, started_at, completed_at, status, current_stage, records_processed, error_message, duration_seconds) FROM stdin;
\.


--
-- Data for Name: pipeline_stage_runs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pipeline_stage_runs (stage_run_id, run_id, stage_name, started_at, completed_at, status, records_processed, error_message) FROM stdin;
\.


--
-- Data for Name: raw_measurements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.raw_measurements (raw_measurement_id, measurement_id, site_id, equipment_id, measurement_date, traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct, source_file, ingestion_run_id, ingested_at) FROM stdin;
\.


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schema_migrations (version, description, applied_at) FROM stdin;
000	create migration tracking table	2026-09-14 09:16:26.320072+00
001	baseline existing schema	2026-09-14 09:16:26.325149+00
002	add migration checksum metadata	2026-09-14 09:16:26.32902+00
003	create raw measurements	2026-09-14 09:16:26.334473+00
004	harden raw source	2026-09-14 09:16:26.34247+00
005	create ingestion batches table	2026-09-14 09:16:26.353609+00
\.


--
-- Data for Name: silver_measurements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.silver_measurements (measurement_id, measured_at, site_id, site_name, region, district, site_type, equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at) FROM stdin;
\.


--
-- Data for Name: silver_network_health; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.silver_network_health (measurement_id, measured_at, site_id, site_name, region, district, site_type, equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id, inserted_at) FROM stdin;
\.


--
-- Data for Name: sites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sites (site_id, site_name, region, district, site_type, latitude, longitude, created_at) FROM stdin;
\.


--
-- Name: data_quality_results_quality_result_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.data_quality_results_quality_result_id_seq', 1, false);


--
-- Name: ingestion_batches_batch_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ingestion_batches_batch_id_seq', 1, false);


--
-- Name: pipeline_lineage_lineage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pipeline_lineage_lineage_id_seq', 1, false);


--
-- Name: pipeline_runs_run_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pipeline_runs_run_id_seq', 1, false);


--
-- Name: pipeline_stage_runs_stage_run_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pipeline_stage_runs_stage_run_id_seq', 1, false);


--
-- Name: raw_measurements_raw_measurement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.raw_measurements_raw_measurement_id_seq', 1, false);


--
-- Name: data_quality_results data_quality_results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_quality_results
    ADD CONSTRAINT data_quality_results_pkey PRIMARY KEY (quality_result_id);


--
-- Name: equipment equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_pkey PRIMARY KEY (equipment_id);


--
-- Name: gold_equipment_health gold_equipment_health_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gold_equipment_health
    ADD CONSTRAINT gold_equipment_health_pkey PRIMARY KEY (equipment_id);


--
-- Name: gold_site_daily_performance gold_site_daily_performance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gold_site_daily_performance
    ADD CONSTRAINT gold_site_daily_performance_pkey PRIMARY KEY (site_id, measurement_date);


--
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (incident_id);


--
-- Name: ingestion_batches ingestion_batches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingestion_batches
    ADD CONSTRAINT ingestion_batches_pkey PRIMARY KEY (batch_id);


--
-- Name: measurements measurements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT measurements_pkey PRIMARY KEY (measurement_id);


--
-- Name: pipeline_lineage pipeline_lineage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_lineage
    ADD CONSTRAINT pipeline_lineage_pkey PRIMARY KEY (lineage_id);


--
-- Name: pipeline_runs pipeline_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_runs
    ADD CONSTRAINT pipeline_runs_pkey PRIMARY KEY (run_id);


--
-- Name: pipeline_stage_runs pipeline_stage_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_stage_runs
    ADD CONSTRAINT pipeline_stage_runs_pkey PRIMARY KEY (stage_run_id);


--
-- Name: raw_measurements raw_measurements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.raw_measurements
    ADD CONSTRAINT raw_measurements_pkey PRIMARY KEY (raw_measurement_id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: silver_measurements silver_measurements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.silver_measurements
    ADD CONSTRAINT silver_measurements_pkey PRIMARY KEY (measurement_id);


--
-- Name: silver_network_health silver_network_health_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.silver_network_health
    ADD CONSTRAINT silver_network_health_pkey PRIMARY KEY (measurement_id);


--
-- Name: sites sites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_pkey PRIMARY KEY (site_id);


--
-- Name: raw_measurements uq_raw_measurement_source; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.raw_measurements
    ADD CONSTRAINT uq_raw_measurement_source UNIQUE (measurement_id, source_file);


--
-- Name: idx_ingestion_batches_pipeline_run; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ingestion_batches_pipeline_run ON public.ingestion_batches USING btree (pipeline_run_id);


--
-- Name: idx_ingestion_batches_source; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ingestion_batches_source ON public.ingestion_batches USING btree (source_type, source_name);


--
-- Name: idx_ingestion_batches_started; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ingestion_batches_started ON public.ingestion_batches USING btree (started_at);


--
-- Name: idx_pipeline_lineage_run_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pipeline_lineage_run_id ON public.pipeline_lineage USING btree (run_id);


--
-- Name: idx_pipeline_lineage_stage_run_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pipeline_lineage_stage_run_id ON public.pipeline_lineage USING btree (stage_run_id);


--
-- Name: idx_pipeline_stage_runs_run_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pipeline_stage_runs_run_id ON public.pipeline_stage_runs USING btree (run_id);


--
-- Name: idx_pipeline_stage_runs_stage_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pipeline_stage_runs_stage_name ON public.pipeline_stage_runs USING btree (stage_name);


--
-- Name: idx_raw_measurements_ingested_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_raw_measurements_ingested_at ON public.raw_measurements USING btree (ingested_at);


--
-- Name: idx_raw_measurements_ingestion_run; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_raw_measurements_ingestion_run ON public.raw_measurements USING btree (ingestion_run_id);


--
-- Name: idx_raw_measurements_measurement_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_raw_measurements_measurement_id ON public.raw_measurements USING btree (measurement_id);


--
-- Name: uq_pipeline_lineage_relationship; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_pipeline_lineage_relationship ON public.pipeline_lineage USING btree (run_id, stage_run_id, source_table, target_table);


--
-- Name: uq_pipeline_stage_run; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_pipeline_stage_run ON public.pipeline_stage_runs USING btree (run_id, stage_name);


--
-- Name: data_quality_results data_quality_results_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_quality_results
    ADD CONSTRAINT data_quality_results_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.pipeline_runs(run_id) ON DELETE CASCADE;


--
-- Name: equipment equipment_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(site_id) ON DELETE CASCADE;


--
-- Name: ingestion_batches fk_ingestion_pipeline_run; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingestion_batches
    ADD CONSTRAINT fk_ingestion_pipeline_run FOREIGN KEY (pipeline_run_id) REFERENCES public.pipeline_runs(run_id) ON DELETE CASCADE;


--
-- Name: incidents incidents_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(equipment_id) ON DELETE CASCADE;


--
-- Name: incidents incidents_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(site_id) ON DELETE CASCADE;


--
-- Name: measurements measurements_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT measurements_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(equipment_id) ON DELETE CASCADE;


--
-- Name: measurements measurements_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT measurements_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(site_id) ON DELETE CASCADE;


--
-- Name: pipeline_lineage pipeline_lineage_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_lineage
    ADD CONSTRAINT pipeline_lineage_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.pipeline_runs(run_id) ON DELETE CASCADE;


--
-- Name: pipeline_lineage pipeline_lineage_stage_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_lineage
    ADD CONSTRAINT pipeline_lineage_stage_run_id_fkey FOREIGN KEY (stage_run_id) REFERENCES public.pipeline_stage_runs(stage_run_id) ON DELETE SET NULL;


--
-- Name: pipeline_stage_runs pipeline_stage_runs_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_stage_runs
    ADD CONSTRAINT pipeline_stage_runs_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.pipeline_runs(run_id) ON DELETE CASCADE;


--
-- Name: silver_measurements silver_measurements_measurement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.silver_measurements
    ADD CONSTRAINT silver_measurements_measurement_id_fkey FOREIGN KEY (measurement_id) REFERENCES public.measurements(measurement_id);


--
-- Name: silver_network_health silver_network_health_measurement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.silver_network_health
    ADD CONSTRAINT silver_network_health_measurement_id_fkey FOREIGN KEY (measurement_id) REFERENCES public.measurements(measurement_id);


--
-- PostgreSQL database dump complete
--

\unrestrict w04AfHKejhK5qGGXZ4QXkvZLatja60qdaoDV6YDU3FIaMBXYsS8IX0eTOuUyrrV

