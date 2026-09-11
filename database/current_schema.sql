--
-- PostgreSQL database dump
--

\restrict 4d66BpHwMy1jhDpnnOcXIzjIEkHHcvBkQIhEGxXJ9RslCD2SU529fhoKtkHKxgc

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: data_lineage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_lineage (
    lineage_id bigint NOT NULL,
    run_id integer NOT NULL,
    source_layer character varying(30) NOT NULL,
    source_table character varying(100) NOT NULL,
    target_layer character varying(30) NOT NULL,
    target_table character varying(100) NOT NULL,
    transformation_name character varying(100) NOT NULL,
    records_processed integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.data_lineage OWNER TO postgres;

--
-- Name: data_lineage_lineage_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.data_lineage ALTER COLUMN lineage_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.data_lineage_lineage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: data_quality_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_quality_results (
    quality_result_id bigint NOT NULL,
    run_id integer NOT NULL,
    table_name character varying(100) NOT NULL,
    check_name character varying(100) NOT NULL,
    check_type character varying(50) DEFAULT 'VALIDITY'::character varying NOT NULL,
    status character varying(20) NOT NULL,
    records_checked bigint DEFAULT 0,
    records_failed bigint DEFAULT 0,
    failure_rate_pct numeric(8,3) DEFAULT 0.0,
    details text,
    checked_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    error_message text,
    severity character varying(20) DEFAULT 'INFO'::character varying,
    CONSTRAINT chk_quality_severity CHECK (((severity)::text = ANY ((ARRAY['INFO'::character varying, 'WARNING'::character varying, 'CRITICAL'::character varying])::text[])))
);


ALTER TABLE public.data_quality_results OWNER TO postgres;

--
-- Name: data_quality_results_quality_result_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.data_quality_results ALTER COLUMN quality_result_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.data_quality_results_quality_result_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment (
    equipment_id integer NOT NULL,
    site_id integer NOT NULL,
    equipment_type character varying(50) NOT NULL,
    manufacturer character varying(100),
    model character varying(100),
    installation_date date,
    status character varying(20) NOT NULL,
    CONSTRAINT chk_equipment_status CHECK (((status)::text = ANY ((ARRAY['Active'::character varying, 'Active'::character varying, 'Inactive'::character varying, 'Maintenance'::character varying, 'Retired'::character varying])::text[])))
);


ALTER TABLE public.equipment OWNER TO postgres;

--
-- Name: equipment_equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.equipment ALTER COLUMN equipment_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.equipment_equipment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: gold_equipment_health; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gold_equipment_health (
    equipment_id integer NOT NULL,
    equipment_type character varying(50),
    manufacturer character varying(100),
    model character varying(100),
    measurement_count bigint,
    avg_latency_ms numeric,
    avg_packet_loss_pct numeric,
    avg_signal_strength_dbm numeric,
    avg_availability_pct numeric,
    health_status text,
    record_count integer DEFAULT 0,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.gold_equipment_health OWNER TO postgres;

--
-- Name: gold_incident_summary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gold_incident_summary (
    site_id integer,
    site_name character varying(100),
    region character varying(50),
    district character varying(100),
    total_incidents bigint,
    critical_incidents bigint,
    high_incidents bigint,
    medium_incidents bigint,
    low_incidents bigint,
    avg_resolution_minutes numeric
);


ALTER TABLE public.gold_incident_summary OWNER TO postgres;

--
-- Name: gold_network_intelligence; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gold_network_intelligence (
    site_id integer,
    site_name character varying(100),
    region character varying(50),
    district character varying(100),
    measurement_date date,
    measurement_count bigint,
    avg_traffic_mb numeric,
    avg_latency_ms numeric,
    avg_packet_loss_pct numeric,
    avg_signal_strength_dbm numeric,
    avg_availability_pct numeric,
    total_incidents bigint,
    critical_incidents bigint,
    high_incidents bigint,
    avg_resolution_minutes numeric,
    network_health text
);


ALTER TABLE public.gold_network_intelligence OWNER TO postgres;

--
-- Name: pipeline_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pipeline_runs (
    run_id integer NOT NULL,
    pipeline_name character varying(100) NOT NULL,
    status character varying(30) NOT NULL,
    started_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp with time zone,
    records_processed integer DEFAULT 0,
    error_message text,
    records_read integer DEFAULT 0,
    records_rejected integer DEFAULT 0,
    duration_seconds numeric(10,3),
    records_inserted integer DEFAULT 0,
    silver_records_processed integer DEFAULT 0,
    gold_records_processed integer DEFAULT 0,
    quality_checks_run integer DEFAULT 0,
    quality_checks_failed integer DEFAULT 0,
    quality_checks_passed integer DEFAULT 0,
    source_file character varying(255),
    records_skipped integer DEFAULT 0,
    current_stage character varying(50) DEFAULT 'START'::character varying
);


ALTER TABLE public.pipeline_runs OWNER TO postgres;

--
-- Name: transformation_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transformation_runs (
    transformation_run_id bigint NOT NULL,
    run_id integer NOT NULL,
    layer character varying(20) NOT NULL,
    transformation_name character varying(100) NOT NULL,
    started_at timestamp without time zone NOT NULL,
    completed_at timestamp without time zone,
    status character varying(20) NOT NULL,
    records_processed integer DEFAULT 0,
    error_message text
);


ALTER TABLE public.transformation_runs OWNER TO postgres;

--
-- Name: gold_pipeline_lineage; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.gold_pipeline_lineage AS
 SELECT p.run_id,
    p.pipeline_name,
    p.source_file,
    p.started_at AS pipeline_started_at,
    p.completed_at AS pipeline_completed_at,
    p.status AS pipeline_status,
    t.transformation_run_id,
    t.layer,
    t.transformation_name,
    t.started_at AS transformation_started_at,
    t.completed_at AS transformation_completed_at,
    t.status AS transformation_status,
    t.records_processed
   FROM (public.pipeline_runs p
     LEFT JOIN public.transformation_runs t ON ((p.run_id = t.run_id)));


ALTER VIEW public.gold_pipeline_lineage OWNER TO postgres;

--
-- Name: gold_pipeline_run_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.gold_pipeline_run_summary AS
 SELECT run_id,
    pipeline_name,
    source_file,
    started_at,
    completed_at,
    (completed_at - started_at) AS duration,
    status,
    records_read,
    records_inserted,
    records_rejected,
    records_skipped,
    records_processed,
    error_message
   FROM public.pipeline_runs
  ORDER BY run_id DESC;


ALTER VIEW public.gold_pipeline_run_summary OWNER TO postgres;

--
-- Name: gold_site_daily_performance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gold_site_daily_performance (
    site_id integer,
    site_name character varying(100),
    region character varying(50),
    district character varying(100),
    measurement_date date,
    measurement_count bigint,
    avg_traffic_mb numeric,
    avg_latency_ms numeric,
    avg_packet_loss_pct numeric,
    avg_signal_strength_dbm numeric,
    avg_availability_pct numeric,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.gold_site_daily_performance OWNER TO postgres;

--
-- Name: incidents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.incidents (
    incident_id integer NOT NULL,
    site_id integer NOT NULL,
    equipment_id integer,
    incident_type character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone,
    status character varying(20) NOT NULL,
    description text,
    CONSTRAINT chk_incidents_severity CHECK (((severity)::text = ANY ((ARRAY['Low'::character varying, 'Medium'::character varying, 'High'::character varying, 'Critical'::character varying, 'LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'CRITICAL'::character varying])::text[]))),
    CONSTRAINT chk_incidents_status CHECK (((status)::text = ANY ((ARRAY['Open'::character varying, 'In Progress'::character varying, 'Resolved'::character varying, 'Closed'::character varying, 'OPEN'::character varying, 'IN_PROGRESS'::character varying, 'RESOLVED'::character varying, 'CLOSED'::character varying])::text[]))),
    CONSTRAINT chk_incidents_time CHECK (((end_time IS NULL) OR (end_time >= start_time)))
);


ALTER TABLE public.incidents OWNER TO postgres;

--
-- Name: incidents_incident_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.incidents ALTER COLUMN incident_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.incidents_incident_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: measurements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.measurements (
    measurement_id bigint NOT NULL,
    equipment_id integer NOT NULL,
    site_id integer NOT NULL,
    measured_at timestamp without time zone NOT NULL,
    traffic_mb numeric(12,2),
    latency_ms numeric(10,2),
    packet_loss_pct numeric(5,2),
    signal_strength_dbm numeric(6,2),
    availability_pct numeric(5,2),
    ingested_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    batch_id bigint,
    source_record_id character varying(100),
    CONSTRAINT chk_availability_range CHECK (((availability_pct >= (0)::numeric) AND (availability_pct <= (100)::numeric))),
    CONSTRAINT chk_latency_nonnegative CHECK ((latency_ms >= (0)::numeric)),
    CONSTRAINT chk_measurements_availability CHECK (((availability_pct IS NULL) OR ((availability_pct >= (0)::numeric) AND (availability_pct <= (100)::numeric)))),
    CONSTRAINT chk_measurements_latency CHECK (((latency_ms IS NULL) OR (latency_ms >= (0)::numeric))),
    CONSTRAINT chk_measurements_packet_loss CHECK (((packet_loss_pct IS NULL) OR ((packet_loss_pct >= (0)::numeric) AND (packet_loss_pct <= (100)::numeric)))),
    CONSTRAINT chk_measurements_signal CHECK (((signal_strength_dbm IS NULL) OR ((signal_strength_dbm >= ('-150'::integer)::numeric) AND (signal_strength_dbm <= (0)::numeric)))),
    CONSTRAINT chk_measurements_traffic CHECK (((traffic_mb IS NULL) OR (traffic_mb >= (0)::numeric))),
    CONSTRAINT chk_packet_loss_range CHECK (((packet_loss_pct >= (0)::numeric) AND (packet_loss_pct <= (100)::numeric))),
    CONSTRAINT chk_traffic_nonnegative CHECK ((traffic_mb >= (0)::numeric))
);


ALTER TABLE public.measurements OWNER TO postgres;

--
-- Name: measurements_measurement_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.measurements ALTER COLUMN measurement_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.measurements_measurement_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
    CONSTRAINT chk_lineage_records CHECK ((records_processed >= 0))
);


ALTER TABLE public.pipeline_lineage OWNER TO postgres;

--
-- Name: pipeline_stage_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pipeline_stage_runs (
    stage_run_id bigint NOT NULL,
    run_id integer NOT NULL,
    stage_name character varying(50) NOT NULL,
    started_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    status character varying(20) NOT NULL,
    records_read integer DEFAULT 0,
    records_inserted integer DEFAULT 0,
    records_rejected integer DEFAULT 0,
    records_skipped integer DEFAULT 0,
    duration_seconds numeric(12,3),
    error_message text
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
-- Name: pipeline_run_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.pipeline_run_summary AS
 SELECT p.run_id,
    p.pipeline_name,
    p.started_at,
    p.completed_at,
    p.current_stage,
    p.status,
    p.records_processed,
    (EXTRACT(epoch FROM (p.completed_at - p.started_at)))::numeric(10,3) AS duration_seconds,
    COALESCE(q.quality_checks, (0)::bigint) AS quality_checks,
    COALESCE(q.quality_passed, (0)::bigint) AS quality_passed,
    COALESCE(q.quality_failed, (0)::bigint) AS quality_failed,
    COALESCE(q.critical_failed, (0)::bigint) AS critical_failed,
    COALESCE(q.warning_failed, (0)::bigint) AS warning_failed,
    COALESCE(q.failed_records, (0)::numeric) AS failed_records,
        CASE
            WHEN (COALESCE(q.critical_failed, (0)::bigint) > 0) THEN 'CRITICAL'::text
            WHEN (COALESCE(q.warning_failed, (0)::bigint) > 0) THEN 'WARNING'::text
            WHEN ((p.status)::text = 'FAILED'::text) THEN 'FAILED'::text
            ELSE 'HEALTHY'::text
        END AS pipeline_health
   FROM (public.pipeline_runs p
     LEFT JOIN ( SELECT data_quality_results.run_id,
            count(*) AS quality_checks,
            count(*) FILTER (WHERE ((data_quality_results.status)::text = 'PASS'::text)) AS quality_passed,
            count(*) FILTER (WHERE ((data_quality_results.status)::text = 'FAIL'::text)) AS quality_failed,
            count(*) FILTER (WHERE (((data_quality_results.severity)::text = 'CRITICAL'::text) AND ((data_quality_results.status)::text = 'FAIL'::text))) AS critical_failed,
            count(*) FILTER (WHERE (((data_quality_results.severity)::text = 'WARNING'::text) AND ((data_quality_results.status)::text = 'FAIL'::text))) AS warning_failed,
            COALESCE(sum(data_quality_results.records_failed), (0)::numeric) AS failed_records
           FROM public.data_quality_results
          GROUP BY data_quality_results.run_id) q ON ((p.run_id = q.run_id)));


ALTER VIEW public.pipeline_run_summary OWNER TO postgres;

--
-- Name: pipeline_runs_run_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.pipeline_runs ALTER COLUMN run_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.pipeline_runs_run_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: pipeline_stage_runs_stage_run_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.pipeline_stage_runs ALTER COLUMN stage_run_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.pipeline_stage_runs_stage_run_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: rejected_measurements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rejected_measurements (
    rejection_id bigint NOT NULL,
    source_record_id character varying(100),
    rejected_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    equipment_id character varying(50),
    site_id character varying(50),
    measured_at character varying(100),
    traffic_mb character varying(50),
    latency_ms character varying(50),
    packet_loss_pct character varying(50),
    signal_strength_dbm character varying(50),
    availability_pct character varying(50),
    rejection_reason text NOT NULL,
    source_file character varying(255),
    ingested_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.rejected_measurements OWNER TO postgres;

--
-- Name: rejected_measurements_rejection_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.rejected_measurements ALTER COLUMN rejection_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.rejected_measurements_rejection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: silver_measurements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.silver_measurements (
    measurement_id bigint NOT NULL,
    measured_at timestamp without time zone,
    site_id integer,
    site_name character varying(100),
    region character varying(50),
    district character varying(100),
    site_type character varying(30),
    equipment_id integer,
    equipment_type character varying(50),
    manufacturer character varying(100),
    model character varying(100),
    traffic_mb numeric(12,2),
    latency_ms numeric(10,2),
    packet_loss_pct numeric(5,2),
    signal_strength_dbm numeric(6,2),
    availability_pct numeric(5,2),
    ingested_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    batch_id bigint,
    source_record_id character varying(100),
    run_id integer
);


ALTER TABLE public.silver_measurements OWNER TO postgres;

--
-- Name: silver_network_health; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.silver_network_health (
    measurement_id integer NOT NULL,
    measured_at timestamp without time zone NOT NULL,
    site_id integer NOT NULL,
    site_name character varying(255),
    region character varying(100),
    district character varying(100),
    site_type character varying(100),
    equipment_id integer NOT NULL,
    equipment_type character varying(100),
    manufacturer character varying(100),
    model character varying(100),
    traffic_mb numeric(12,3),
    latency_ms numeric(12,3),
    packet_loss_pct numeric(5,2),
    signal_strength_dbm numeric(5,2),
    availability_pct numeric(5,2),
    health_status character varying(50),
    ingested_at timestamp without time zone,
    batch_id integer,
    run_id integer,
    inserted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
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
    latitude numeric(9,6),
    longitude numeric(9,6),
    site_type character varying(30) NOT NULL,
    status character varying(20) NOT NULL,
    CONSTRAINT chk_sites_latitude CHECK (((latitude IS NULL) OR ((latitude >= ('-90'::integer)::numeric) AND (latitude <= (90)::numeric)))),
    CONSTRAINT chk_sites_longitude CHECK (((longitude IS NULL) OR ((longitude >= ('-180'::integer)::numeric) AND (longitude <= (180)::numeric)))),
    CONSTRAINT chk_sites_site_type CHECK (((site_type)::text = ANY ((ARRAY['Data Center'::character varying, 'Macro Tower'::character varying, 'Micro Cell'::character varying, 'Rooftop Hub'::character varying])::text[]))),
    CONSTRAINT chk_sites_status CHECK (((status)::text = ANY ((ARRAY['Active'::character varying, 'Active'::character varying, 'Inactive'::character varying, 'Maintenance'::character varying, 'Planned'::character varying])::text[])))
);


ALTER TABLE public.sites OWNER TO postgres;

--
-- Name: sites_site_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.sites ALTER COLUMN site_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.sites_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: source_batches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.source_batches (
    batch_id bigint NOT NULL,
    source_name character varying(100) NOT NULL,
    file_name character varying(255) NOT NULL,
    file_checksum character varying(64) NOT NULL,
    records_read integer DEFAULT 0 NOT NULL,
    records_inserted integer DEFAULT 0 NOT NULL,
    records_rejected integer DEFAULT 0 NOT NULL,
    status character varying(20) NOT NULL,
    started_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at timestamp without time zone,
    error_message text
);


ALTER TABLE public.source_batches OWNER TO postgres;

--
-- Name: source_batches_batch_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.source_batches ALTER COLUMN batch_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.source_batches_batch_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: transformation_runs_transformation_run_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.transformation_runs ALTER COLUMN transformation_run_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.transformation_runs_transformation_run_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: v_pipeline_lineage; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_pipeline_lineage AS
 SELECT p.run_id,
    p.pipeline_name,
    p.started_at,
    p.completed_at,
    p.status AS pipeline_status,
    l.lineage_id,
    l.source_layer,
    l.source_table,
    l.target_layer,
    l.target_table,
    l.transformation_name,
    l.records_processed,
    l.created_at AS lineage_created_at
   FROM (public.pipeline_runs p
     JOIN public.data_lineage l ON ((p.run_id = l.run_id)));


ALTER VIEW public.v_pipeline_lineage OWNER TO postgres;

--
-- Name: pipeline_lineage lineage_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_lineage ALTER COLUMN lineage_id SET DEFAULT nextval('public.pipeline_lineage_lineage_id_seq'::regclass);


--
-- Name: data_lineage data_lineage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_lineage
    ADD CONSTRAINT data_lineage_pkey PRIMARY KEY (lineage_id);


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
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (incident_id);


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
-- Name: rejected_measurements rejected_measurements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rejected_measurements
    ADD CONSTRAINT rejected_measurements_pkey PRIMARY KEY (rejection_id);


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
-- Name: source_batches source_batches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_batches
    ADD CONSTRAINT source_batches_pkey PRIMARY KEY (batch_id);


--
-- Name: transformation_runs transformation_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transformation_runs
    ADD CONSTRAINT transformation_runs_pkey PRIMARY KEY (transformation_run_id);


--
-- Name: measurements unique_measurement; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT unique_measurement UNIQUE (equipment_id, site_id, measured_at);


--
-- Name: sites unique_site_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT unique_site_name UNIQUE (site_name);


--
-- Name: equipment uq_equipment; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT uq_equipment UNIQUE (site_id, equipment_type, manufacturer, model);


--
-- Name: measurements uq_equipment_measurement_time; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT uq_equipment_measurement_time UNIQUE (equipment_id, measured_at);


--
-- Name: gold_site_daily_performance uq_gold_site_daily; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gold_site_daily_performance
    ADD CONSTRAINT uq_gold_site_daily UNIQUE (site_id, measurement_date);


--
-- Name: incidents uq_incident; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT uq_incident UNIQUE (site_id, equipment_id, incident_type, start_time);


--
-- Name: measurements uq_measurement; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT uq_measurement UNIQUE (equipment_id, measured_at);


--
-- Name: measurements uq_measurement_equipment_time; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT uq_measurement_equipment_time UNIQUE (equipment_id, measured_at);


--
-- Name: measurements uq_measurements_source_record; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT uq_measurements_source_record UNIQUE (source_record_id);


--
-- Name: rejected_measurements uq_rejected_source_record; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rejected_measurements
    ADD CONSTRAINT uq_rejected_source_record UNIQUE (source_record_id);


--
-- Name: sites uq_site_name_district; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT uq_site_name_district UNIQUE (site_name, district);


--
-- Name: sites uq_sites_name_district; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT uq_sites_name_district UNIQUE (site_name, district);


--
-- Name: idx_lineage_run_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_lineage_run_id ON public.data_lineage USING btree (run_id);


--
-- Name: idx_lineage_source_table; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_lineage_source_table ON public.data_lineage USING btree (source_table);


--
-- Name: idx_lineage_target_table; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_lineage_target_table ON public.data_lineage USING btree (target_table);


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
-- Name: idx_quality_run_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_quality_run_id ON public.data_quality_results USING btree (run_id);


--
-- Name: idx_quality_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_quality_status ON public.data_quality_results USING btree (status);


--
-- Name: idx_silver_source_record_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_silver_source_record_id ON public.silver_measurements USING btree (source_record_id);


--
-- Name: idx_stage_runs_run_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_stage_runs_run_id ON public.pipeline_stage_runs USING btree (run_id);


--
-- Name: idx_stage_runs_stage_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_stage_runs_stage_name ON public.pipeline_stage_runs USING btree (stage_name);


--
-- Name: uq_pipeline_lineage_relationship; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_pipeline_lineage_relationship ON public.pipeline_lineage USING btree (run_id, stage_run_id, source_table, target_table);


--
-- Name: uq_pipeline_stage_run; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_pipeline_stage_run ON public.pipeline_stage_runs USING btree (run_id, stage_name);


--
-- Name: ux_measurements_source_record; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_measurements_source_record ON public.measurements USING btree (source_record_id);


--
-- Name: ux_rejected_source_and_reason; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_rejected_source_and_reason ON public.rejected_measurements USING btree (source_record_id, rejection_reason);


--
-- Name: equipment fk_equipment_site; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT fk_equipment_site FOREIGN KEY (site_id) REFERENCES public.sites(site_id);


--
-- Name: incidents fk_incident_equipment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT fk_incident_equipment FOREIGN KEY (equipment_id) REFERENCES public.equipment(equipment_id);


--
-- Name: incidents fk_incident_site; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT fk_incident_site FOREIGN KEY (site_id) REFERENCES public.sites(site_id);


--
-- Name: data_lineage fk_lineage_pipeline_run; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_lineage
    ADD CONSTRAINT fk_lineage_pipeline_run FOREIGN KEY (run_id) REFERENCES public.pipeline_runs(run_id);


--
-- Name: pipeline_lineage fk_lineage_run; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_lineage
    ADD CONSTRAINT fk_lineage_run FOREIGN KEY (run_id) REFERENCES public.pipeline_runs(run_id);


--
-- Name: pipeline_lineage fk_lineage_stage; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_lineage
    ADD CONSTRAINT fk_lineage_stage FOREIGN KEY (stage_run_id) REFERENCES public.pipeline_stage_runs(stage_run_id);


--
-- Name: measurements fk_measurement_batch; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT fk_measurement_batch FOREIGN KEY (batch_id) REFERENCES public.source_batches(batch_id);


--
-- Name: measurements fk_measurement_equipment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT fk_measurement_equipment FOREIGN KEY (equipment_id) REFERENCES public.equipment(equipment_id);


--
-- Name: measurements fk_measurement_site; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT fk_measurement_site FOREIGN KEY (site_id) REFERENCES public.sites(site_id);


--
-- Name: data_quality_results fk_quality_run; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_quality_results
    ADD CONSTRAINT fk_quality_run FOREIGN KEY (run_id) REFERENCES public.pipeline_runs(run_id);


--
-- Name: silver_measurements fk_silver_measurement_batch; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.silver_measurements
    ADD CONSTRAINT fk_silver_measurement_batch FOREIGN KEY (batch_id) REFERENCES public.source_batches(batch_id);


--
-- Name: silver_measurements fk_silver_measurements_run; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.silver_measurements
    ADD CONSTRAINT fk_silver_measurements_run FOREIGN KEY (run_id) REFERENCES public.pipeline_runs(run_id);


--
-- Name: pipeline_stage_runs fk_stage_pipeline_run; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_stage_runs
    ADD CONSTRAINT fk_stage_pipeline_run FOREIGN KEY (run_id) REFERENCES public.pipeline_runs(run_id);


--
-- Name: transformation_runs fk_transformation_pipeline_run; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transformation_runs
    ADD CONSTRAINT fk_transformation_pipeline_run FOREIGN KEY (run_id) REFERENCES public.pipeline_runs(run_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 4d66BpHwMy1jhDpnnOcXIzjIEkHHcvBkQIhEGxXJ9RslCD2SU529fhoKtkHKxgc

