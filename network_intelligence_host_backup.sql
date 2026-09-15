--
-- PostgreSQL database dump
--

\restrict F1iqCZVdvdMeXSaCKjfE0hFocMOaCepjPe5W2EPVaEcIUNAWknU2N2aN63RIEOt

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
-- Name: raw_measurements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.raw_measurements (
    raw_measurement_id bigint NOT NULL,
    measurement_id bigint NOT NULL,
    site_id bigint NOT NULL,
    equipment_id bigint NOT NULL,
    measurement_date date NOT NULL,
    traffic_mb numeric(14,2),
    latency_ms numeric(10,2),
    packet_loss_pct numeric(6,2),
    signal_strength_dbm numeric(8,2),
    availability_pct numeric(6,2),
    source_file character varying(255) NOT NULL,
    ingestion_run_id bigint,
    ingested_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_raw_availability CHECK (((availability_pct IS NULL) OR ((availability_pct >= (0)::numeric) AND (availability_pct <= (100)::numeric)))),
    CONSTRAINT chk_raw_latency CHECK (((latency_ms IS NULL) OR (latency_ms >= (0)::numeric))),
    CONSTRAINT chk_raw_packet_loss CHECK (((packet_loss_pct IS NULL) OR ((packet_loss_pct >= (0)::numeric) AND (packet_loss_pct <= (100)::numeric)))),
    CONSTRAINT chk_raw_traffic CHECK (((traffic_mb IS NULL) OR (traffic_mb >= (0)::numeric)))
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
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schema_migrations (
    version character varying(50) NOT NULL,
    description character varying(255) NOT NULL,
    applied_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    checksum character varying(128)
);


ALTER TABLE public.schema_migrations OWNER TO postgres;

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
-- Name: ingestion_batches batch_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingestion_batches ALTER COLUMN batch_id SET DEFAULT nextval('public.ingestion_batches_batch_id_seq'::regclass);


--
-- Name: pipeline_lineage lineage_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pipeline_lineage ALTER COLUMN lineage_id SET DEFAULT nextval('public.pipeline_lineage_lineage_id_seq'::regclass);


--
-- Name: raw_measurements raw_measurement_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.raw_measurements ALTER COLUMN raw_measurement_id SET DEFAULT nextval('public.raw_measurements_raw_measurement_id_seq'::regclass);


--
-- Data for Name: data_lineage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_lineage (lineage_id, run_id, source_layer, source_table, target_layer, target_table, transformation_name, records_processed, created_at) FROM stdin;
1	106	SOURCE	measurements	SILVER	silver_measurements	load_silver_measurements	0	2026-09-07 09:27:40.231451+03
2	106	SILVER	silver_measurements	SILVER	silver_network_health	load_silver_network_health	40	2026-09-07 09:27:40.240327+03
\.


--
-- Data for Name: data_quality_results; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_quality_results (quality_result_id, run_id, table_name, check_name, check_type, status, records_checked, records_failed, failure_rate_pct, details, checked_at, error_message, severity) FROM stdin;
1	101	measurements	traffic_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 08:42:58.322164+03	\N	INFO
2	101	measurements	latency_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 08:42:58.329883+03	\N	INFO
3	101	measurements	packet_loss_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 08:42:58.333205+03	\N	INFO
4	101	measurements	availability_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 08:42:58.337324+03	\N	INFO
5	101	measurements	measured_at_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 08:42:58.347055+03	\N	INFO
6	101	measurements	site_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 08:42:58.35302+03	\N	INFO
7	101	measurements	equipment_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 08:42:58.357581+03	\N	INFO
8	101	measurements	measurement_site_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 08:42:58.424351+03	\N	INFO
9	101	measurements	measurement_equipment_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 08:42:58.434934+03	\N	INFO
10	101	measurements	negative_traffic	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:42:58.484688+03	\N	INFO
11	101	measurements	negative_latency	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:42:58.487896+03	\N	INFO
12	101	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:42:58.489639+03	\N	INFO
13	101	measurements	invalid_availability	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:42:58.491496+03	\N	INFO
14	101	measurements	orphan_sites	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:42:58.493196+03	\N	INFO
15	101	measurements	orphan_equipment	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:42:58.494953+03	\N	INFO
16	102	measurements	traffic_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 08:58:41.82789+03	\N	INFO
17	102	measurements	latency_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 08:58:41.836664+03	\N	INFO
18	102	measurements	packet_loss_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 08:58:41.83979+03	\N	INFO
19	102	measurements	availability_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 08:58:41.844079+03	\N	INFO
20	102	measurements	measured_at_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 08:58:41.847266+03	\N	INFO
21	102	measurements	site_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 08:58:41.850058+03	\N	INFO
22	102	measurements	equipment_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 08:58:41.852926+03	\N	INFO
23	102	measurements	measurement_site_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 08:58:41.924741+03	\N	INFO
24	102	measurements	measurement_equipment_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 08:58:41.935037+03	\N	INFO
25	102	measurements	negative_traffic	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:58:41.990597+03	\N	INFO
26	102	measurements	negative_latency	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:58:41.993621+03	\N	INFO
27	102	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:58:41.995164+03	\N	INFO
28	102	measurements	invalid_availability	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:58:41.99683+03	\N	INFO
29	102	measurements	orphan_sites	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:58:41.99834+03	\N	INFO
30	102	measurements	orphan_equipment	CRITICAL_GATE	PASS	40	0	0.000	Critical parameter values honor all boundary rules perfectly.	2026-09-07 08:58:41.999799+03	\N	INFO
31	103	measurements	traffic_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:01:48.289961+03	\N	INFO
32	103	measurements	latency_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:01:48.296298+03	\N	INFO
33	103	measurements	packet_loss_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:01:48.299808+03	\N	INFO
34	103	measurements	availability_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:01:48.303057+03	\N	INFO
35	103	measurements	measured_at_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:01:48.307213+03	\N	INFO
36	103	measurements	site_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:01:48.311402+03	\N	INFO
37	103	measurements	equipment_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:01:48.314488+03	\N	INFO
38	103	measurements	measurement_site_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:01:48.381577+03	\N	INFO
39	103	measurements	measurement_equipment_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:01:48.394427+03	\N	INFO
40	103	sites	duplicate_sites	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for duplicate_sites pass perfectly.	2026-09-07 09:01:48.437451+03	\N	INFO
41	103	sites	invalid_latitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_latitude pass perfectly.	2026-09-07 09:01:48.446133+03	\N	INFO
42	103	sites	invalid_longitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_longitude pass perfectly.	2026-09-07 09:01:48.452342+03	\N	INFO
43	103	sites	missing_site_name	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for missing_site_name pass perfectly.	2026-09-07 09:01:48.464169+03	\N	INFO
44	103	equipment	orphan_equipment_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_equipment_sites pass perfectly.	2026-09-07 09:01:48.474824+03	\N	INFO
46	103	equipment	future_installation_date	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for future_installation_date pass perfectly.	2026-09-07 09:01:48.500865+03	\N	INFO
48	103	measurements	negative_latency	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_latency pass perfectly.	2026-09-07 09:01:48.521788+03	\N	INFO
50	103	measurements	invalid_availability	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_availability pass perfectly.	2026-09-07 09:01:48.536448+03	\N	INFO
52	103	measurements	orphan_measurement_equipment	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_equipment pass perfectly.	2026-09-07 09:01:48.551046+03	\N	INFO
54	103	incidents	orphan_incident_equipment	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_equipment pass perfectly.	2026-09-07 09:01:48.571719+03	\N	INFO
56	103	incidents	missing_incident_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_incident_type pass perfectly.	2026-09-07 09:01:48.583822+03	\N	INFO
45	103	equipment	missing_equipment_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_equipment_type pass perfectly.	2026-09-07 09:01:48.483992+03	\N	INFO
47	103	measurements	negative_traffic	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_traffic pass perfectly.	2026-09-07 09:01:48.51678+03	\N	INFO
49	103	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_packet_loss pass perfectly.	2026-09-07 09:01:48.530077+03	\N	INFO
51	103	measurements	orphan_measurement_sites	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_sites pass perfectly.	2026-09-07 09:01:48.544161+03	\N	INFO
53	103	incidents	orphan_incident_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_sites pass perfectly.	2026-09-07 09:01:48.566399+03	\N	INFO
55	103	incidents	invalid_incident_times	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for invalid_incident_times pass perfectly.	2026-09-07 09:01:48.578805+03	\N	INFO
57	103	incidents	missing_severity	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_severity pass perfectly.	2026-09-07 09:01:48.588611+03	\N	INFO
58	104	measurements	traffic_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:25:55.13759+03	\N	INFO
59	104	measurements	latency_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:25:55.15049+03	\N	INFO
60	104	measurements	packet_loss_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:25:55.155548+03	\N	INFO
61	104	measurements	availability_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:25:55.158997+03	\N	INFO
62	104	measurements	measured_at_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:25:55.162757+03	\N	INFO
63	104	measurements	site_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:25:55.166722+03	\N	INFO
64	104	measurements	equipment_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:25:55.172198+03	\N	INFO
65	104	measurements	measurement_site_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:25:55.243455+03	\N	INFO
66	104	measurements	measurement_equipment_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:25:55.254252+03	\N	INFO
67	105	measurements	traffic_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:26:05.838432+03	\N	INFO
68	105	measurements	latency_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:26:05.844086+03	\N	INFO
69	105	measurements	packet_loss_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:26:05.848211+03	\N	INFO
70	105	measurements	availability_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:26:05.851669+03	\N	INFO
71	105	measurements	measured_at_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:26:05.854881+03	\N	INFO
72	105	measurements	site_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:26:05.858026+03	\N	INFO
73	105	measurements	equipment_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:26:05.861094+03	\N	INFO
74	105	measurements	measurement_site_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:26:05.928088+03	\N	INFO
75	105	measurements	measurement_equipment_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:26:05.939239+03	\N	INFO
76	106	measurements	traffic_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:27:40.045371+03	\N	INFO
77	106	measurements	latency_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:27:40.051593+03	\N	INFO
78	106	measurements	packet_loss_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:27:40.05599+03	\N	INFO
79	106	measurements	availability_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:27:40.06017+03	\N	INFO
80	106	measurements	measured_at_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:27:40.063312+03	\N	INFO
81	106	measurements	site_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:27:40.067625+03	\N	INFO
82	106	measurements	equipment_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:27:40.073461+03	\N	INFO
83	106	measurements	measurement_site_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:27:40.14589+03	\N	INFO
84	106	measurements	measurement_equipment_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:27:40.156148+03	\N	INFO
85	106	sites	duplicate_sites	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for duplicate_sites pass perfectly.	2026-09-07 09:27:40.25175+03	\N	INFO
86	106	sites	invalid_latitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_latitude pass perfectly.	2026-09-07 09:27:40.25808+03	\N	INFO
87	106	sites	invalid_longitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_longitude pass perfectly.	2026-09-07 09:27:40.262283+03	\N	INFO
88	106	sites	missing_site_name	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for missing_site_name pass perfectly.	2026-09-07 09:27:40.265819+03	\N	INFO
89	106	equipment	orphan_equipment_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_equipment_sites pass perfectly.	2026-09-07 09:27:40.273416+03	\N	INFO
90	106	equipment	missing_equipment_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_equipment_type pass perfectly.	2026-09-07 09:27:40.277722+03	\N	INFO
91	106	equipment	future_installation_date	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for future_installation_date pass perfectly.	2026-09-07 09:27:40.281528+03	\N	INFO
92	106	measurements	negative_traffic	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_traffic pass perfectly.	2026-09-07 09:27:40.284922+03	\N	INFO
93	106	measurements	negative_latency	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_latency pass perfectly.	2026-09-07 09:27:40.29052+03	\N	INFO
94	106	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_packet_loss pass perfectly.	2026-09-07 09:27:40.294687+03	\N	INFO
96	106	measurements	orphan_measurement_sites	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_sites pass perfectly.	2026-09-07 09:27:40.303367+03	\N	INFO
98	106	incidents	orphan_incident_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_sites pass perfectly.	2026-09-07 09:27:40.317008+03	\N	INFO
100	106	incidents	invalid_incident_times	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for invalid_incident_times pass perfectly.	2026-09-07 09:27:40.328882+03	\N	INFO
102	106	incidents	missing_severity	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_severity pass perfectly.	2026-09-07 09:27:40.340524+03	\N	INFO
95	106	measurements	invalid_availability	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_availability pass perfectly.	2026-09-07 09:27:40.298466+03	\N	INFO
97	106	measurements	orphan_measurement_equipment	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_equipment pass perfectly.	2026-09-07 09:27:40.308112+03	\N	INFO
99	106	incidents	orphan_incident_equipment	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_equipment pass perfectly.	2026-09-07 09:27:40.322535+03	\N	INFO
101	106	incidents	missing_incident_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_incident_type pass perfectly.	2026-09-07 09:27:40.333516+03	\N	INFO
103	107	measurements	traffic_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:28:18.995543+03	\N	INFO
104	107	measurements	latency_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:28:19.007977+03	\N	INFO
105	107	measurements	packet_loss_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:28:19.011508+03	\N	INFO
106	107	measurements	availability_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:28:19.014758+03	\N	INFO
107	107	measurements	measured_at_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:28:19.018245+03	\N	INFO
108	107	measurements	site_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:28:19.023239+03	\N	INFO
109	107	measurements	equipment_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:28:19.02708+03	\N	INFO
110	107	measurements	measurement_site_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:28:19.095167+03	\N	INFO
111	107	measurements	measurement_equipment_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:28:19.105703+03	\N	INFO
112	108	measurements	traffic_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:28:26.388482+03	\N	INFO
113	108	measurements	latency_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:28:26.394635+03	\N	INFO
114	108	measurements	packet_loss_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:28:26.398776+03	\N	INFO
115	108	measurements	availability_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:28:26.403055+03	\N	INFO
116	108	measurements	measured_at_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:28:26.406857+03	\N	INFO
117	108	measurements	site_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:28:26.410482+03	\N	INFO
118	108	measurements	equipment_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:28:26.414054+03	\N	INFO
119	108	measurements	measurement_site_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:28:26.481345+03	\N	INFO
120	108	measurements	measurement_equipment_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:28:26.491761+03	\N	INFO
121	109	measurements	traffic_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:29:32.844116+03	\N	INFO
122	109	measurements	latency_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:29:32.849639+03	\N	INFO
123	109	measurements	packet_loss_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:29:32.853807+03	\N	INFO
124	109	measurements	availability_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:29:32.857429+03	\N	INFO
125	109	measurements	measured_at_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:29:32.860573+03	\N	INFO
126	109	measurements	site_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:29:32.863842+03	\N	INFO
127	109	measurements	equipment_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:29:32.867003+03	\N	INFO
128	109	measurements	measurement_site_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:29:32.932614+03	\N	INFO
129	109	measurements	measurement_equipment_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:29:32.943342+03	\N	INFO
130	110	measurements	traffic_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:30:29.681674+03	\N	INFO
131	110	measurements	latency_non_negative	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:30:29.687649+03	\N	INFO
132	110	measurements	packet_loss_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:30:29.691454+03	\N	INFO
133	110	measurements	availability_valid_range	VALIDITY	PASS	40	0	0.000	Measurement values are within expected ranges.	2026-09-07 09:30:29.695919+03	\N	INFO
134	110	measurements	measured_at_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:30:29.699858+03	\N	INFO
135	110	measurements	site_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:30:29.703463+03	\N	INFO
136	110	measurements	equipment_id_not_null	COMPLETENESS	PASS	40	0	0.000	Required fields contain no null elements.	2026-09-07 09:30:29.706989+03	\N	INFO
137	110	measurements	measurement_site_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:30:29.773064+03	\N	INFO
138	110	measurements	measurement_equipment_exists	REFERENTIAL_INTEGRITY	PASS	40	0	0.000	Referential integrity targets map perfectly to upstream parents.	2026-09-07 09:30:29.783596+03	\N	INFO
139	116	sites	duplicate_sites	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for duplicate_sites pass perfectly.	2026-09-07 10:14:49.244484+03	\N	INFO
140	116	sites	invalid_latitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_latitude pass perfectly.	2026-09-07 10:14:49.25957+03	\N	INFO
141	116	sites	invalid_longitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_longitude pass perfectly.	2026-09-07 10:14:49.264481+03	\N	INFO
142	116	sites	missing_site_name	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for missing_site_name pass perfectly.	2026-09-07 10:14:49.269164+03	\N	INFO
143	116	equipment	orphan_equipment_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_equipment_sites pass perfectly.	2026-09-07 10:14:49.277125+03	\N	INFO
144	116	equipment	missing_equipment_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_equipment_type pass perfectly.	2026-09-07 10:14:49.281082+03	\N	INFO
145	116	equipment	future_installation_date	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for future_installation_date pass perfectly.	2026-09-07 10:14:49.285571+03	\N	INFO
146	116	measurements	negative_traffic	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_traffic pass perfectly.	2026-09-07 10:14:49.290705+03	\N	INFO
147	116	measurements	negative_latency	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_latency pass perfectly.	2026-09-07 10:14:49.296805+03	\N	INFO
148	116	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_packet_loss pass perfectly.	2026-09-07 10:14:49.301692+03	\N	INFO
149	116	measurements	invalid_availability	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_availability pass perfectly.	2026-09-07 10:14:49.305458+03	\N	INFO
150	116	measurements	orphan_measurement_sites	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_sites pass perfectly.	2026-09-07 10:14:49.309814+03	\N	INFO
151	116	measurements	orphan_measurement_equipment	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_equipment pass perfectly.	2026-09-07 10:14:49.314544+03	\N	INFO
152	116	incidents	orphan_incident_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_sites pass perfectly.	2026-09-07 10:14:49.321484+03	\N	INFO
153	116	incidents	orphan_incident_equipment	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_equipment pass perfectly.	2026-09-07 10:14:49.325545+03	\N	INFO
154	116	incidents	invalid_incident_times	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for invalid_incident_times pass perfectly.	2026-09-07 10:14:49.330507+03	\N	INFO
155	116	incidents	missing_incident_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_incident_type pass perfectly.	2026-09-07 10:14:49.335191+03	\N	INFO
156	116	incidents	missing_severity	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_severity pass perfectly.	2026-09-07 10:14:49.33871+03	\N	INFO
157	117	sites	duplicate_sites	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for duplicate_sites pass perfectly.	2026-09-07 10:14:55.219597+03	\N	INFO
158	117	sites	invalid_latitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_latitude pass perfectly.	2026-09-07 10:14:55.225472+03	\N	INFO
159	117	sites	invalid_longitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_longitude pass perfectly.	2026-09-07 10:14:55.229491+03	\N	INFO
160	117	sites	missing_site_name	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for missing_site_name pass perfectly.	2026-09-07 10:14:55.23321+03	\N	INFO
161	117	equipment	orphan_equipment_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_equipment_sites pass perfectly.	2026-09-07 10:14:55.242612+03	\N	INFO
162	117	equipment	missing_equipment_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_equipment_type pass perfectly.	2026-09-07 10:14:55.246722+03	\N	INFO
163	117	equipment	future_installation_date	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for future_installation_date pass perfectly.	2026-09-07 10:14:55.250369+03	\N	INFO
164	117	measurements	negative_traffic	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_traffic pass perfectly.	2026-09-07 10:14:55.254328+03	\N	INFO
165	117	measurements	negative_latency	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_latency pass perfectly.	2026-09-07 10:14:55.258921+03	\N	INFO
166	117	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_packet_loss pass perfectly.	2026-09-07 10:14:55.262906+03	\N	INFO
167	117	measurements	invalid_availability	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_availability pass perfectly.	2026-09-07 10:14:55.266808+03	\N	INFO
168	117	measurements	orphan_measurement_sites	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_sites pass perfectly.	2026-09-07 10:14:55.270607+03	\N	INFO
169	117	measurements	orphan_measurement_equipment	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_equipment pass perfectly.	2026-09-07 10:14:55.275599+03	\N	INFO
170	117	incidents	orphan_incident_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_sites pass perfectly.	2026-09-07 10:14:55.282086+03	\N	INFO
171	117	incidents	orphan_incident_equipment	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_equipment pass perfectly.	2026-09-07 10:14:55.285774+03	\N	INFO
172	117	incidents	invalid_incident_times	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for invalid_incident_times pass perfectly.	2026-09-07 10:14:55.289733+03	\N	INFO
173	117	incidents	missing_incident_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_incident_type pass perfectly.	2026-09-07 10:14:55.294104+03	\N	INFO
174	117	incidents	missing_severity	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_severity pass perfectly.	2026-09-07 10:14:55.297672+03	\N	INFO
175	118	sites	duplicate_sites	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for duplicate_sites pass perfectly.	2026-09-07 10:23:49.489871+03	\N	INFO
176	118	sites	invalid_latitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_latitude pass perfectly.	2026-09-07 10:23:49.504233+03	\N	INFO
177	118	sites	invalid_longitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_longitude pass perfectly.	2026-09-07 10:23:49.508705+03	\N	INFO
178	118	sites	missing_site_name	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for missing_site_name pass perfectly.	2026-09-07 10:23:49.51257+03	\N	INFO
179	118	equipment	orphan_equipment_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_equipment_sites pass perfectly.	2026-09-07 10:23:49.520202+03	\N	INFO
180	118	equipment	missing_equipment_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_equipment_type pass perfectly.	2026-09-07 10:23:49.523786+03	\N	INFO
181	118	equipment	future_installation_date	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for future_installation_date pass perfectly.	2026-09-07 10:23:49.527415+03	\N	INFO
182	118	measurements	negative_traffic	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_traffic pass perfectly.	2026-09-07 10:23:49.532066+03	\N	INFO
183	118	measurements	negative_latency	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_latency pass perfectly.	2026-09-07 10:23:49.537627+03	\N	INFO
184	118	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_packet_loss pass perfectly.	2026-09-07 10:23:49.541855+03	\N	INFO
185	118	measurements	invalid_availability	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_availability pass perfectly.	2026-09-07 10:23:49.545577+03	\N	INFO
186	118	measurements	orphan_measurement_sites	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_sites pass perfectly.	2026-09-07 10:23:49.550426+03	\N	INFO
187	118	measurements	orphan_measurement_equipment	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_equipment pass perfectly.	2026-09-07 10:23:49.554671+03	\N	INFO
188	118	incidents	orphan_incident_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_sites pass perfectly.	2026-09-07 10:23:49.560783+03	\N	INFO
189	118	incidents	orphan_incident_equipment	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_equipment pass perfectly.	2026-09-07 10:23:49.565277+03	\N	INFO
190	118	incidents	invalid_incident_times	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for invalid_incident_times pass perfectly.	2026-09-07 10:23:49.569468+03	\N	INFO
191	118	incidents	missing_incident_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_incident_type pass perfectly.	2026-09-07 10:23:49.572905+03	\N	INFO
192	118	incidents	missing_severity	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_severity pass perfectly.	2026-09-07 10:23:49.576421+03	\N	INFO
193	119	sites	duplicate_sites	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for duplicate_sites pass perfectly.	2026-09-07 16:56:58.867076+03	\N	INFO
194	119	sites	invalid_latitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_latitude pass perfectly.	2026-09-07 16:56:58.893145+03	\N	INFO
195	119	sites	invalid_longitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_longitude pass perfectly.	2026-09-07 16:56:58.898801+03	\N	INFO
196	119	sites	missing_site_name	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for missing_site_name pass perfectly.	2026-09-07 16:56:58.907129+03	\N	INFO
197	119	equipment	orphan_equipment_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_equipment_sites pass perfectly.	2026-09-07 16:56:58.919744+03	\N	INFO
198	119	equipment	missing_equipment_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_equipment_type pass perfectly.	2026-09-07 16:56:58.925711+03	\N	INFO
199	119	equipment	future_installation_date	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for future_installation_date pass perfectly.	2026-09-07 16:56:58.930013+03	\N	INFO
200	119	measurements	negative_traffic	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_traffic pass perfectly.	2026-09-07 16:56:58.934591+03	\N	INFO
201	119	measurements	negative_latency	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_latency pass perfectly.	2026-09-07 16:56:58.940103+03	\N	INFO
202	119	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_packet_loss pass perfectly.	2026-09-07 16:56:58.944446+03	\N	INFO
203	119	measurements	invalid_availability	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_availability pass perfectly.	2026-09-07 16:56:58.947637+03	\N	INFO
204	119	measurements	orphan_measurement_sites	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_sites pass perfectly.	2026-09-07 16:56:58.950968+03	\N	INFO
205	119	measurements	orphan_measurement_equipment	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_equipment pass perfectly.	2026-09-07 16:56:58.956151+03	\N	INFO
206	119	incidents	orphan_incident_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_sites pass perfectly.	2026-09-07 16:56:58.962205+03	\N	INFO
207	119	incidents	orphan_incident_equipment	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_equipment pass perfectly.	2026-09-07 16:56:58.965654+03	\N	INFO
208	119	incidents	invalid_incident_times	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for invalid_incident_times pass perfectly.	2026-09-07 16:56:58.969158+03	\N	INFO
209	119	incidents	missing_incident_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_incident_type pass perfectly.	2026-09-07 16:56:58.97361+03	\N	INFO
210	119	incidents	missing_severity	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_severity pass perfectly.	2026-09-07 16:56:58.97688+03	\N	INFO
211	120	sites	duplicate_sites	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for duplicate_sites pass perfectly.	2026-09-09 06:32:27.364886+03	\N	INFO
212	120	sites	invalid_latitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_latitude pass perfectly.	2026-09-09 06:32:27.394057+03	\N	INFO
213	120	sites	invalid_longitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_longitude pass perfectly.	2026-09-09 06:32:27.398265+03	\N	INFO
214	120	sites	missing_site_name	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for missing_site_name pass perfectly.	2026-09-09 06:32:27.403577+03	\N	INFO
215	120	equipment	orphan_equipment_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_equipment_sites pass perfectly.	2026-09-09 06:32:27.409206+03	\N	INFO
216	120	equipment	missing_equipment_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_equipment_type pass perfectly.	2026-09-09 06:32:27.413573+03	\N	INFO
217	120	equipment	future_installation_date	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for future_installation_date pass perfectly.	2026-09-09 06:32:27.417903+03	\N	INFO
218	120	measurements	negative_traffic	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_traffic pass perfectly.	2026-09-09 06:32:27.42202+03	\N	INFO
219	120	measurements	negative_latency	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_latency pass perfectly.	2026-09-09 06:32:27.427368+03	\N	INFO
220	120	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_packet_loss pass perfectly.	2026-09-09 06:32:27.433771+03	\N	INFO
221	120	measurements	invalid_availability	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_availability pass perfectly.	2026-09-09 06:32:27.437293+03	\N	INFO
222	120	measurements	orphan_measurement_sites	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_sites pass perfectly.	2026-09-09 06:32:27.441535+03	\N	INFO
223	120	measurements	orphan_measurement_equipment	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_equipment pass perfectly.	2026-09-09 06:32:27.446321+03	\N	INFO
224	120	incidents	orphan_incident_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_sites pass perfectly.	2026-09-09 06:32:27.45687+03	\N	INFO
225	120	incidents	orphan_incident_equipment	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_equipment pass perfectly.	2026-09-09 06:32:27.461706+03	\N	INFO
226	120	incidents	invalid_incident_times	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for invalid_incident_times pass perfectly.	2026-09-09 06:32:27.467522+03	\N	INFO
227	120	incidents	missing_incident_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_incident_type pass perfectly.	2026-09-09 06:32:27.472563+03	\N	INFO
228	120	incidents	missing_severity	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_severity pass perfectly.	2026-09-09 06:32:27.476166+03	\N	INFO
229	121	sites	duplicate_sites	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for duplicate_sites pass perfectly.	2026-09-09 06:32:33.78824+03	\N	INFO
230	121	sites	invalid_latitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_latitude pass perfectly.	2026-09-09 06:32:33.793846+03	\N	INFO
231	121	sites	invalid_longitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_longitude pass perfectly.	2026-09-09 06:32:33.797475+03	\N	INFO
232	121	sites	missing_site_name	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for missing_site_name pass perfectly.	2026-09-09 06:32:33.801314+03	\N	INFO
233	121	equipment	orphan_equipment_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_equipment_sites pass perfectly.	2026-09-09 06:32:33.806613+03	\N	INFO
234	121	equipment	missing_equipment_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_equipment_type pass perfectly.	2026-09-09 06:32:33.810829+03	\N	INFO
235	121	equipment	future_installation_date	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for future_installation_date pass perfectly.	2026-09-09 06:32:33.816383+03	\N	INFO
236	121	measurements	negative_traffic	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_traffic pass perfectly.	2026-09-09 06:32:33.821739+03	\N	INFO
237	121	measurements	negative_latency	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for negative_latency pass perfectly.	2026-09-09 06:32:33.827747+03	\N	INFO
238	121	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_packet_loss pass perfectly.	2026-09-09 06:32:33.833725+03	\N	INFO
239	121	measurements	invalid_availability	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for invalid_availability pass perfectly.	2026-09-09 06:32:33.837349+03	\N	INFO
240	121	measurements	orphan_measurement_sites	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_sites pass perfectly.	2026-09-09 06:32:33.841325+03	\N	INFO
241	121	measurements	orphan_measurement_equipment	CRITICAL_GATE	PASS	40	0	0.000	Critical contract rules for orphan_measurement_equipment pass perfectly.	2026-09-09 06:32:33.845685+03	\N	INFO
242	121	incidents	orphan_incident_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_sites pass perfectly.	2026-09-09 06:32:33.852866+03	\N	INFO
243	121	incidents	orphan_incident_equipment	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_equipment pass perfectly.	2026-09-09 06:32:33.85654+03	\N	INFO
244	121	incidents	invalid_incident_times	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for invalid_incident_times pass perfectly.	2026-09-09 06:32:33.8617+03	\N	INFO
245	121	incidents	missing_incident_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_incident_type pass perfectly.	2026-09-09 06:32:33.869424+03	\N	INFO
246	121	incidents	missing_severity	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_severity pass perfectly.	2026-09-09 06:32:33.875007+03	\N	INFO
247	122	sites	duplicate_sites	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for duplicate_sites pass perfectly.	2026-09-09 06:38:59.413079+03	\N	INFO
248	122	sites	invalid_latitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_latitude pass perfectly.	2026-09-09 06:38:59.4309+03	\N	INFO
249	122	sites	invalid_longitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_longitude pass perfectly.	2026-09-09 06:38:59.437606+03	\N	INFO
250	122	sites	missing_site_name	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for missing_site_name pass perfectly.	2026-09-09 06:38:59.442388+03	\N	INFO
251	122	equipment	orphan_equipment_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_equipment_sites pass perfectly.	2026-09-09 06:38:59.449345+03	\N	INFO
252	122	equipment	missing_equipment_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_equipment_type pass perfectly.	2026-09-09 06:38:59.454776+03	\N	INFO
253	122	equipment	future_installation_date	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for future_installation_date pass perfectly.	2026-09-09 06:38:59.459234+03	\N	INFO
254	122	measurements	negative_traffic	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for negative_traffic pass perfectly.	2026-09-09 06:38:59.467895+03	\N	INFO
255	122	measurements	negative_latency	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for negative_latency pass perfectly.	2026-09-09 06:38:59.472524+03	\N	INFO
256	122	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for invalid_packet_loss pass perfectly.	2026-09-09 06:38:59.477295+03	\N	INFO
257	122	measurements	invalid_availability	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for invalid_availability pass perfectly.	2026-09-09 06:38:59.483539+03	\N	INFO
258	122	measurements	orphan_measurement_sites	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for orphan_measurement_sites pass perfectly.	2026-09-09 06:38:59.487271+03	\N	INFO
259	122	measurements	orphan_measurement_equipment	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for orphan_measurement_equipment pass perfectly.	2026-09-09 06:38:59.490749+03	\N	INFO
260	122	incidents	orphan_incident_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_sites pass perfectly.	2026-09-09 06:38:59.501427+03	\N	INFO
261	122	incidents	orphan_incident_equipment	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_equipment pass perfectly.	2026-09-09 06:38:59.505224+03	\N	INFO
262	122	incidents	invalid_incident_times	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for invalid_incident_times pass perfectly.	2026-09-09 06:38:59.509254+03	\N	INFO
263	122	incidents	missing_incident_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_incident_type pass perfectly.	2026-09-09 06:38:59.514846+03	\N	INFO
264	122	incidents	missing_severity	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_severity pass perfectly.	2026-09-09 06:38:59.520254+03	\N	INFO
265	127	sites	duplicate_sites	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for duplicate_sites pass perfectly.	2026-09-09 08:03:31.869128+03	\N	INFO
266	127	sites	invalid_latitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_latitude pass perfectly.	2026-09-09 08:03:31.876913+03	\N	INFO
267	127	sites	invalid_longitude	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for invalid_longitude pass perfectly.	2026-09-09 08:03:31.880916+03	\N	INFO
268	127	sites	missing_site_name	CRITICAL_GATE	PASS	11	0	0.000	Critical contract rules for missing_site_name pass perfectly.	2026-09-09 08:03:31.88627+03	\N	INFO
269	127	equipment	orphan_equipment_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_equipment_sites pass perfectly.	2026-09-09 08:03:31.891297+03	\N	INFO
270	127	equipment	missing_equipment_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_equipment_type pass perfectly.	2026-09-09 08:03:31.894968+03	\N	INFO
271	127	equipment	future_installation_date	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for future_installation_date pass perfectly.	2026-09-09 08:03:31.899373+03	\N	INFO
272	127	measurements	negative_traffic	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for negative_traffic pass perfectly.	2026-09-09 08:03:31.90428+03	\N	INFO
273	127	measurements	negative_latency	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for negative_latency pass perfectly.	2026-09-09 08:03:31.909152+03	\N	INFO
274	127	measurements	invalid_packet_loss	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for invalid_packet_loss pass perfectly.	2026-09-09 08:03:31.912885+03	\N	INFO
275	127	measurements	invalid_availability	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for invalid_availability pass perfectly.	2026-09-09 08:03:31.91678+03	\N	INFO
276	127	measurements	orphan_measurement_sites	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for orphan_measurement_sites pass perfectly.	2026-09-09 08:03:31.922385+03	\N	INFO
277	127	measurements	orphan_measurement_equipment	CRITICAL_GATE	PASS	41	0	0.000	Critical contract rules for orphan_measurement_equipment pass perfectly.	2026-09-09 08:03:31.926488+03	\N	INFO
278	127	incidents	orphan_incident_sites	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_sites pass perfectly.	2026-09-09 08:03:31.932937+03	\N	INFO
279	127	incidents	orphan_incident_equipment	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for orphan_incident_equipment pass perfectly.	2026-09-09 08:03:31.938272+03	\N	INFO
280	127	incidents	invalid_incident_times	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for invalid_incident_times pass perfectly.	2026-09-09 08:03:31.943272+03	\N	INFO
281	127	incidents	missing_incident_type	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_incident_type pass perfectly.	2026-09-09 08:03:31.947187+03	\N	INFO
282	127	incidents	missing_severity	CRITICAL_GATE	PASS	8	0	0.000	Critical contract rules for missing_severity pass perfectly.	2026-09-09 08:03:31.951239+03	\N	INFO
283	128	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
284	128	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
285	128	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
286	128	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
287	128	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
288	128	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
289	128	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
290	128	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
291	128	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
292	128	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
293	128	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
294	128	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
295	128	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
296	128	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
297	128	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
298	128	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
299	128	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
300	128	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:07:37.072598+03	\N	INFO
302	129	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
303	129	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
304	129	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
305	129	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
306	129	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
307	129	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
308	129	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
310	129	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
311	129	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
312	129	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
313	129	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
314	129	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
315	129	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
316	129	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
317	129	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
318	129	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:13:47.988534+03	\N	INFO
322	130	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
323	130	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
324	130	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
325	130	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
326	130	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
327	130	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
328	130	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
329	130	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
330	130	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
331	130	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
332	130	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
333	130	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
334	130	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
335	130	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
336	130	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
337	130	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
338	130	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
339	130	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-09 08:46:19.9069+03	\N	INFO
340	131	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
341	131	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
342	131	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
343	131	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
344	131	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
345	131	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
346	131	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
347	131	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
348	131	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
349	131	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
350	131	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
351	131	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
352	131	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
353	131	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
354	131	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
355	131	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
356	131	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
357	131	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:00:46.033109+03	\N	INFO
358	132	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
359	132	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
360	132	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
361	132	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
362	132	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
363	132	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
364	132	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
365	132	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
366	132	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
367	132	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
368	132	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
369	132	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
370	132	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
371	132	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
372	132	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
373	132	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
374	132	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
375	132	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:03:00.376761+03	\N	INFO
376	133	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
377	133	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
378	133	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
379	133	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
380	133	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
381	133	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
382	133	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
383	133	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
384	133	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
385	133	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
386	133	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
387	133	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
388	133	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
389	133	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
390	133	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
391	133	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
392	133	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
393	133	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:13:19.67963+03	\N	INFO
394	136	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
395	136	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
396	136	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
397	136	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
398	136	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
399	136	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
400	136	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
401	136	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
402	136	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
403	136	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
404	136	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
405	136	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
406	136	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
407	136	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
408	136	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
409	136	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
410	136	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
411	136	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:11.892054+03	\N	INFO
412	137	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
413	137	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
414	137	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
415	137	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
416	137	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
417	137	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
418	137	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
419	137	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
420	137	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
421	137	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
422	137	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
423	137	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
424	137	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
425	137	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
426	137	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
427	137	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
428	137	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
429	137	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-10 21:30:18.321931+03	\N	INFO
430	138	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
431	138	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
432	138	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
433	138	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
434	138	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
435	138	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
436	138	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
437	138	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
438	138	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
439	138	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
440	138	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
441	138	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
442	138	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
443	138	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
444	138	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
445	138	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
446	138	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
447	138	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:29:14.70168+03	\N	INFO
448	139	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
449	139	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
450	139	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
451	139	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
452	139	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
453	139	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
454	139	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
455	139	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
456	139	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
457	139	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
458	139	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
459	139	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
460	139	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
461	139	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
462	139	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
463	139	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
464	139	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
465	139	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:36:40.501224+03	\N	INFO
466	140	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
467	140	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
468	140	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
469	140	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
470	140	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
471	140	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
472	140	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
473	140	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
474	140	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
475	140	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
476	140	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
477	140	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
478	140	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
479	140	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
480	140	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
481	140	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
482	140	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
483	140	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:15.891618+03	\N	INFO
484	141	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
485	141	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
486	141	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
487	141	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
488	141	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
489	141	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
490	141	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
491	141	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
492	141	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
493	141	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
494	141	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
495	141	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
496	141	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
497	141	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
498	141	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
499	141	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
500	141	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
501	141	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 11:47:19.951327+03	\N	INFO
502	142	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
503	142	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
504	142	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
505	142	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
506	142	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
507	142	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
508	142	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
509	142	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
510	142	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
511	142	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
512	142	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
513	142	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
514	142	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
515	142	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
516	142	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
517	142	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
518	142	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
519	142	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:22:25.812672+03	\N	INFO
520	143	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
521	143	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
522	143	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
523	143	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
524	143	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
525	143	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
526	143	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
527	143	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
528	143	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
529	143	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
530	143	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
531	143	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
532	143	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
533	143	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
534	143	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
535	143	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
536	143	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
537	143	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:28:20.795211+03	\N	INFO
538	144	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
539	144	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
540	144	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
541	144	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
542	144	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
543	144	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
544	144	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
545	144	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
546	144	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
547	144	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
548	144	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
549	144	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
550	144	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
551	144	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
552	144	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
553	144	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
554	144	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
555	144	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 12:46:18.546152+03	\N	INFO
556	145	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
557	145	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
558	145	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
559	145	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
560	145	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
561	145	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
562	145	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
563	145	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
564	145	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
565	145	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
566	145	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
567	145	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
568	145	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
569	145	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
570	145	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
571	145	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
572	145	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
573	145	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:18:59.562008+03	\N	INFO
574	147	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
575	147	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
576	147	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
577	147	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
578	147	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
579	147	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
580	147	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
581	147	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
582	147	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
583	147	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
584	147	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
585	147	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
586	147	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
587	147	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
588	147	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
589	147	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
590	147	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
591	147	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:43:00.897082+03	\N	INFO
592	148	sites	duplicate_sites	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
593	148	sites	invalid_latitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
594	148	sites	invalid_longitude	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
595	148	sites	missing_site_name	VALIDITY	PASS	11	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
596	148	equipment	orphan_equipment_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
597	148	equipment	missing_equipment_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
598	148	equipment	future_installation_date	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
599	148	measurements	negative_traffic	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
600	148	measurements	negative_latency	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
601	148	measurements	invalid_packet_loss	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
602	148	measurements	invalid_availability	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
603	148	measurements	orphan_measurement_sites	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
604	148	measurements	orphan_measurement_equipment	VALIDITY	PASS	41	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
605	148	incidents	orphan_incident_sites	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
606	148	incidents	orphan_incident_equipment	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
607	148	incidents	invalid_incident_times	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
608	148	incidents	missing_incident_type	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
609	148	incidents	missing_severity	VALIDITY	PASS	8	0	0.000	\N	2026-09-11 13:44:35.246055+03	\N	INFO
\.


--
-- Data for Name: equipment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment (equipment_id, site_id, equipment_type, manufacturer, model, installation_date, status) FROM stdin;
1	6	Router	Cisco	ASR1001-X	2024-01-15	Active
2	6	Radio	Ericsson	MINI-LINK 6352	2024-02-10	Active
3	7	Router	Cisco	ASR1001-X	2023-11-20	Active
4	7	Switch	Huawei	S5735	2023-12-05	Active
5	8	Radio	Ericsson	MINI-LINK 6352	2024-03-18	Active
6	9	Router	Cisco	ASR1001-X	2024-04-12	Active
7	10	Radio	Nokia	FlexiPacket	2023-09-25	Maintenance
8	12	Router	Cisco	ISR4331	2024-05-10	Active
\.


--
-- Data for Name: gold_equipment_health; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gold_equipment_health (equipment_id, equipment_type, manufacturer, model, measurement_count, avg_latency_ms, avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct, health_status, record_count, updated_at) FROM stdin;
4	Switch	Huawei	S5735	5	23.2600000000000000	0.80000000000000000000	-53.30	99.1000000000000000	Healthy	5	2026-09-11 13:18:59.633708
7	Radio	Nokia	FlexiPacket	3	62.9333333333333333	5.1000000000000000	-73.80	95.5000000000000000	Warning	3	2026-09-11 13:18:59.633708
6	Router	Cisco	ASR1001-X	3	63.5000000000000000	5.2666666666666667	-74.60	95.3333333333333333	Warning	3	2026-09-11 13:18:59.633708
3	Router	Cisco	ASR1001-X	4	34.8000000000000000	1.2500000000000000	-62.10	98.9000000000000000	Healthy	4	2026-09-11 13:18:59.633708
1	Router	Cisco	ASR1001-X	11	26.2909090909090909	0.58181818181818181818	-59.66	99.5181818181818182	Healthy	11	2026-09-11 13:18:59.633708
5	Radio	Ericsson	MINI-LINK 6352	4	45.1500000000000000	2.6750000000000000	-68.35	97.5000000000000000	Warning	4	2026-09-11 13:18:59.633708
2	Radio	Ericsson	MINI-LINK 6352	8	32.1500000000000000	1.6625000000000000	-58.54	98.5500000000000000	Healthy	8	2026-09-11 13:18:59.633708
8	Router	Cisco	ISR4331	3	31.7000000000000000	0.96666666666666666667	-61.97	98.6000000000000000	Healthy	3	2026-09-11 13:18:59.633708
\.


--
-- Data for Name: gold_incident_summary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gold_incident_summary (site_id, site_name, region, district, total_incidents, critical_incidents, high_incidents, medium_incidents, low_incidents, avg_resolution_minutes) FROM stdin;
8	Masaka South	Central	Masaka	1	0	1	0	0	150.00
9	Arua North	West Nile	Arua	1	1	0	0	0	140.00
10	Kabale Rural	Western	Kabale	1	1	0	0	0	50.00
7	Mbale East	Eastern	Mbale	2	0	1	1	0	75.00
6	Entebbe Central	Central	Wakiso	2	0	0	1	1	22.50
12	Soroti Central	Eastern	Soroti	1	0	0	1	0	45.00
\.


--
-- Data for Name: gold_network_intelligence; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gold_network_intelligence (site_id, site_name, region, district, measurement_date, measurement_count, avg_traffic_mb, avg_latency_ms, avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct, total_incidents, critical_incidents, high_incidents, avg_resolution_minutes, network_health) FROM stdin;
8	Masaka South	Central	Masaka	2026-08-28	2	7515.60	45.35	2.75	-69.85	97.35	1	0	1	150.00	Warning
9	Arua North	West Nile	Arua	2026-08-28	2	6300.60	58.45	4.65	-72.80	96.10	1	1	0	140.00	Warning
10	Kabale Rural	Western	Kabale	2026-08-28	2	4095.35	77.05	7.05	-79.15	94.15	1	1	0	50.00	Critical
7	Mbale East	Eastern	Mbale	2026-08-28	4	10945.48	25.65	0.93	-54.75	99.18	2	0	1	75.00	Healthy
6	Entebbe Central	Central	Wakiso	2026-08-30	1	18500.50	35.20	1.10	-62.50	98.80	2	0	0	22.50	Healthy
6	Entebbe Central	Central	Wakiso	2026-08-28	4	12329.34	22.75	0.38	-55.70	99.80	2	0	0	22.50	Healthy
12	Soroti Central	Eastern	Soroti	2026-08-28	2	9000.60	32.85	1.00	-61.80	98.55	1	0	0	45.00	Healthy
1	Kampala Central Tower Hub	Central	Kampala	2026-08-01	1	1000.00	20.00	0.50	-60.00	99.90	0	0	0	0	Healthy
\.


--
-- Data for Name: gold_site_daily_performance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gold_site_daily_performance (site_id, site_name, region, district, measurement_date, measurement_count, avg_traffic_mb, avg_latency_ms, avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct, updated_at) FROM stdin;
8	Site 8	\N	District	\N	3	7410.53	44.30	2.53	\N	97.50	2026-09-11 13:18:59.615045
7	Site 7	\N	District	\N	5	10916.53	26.20	0.90	\N	99.20	2026-09-11 13:18:59.615045
10	Site 10	\N	District	\N	3	4030.32	75.90	6.87	\N	94.03	2026-09-11 13:18:59.615045
1	Kampala Central Tower Hub	\N	Kampala	\N	1	15000.00	30.00	1.00	\N	99.00	2026-09-11 13:18:59.615045
2	Site 2	\N	District	\N	1	9800.20	19.80	0.20	\N	99.90	2026-09-11 13:18:59.615045
3	Site 3	\N	District	\N	1	11200.75	35.60	1.20	\N	98.90	2026-09-11 13:18:59.615045
1	Site 1	\N	District	\N	7	12743.07	24.66	0.47	\N	99.61	2026-09-11 13:18:59.615045
4	Site 4	\N	District	\N	2	12250.28	23.35	0.60	\N	99.20	2026-09-11 13:18:59.615045
12	Site 12	\N	District	\N	4	9050.71	32.45	1.03	\N	98.50	2026-09-11 13:18:59.615045
9	Site 9	\N	District	\N	3	6233.93	57.33	4.50	\N	96.20	2026-09-11 13:18:59.615045
6	Site 6	\N	District	\N	11	13279.18	32.62	1.47	\N	98.71	2026-09-11 13:18:59.615045
10	Kabale Rural	\N	\N	2026-08-31	1	3900.2500000000000000	73.6000000000000000	6.5000000000000000	-78.2000000000000000	93.8000000000000000	2026-09-11 13:43:00.957435
6	Entebbe Central	\N	\N	2026-08-31	3	16400.400000000000	20.6333333333333333	0.23333333333333333333	-52.9000000000000000	99.6333333333333333	2026-09-11 13:43:00.957435
8	Masaka South	\N	\N	2026-08-28	2	7515.6000000000000000	45.3500000000000000	2.7500000000000000	-69.8500000000000000	97.3500000000000000	2026-09-11 13:43:00.957435
6	\N	\N	\N	2026-09-02	3	9683.9666666666666667	56.9000000000000000	4.3000000000000000	-71.4333333333333333	96.2666666666666667	2026-09-11 13:43:00.957435
1	\N	\N	\N	2026-09-01	1	15000.0000000000000000	25.0000000000000000	0.50000000000000000000	-60.0000000000000000	99.5000000000000000	2026-09-11 13:43:00.957435
1	Kampala Central Tower Hub	\N	\N	2026-08-01	1	1000.0000000000000000	20.0000000000000000	0.50000000000000000000	-60.0000000000000000	99.9000000000000000	2026-09-11 13:43:00.957435
6	Entebbe Central	\N	\N	2026-08-28	4	12329.3375000000000000	22.7500000000000000	0.37500000000000000000	-55.7000000000000000	99.8000000000000000	2026-09-11 13:43:00.957435
12	Soroti Central	\N	\N	2026-08-31	2	9100.8250000000000000	32.0500000000000000	1.05000000000000000000	-62.7000000000000000	98.4500000000000000	2026-09-11 13:43:00.957435
10	Kabale Rural	\N	\N	2026-08-28	2	4095.3500000000000000	77.0500000000000000	7.0500000000000000	-79.1500000000000000	94.1500000000000000	2026-09-11 13:43:00.957435
1	Kampala Central Tower Hub	\N	\N	2026-09-09	1	15000.0000000000000000	30.0000000000000000	1.00000000000000000000	-60.0000000000000000	99.0000000000000000	2026-09-11 13:43:00.957435
2	\N	\N	\N	2026-09-02	1	9800.2000000000000000	19.8000000000000000	0.20000000000000000000	-52.0000000000000000	99.9000000000000000	2026-09-11 13:43:00.957435
1	Kampala Central Tower Hub	\N	\N	2026-08-30	1	22000.000000000000	31.5000000000000000	0.70000000000000000000	-60.5000000000000000	99.1000000000000000	2026-09-11 13:43:00.957435
1	Kampala Central Tower Hub	\N	\N	2026-08-31	1	12500.5000000000000000	24.5000000000000000	0.40000000000000000000	-59.5000000000000000	99.8000000000000000	2026-09-11 13:43:00.957435
3	\N	\N	\N	2026-09-02	1	11200.7500000000000000	35.6000000000000000	1.20000000000000000000	-64.0000000000000000	98.9000000000000000	2026-09-11 13:43:00.957435
9	Arua North	\N	\N	2026-08-28	2	6300.6000000000000000	58.4500000000000000	4.6500000000000000	-72.8000000000000000	96.1000000000000000	2026-09-11 13:43:00.957435
4	\N	\N	\N	2026-09-02	2	12250.2750000000000000	23.3500000000000000	0.60000000000000000000	-53.4000000000000000	99.2000000000000000	2026-09-11 13:43:00.957435
7	Mbale East	\N	\N	2026-08-31	1	10800.7500000000000000	28.4000000000000000	0.80000000000000000000	-56.7000000000000000	99.3000000000000000	2026-09-11 13:43:00.957435
9	Arua North	\N	\N	2026-08-31	1	6100.6000000000000000	55.1000000000000000	4.2000000000000000	-71.5000000000000000	96.4000000000000000	2026-09-11 13:43:00.957435
6	Entebbe Central	\N	\N	2026-08-30	1	18500.5000000000000000	35.2000000000000000	1.10000000000000000000	-62.5000000000000000	98.8000000000000000	2026-09-11 13:43:00.957435
1	\N	\N	\N	2026-09-02	2	12250.2500000000000000	24.7500000000000000	0.45000000000000000000	-59.7500000000000000	99.6000000000000000	2026-09-11 13:43:00.957435
8	Masaka South	\N	\N	2026-08-31	1	7200.4000000000000000	42.2000000000000000	2.1000000000000000	-68.4000000000000000	97.8000000000000000	2026-09-11 13:43:00.957435
1	\N	\N	\N	2026-09-03	1	14200.5000000000000000	22.1000000000000000	0.30000000000000000000	-57.0000000000000000	99.8000000000000000	2026-09-11 13:43:00.957435
12	Soroti Central	\N	\N	2026-08-28	2	9000.6000000000000000	32.8500000000000000	1.00000000000000000000	-61.8000000000000000	98.5500000000000000	2026-09-11 13:43:00.957435
7	Mbale East	\N	\N	2026-08-28	4	10945.4750000000000000	25.6500000000000000	0.92500000000000000000	-54.7500000000000000	99.1750000000000000	2026-09-11 13:43:00.957435
\.


--
-- Data for Name: incidents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.incidents (incident_id, site_id, equipment_id, incident_type, severity, start_time, end_time, status, description) FROM stdin;
2	7	3	Packet Loss	High	2026-08-28 08:30:00	2026-08-28 10:00:00	Resolved	High packet loss detected on network router
3	7	4	Link Degradation	Medium	2026-08-28 09:20:00	2026-08-28 10:20:00	Resolved	Network link experiencing intermittent degradation
4	8	5	Signal Degradation	High	2026-08-28 08:45:00	2026-08-28 11:15:00	Resolved	Radio signal strength dropped below acceptable level
5	9	6	High Packet Loss	Critical	2026-08-28 08:10:00	2026-08-28 10:30:00	Resolved	Severe packet loss affecting network service
6	10	7	Link Down	Critical	2026-08-28 08:50:00	2026-08-28 09:40:00	Resolved	Radio link temporarily unavailable
7	12	8	High Latency	Medium	2026-08-28 09:10:00	2026-08-28 09:55:00	Resolved	Latency exceeded normal threshold
8	6	2	Packet Loss	Low	2026-08-28 08:25:00	2026-08-28 08:40:00	Resolved	Minor packet loss detected
1	6	1	High Latency	Medium	2026-08-28 09:15:00	\N	Resolved	Latency increased above normal operating threshold
\.


--
-- Data for Name: ingestion_batches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ingestion_batches (batch_id, pipeline_run_id, source_type, source_name, started_at, completed_at, records_received, records_loaded, status, error_message) FROM stdin;
\.


--
-- Data for Name: measurements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.measurements (measurement_id, equipment_id, site_id, measured_at, traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at, batch_id, source_record_id) FROM stdin;
2	1	6	2026-08-28 09:00:00	16820.75	27.10	0.60	-59.10	99.70	2026-08-30 08:05:39.994006	\N	\N
3	2	6	2026-08-28 08:00:00	8240.30	18.40	0.20	-52.40	99.90	2026-08-30 08:05:39.994006	\N	\N
4	2	6	2026-08-28 09:00:00	9015.80	21.20	0.30	-53.10	99.80	2026-08-30 08:05:39.994006	\N	\N
5	3	7	2026-08-28 08:00:00	11240.60	35.80	1.20	-63.50	98.90	2026-08-30 08:05:39.994006	\N	\N
6	3	7	2026-08-28 09:00:00	12450.20	39.40	1.80	-64.20	98.50	2026-08-30 08:05:39.994006	\N	\N
7	4	7	2026-08-28 08:00:00	9850.40	12.60	0.30	-45.20	99.70	2026-08-30 08:05:39.994006	\N	\N
8	4	7	2026-08-28 09:00:00	10240.70	14.80	0.40	-46.10	99.60	2026-08-30 08:05:39.994006	\N	\N
9	5	8	2026-08-28 08:00:00	7350.80	42.50	2.40	-69.30	97.80	2026-08-30 08:05:39.994006	\N	\N
10	5	8	2026-08-28 09:00:00	7680.40	48.20	3.10	-70.40	96.90	2026-08-30 08:05:39.994006	\N	\N
11	6	9	2026-08-28 08:00:00	6420.30	55.60	4.20	-72.10	96.40	2026-08-30 08:05:39.994006	\N	\N
12	6	9	2026-08-28 09:00:00	6180.90	61.30	5.10	-73.50	95.80	2026-08-30 08:05:39.994006	\N	\N
13	7	10	2026-08-28 08:00:00	4280.50	72.40	6.30	-78.20	94.70	2026-08-30 08:05:39.994006	\N	\N
14	7	10	2026-08-28 09:00:00	3910.20	81.70	7.80	-80.10	93.60	2026-08-30 08:05:39.994006	\N	\N
15	8	12	2026-08-28 08:00:00	8760.40	31.20	0.90	-61.40	98.70	2026-08-30 08:05:39.994006	\N	\N
16	8	12	2026-08-28 09:00:00	9240.80	34.50	1.10	-62.20	98.40	2026-08-30 08:05:39.994006	\N	\N
17	1	1	2026-08-01 08:00:00	1000.00	20.00	0.50	-60.00	99.90	2026-08-30 08:15:45.13512	\N	\N
19	1	6	2026-08-30 08:30:22.922971	18500.50	35.20	1.10	-62.50	98.80	2026-08-30 08:30:22.922971	\N	\N
20	1	1	2026-08-30 09:59:10.396175	22000.00	31.50	0.70	-60.50	99.10	2026-08-30 09:59:10.396175	\N	\N
23	1	1	2026-08-31 06:00:00	12500.50	24.50	0.40	-59.50	99.80	2026-08-31 08:41:26.585871	\N	\N
24	2	6	2026-08-31 06:00:00	14200.20	21.30	0.30	-54.20	99.90	2026-08-31 08:41:26.618198	\N	\N
25	3	7	2026-08-31 06:00:00	10800.75	28.40	0.80	-56.70	99.30	2026-08-31 08:41:26.619989	\N	\N
26	4	8	2026-08-31 06:00:00	7200.40	42.20	2.10	-68.40	97.80	2026-08-31 08:41:26.621611	\N	\N
27	5	9	2026-08-31 06:00:00	6100.60	55.10	4.20	-71.50	96.40	2026-08-31 08:41:26.623078	\N	\N
28	6	10	2026-08-31 06:00:00	3900.25	73.60	6.50	-78.20	93.80	2026-08-31 08:41:26.624467	\N	\N
29	7	12	2026-08-31 06:00:00	8700.90	34.70	1.20	-63.10	98.20	2026-08-31 08:41:26.626619	\N	\N
86	8	12	2026-08-31 07:00:00	9500.75	29.40	0.90	-62.30	98.70	2026-08-31 09:33:08.18734	\N	\N
103	2	6	2026-08-31 11:00:00	16500.25	19.20	0.15	-51.40	99.90	2026-08-31 13:08:29.342617	2	\N
113	2	6	2026-08-31 12:00:00	18500.75	21.40	0.25	-53.10	99.10	2026-08-31 13:10:50.480037	3	\N
114	1	1	2026-09-01 08:47:44.741623	15000.00	25.00	0.50	-60.00	99.50	2026-09-01 08:47:44.741623	\N	\N
116	1	1	2026-09-02 09:31:38.83634	12000.00	25.00	0.50	-60.00	99.50	2026-09-02 09:31:38.83634	\N	\N
117	1	1	2026-09-02 08:00:00	12500.50	24.50	0.40	-59.50	99.70	2026-09-02 13:02:40.944066	\N	1_1_2026-09-02 08:00:00
118	2	2	2026-09-02 08:05:00	9800.20	19.80	0.20	-52.00	99.90	2026-09-02 13:02:40.944066	\N	2_2_2026-09-02 08:05:00
119	3	3	2026-09-02 08:10:00	11200.75	35.60	1.20	-64.00	98.90	2026-09-02 13:02:40.944066	\N	3_3_2026-09-02 08:10:00
120	4	4	2026-09-02 08:15:00	15400.30	15.20	0.30	-45.50	99.80	2026-09-02 13:02:40.944066	\N	4_4_2026-09-02 08:15:00
121	5	6	2026-09-02 08:20:00	18750.90	34.80	1.00	-62.20	98.90	2026-09-02 13:02:40.944066	\N	5_6_2026-09-02 08:20:00
122	2	6	2026-09-02 08:25:00	6200.40	59.10	4.80	-73.10	95.90	2026-09-02 13:02:40.944066	\N	2_6_2026-09-02 08:25:00
123	2	6	2026-09-02 08:30:00	4100.60	76.80	7.10	-79.00	94.00	2026-09-02 13:02:40.944066	\N	2_6_2026-09-02 08:30:00
124	4	4	2026-09-02 08:35:00	9100.25	31.50	0.90	-61.30	98.60	2026-09-02 13:02:40.944066	\N	4_4_2026-09-02 08:35:00
149	1	1	2026-09-03 08:00:00	14200.50	22.10	0.30	-57.00	99.80	2026-09-03 09:02:45.765226	\N	1_1_2026-09-03 08:00:00
1	1	6	2026-08-28 08:00:00	15240.50	24.30	0.40	-58.20	99.90	2026-08-30 08:05:39.994006	\N	\N
204	1	1	2026-09-09 06:36:15.648342	15000.00	30.00	1.00	-60.00	99.00	2026-09-09 06:36:15.648342	\N	\N
\.


--
-- Data for Name: pipeline_lineage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pipeline_lineage (lineage_id, run_id, stage_run_id, source_table, target_table, records_processed, created_at) FROM stdin;
1	138	20	measurements	silver_measurements	0	2026-09-11 11:29:14.687018+03
2	138	20	measurements	silver_network_health	0	2026-09-11 11:29:14.693043+03
3	138	22	silver_measurements	gold_site_daily_performance	0	2026-09-11 11:29:14.815475+03
4	138	22	silver_network_health	gold_equipment_health	0	2026-09-11 11:29:14.818407+03
5	139	23	measurements	silver_measurements	0	2026-09-11 11:36:40.483166+03
6	139	23	measurements	silver_network_health	0	2026-09-11 11:36:40.491116+03
7	139	25	silver_measurements	gold_site_daily_performance	0	2026-09-11 11:36:40.590084+03
8	139	25	silver_network_health	gold_equipment_health	0	2026-09-11 11:36:40.592141+03
9	140	26	measurements	silver_measurements	0	2026-09-11 11:47:15.87688+03
10	140	26	measurements	silver_network_health	0	2026-09-11 11:47:15.883111+03
11	140	28	silver_measurements	gold_site_daily_performance	0	2026-09-11 11:47:15.97771+03
12	140	28	silver_network_health	gold_equipment_health	0	2026-09-11 11:47:15.979948+03
13	141	29	measurements	silver_measurements	0	2026-09-11 11:47:19.935215+03
14	141	29	measurements	silver_network_health	0	2026-09-11 11:47:19.943674+03
15	141	31	silver_measurements	gold_site_daily_performance	0	2026-09-11 11:47:20.034912+03
16	141	31	silver_network_health	gold_equipment_health	0	2026-09-11 11:47:20.037367+03
17	142	32	measurements	silver_measurements	0	2026-09-11 12:22:25.797081+03
18	142	32	measurements	silver_network_health	0	2026-09-11 12:22:25.804915+03
19	142	34	silver_measurements	gold_site_daily_performance	0	2026-09-11 12:22:25.908031+03
20	142	34	silver_network_health	gold_equipment_health	0	2026-09-11 12:22:25.910012+03
21	143	35	measurements	silver_measurements	0	2026-09-11 12:28:20.779069+03
22	143	35	measurements	silver_network_health	0	2026-09-11 12:28:20.786367+03
23	143	37	silver_measurements	gold_site_daily_performance	0	2026-09-11 12:28:20.877785+03
24	143	37	silver_network_health	gold_equipment_health	0	2026-09-11 12:28:20.879695+03
25	144	38	measurements	silver_measurements	0	2026-09-11 12:46:18.450289+03
26	144	38	measurements	silver_network_health	0	2026-09-11 12:46:18.460273+03
27	144	40	silver_measurements	gold_site_daily_performance	0	2026-09-11 12:46:18.712084+03
28	144	40	silver_network_health	gold_equipment_health	0	2026-09-11 12:46:18.714926+03
29	145	41	measurements	silver_measurements	0	2026-09-11 13:18:59.504286+03
30	145	41	measurements	silver_network_health	0	2026-09-11 13:18:59.51144+03
31	145	43	silver_measurements	gold_site_daily_performance	0	2026-09-11 13:18:59.647434+03
32	145	43	silver_network_health	gold_equipment_health	0	2026-09-11 13:18:59.650169+03
33	147	45	measurements	silver_measurements	0	2026-09-11 13:43:00.83979+03
34	147	45	measurements	silver_network_health	0	2026-09-11 13:43:00.848629+03
35	148	48	measurements	silver_measurements	0	2026-09-11 13:44:35.160289+03
36	148	48	measurements	silver_network_health	0	2026-09-11 13:44:35.170434+03
37	148	50	silver_measurements	gold_site_daily_performance	24	2026-09-11 13:44:35.344575+03
38	148	50	silver_network_health	gold_equipment_health	8	2026-09-11 13:44:35.346137+03
\.


--
-- Data for Name: pipeline_runs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pipeline_runs (run_id, pipeline_name, status, started_at, completed_at, records_processed, error_message, records_read, records_rejected, duration_seconds, records_inserted, silver_records_processed, gold_records_processed, quality_checks_run, quality_checks_failed, quality_checks_passed, source_file, records_skipped, current_stage) FROM stdin;
1	uganda_network_intelligence	SUCCESS	2026-08-30 08:40:00.171688+03	2026-08-30 08:40:00.398876+03	0	\N	0	0	\N	0	0	0	0	0	0	\N	0	START
2	uganda_network_intelligence	SUCCESS	2026-08-30 09:38:01.276335+03	2026-08-30 09:38:01.353122+03	0	\N	0	0	\N	0	0	0	0	0	0	\N	0	START
3	uganda_network_intelligence	SUCCESS	2026-08-30 09:57:12.048855+03	2026-08-30 09:57:12.157674+03	0	\N	0	0	\N	0	0	0	0	0	0	\N	0	START
4	uganda_network_intelligence	SUCCESS	2026-08-30 09:59:41.903718+03	2026-08-30 09:59:41.979659+03	1	\N	0	0	\N	0	0	0	0	0	0	\N	0	START
5	uganda_network_intelligence	SUCCESS	2026-08-30 10:27:14.017804+03	2026-08-30 10:27:14.098396+03	0	\N	0	0	\N	0	0	0	0	0	0	\N	0	START
6	uganda_network_intelligence	FAILED	2026-08-30 10:35:18.349317+03	2026-08-30 10:35:18.375858+03	0	Data quality checks failed:\n- Invalid signal strength: 1	0	0	\N	0	0	0	0	0	0	\N	0	START
7	uganda_network_intelligence	FAILED	2026-08-30 10:42:34.996727+03	2026-08-30 10:42:35.022221+03	0	Data quality checks failed:\n- Invalid signal strength: 1	0	0	\N	0	0	0	0	0	0	\N	0	START
8	uganda_network_intelligence	FAILED	2026-08-30 20:36:24.01067+03	2026-08-30 20:36:24.076185+03	0	Data quality checks failed:\n- Invalid signal strength: 1	0	0	0.182	0	0	0	0	0	0	\N	0	START
9	uganda_network_intelligence	SUCCESS	2026-08-30 20:38:56.551373+03	2026-08-30 20:38:56.654375+03	0	\N	0	0	0.192	0	0	0	0	0	0	\N	0	START
10	uganda_network_intelligence	SUCCESS	2026-08-30 20:41:30.148097+03	2026-08-30 20:41:30.230124+03	0	\N	19	0	0.278	0	0	0	0	0	0	\N	0	START
11	uganda_network_intelligence	SUCCESS	2026-08-31 07:47:46.081918+03	2026-08-31 07:47:46.203364+03	0	\N	19	0	0.208	0	0	0	0	0	0	\N	0	START
12	uganda_network_intelligence	SUCCESS	2026-08-31 07:50:59.361218+03	2026-08-31 07:50:59.462113+03	0	\N	19	0	0.192	0	0	0	0	0	0	\N	0	START
13	uganda_network_intelligence	SUCCESS	2026-08-31 07:52:01.730762+03	2026-08-31 07:52:01.821742+03	0	\N	19	0	0.179	0	0	0	0	0	0	\N	0	START
14	uganda_network_intelligence	SUCCESS	2026-08-31 09:00:27.56262+03	2026-08-31 09:00:27.65772+03	7	\N	7	0	0.184	0	0	0	0	0	0	\N	0	START
15	uganda_network_intelligence	SUCCESS	2026-08-31 09:28:02.634768+03	2026-08-31 09:28:02.787997+03	0	\N	7	0	0.261	0	0	0	0	0	0	\N	0	START
16	uganda_network_intelligence	SUCCESS	2026-08-31 09:33:08.120988+03	2026-08-31 09:33:08.267707+03	1	\N	8	0	0.233	0	0	0	0	0	0	\N	0	START
17	uganda_network_intelligence	SUCCESS	2026-08-31 11:00:26.34001+03	2026-08-31 11:00:26.445963+03	0	\N	0	0	0.191	0	0	0	0	0	0	\N	0	START
18	uganda_network_intelligence	SUCCESS	2026-08-31 11:05:24.436881+03	2026-08-31 11:05:24.506042+03	0	\N	0	0	0.282	0	0	0	0	0	0	\N	0	START
19	uganda_network_intelligence	SUCCESS	2026-08-31 11:10:34.288879+03	2026-08-31 11:10:34.374607+03	0	\N	0	0	0.172	0	0	0	0	0	0	\N	0	START
20	uganda_network_intelligence	SUCCESS	2026-08-31 12:19:50.695905+03	2026-08-31 12:19:50.782561+03	0	\N	0	0	0.205	0	0	0	0	0	0	\N	0	START
21	uganda_network_intelligence	SUCCESS	2026-08-31 12:28:25.342166+03	2026-08-31 12:28:25.436035+03	0	\N	0	0	0.311	0	0	0	0	0	0	\N	0	START
22	uganda_network_intelligence	SUCCESS	2026-08-31 12:38:31.820044+03	2026-08-31 12:38:31.91105+03	0	\N	0	0	0.178	0	0	0	0	0	0	\N	0	START
23	uganda_network_intelligence	SUCCESS	2026-08-31 12:41:03.577294+03	2026-08-31 12:41:03.664779+03	0	\N	0	0	0.177	0	0	0	0	0	0	\N	0	START
24	uganda_network_intelligence	FAILED	2026-08-31 12:45:25.496553+03	2026-08-31 12:45:25.565102+03	0	name 'run_gold' is not defined	0	0	0.183	0	0	0	0	0	0	\N	0	START
25	uganda_network_intelligence	SUCCESS	2026-08-31 12:52:22.550444+03	2026-08-31 12:52:22.642003+03	0	\N	0	0	0.193	0	0	0	0	0	0	\N	0	START
26	uganda_network_intelligence	SUCCESS	2026-08-31 12:56:37.645685+03	2026-08-31 12:56:37.709563+03	0	\N	0	0	0.156	0	0	0	0	0	0	\N	0	START
27	uganda_network_intelligence	SUCCESS	2026-08-31 13:08:29.303825+03	2026-08-31 13:08:29.465539+03	1	\N	9	0	0.280	0	0	0	0	0	0	\N	0	START
28	uganda_network_intelligence	SUCCESS	2026-08-31 13:10:50.395856+03	2026-08-31 13:10:50.549875+03	1	\N	10	0	0.257	0	0	0	0	0	0	\N	0	START
29	uganda_network_intelligence	SUCCESS	2026-08-31 13:32:37.838052+03	2026-08-31 13:32:37.926012+03	0	\N	0	0	0.088	0	0	1	0	0	0	\N	0	START
30	uganda_network_intelligence	SUCCESS	2026-08-31 13:35:00.34142+03	2026-08-31 13:35:00.465058+03	0	\N	0	0	0.124	0	0	1	0	0	0	\N	0	START
31	uganda_network_intelligence	SUCCESS	2026-08-31 18:07:51.957537+03	2026-08-31 18:07:52.093409+03	0	\N	0	0	0.136	0	0	1	0	0	0	\N	0	START
32	uganda_network_intelligence	SUCCESS	2026-08-31 18:13:05.862944+03	2026-08-31 18:13:05.963667+03	0	\N	0	0	0.101	0	0	1	9	0	0	\N	0	START
33	uganda_network_intelligence	SUCCESS	2026-09-01 07:31:01.852356+03	2026-09-01 07:31:02.054998+03	0	\N	0	0	0.203	0	0	1	9	0	0	\N	0	START
34	uganda_network_intelligence	SUCCESS	2026-09-01 07:39:46.4114+03	2026-09-01 07:39:46.507738+03	0	\N	0	0	0.096	0	0	1	9	0	0	\N	0	START
35	uganda_network_intelligence	SUCCESS	2026-09-01 07:45:38.294639+03	2026-09-01 07:45:38.395097+03	0	\N	0	0	0.100	0	0	1	9	0	0	\N	0	START
36	uganda_network_intelligence	SUCCESS	2026-09-01 08:11:11.979618+03	2026-09-01 08:11:12.079219+03	0	\N	0	0	0.100	0	0	1	9	0	0	\N	0	START
37	uganda_network_intelligence	SUCCESS	2026-09-01 08:15:14.669014+03	2026-09-01 08:15:14.773046+03	0	\N	0	0	0.104	0	0	1	9	0	0	\N	0	START
38	uganda_network_intelligence	SUCCESS	2026-09-01 08:38:22.726894+03	2026-09-01 08:38:22.839793+03	0	\N	0	0	0.113	0	0	1	9	0	0	\N	0	START
39	uganda_network_intelligence	SUCCESS	2026-09-01 08:41:01.159654+03	2026-09-01 08:41:01.27486+03	0	\N	0	0	0.115	0	0	1	9	0	0	\N	0	START
40	uganda_network_intelligence	SUCCESS	2026-09-01 08:44:30.872984+03	2026-09-01 08:44:30.987713+03	0	\N	0	0	0.115	0	0	1	9	0	0	\N	0	START
41	uganda_network_intelligence	SUCCESS	2026-09-01 08:44:47.886247+03	2026-09-01 08:44:47.980609+03	0	\N	0	0	0.094	0	0	1	9	0	0	\N	0	START
42	uganda_network_intelligence	SUCCESS	2026-09-01 08:50:52.743672+03	2026-09-01 08:50:52.858346+03	0	\N	0	0	0.115	0	0	1	9	0	0	\N	0	START
43	uganda_network_intelligence	SUCCESS	2026-09-01 12:07:16.209921+03	2026-09-01 12:07:16.360993+03	0	\N	0	0	0.151	0	0	1	9	0	0	\N	0	START
44	uganda_network_intelligence	SUCCESS	2026-09-01 12:14:54.901142+03	2026-09-01 12:14:55.010512+03	0	\N	0	0	0.109	0	0	1	9	0	0	\N	0	START
45	uganda_network_intelligence	SUCCESS	2026-09-01 12:32:51.984775+03	2026-09-01 12:32:52.097264+03	0	\N	0	0	0.112	0	0	1	9	0	0	\N	0	START
46	uganda_network_intelligence	SUCCESS	2026-09-01 12:34:01.724419+03	2026-09-01 12:34:01.827583+03	0	\N	0	0	0.103	0	0	1	3	0	0	\N	0	START
47	uganda_network_intelligence	FAILED	2026-09-01 12:36:18.216354+03	2026-09-01 12:36:18.313885+03	0	Data-quality checks failed. Pipeline stopped before Silver.	0	0	0.098	0	0	0	3	1	0	\N	0	START
48	uganda_network_intelligence	SUCCESS	2026-09-01 12:38:45.019603+03	2026-09-01 12:38:45.155721+03	0	\N	0	0	0.136	0	0	1	3	0	0	\N	0	START
49	uganda_network_intelligence	SUCCESS	2026-09-02 07:05:18.457129+03	2026-09-02 07:05:18.629957+03	0	\N	0	0	0.173	0	0	1	3	0	0	\N	0	START
50	uganda_network_intelligence	SUCCESS	2026-09-02 07:06:59.401337+03	2026-09-02 07:06:59.473995+03	0	\N	0	0	0.073	0	0	1	3	0	0	\N	0	START
51	uganda_network_intelligence	SUCCESS	2026-09-02 07:07:00.448338+03	2026-09-02 07:07:00.557919+03	0	\N	0	0	0.110	0	0	1	3	0	0	\N	0	START
52	uganda_network_intelligence	SUCCESS	2026-09-02 07:29:21.005645+03	2026-09-02 07:29:21.094492+03	0	\N	0	0	0.089	0	0	1	6	0	0	\N	0	START
53	uganda_network_intelligence	SUCCESS	2026-09-02 07:31:13.864968+03	2026-09-02 07:31:13.956812+03	0	\N	0	0	0.092	0	0	1	6	0	0	\N	0	START
54	uganda_network_intelligence	SUCCESS	2026-09-02 07:33:29.67919+03	2026-09-02 07:33:29.771716+03	0	\N	0	0	0.093	0	0	1	6	0	0	\N	0	START
55	uganda_network_intelligence	SUCCESS	2026-09-02 07:35:55.962522+03	2026-09-02 07:35:56.0548+03	0	\N	0	0	0.092	0	0	1	6	0	0	\N	0	START
56	uganda_network_intelligence	FAILED	2026-09-02 08:59:01.88611+03	2026-09-02 08:59:01.937948+03	30	'bool' object is not subscriptable	30	0	0.052	30	0	0	0	0	0	\N	0	START
57	uganda_network_intelligence	SUCCESS	2026-09-02 09:00:30.153393+03	2026-09-02 09:00:30.301958+03	30	\N	30	0	0.149	30	0	1	0	0	6	\N	0	START
58	uganda_network_intelligence	SUCCESS	2026-09-02 09:02:57.322289+03	2026-09-02 09:02:57.451158+03	30	\N	30	0	0.129	30	0	1	0	0	6	\N	0	START
77	uganda_network_intelligence	SUCCESS	2026-09-04 08:18:44.192417+03	2026-09-04 08:18:44.385671+03	0	\N	0	0	0.193	0	0	9	0	0	6	\N	0	START
78	uganda_network_intelligence	SUCCESS	2026-09-04 08:23:01.435751+03	2026-09-04 08:23:01.54495+03	0	\N	0	0	0.109	0	0	9	0	0	6	\N	0	START
79	uganda_network_intelligence	SUCCESS	2026-09-04 08:23:02.484051+03	2026-09-04 08:23:02.586071+03	0	\N	0	0	0.102	0	0	9	0	0	6	\N	0	START
80	uganda_network_intelligence	SUCCESS	2026-09-04 08:33:11.801867+03	2026-09-04 08:33:11.910387+03	0	\N	0	0	0.109	0	0	9	0	0	6	\N	0	START
59	uganda_network_intelligence	FAILED	2026-09-02 09:13:29.960356+03	2026-09-02 09:13:30.137331+03	30	(psycopg2.errors.UndefinedColumn) column "record_count" of relation "gold_equipment_health" does not exist\nLINE 4:         health_status, record_count, updated_at\n                               ^\n\n[SQL: \n    INSERT INTO gold_equipment_health (\n        equipment_id, equipment_type, manufacturer, model,\n        health_status, record_count, updated_at\n    )\n    SELECT\n        equipment_id,\n        equipment_type,\n        manufacturer,\n        model,\n        health_status,\n        COUNT(*) AS record_count,\n        CURRENT_TIMESTAMP\n    FROM silver_network_health\n    GROUP BY equipment_id, equipment_type, manufacturer, model, health_status\n    ON CONFLICT (equipment_id) DO UPDATE\n    SET\n        health_status = EXCLUDED.health_status,\n        record_count = EXCLUDED.record_count,\n        updated_at = CURRENT_TIMESTAMP;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)	30	0	0.177	30	0	0	0	0	6	\N	0	START
60	uganda_network_intelligence	FAILED	2026-09-02 09:15:15.629445+03	2026-09-02 09:15:15.714115+03	30	(psycopg2.errors.UndefinedColumn) column "updated_at" of relation "gold_equipment_health" does not exist\nLINE 4:         health_status, record_count, updated_at\n                                             ^\n\n[SQL: \n    INSERT INTO gold_equipment_health (\n        equipment_id, equipment_type, manufacturer, model,\n        health_status, record_count, updated_at\n    )\n    SELECT\n        equipment_id,\n        equipment_type,\n        manufacturer,\n        model,\n        health_status,\n        COUNT(*) AS record_count,\n        CURRENT_TIMESTAMP\n    FROM silver_network_health\n    GROUP BY equipment_id, equipment_type, manufacturer, model, health_status\n    ON CONFLICT (equipment_id) DO UPDATE\n    SET\n        health_status = EXCLUDED.health_status,\n        record_count = EXCLUDED.record_count,\n        updated_at = CURRENT_TIMESTAMP;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)	30	0	0.085	30	0	0	0	0	6	\N	0	START
61	uganda_network_intelligence	FAILED	2026-09-02 09:17:00.888692+03	2026-09-02 09:17:01.003986+03	30	(psycopg2.errors.InvalidColumnReference) there is no unique or exclusion constraint matching the ON CONFLICT specification\n\n[SQL: \n    INSERT INTO gold_equipment_health (\n        equipment_id, equipment_type, manufacturer, model,\n        health_status, record_count, updated_at\n    )\n    SELECT\n        equipment_id,\n        equipment_type,\n        manufacturer,\n        model,\n        health_status,\n        COUNT(*) AS record_count,\n        CURRENT_TIMESTAMP\n    FROM silver_network_health\n    GROUP BY equipment_id, equipment_type, manufacturer, model, health_status\n    ON CONFLICT (equipment_id) DO UPDATE\n    SET\n        health_status = EXCLUDED.health_status,\n        record_count = EXCLUDED.record_count,\n        updated_at = CURRENT_TIMESTAMP;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)	30	0	0.115	30	0	0	0	0	6	\N	0	START
62	uganda_network_intelligence	FAILED	2026-09-02 09:19:00.837794+03	2026-09-02 09:19:00.962608+03	30	(psycopg2.errors.CardinalityViolation) ON CONFLICT DO UPDATE command cannot affect row a second time\nHINT:  Ensure that no rows proposed for insertion within the same command have duplicate constrained values.\n\n[SQL: \n    INSERT INTO gold_equipment_health (\n        equipment_id, equipment_type, manufacturer, model,\n        health_status, record_count, updated_at\n    )\n    SELECT\n        equipment_id,\n        equipment_type,\n        manufacturer,\n        model,\n        health_status,\n        COUNT(*) AS record_count,\n        CURRENT_TIMESTAMP\n    FROM silver_network_health\n    GROUP BY equipment_id, equipment_type, manufacturer, model, health_status\n    ON CONFLICT (equipment_id) DO UPDATE\n    SET\n        health_status = EXCLUDED.health_status,\n        record_count = EXCLUDED.record_count,\n        updated_at = CURRENT_TIMESTAMP;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)	30	0	0.125	30	0	0	0	0	6	\N	0	START
63	uganda_network_intelligence	FAILED	2026-09-02 09:19:31.644945+03	2026-09-02 09:19:31.818727+03	30	'site_daily_performance'	30	0	0.174	30	0	0	0	0	6	\N	0	START
64	uganda_network_intelligence	FAILED	2026-09-02 09:21:01.780636+03	2026-09-02 09:21:01.929034+03	30	(psycopg2.errors.CardinalityViolation) ON CONFLICT DO UPDATE command cannot affect row a second time\nHINT:  Ensure that no rows proposed for insertion within the same command have duplicate constrained values.\n\n[SQL: \n    INSERT INTO gold_equipment_health (\n        equipment_id, equipment_type, manufacturer, model,\n        health_status, record_count, updated_at\n    )\n    SELECT\n        equipment_id,\n        equipment_type,\n        manufacturer,\n        model,\n        health_status,\n        COUNT(*) AS record_count,\n        CURRENT_TIMESTAMP\n    FROM silver_network_health\n    GROUP BY equipment_id, equipment_type, manufacturer, model, health_status\n    ON CONFLICT (equipment_id) DO UPDATE\n    SET\n        health_status = EXCLUDED.health_status,\n        record_count = EXCLUDED.record_count,\n        updated_at = CURRENT_TIMESTAMP;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)	30	0	0.148	30	0	0	0	0	6	\N	0	START
65	uganda_network_intelligence	FAILED	2026-09-02 09:24:43.570226+03	2026-09-02 09:24:43.702027+03	30	(psycopg2.errors.CardinalityViolation) ON CONFLICT DO UPDATE command cannot affect row a second time\nHINT:  Ensure that no rows proposed for insertion within the same command have duplicate constrained values.\n\n[SQL: \n    INSERT INTO gold_equipment_health (\n        equipment_id, equipment_type, manufacturer, model,\n        health_status, record_count, updated_at\n    )\n    SELECT\n        equipment_id,\n        equipment_type,\n        manufacturer,\n        model,\n        health_status,\n        COUNT(*) AS record_count,\n        CURRENT_TIMESTAMP\n    FROM silver_network_health\n    GROUP BY equipment_id, equipment_type, manufacturer, model, health_status\n    ON CONFLICT (equipment_id) DO UPDATE\n    SET\n        health_status = EXCLUDED.health_status,\n        record_count = EXCLUDED.record_count,\n        updated_at = CURRENT_TIMESTAMP;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)	30	0	0.132	30	0	0	0	0	6	\N	0	START
66	uganda_network_intelligence	SUCCESS	2026-09-02 09:26:08.63313+03	2026-09-02 09:26:08.715776+03	30	\N	30	0	0.083	30	0	9	0	0	6	\N	0	START
67	uganda_network_intelligence	SUCCESS	2026-09-02 09:33:04.254998+03	2026-09-02 09:33:04.390555+03	31	\N	31	0	0.136	31	0	9	0	0	6	\N	0	START
68	uganda_network_intelligence	SUCCESS	2026-09-02 11:50:00.860478+03	2026-09-02 11:50:01.056028+03	31	\N	31	0	0.196	31	0	9	0	0	6	\N	0	START
69	uganda_network_intelligence	SUCCESS	2026-09-02 11:53:06.841512+03	2026-09-02 11:53:06.922616+03	31	\N	31	0	0.081	31	0	9	0	0	6	\N	0	START
70	uganda_network_intelligence	SUCCESS	2026-09-03 09:02:45.684425+03	2026-09-03 09:02:45.906757+03	1	\N	1	0	0.222	1	0	9	0	0	6	\N	0	START
71	uganda_network_intelligence	SUCCESS	2026-09-03 09:04:38.005601+03	2026-09-03 09:04:38.128976+03	0	\N	0	0	0.123	0	0	9	0	0	6	\N	0	START
72	uganda_network_intelligence	SUCCESS	2026-09-03 09:04:39.21152+03	2026-09-03 09:04:39.356334+03	0	\N	0	0	0.145	0	0	9	0	0	6	\N	0	START
73	uganda_network_intelligence	FAILED	2026-09-03 09:08:53.014221+03	2026-09-03 09:08:53.054894+03	0	Missing required field: measured_at	0	0	0.041	0	0	0	0	0	0	\N	0	START
74	uganda_network_intelligence	SUCCESS	2026-09-03 09:09:52.36962+03	2026-09-03 09:09:52.469545+03	0	\N	0	0	0.100	0	0	9	0	0	6	\N	0	START
75	uganda_network_intelligence	SUCCESS	2026-09-03 09:21:46.02739+03	2026-09-03 09:21:46.139368+03	0	\N	0	0	0.112	0	0	9	0	0	6	\N	0	START
76	uganda_network_intelligence	SUCCESS	2026-09-03 14:17:22.116338+03	2026-09-03 14:17:22.363726+03	0	\N	0	0	0.247	0	0	9	0	0	6	\N	0	START
81	uganda_network_intelligence	SUCCESS	2026-09-04 08:34:32.076031+03	2026-09-04 08:34:32.173208+03	9	\N	9	0	0.097	0	0	9	0	0	6	network_measurements.csv	9	START
82	uganda_network_intelligence	SUCCESS	2026-09-04 08:41:12.866322+03	2026-09-04 08:41:13.052908+03	9	\N	9	0	0.187	0	0	9	0	0	6	network_measurements.csv	9	START
83	uganda_network_intelligence	SUCCESS	2026-09-04 09:18:06.565001+03	2026-09-04 09:18:06.680148+03	9	\N	9	0	0.115	0	0	9	0	0	6	network_measurements.csv	9	START
84	uganda_network_intelligence	FAILED	2026-09-04 09:24:41.824229+03	2026-09-04 09:24:41.925649+03	9	(sqlalchemy.exc.InvalidRequestError) A value is required for bind parameter 'availability_pct'\n[SQL: \n    INSERT INTO gold_site_daily_performance (\n        site_id, site_name, region, district, measurement_date,\n        measurement_count, avg_traffic_mb, avg_latency_ms,\n        avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct,\n        updated_at\n    )\n    VALUES (\n        %(site_id)s, %(site_name)s, %(region)s, %(district)s, %(measurement_date)s,\n        %(measurement_count)s, %(avg_traffic_mb)s, %(avg_latency_ms)s,\n        %(avg_packet_loss_pct)s, %(avg_signal_strength_dbm)s, %(availability_pct)s,\n        CURRENT_TIMESTAMP\n    )\n    ON CONFLICT (site_id, measurement_date) \n    DO UPDATE SET\n        site_name = EXCLUDED.site_name,\n        region = EXCLUDED.region,\n        district = EXCLUDED.district,\n        measurement_count = EXCLUDED.measurement_count,\n        avg_traffic_mb = EXCLUDED.avg_traffic_mb,\n        avg_latency_ms = EXCLUDED.avg_latency_ms,\n        avg_packet_loss_pct = EXCLUDED.avg_packet_loss_pct,\n        avg_signal_strength_dbm = EXCLUDED.avg_signal_strength_dbm,\n        avg_availability_pct = EXCLUDED.avg_availability_pct,\n        updated_at = CURRENT_TIMESTAMP;\n    ]\n[parameters: [{'site_id': 6, 'site_name': 'Entebbe Central', 'region': 'Central', 'district': 'Wakiso', 'measurement_date': datetime.date(2026, 8, 31), 'measurement ... (64 characters truncated) ... ms': Decimal('20.63'), 'avg_packet_loss_pct': Decimal('0.23'), 'avg_signal_strength_dbm': Decimal('-52.90'), 'avg_availability_pct': Decimal('99.63')}]]\n(Background on this error at: https://sqlalche.me/e/20/cd3x)	9	0	0.101	0	0	0	0	0	6	network_measurements.csv	9	START
85	uganda_network_intelligence	FAILED	2026-09-04 09:24:51.089731+03	2026-09-04 09:24:51.168704+03	9	(sqlalchemy.exc.InvalidRequestError) A value is required for bind parameter 'availability_pct'\n[SQL: \n    INSERT INTO gold_site_daily_performance (\n        site_id, site_name, region, district, measurement_date,\n        measurement_count, avg_traffic_mb, avg_latency_ms,\n        avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct,\n        updated_at\n    )\n    VALUES (\n        %(site_id)s, %(site_name)s, %(region)s, %(district)s, %(measurement_date)s,\n        %(measurement_count)s, %(avg_traffic_mb)s, %(avg_latency_ms)s,\n        %(avg_packet_loss_pct)s, %(avg_signal_strength_dbm)s, %(availability_pct)s,\n        CURRENT_TIMESTAMP\n    )\n    ON CONFLICT (site_id, measurement_date) \n    DO UPDATE SET\n        site_name = EXCLUDED.site_name,\n        region = EXCLUDED.region,\n        district = EXCLUDED.district,\n        measurement_count = EXCLUDED.measurement_count,\n        avg_traffic_mb = EXCLUDED.avg_traffic_mb,\n        avg_latency_ms = EXCLUDED.avg_latency_ms,\n        avg_packet_loss_pct = EXCLUDED.avg_packet_loss_pct,\n        avg_signal_strength_dbm = EXCLUDED.avg_signal_strength_dbm,\n        avg_availability_pct = EXCLUDED.avg_availability_pct,\n        updated_at = CURRENT_TIMESTAMP;\n    ]\n[parameters: [{'site_id': 6, 'site_name': 'Entebbe Central', 'region': 'Central', 'district': 'Wakiso', 'measurement_date': datetime.date(2026, 8, 31), 'measurement ... (64 characters truncated) ... ms': Decimal('20.63'), 'avg_packet_loss_pct': Decimal('0.23'), 'avg_signal_strength_dbm': Decimal('-52.90'), 'avg_availability_pct': Decimal('99.63')}]]\n(Background on this error at: https://sqlalche.me/e/20/cd3x)	9	0	0.079	0	0	0	0	0	6	network_measurements.csv	9	START
86	uganda_network_intelligence	FAILED	2026-09-04 09:26:50.867666+03	2026-09-04 09:26:50.982094+03	9	name 'gold_records' is not defined	9	0	0.114	0	0	0	0	0	6	network_measurements.csv	9	START
87	uganda_network_intelligence	SUCCESS	2026-09-04 09:29:02.095241+03	2026-09-04 09:29:02.198912+03	9	\N	9	0	0.104	0	0	9	0	0	6	network_measurements.csv	9	START
88	uganda_network_intelligence	SUCCESS	2026-09-04 09:50:14.090424+03	2026-09-04 09:50:14.209569+03	9	\N	9	0	0.119	0	0	9	0	0	6	network_measurements.csv	9	START
89	uganda_network_intelligence	SUCCESS	2026-09-04 09:53:18.077842+03	2026-09-04 09:53:18.191168+03	9	\N	9	0	0.113	0	0	9	0	0	6	network_measurements.csv	9	START
90	uganda_network_intelligence	SUCCESS	2026-09-04 11:19:53.962465+03	2026-09-04 11:19:54.087786+03	9	\N	9	0	0.125	0	0	9	0	0	6	network_measurements.csv	9	START
91	uganda_network_intelligence	SUCCESS	2026-09-04 11:47:32.339622+03	2026-09-04 11:47:32.449852+03	0	\N	9	0	0.110	0	0	9	0	0	6	network_measurements.csv	9	START
92	uganda_network_intelligence	SUCCESS	2026-09-04 11:50:29.599719+03	2026-09-04 11:50:29.722568+03	0	\N	9	0	0.123	0	0	9	0	0	6	network_measurements.csv	9	START
93	uganda_network_intelligence	SUCCESS	2026-09-04 11:52:39.579683+03	2026-09-04 11:52:39.699923+03	0	\N	9	0	0.120	0	0	9	0	0	6	network_measurements.csv	9	START
94	uganda_network_intelligence	SUCCESS	2026-09-06 07:36:02.685072+03	2026-09-06 07:36:02.852772+03	0	\N	9	0	0.168	0	0	9	0	0	6	network_measurements.csv	9	START
95	uganda_network_intelligence	FAILED	2026-09-07 07:08:20.391795+03	2026-09-07 07:08:20.572777+03	0	(psycopg2.errors.UndefinedColumn) column "check_type" of relation "data_quality_results" does not exist\nLINE 6:         check_type,\n                ^\n\n[SQL: \n    INSERT INTO data_quality_results (\n        run_id,\n        table_name,\n        check_name,\n        check_type,\n        status,\n        records_checked,\n        records_failed,\n        failure_rate_pct,\n        details\n    )\n    VALUES (\n        %(run_id)s,\n        %(table_name)s,\n        %(check_name)s,\n        %(check_type)s,\n        %(status)s,\n        %(records_checked)s,\n        %(records_failed)s,\n        %(failure_rate_pct)s,\n        %(details)s\n    );\n    ]\n[parameters: {'run_id': 95, 'table_name': 'measurements', 'check_name': 'traffic_non_negative', 'check_type': 'VALIDITY', 'status': 'PASS', 'records_checked': 40, 'records_failed': 0, 'failure_rate_pct': 0.0, 'details': 'Measurement values are within expected ranges.'}]\n(Background on this error at: https://sqlalche.me/e/20/f405)	9	0	0.181	0	0	0	0	0	0	network_measurements.csv	9	START
96	uganda_network_intelligence	FAILED	2026-09-07 07:11:06.779549+03	2026-09-07 07:11:06.88322+03	0	(psycopg2.errors.UndefinedColumn) column "records_checked" of relation "data_quality_results" does not exist\nLINE 8:         records_checked,\n                ^\n\n[SQL: \n    INSERT INTO data_quality_results (\n        run_id,\n        table_name,\n        check_name,\n        check_type,\n        status,\n        records_checked,\n        records_failed,\n        failure_rate_pct,\n        details\n    )\n    VALUES (\n        %(run_id)s,\n        %(table_name)s,\n        %(check_name)s,\n        %(check_type)s,\n        %(status)s,\n        %(records_checked)s,\n        %(records_failed)s,\n        %(failure_rate_pct)s,\n        %(details)s\n    );\n    ]\n[parameters: {'run_id': 96, 'table_name': 'measurements', 'check_name': 'traffic_non_negative', 'check_type': 'VALIDITY', 'status': 'PASS', 'records_checked': 40, 'records_failed': 0, 'failure_rate_pct': 0.0, 'details': 'Measurement values are within expected ranges.'}]\n(Background on this error at: https://sqlalche.me/e/20/f405)	9	0	0.104	0	0	0	0	0	0	network_measurements.csv	9	START
97	uganda_network_intelligence	FAILED	2026-09-07 07:13:59.690703+03	2026-09-07 07:13:59.851984+03	0	Data-quality checks failed. Pipeline stopped before Silver.	9	0	0.161	0	0	0	0	0	0	network_measurements.csv	9	START
98	uganda_network_intelligence	SUCCESS	2026-09-07 07:17:08.827072+03	2026-09-07 07:17:09.087242+03	0	\N	9	0	0.260	0	0	9	0	0	9	network_measurements.csv	9	START
99	uganda_network_intelligence	SUCCESS	2026-09-07 07:42:04.326183+03	2026-09-07 07:42:04.526347+03	0	\N	9	0	0.200	0	0	9	0	0	9	network_measurements.csv	9	START
100	uganda_network_intelligence	SUCCESS	2026-09-07 07:54:38.179878+03	2026-09-07 07:54:38.551011+03	0	\N	9	0	0.371	0	0	9	0	0	9	network_measurements.csv	9	START
101	uganda_network_intelligence	SUCCESS	2026-09-07 08:42:58.300023+03	2026-09-07 08:42:58.534828+03	0	\N	9	0	0.235	0	0	9	0	0	9	network_measurements.csv	9	START
102	uganda_network_intelligence	SUCCESS	2026-09-07 08:58:41.781119+03	2026-09-07 08:58:42.041086+03	0	\N	9	0	0.260	0	0	9	0	0	9	network_measurements.csv	9	START
103	uganda_network_intelligence	SUCCESS	2026-09-07 09:01:48.258608+03	2026-09-07 09:01:48.644536+03	0	\N	9	0	0.386	0	0	9	0	0	9	network_measurements.csv	9	START
104	uganda_network_intelligence	FAILED	2026-09-07 09:25:55.096498+03	2026-09-07 09:25:55.288384+03	0	(psycopg2.errors.UndefinedColumn) column "health_score" of relation "silver_network_health" does not exist\nLINE 3: ...asurement_id, site_id, equipment_id, measured_at, health_sco...\n                                                             ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, site_id, equipment_id, measured_at, health_score, status_classification\n    )\n    SELECT \n        measurement_id,\n        site_id,\n        equipment_id,\n        measured_at,\n        ROUND((availability_pct - packet_loss_pct), 2) AS health_score,\n        CASE \n            WHEN (availability_pct - packet_loss_pct) >= 95 THEN 'Healthy'\n            WHEN (availability_pct - packet_loss_pct) >= 80 THEN 'Warning'\n            ELSE 'Critical'\n        END AS status_classification\n    FROM measurements\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)	9	0	0.192	0	0	0	0	0	9	network_measurements.csv	9	START
105	uganda_network_intelligence	FAILED	2026-09-07 09:26:05.816349+03	2026-09-07 09:26:05.966029+03	0	(psycopg2.errors.UndefinedColumn) column "health_score" of relation "silver_network_health" does not exist\nLINE 3: ...asurement_id, site_id, equipment_id, measured_at, health_sco...\n                                                             ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, site_id, equipment_id, measured_at, health_score, status_classification\n    )\n    SELECT \n        measurement_id,\n        site_id,\n        equipment_id,\n        measured_at,\n        ROUND((availability_pct - packet_loss_pct), 2) AS health_score,\n        CASE \n            WHEN (availability_pct - packet_loss_pct) >= 95 THEN 'Healthy'\n            WHEN (availability_pct - packet_loss_pct) >= 80 THEN 'Warning'\n            ELSE 'Critical'\n        END AS status_classification\n    FROM measurements\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)	9	0	0.150	0	0	0	0	0	9	network_measurements.csv	9	START
106	uganda_network_intelligence	FAILED	2026-09-07 09:27:40.007002+03	2026-09-07 09:27:40.406411+03	0	(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "gold_equipment_health_pkey"\nDETAIL:  Key (equipment_id)=(2) already exists.\n\n[SQL: \n    TRUNCATE TABLE gold_equipment_health;\n    INSERT INTO gold_equipment_health (\n        equipment_id, equipment_type, manufacturer, model, measurement_count,\n        avg_latency_ms, avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct,\n        health_status, record_count, updated_at\n    )\n    SELECT\n        equipment_id, equipment_type, manufacturer, model, COUNT(*) AS measurement_count,\n        ROUND(AVG(latency_ms), 2) AS avg_latency_ms,\n        ROUND(AVG(packet_loss_pct), 2) AS avg_packet_loss_pct,\n        ROUND(AVG(signal_strength_dbm), 2) AS avg_signal_strength_dbm,\n        ROUND(AVG(availability_pct), 2) AS avg_availability_pct,\n        CASE\n            WHEN AVG(availability_pct) < 95 OR AVG(packet_loss_pct) > 5 OR AVG(latency_ms) > 70 THEN 'Critical'\n            WHEN AVG(availability_pct) < 98 OR AVG(packet_loss_pct) > 2 OR AVG(latency_ms) > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END AS health_status,\n        COUNT(*) AS record_count,\n        CURRENT_TIMESTAMP\n    FROM silver_measurements\n    GROUP BY equipment_id, equipment_type, manufacturer, model;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/gkpj)	9	0	0.399	0	0	0	0	0	9	network_measurements.csv	9	START
107	uganda_network_intelligence	FAILED	2026-09-07 09:28:18.971591+03	2026-09-07 09:28:19.157036+03	0	(sqlalchemy.exc.InvalidRequestError) A value is required for bind parameter 'run_id'\n[SQL: \n    INSERT INTO silver_measurements (\n        measurement_id, source_record_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at, batch_id, run_id\n    )\n    SELECT\n        m.measurement_id, m.source_record_id, m.measured_at, m.site_id, s.site_name, s.region, s.district, s.site_type,\n        m.equipment_id, e.equipment_type, e.manufacturer, e.model, m.traffic_mb, m.latency_ms,\n        m.packet_loss_pct, m.signal_strength_dbm, m.availability_pct,\n        COALESCE(m.ingested_at, CURRENT_TIMESTAMP), m.batch_id, %(run_id)s\n    FROM measurements m\n    JOIN sites s ON m.site_id = s.site_id\n    JOIN equipment e ON m.equipment_id = e.equipment_id\n    WHERE m.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/cd3x)	9	0	0.185	0	0	0	0	0	9	network_measurements.csv	9	START
108	uganda_network_intelligence	FAILED	2026-09-07 09:28:26.357832+03	2026-09-07 09:28:26.527344+03	0	(sqlalchemy.exc.InvalidRequestError) A value is required for bind parameter 'run_id'\n[SQL: \n    INSERT INTO silver_measurements (\n        measurement_id, source_record_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at, batch_id, run_id\n    )\n    SELECT\n        m.measurement_id, m.source_record_id, m.measured_at, m.site_id, s.site_name, s.region, s.district, s.site_type,\n        m.equipment_id, e.equipment_type, e.manufacturer, e.model, m.traffic_mb, m.latency_ms,\n        m.packet_loss_pct, m.signal_strength_dbm, m.availability_pct,\n        COALESCE(m.ingested_at, CURRENT_TIMESTAMP), m.batch_id, %(run_id)s\n    FROM measurements m\n    JOIN sites s ON m.site_id = s.site_id\n    JOIN equipment e ON m.equipment_id = e.equipment_id\n    WHERE m.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/cd3x)	9	0	0.170	0	0	0	0	0	9	network_measurements.csv	9	START
109	uganda_network_intelligence	FAILED	2026-09-07 09:29:32.821456+03	2026-09-07 09:29:32.997814+03	0	(psycopg2.errors.UndefinedColumn) column "site_name" of relation "silver_network_health" does not exist\nLINE 3:         measurement_id, measured_at, site_id, site_name, reg...\n                                                      ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id\n    )\n    SELECT\n        sm.measurement_id, sm.measured_at, sm.site_id, sm.site_name, sm.region, sm.district, sm.site_type,\n        sm.equipment_id, sm.equipment_type, sm.manufacturer, sm.model, sm.traffic_mb, sm.latency_ms,\n        sm.packet_loss_pct, sm.signal_strength_dbm, sm.availability_pct,\n        CASE\n            WHEN sm.availability_pct < 95 OR sm.packet_loss_pct > 5 OR sm.latency_ms > 70 THEN 'Critical'\n            WHEN sm.availability_pct < 98 OR sm.packet_loss_pct > 2 OR sm.latency_ms > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END,\n        sm.ingested_at, sm.batch_id, %(run_id)s\n    FROM silver_measurements sm\n    WHERE sm.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n[parameters: {'run_id': 109, 'batch_id': 3}]\n(Background on this error at: https://sqlalche.me/e/20/f405)	9	0	0.176	0	0	0	0	0	9	network_measurements.csv	9	START
110	uganda_network_intelligence	FAILED	2026-09-07 09:30:29.651066+03	2026-09-07 09:30:29.816778+03	0	(psycopg2.errors.UndefinedColumn) column "site_name" of relation "silver_network_health" does not exist\nLINE 3:         measurement_id, measured_at, site_id, site_name, reg...\n                                                      ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id\n    )\n    SELECT\n        sm.measurement_id, sm.measured_at, sm.site_id, sm.site_name, sm.region, sm.district, sm.site_type,\n        sm.equipment_id, sm.equipment_type, sm.manufacturer, sm.model, sm.traffic_mb, sm.latency_ms,\n        sm.packet_loss_pct, sm.signal_strength_dbm, sm.availability_pct,\n        CASE\n            WHEN sm.availability_pct < 95 OR sm.packet_loss_pct > 5 OR sm.latency_ms > 70 THEN 'Critical'\n            WHEN sm.availability_pct < 98 OR sm.packet_loss_pct > 2 OR sm.latency_ms > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END,\n        sm.ingested_at, sm.batch_id, %(run_id)s\n    FROM silver_measurements sm\n    WHERE sm.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n[parameters: {'run_id': 110, 'batch_id': 3}]\n(Background on this error at: https://sqlalche.me/e/20/f405)	9	0	0.166	0	0	0	0	0	9	network_measurements.csv	9	START
111	uganda_network_intelligence	FAILED	2026-09-07 09:31:03.433497+03	2026-09-07 09:31:03.507988+03	0	(psycopg2.errors.UndefinedColumn) column "site_name" of relation "silver_network_health" does not exist\nLINE 3:         measurement_id, measured_at, site_id, site_name, reg...\n                                                      ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id\n    )\n    SELECT\n        sm.measurement_id, sm.measured_at, sm.site_id, sm.site_name, sm.region, sm.district, sm.site_type,\n        sm.equipment_id, sm.equipment_type, sm.manufacturer, sm.model, sm.traffic_mb, sm.latency_ms,\n        sm.packet_loss_pct, sm.signal_strength_dbm, sm.availability_pct,\n        CASE\n            WHEN sm.availability_pct < 95 OR sm.packet_loss_pct > 5 OR sm.latency_ms > 70 THEN 'Critical'\n            WHEN sm.availability_pct < 98 OR sm.packet_loss_pct > 2 OR sm.latency_ms > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END,\n        sm.ingested_at, sm.batch_id, %(run_id)s\n    FROM silver_measurements sm\n    WHERE sm.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n[parameters: {'run_id': 111, 'batch_id': 3}]\n(Background on this error at: https://sqlalche.me/e/20/f405)	9	0	0.074	0	0	0	0	0	6	network_measurements.csv	9	START
112	uganda_network_intelligence	FAILED	2026-09-07 09:31:12.910918+03	2026-09-07 09:31:12.986388+03	0	(psycopg2.errors.UndefinedColumn) column "site_name" of relation "silver_network_health" does not exist\nLINE 3:         measurement_id, measured_at, site_id, site_name, reg...\n                                                      ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id\n    )\n    SELECT\n        sm.measurement_id, sm.measured_at, sm.site_id, sm.site_name, sm.region, sm.district, sm.site_type,\n        sm.equipment_id, sm.equipment_type, sm.manufacturer, sm.model, sm.traffic_mb, sm.latency_ms,\n        sm.packet_loss_pct, sm.signal_strength_dbm, sm.availability_pct,\n        CASE\n            WHEN sm.availability_pct < 95 OR sm.packet_loss_pct > 5 OR sm.latency_ms > 70 THEN 'Critical'\n            WHEN sm.availability_pct < 98 OR sm.packet_loss_pct > 2 OR sm.latency_ms > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END,\n        sm.ingested_at, sm.batch_id, %(run_id)s\n    FROM silver_measurements sm\n    WHERE sm.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n[parameters: {'run_id': 112, 'batch_id': 3}]\n(Background on this error at: https://sqlalche.me/e/20/f405)	9	0	0.075	0	0	0	0	0	6	network_measurements.csv	9	START
113	uganda_network_intelligence	FAILED	2026-09-07 09:33:04.263004+03	2026-09-07 09:33:04.416457+03	0	(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "gold_equipment_health_pkey"\nDETAIL:  Key (equipment_id)=(2) already exists.\n\n[SQL: \n    TRUNCATE TABLE gold_equipment_health;\n    INSERT INTO gold_equipment_health (\n        equipment_id, equipment_type, manufacturer, model, measurement_count,\n        avg_latency_ms, avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct,\n        health_status, record_count, updated_at\n    )\n    SELECT\n        equipment_id, equipment_type, manufacturer, model, COUNT(*) AS measurement_count,\n        ROUND(AVG(latency_ms), 2) AS avg_latency_ms,\n        ROUND(AVG(packet_loss_pct), 2) AS avg_packet_loss_pct,\n        ROUND(AVG(signal_strength_dbm), 2) AS avg_signal_strength_dbm,\n        ROUND(AVG(availability_pct), 2) AS avg_availability_pct,\n        CASE\n            WHEN AVG(availability_pct) < 95 OR AVG(packet_loss_pct) > 5 OR AVG(latency_ms) > 70 THEN 'Critical'\n            WHEN AVG(availability_pct) < 98 OR AVG(packet_loss_pct) > 2 OR AVG(latency_ms) > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END AS health_status,\n        COUNT(*) AS record_count,\n        CURRENT_TIMESTAMP\n    FROM silver_measurements\n    GROUP BY equipment_id, equipment_type, manufacturer, model;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/gkpj)	9	0	0.153	0	0	0	0	0	6	network_measurements.csv	9	START
114	uganda_network_intelligence	FAILED	2026-09-07 09:34:31.308878+03	2026-09-07 09:34:31.36068+03	0	(psycopg2.errors.UndefinedTable) relation "gold_site_daily_perf" does not exist\n\n[SQL: \n    TRUNCATE TABLE gold_site_daily_perf CASCADE;\n    INSERT INTO gold_site_daily_perf (\n        site_id, site_name, district, measurement_count,\n        avg_traffic_mb, avg_latency_ms, avg_packet_loss_pct, avg_availability_pct, updated_at\n    )\n    SELECT \n        site_id, site_name, max(district), COUNT(*),\n        ROUND(AVG(traffic_mb), 2), ROUND(AVG(latency_ms), 2),\n        ROUND(AVG(packet_loss_pct), 2), ROUND(AVG(availability_pct), 2),\n        CURRENT_TIMESTAMP\n    FROM silver_network_health\n    GROUP BY site_id, site_name;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)	9	0	0.052	0	0	0	0	0	6	network_measurements.csv	9	START
115	uganda_network_intelligence	SUCCESS	2026-09-07 09:36:17.160099+03	2026-09-07 09:36:17.25983+03	0	\N	9	0	0.100	0	0	18	0	0	6	network_measurements.csv	9	START
128	uganda_network_intel	SUCCESS	2026-09-09 08:07:36.998292+03	2026-09-09 08:07:37.162234+03	0	\N	0	0	0.149	0	0	0	0	0	0	\N	0	SUCCESS
122	uganda_network_intel	SUCCESS	2026-09-09 06:38:59.365274+03	2026-09-09 06:38:59.562866+03	1	\N	0	0	0.191	0	0	0	0	0	0	\N	0	SUCCESS
116	uganda_network_intel	SUCCESS	2026-09-07 10:14:49.192212+03	2026-09-07 10:14:49.392143+03	0	\N	0	0	0.184	0	0	0	0	0	0	\N	0	SUCCESS
132	uganda_network_intel	SUCCESS	2026-09-10 21:03:00.340299+03	2026-09-10 21:03:00.470723+03	0	\N	0	0	0.123	0	0	0	0	0	0	\N	0	SUCCESS
117	uganda_network_intel	SUCCESS	2026-09-07 10:14:55.171208+03	2026-09-07 10:14:55.336164+03	0	\N	0	0	0.150	0	0	0	0	0	0	\N	0	SUCCESS
123	uganda_network_intel	SUCCESS	2026-09-09 07:32:19.969457+03	2026-09-09 07:32:20.056447+03	0	\N	0	0	0.077	0	0	0	0	0	0	\N	0	SUCCESS
118	uganda_network_intel	SUCCESS	2026-09-07 10:23:49.438274+03	2026-09-07 10:23:49.615774+03	0	\N	0	0	0.161	0	0	0	0	0	0	\N	0	SUCCESS
124	uganda_network_intel	FAILED	2026-09-09 07:38:03.305105+03	2026-09-09 07:38:03.355945+03	0	Day 57 test failure	0	0	0.037	0	0	0	0	0	0	\N	0	SILVER
129	uganda_network_intel	SUCCESS	2026-09-09 08:13:47.93263+03	2026-09-09 08:13:48.073726+03	0	\N	0	0	0.126	0	0	0	0	0	0	\N	0	SUCCESS
119	uganda_network_intel	SUCCESS	2026-09-07 16:56:58.769216+03	2026-09-07 16:56:59.018917+03	0	\N	0	0	0.221	0	0	0	0	0	0	\N	0	SUCCESS
125	uganda_network_intel	SUCCESS	2026-09-09 07:39:07.262871+03	2026-09-09 07:39:07.365809+03	0	\N	0	0	0.096	0	0	0	0	0	0	\N	0	SUCCESS
120	uganda_network_intel	SUCCESS	2026-09-09 06:32:27.178824+03	2026-09-09 06:32:27.531354+03	0	\N	0	0	0.288	0	0	0	0	0	0	\N	0	SUCCESS
126	uganda_network_intel	SUCCESS	2026-09-09 07:55:27.417098+03	2026-09-09 07:55:27.504894+03	0	\N	0	0	0.072	0	0	0	0	0	0	\N	0	SUCCESS
121	uganda_network_intel	SUCCESS	2026-09-09 06:32:33.741045+03	2026-09-09 06:32:33.91606+03	0	\N	0	0	0.170	0	0	0	0	0	0	\N	0	SUCCESS
133	uganda_network_intelligence	SUCCESS	2026-09-10 21:13:19.624111+03	2026-09-10 21:13:19.778649+03	0	\N	0	0	0.140	0	0	0	0	0	0	\N	0	SUCCESS
130	uganda_network_intel	SUCCESS	2026-09-09 08:46:19.871151+03	2026-09-09 08:46:19.999777+03	0	\N	0	0	0.124	0	0	0	0	0	0	\N	0	SUCCESS
127	uganda_network_intel	SUCCESS	2026-09-09 08:03:31.825292+03	2026-09-09 08:03:31.992962+03	0	\N	0	0	0.163	0	0	0	0	0	0	\N	0	SUCCESS
134	uganda_network_intelligence	FAILED	2026-09-10 21:26:32.228922+03	2026-09-10 21:26:32.261857+03	0	(psycopg.errors.NotNullViolation) null value in column "started_at" of relation "pipeline_stage_runs" violates not-null constraint\nDETAIL:  Failing row contains (12, 134, SILVER, null, null, RUNNING, 0, 0, 0, 0, null, null).\n[SQL: \n        INSERT INTO pipeline_stage_runs (\n            run_id,\n            stage_name,\n            status\n        )\n        VALUES (\n            %(run_id)s,\n            %(stage_name)s,\n            'RUNNING'\n        )\n        RETURNING stage_run_id;\n    ]\n[parameters: {'run_id': 134, 'stage_name': 'SILVER'}]\n(Background on this error at: https://sqlalche.me/e/20/gkpj)	0	0	0.121	0	0	0	0	0	0	\N	0	SILVER
131	uganda_network_intel	SUCCESS	2026-09-10 21:00:45.902319+03	2026-09-10 21:00:46.178264+03	0	\N	0	0	0.234	0	0	0	0	0	0	\N	0	SUCCESS
135	uganda_network_intelligence	FAILED	2026-09-10 21:27:57.906958+03	2026-09-10 21:27:57.973754+03	0	(psycopg.errors.UndefinedColumn) column "records_processed" of relation "pipeline_stage_runs" does not exist\nLINE 6:             records_processed = $2,\n                    ^\n[SQL: \n        UPDATE pipeline_stage_runs\n        SET\n            completed_at = CURRENT_TIMESTAMP,\n            status = %(status)s,\n            records_processed = %(records_processed)s,\n            error_message = %(error_message)s\n        WHERE stage_run_id = %(stage_run_id)s;\n    ]\n[parameters: {'status': 'FAILED', 'records_processed': 0, 'error_message': '(psycopg.errors.UndefinedColumn) column "records_processed" of relation "pipeline_stage_runs" does not exist\\nLINE 6:             records_processed = ... (350 characters truncated) ...  \\'SUCCESS\\', \\'records_processed\\': 0, \\'error_message\\': None, \\'stage_run_id\\': 13}]\\n(Background on this error at: https://sqlalche.me/e/20/f405)', 'stage_run_id': 13}]\n(Background on this error at: https://sqlalche.me/e/20/f405)	0	0	0.157	0	0	0	0	0	0	\N	0	SILVER
136	uganda_network_intelligence	SUCCESS	2026-09-10 21:30:11.811728+03	2026-09-10 21:30:12.026466+03	0	\N	0	0	0.312	0	0	0	0	0	0	\N	0	SUCCESS
145	uganda_network_intelligence	SUCCESS	2026-09-11 13:18:59.464864+03	2026-09-11 13:18:59.654425+03	0	\N	0	0	0.293	0	0	0	0	0	0	\N	0	SUCCESS
137	uganda_network_intelligence	SUCCESS	2026-09-10 21:30:18.259386+03	2026-09-10 21:30:18.419967+03	0	\N	0	0	0.246	0	0	0	0	0	0	\N	0	SUCCESS
146	uganda_network_intelligence	FAILED	2026-09-11 13:40:59.099147+03	2026-09-11 13:40:59.159036+03	0	\N	0	0	0.150	0	0	0	0	0	0	\N	0	SILVER
138	uganda_network_intelligence	SUCCESS	2026-09-11 11:29:14.576941+03	2026-09-11 11:29:14.821913+03	0	\N	0	0	0.413	0	0	0	0	0	0	\N	0	SUCCESS
139	uganda_network_intelligence	SUCCESS	2026-09-11 11:36:40.431458+03	2026-09-11 11:36:40.596682+03	0	\N	0	0	0.245	0	0	0	0	0	0	\N	0	SUCCESS
147	uganda_network_intelligence	FAILED	2026-09-11 13:43:00.785792+03	2026-09-11 13:43:01.008847+03	0	\N	0	0	0.305	0	0	0	0	0	0	\N	0	GOLD
140	uganda_network_intelligence	SUCCESS	2026-09-11 11:47:15.84009+03	2026-09-11 11:47:15.983235+03	0	\N	0	0	0.255	0	0	0	0	0	0	\N	0	SUCCESS
148	uganda_network_intelligence	SUCCESS	2026-09-11 13:44:35.093265+03	2026-09-11 13:44:35.349345+03	32	\N	0	0	0.337	0	0	0	0	0	0	\N	0	SUCCESS
141	uganda_network_intelligence	SUCCESS	2026-09-11 11:47:19.841304+03	2026-09-11 11:47:20.042015+03	0	\N	0	0	0.283	0	0	0	0	0	0	\N	0	SUCCESS
149	csv_ingestion_test	RUNNING	2026-09-13 14:46:44.354602+03	\N	0	\N	0	0	\N	0	0	0	0	0	0	\N	0	INGESTION
142	uganda_network_intelligence	SUCCESS	2026-09-11 12:22:25.731581+03	2026-09-11 12:22:25.913916+03	0	\N	0	0	0.264	0	0	0	0	0	0	\N	0	SUCCESS
143	uganda_network_intelligence	SUCCESS	2026-09-11 12:28:20.706261+03	2026-09-11 12:28:20.884082+03	0	\N	0	0	0.416	0	0	0	0	0	0	\N	0	SUCCESS
144	uganda_network_intelligence	SUCCESS	2026-09-11 12:46:18.352624+03	2026-09-11 12:46:18.720146+03	0	\N	0	0	0.455	0	0	0	0	0	0	\N	0	SUCCESS
\.


--
-- Data for Name: pipeline_stage_runs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pipeline_stage_runs (stage_run_id, run_id, stage_name, started_at, completed_at, status, records_read, records_inserted, records_rejected, records_skipped, duration_seconds, error_message) FROM stdin;
1	100	GOLD	2026-09-07 07:54:38.500199+03	\N	RUNNING	0	0	0	0	\N	\N
2	101	GOLD	2026-09-07 08:42:58.496564+03	\N	RUNNING	0	0	0	0	\N	\N
3	102	GOLD	2026-09-07 08:58:42.001193+03	\N	RUNNING	0	0	0	0	\N	\N
4	103	GOLD	2026-09-07 09:01:48.591696+03	\N	RUNNING	0	0	0	0	\N	\N
5	104	SILVER	2026-09-07 09:25:55.257132+03	2026-09-07 09:25:55.281411+03	FAILED	0	0	0	0	0.024	(psycopg2.errors.UndefinedColumn) column "health_score" of relation "silver_network_health" does not exist\nLINE 3: ...asurement_id, site_id, equipment_id, measured_at, health_sco...\n                                                             ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, site_id, equipment_id, measured_at, health_score, status_classification\n    )\n    SELECT \n        measurement_id,\n        site_id,\n        equipment_id,\n        measured_at,\n        ROUND((availability_pct - packet_loss_pct), 2) AS health_score,\n        CASE \n            WHEN (availability_pct - packet_loss_pct) >= 95 THEN 'Healthy'\n            WHEN (availability_pct - packet_loss_pct) >= 80 THEN 'Warning'\n            ELSE 'Critical'\n        END AS status_classification\n    FROM measurements\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)
6	105	SILVER	2026-09-07 09:26:05.942248+03	2026-09-07 09:26:05.960569+03	FAILED	0	0	0	0	0.018	(psycopg2.errors.UndefinedColumn) column "health_score" of relation "silver_network_health" does not exist\nLINE 3: ...asurement_id, site_id, equipment_id, measured_at, health_sco...\n                                                             ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, site_id, equipment_id, measured_at, health_score, status_classification\n    )\n    SELECT \n        measurement_id,\n        site_id,\n        equipment_id,\n        measured_at,\n        ROUND((availability_pct - packet_loss_pct), 2) AS health_score,\n        CASE \n            WHEN (availability_pct - packet_loss_pct) >= 95 THEN 'Healthy'\n            WHEN (availability_pct - packet_loss_pct) >= 80 THEN 'Warning'\n            ELSE 'Critical'\n        END AS status_classification\n    FROM measurements\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)
7	106	SILVER	2026-09-07 09:27:40.15936+03	2026-09-07 09:27:40.223629+03	SUCCESS	0	40	0	0	0.064	\N
8	106	GOLD	2026-09-07 09:27:40.344648+03	\N	RUNNING	0	0	0	0	\N	\N
9	107	SILVER	2026-09-07 09:28:19.108676+03	2026-09-07 09:28:19.149925+03	FAILED	0	0	0	0	0.041	(sqlalchemy.exc.InvalidRequestError) A value is required for bind parameter 'run_id'\n[SQL: \n    INSERT INTO silver_measurements (\n        measurement_id, source_record_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at, batch_id, run_id\n    )\n    SELECT\n        m.measurement_id, m.source_record_id, m.measured_at, m.site_id, s.site_name, s.region, s.district, s.site_type,\n        m.equipment_id, e.equipment_type, e.manufacturer, e.model, m.traffic_mb, m.latency_ms,\n        m.packet_loss_pct, m.signal_strength_dbm, m.availability_pct,\n        COALESCE(m.ingested_at, CURRENT_TIMESTAMP), m.batch_id, %(run_id)s\n    FROM measurements m\n    JOIN sites s ON m.site_id = s.site_id\n    JOIN equipment e ON m.equipment_id = e.equipment_id\n    WHERE m.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/cd3x)
10	108	SILVER	2026-09-07 09:28:26.494729+03	2026-09-07 09:28:26.522186+03	FAILED	0	0	0	0	0.027	(sqlalchemy.exc.InvalidRequestError) A value is required for bind parameter 'run_id'\n[SQL: \n    INSERT INTO silver_measurements (\n        measurement_id, source_record_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at, batch_id, run_id\n    )\n    SELECT\n        m.measurement_id, m.source_record_id, m.measured_at, m.site_id, s.site_name, s.region, s.district, s.site_type,\n        m.equipment_id, e.equipment_type, e.manufacturer, e.model, m.traffic_mb, m.latency_ms,\n        m.packet_loss_pct, m.signal_strength_dbm, m.availability_pct,\n        COALESCE(m.ingested_at, CURRENT_TIMESTAMP), m.batch_id, %(run_id)s\n    FROM measurements m\n    JOIN sites s ON m.site_id = s.site_id\n    JOIN equipment e ON m.equipment_id = e.equipment_id\n    WHERE m.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/cd3x)
11	109	SILVER	2026-09-07 09:29:32.946285+03	2026-09-07 09:29:32.991949+03	FAILED	0	0	0	0	0.046	(psycopg2.errors.UndefinedColumn) column "site_name" of relation "silver_network_health" does not exist\nLINE 3:         measurement_id, measured_at, site_id, site_name, reg...\n                                                      ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id\n    )\n    SELECT\n        sm.measurement_id, sm.measured_at, sm.site_id, sm.site_name, sm.region, sm.district, sm.site_type,\n        sm.equipment_id, sm.equipment_type, sm.manufacturer, sm.model, sm.traffic_mb, sm.latency_ms,\n        sm.packet_loss_pct, sm.signal_strength_dbm, sm.availability_pct,\n        CASE\n            WHEN sm.availability_pct < 95 OR sm.packet_loss_pct > 5 OR sm.latency_ms > 70 THEN 'Critical'\n            WHEN sm.availability_pct < 98 OR sm.packet_loss_pct > 2 OR sm.latency_ms > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END,\n        sm.ingested_at, sm.batch_id, %(run_id)s\n    FROM silver_measurements sm\n    WHERE sm.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n[parameters: {'run_id': 109, 'batch_id': 3}]\n(Background on this error at: https://sqlalche.me/e/20/f405)
13	135	SILVER	2026-09-10 21:27:57.928781+03	\N	RUNNING	0	0	0	0	\N	\N
14	136	SILVER	2026-09-10 21:30:11.840645+03	2026-09-10 21:30:11.87679+03	SUCCESS	0	0	0	0	\N	\N
15	136	QUALITY	2026-09-10 21:30:11.889305+03	2026-09-10 21:30:11.960456+03	SUCCESS	0	0	0	0	\N	\N
16	136	GOLD	2026-09-10 21:30:11.964778+03	2026-09-10 21:30:12.024522+03	SUCCESS	0	0	0	0	\N	\N
17	137	SILVER	2026-09-10 21:30:18.281125+03	2026-09-10 21:30:18.309904+03	SUCCESS	0	0	0	0	\N	\N
18	137	QUALITY	2026-09-10 21:30:18.319351+03	2026-09-10 21:30:18.371561+03	SUCCESS	0	0	0	0	\N	\N
19	137	GOLD	2026-09-10 21:30:18.375013+03	2026-09-10 21:30:18.417059+03	SUCCESS	0	0	0	0	\N	\N
20	138	SILVER	2026-09-11 11:29:14.618322+03	2026-09-11 11:29:14.694961+03	SUCCESS	0	0	0	0	\N	\N
21	138	QUALITY	2026-09-11 11:29:14.698899+03	2026-09-11 11:29:14.771455+03	SUCCESS	0	0	0	0	\N	\N
22	138	GOLD	2026-09-11 11:29:14.774832+03	2026-09-11 11:29:14.820218+03	SUCCESS	0	0	0	0	\N	\N
23	139	SILVER	2026-09-11 11:36:40.453145+03	2026-09-11 11:36:40.493656+03	SUCCESS	0	0	0	0	\N	\N
24	139	QUALITY	2026-09-11 11:36:40.498395+03	2026-09-11 11:36:40.552202+03	SUCCESS	0	0	0	0	\N	\N
25	139	GOLD	2026-09-11 11:36:40.555508+03	2026-09-11 11:36:40.594679+03	SUCCESS	0	0	0	0	\N	\N
26	140	SILVER	2026-09-11 11:47:15.848948+03	2026-09-11 11:47:15.884947+03	SUCCESS	0	0	0	0	\N	\N
27	140	QUALITY	2026-09-11 11:47:15.888485+03	2026-09-11 11:47:15.932235+03	SUCCESS	0	0	0	0	\N	\N
28	140	GOLD	2026-09-11 11:47:15.935626+03	2026-09-11 11:47:15.981648+03	SUCCESS	0	0	0	0	\N	\N
29	141	SILVER	2026-09-11 11:47:19.891468+03	2026-09-11 11:47:19.945514+03	SUCCESS	0	0	0	0	\N	\N
30	141	QUALITY	2026-09-11 11:47:19.948925+03	2026-09-11 11:47:19.996979+03	SUCCESS	0	0	0	0	\N	\N
31	141	GOLD	2026-09-11 11:47:20.00029+03	2026-09-11 11:47:20.039699+03	SUCCESS	0	0	0	0	\N	\N
32	142	SILVER	2026-09-11 12:22:25.753282+03	2026-09-11 12:22:25.806731+03	SUCCESS	0	0	0	0	\N	\N
33	142	QUALITY	2026-09-11 12:22:25.81027+03	2026-09-11 12:22:25.86523+03	SUCCESS	0	0	0	0	\N	\N
34	142	GOLD	2026-09-11 12:22:25.87037+03	2026-09-11 12:22:25.911921+03	SUCCESS	0	0	0	0	\N	\N
35	143	SILVER	2026-09-11 12:28:20.751392+03	2026-09-11 12:28:20.78837+03	SUCCESS	0	0	0	0	\N	\N
36	143	QUALITY	2026-09-11 12:28:20.792651+03	2026-09-11 12:28:20.83739+03	SUCCESS	0	0	0	0	\N	\N
37	143	GOLD	2026-09-11 12:28:20.841176+03	2026-09-11 12:28:20.881741+03	SUCCESS	0	0	0	0	\N	\N
38	144	SILVER	2026-09-11 12:46:18.400697+03	2026-09-11 12:46:18.463044+03	SUCCESS	0	0	0	0	\N	\N
39	144	QUALITY	2026-09-11 12:46:18.469259+03	2026-09-11 12:46:18.65597+03	SUCCESS	0	0	0	0	\N	\N
40	144	GOLD	2026-09-11 12:46:18.660316+03	2026-09-11 12:46:18.717711+03	SUCCESS	0	0	0	0	\N	\N
41	145	SILVER	2026-09-11 13:18:59.474272+03	2026-09-11 13:18:59.513267+03	SUCCESS	0	0	0	0	\N	\N
42	145	QUALITY	2026-09-11 13:18:59.517522+03	2026-09-11 13:18:59.608464+03	SUCCESS	0	0	0	0	\N	\N
43	145	GOLD	2026-09-11 13:18:59.611754+03	2026-09-11 13:18:59.652057+03	SUCCESS	0	0	0	0	\N	\N
44	146	SILVER	2026-09-11 13:40:59.123406+03	2026-09-11 13:40:59.151887+03	FAILED	0	0	0	0	\N	'int' object has no attribute 'values'
45	147	SILVER	2026-09-11 13:43:00.808853+03	2026-09-11 13:43:00.850466+03	SUCCESS	0	0	0	0	\N	\N
46	147	QUALITY	2026-09-11 13:43:00.85399+03	2026-09-11 13:43:00.950503+03	SUCCESS	0	0	0	0	\N	\N
47	147	GOLD	2026-09-11 13:43:00.954857+03	2026-09-11 13:43:00.966314+03	FAILED	0	0	0	0	\N	(psycopg.errors.CardinalityViolation) ON CONFLICT DO UPDATE command cannot affect row a second time\nHINT:  Ensure that no rows proposed for insertion within the same command have duplicate constrained values.\n[SQL: \n    INSERT INTO gold_equipment_health (\n        equipment_id, equipment_type, manufacturer, model, measurement_count,\n        avg_latency_ms, avg_packet_loss_pct, avg_availability_pct, health_status\n    )\n    SELECT \n        equipment_id, equipment_type, manufacturer, model, COUNT(*),\n        AVG(latency_ms), AVG(packet_loss_pct), AVG(availability_pct),\n        CASE \n            WHEN AVG(availability_pct) < 95 THEN 'Critical'\n            WHEN AVG(availability_pct) < 98 THEN 'Warning'\n            ELSE 'Healthy'\n        END\n    FROM silver_network_health\n    GROUP BY equipment_id, equipment_type, manufacturer, model\n    ON CONFLICT (equipment_id) DO UPDATE SET\n        measurement_count = EXCLUDED.measurement_count,\n        avg_availability_pct = EXCLUDED.avg_availability_pct;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/f405)
48	148	SILVER	2026-09-11 13:44:35.116826+03	2026-09-11 13:44:35.173044+03	SUCCESS	0	0	0	0	\N	\N
49	148	QUALITY	2026-09-11 13:44:35.177351+03	2026-09-11 13:44:35.327889+03	SUCCESS	0	0	0	0	\N	\N
50	148	GOLD	2026-09-11 13:44:35.332208+03	2026-09-11 13:44:35.347632+03	SUCCESS	0	0	0	0	\N	\N
\.


--
-- Data for Name: raw_measurements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.raw_measurements (raw_measurement_id, measurement_id, site_id, equipment_id, measurement_date, traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct, source_file, ingestion_run_id, ingested_at) FROM stdin;
\.


--
-- Data for Name: rejected_measurements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rejected_measurements (rejection_id, source_record_id, rejected_at, equipment_id, site_id, measured_at, traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct, rejection_reason, source_file, ingested_at) FROM stdin;
\.


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schema_migrations (version, description, applied_at, checksum) FROM stdin;
000	create migration tracking table	2026-09-13 09:04:34.895093+03	\N
002	add migration checksum metadata	2026-09-13 09:06:09.028725+03	baseline-002
001	baseline existing Uganda Network Intelligence schema	2026-09-13 09:09:32.057629+03	\N
003	create raw measurements	2026-09-13 09:41:22.855886+03	\N
004	harden raw source	2026-09-13 14:43:36.405513+03	\N
005	create ingestion batches	2026-09-14 12:08:20.098516+03	\N
\.


--
-- Data for Name: silver_measurements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.silver_measurements (measurement_id, measured_at, site_id, site_name, region, district, site_type, equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at, batch_id, source_record_id, run_id) FROM stdin;
1	2026-08-28 08:00:00	6	Entebbe Central	Central	Wakiso	Macro Tower	1	Router	Cisco	ASR1001-X	15240.50	24.30	0.40	-58.20	99.80	2026-08-30 09:19:04.206671	\N	\N	\N
2	2026-08-28 09:00:00	6	Entebbe Central	Central	Wakiso	Macro Tower	1	Router	Cisco	ASR1001-X	16820.75	27.10	0.60	-59.10	99.70	2026-08-30 09:19:04.206671	\N	\N	\N
3	2026-08-28 08:00:00	6	Entebbe Central	Central	Wakiso	Macro Tower	2	Radio	Ericsson	MINI-LINK 6352	8240.30	18.40	0.20	-52.40	99.90	2026-08-30 09:19:04.206671	\N	\N	\N
4	2026-08-28 09:00:00	6	Entebbe Central	Central	Wakiso	Macro Tower	2	Radio	Ericsson	MINI-LINK 6352	9015.80	21.20	0.30	-53.10	99.80	2026-08-30 09:19:04.206671	\N	\N	\N
5	2026-08-28 08:00:00	7	Mbale East	Eastern	Mbale	Macro Tower	3	Router	Cisco	ASR1001-X	11240.60	35.80	1.20	-63.50	98.90	2026-08-30 09:19:04.206671	\N	\N	\N
6	2026-08-28 09:00:00	7	Mbale East	Eastern	Mbale	Macro Tower	3	Router	Cisco	ASR1001-X	12450.20	39.40	1.80	-64.20	98.50	2026-08-30 09:19:04.206671	\N	\N	\N
7	2026-08-28 08:00:00	7	Mbale East	Eastern	Mbale	Macro Tower	4	Switch	Huawei	S5735	9850.40	12.60	0.30	-45.20	99.70	2026-08-30 09:19:04.206671	\N	\N	\N
8	2026-08-28 09:00:00	7	Mbale East	Eastern	Mbale	Macro Tower	4	Switch	Huawei	S5735	10240.70	14.80	0.40	-46.10	99.60	2026-08-30 09:19:04.206671	\N	\N	\N
9	2026-08-28 08:00:00	8	Masaka South	Central	Masaka	Macro Tower	5	Radio	Ericsson	MINI-LINK 6352	7350.80	42.50	2.40	-69.30	97.80	2026-08-30 09:19:04.206671	\N	\N	\N
10	2026-08-28 09:00:00	8	Masaka South	Central	Masaka	Macro Tower	5	Radio	Ericsson	MINI-LINK 6352	7680.40	48.20	3.10	-70.40	96.90	2026-08-30 09:19:04.206671	\N	\N	\N
11	2026-08-28 08:00:00	9	Arua North	West Nile	Arua	Macro Tower	6	Router	Cisco	ASR1001-X	6420.30	55.60	4.20	-72.10	96.40	2026-08-30 09:19:04.206671	\N	\N	\N
12	2026-08-28 09:00:00	9	Arua North	West Nile	Arua	Macro Tower	6	Router	Cisco	ASR1001-X	6180.90	61.30	5.10	-73.50	95.80	2026-08-30 09:19:04.206671	\N	\N	\N
13	2026-08-28 08:00:00	10	Kabale Rural	Western	Kabale	Micro Cell	7	Radio	Nokia	FlexiPacket	4280.50	72.40	6.30	-78.20	94.70	2026-08-30 09:19:04.206671	\N	\N	\N
14	2026-08-28 09:00:00	10	Kabale Rural	Western	Kabale	Micro Cell	7	Radio	Nokia	FlexiPacket	3910.20	81.70	7.80	-80.10	93.60	2026-08-30 09:19:04.206671	\N	\N	\N
15	2026-08-28 08:00:00	12	Soroti Central	Eastern	Soroti	Macro Tower	8	Router	Cisco	ISR4331	8760.40	31.20	0.90	-61.40	98.70	2026-08-30 09:19:04.206671	\N	\N	\N
16	2026-08-28 09:00:00	12	Soroti Central	Eastern	Soroti	Macro Tower	8	Router	Cisco	ISR4331	9240.80	34.50	1.10	-62.20	98.40	2026-08-30 09:19:04.206671	\N	\N	\N
17	2026-08-01 08:00:00	1	Kampala Central Tower Hub	Central	Kampala	Macro Tower	1	Router	Cisco	ASR1001-X	1000.00	20.00	0.50	-60.00	99.90	2026-08-30 09:19:04.206671	\N	\N	\N
19	2026-08-30 08:30:22.922971	6	Entebbe Central	Central	Wakiso	Macro Tower	1	Router	Cisco	ASR1001-X	18500.50	35.20	1.10	-62.50	98.80	2026-08-30 09:19:04.206671	\N	\N	\N
20	2026-08-30 09:59:10.396175	1	Kampala Central Tower Hub	Central	Kampala	Macro Tower	1	Router	Cisco	ASR1001-X	22000.00	31.50	0.70	-60.50	99.10	2026-08-30 09:59:10.396175	\N	\N	\N
23	2026-08-31 06:00:00	1	Kampala Central Tower Hub	Central	Kampala	Macro Tower	1	Router	Cisco	ASR1001-X	12500.50	24.50	0.40	-59.50	99.80	2026-08-31 08:41:26.585871	\N	\N	\N
24	2026-08-31 06:00:00	6	Entebbe Central	Central	Wakiso	Macro Tower	2	Radio	Ericsson	MINI-LINK 6352	14200.20	21.30	0.30	-54.20	99.90	2026-08-31 08:41:26.618198	\N	\N	\N
25	2026-08-31 06:00:00	7	Mbale East	Eastern	Mbale	Macro Tower	3	Router	Cisco	ASR1001-X	10800.75	28.40	0.80	-56.70	99.30	2026-08-31 08:41:26.619989	\N	\N	\N
26	2026-08-31 06:00:00	8	Masaka South	Central	Masaka	Macro Tower	4	Switch	Huawei	S5735	7200.40	42.20	2.10	-68.40	97.80	2026-08-31 08:41:26.621611	\N	\N	\N
27	2026-08-31 06:00:00	9	Arua North	West Nile	Arua	Macro Tower	5	Radio	Ericsson	MINI-LINK 6352	6100.60	55.10	4.20	-71.50	96.40	2026-08-31 08:41:26.623078	\N	\N	\N
28	2026-08-31 06:00:00	10	Kabale Rural	Western	Kabale	Micro Cell	6	Router	Cisco	ASR1001-X	3900.25	73.60	6.50	-78.20	93.80	2026-08-31 08:41:26.624467	\N	\N	\N
29	2026-08-31 06:00:00	12	Soroti Central	Eastern	Soroti	Macro Tower	7	Radio	Nokia	FlexiPacket	8700.90	34.70	1.20	-63.10	98.20	2026-08-31 08:41:26.626619	\N	\N	\N
86	2026-08-31 07:00:00	12	Soroti Central	Eastern	Soroti	Macro Tower	8	Router	Cisco	ISR4331	9500.75	29.40	0.90	-62.30	98.70	2026-08-31 09:33:08.18734	\N	\N	\N
103	2026-08-31 11:00:00	6	Entebbe Central	Central	Wakiso	Macro Tower	2	Radio	Ericsson	MINI-LINK 6352	16500.25	19.20	0.15	-51.40	99.90	2026-08-31 13:08:29.342617	2	\N	\N
113	2026-08-31 12:00:00	6	Entebbe Central	Central	Wakiso	Macro Tower	2	Radio	Ericsson	MINI-LINK 6352	18500.75	21.40	0.25	-53.10	99.10	2026-08-31 13:10:50.480037	3	\N	\N
114	2026-09-01 08:47:44.741623	1	\N	\N	\N	\N	1	\N	\N	\N	15000.00	25.00	0.50	-60.00	99.50	2026-09-07 09:25:55.264533	\N	\N	\N
116	2026-09-02 09:31:38.83634	1	\N	\N	\N	\N	1	\N	\N	\N	12000.00	25.00	0.50	-60.00	99.50	2026-09-07 09:25:55.264533	\N	\N	\N
117	2026-09-02 08:00:00	1	\N	\N	\N	\N	1	\N	\N	\N	12500.50	24.50	0.40	-59.50	99.70	2026-09-07 09:25:55.264533	\N	\N	\N
118	2026-09-02 08:05:00	2	\N	\N	\N	\N	2	\N	\N	\N	9800.20	19.80	0.20	-52.00	99.90	2026-09-07 09:25:55.264533	\N	\N	\N
119	2026-09-02 08:10:00	3	\N	\N	\N	\N	3	\N	\N	\N	11200.75	35.60	1.20	-64.00	98.90	2026-09-07 09:25:55.264533	\N	\N	\N
120	2026-09-02 08:15:00	4	\N	\N	\N	\N	4	\N	\N	\N	15400.30	15.20	0.30	-45.50	99.80	2026-09-07 09:25:55.264533	\N	\N	\N
121	2026-09-02 08:20:00	6	\N	\N	\N	\N	5	\N	\N	\N	18750.90	34.80	1.00	-62.20	98.90	2026-09-07 09:25:55.264533	\N	\N	\N
122	2026-09-02 08:25:00	6	\N	\N	\N	\N	2	\N	\N	\N	6200.40	59.10	4.80	-73.10	95.90	2026-09-07 09:25:55.264533	\N	\N	\N
123	2026-09-02 08:30:00	6	\N	\N	\N	\N	2	\N	\N	\N	4100.60	76.80	7.10	-79.00	94.00	2026-09-07 09:25:55.264533	\N	\N	\N
124	2026-09-02 08:35:00	4	\N	\N	\N	\N	4	\N	\N	\N	9100.25	31.50	0.90	-61.30	98.60	2026-09-07 09:25:55.264533	\N	\N	\N
149	2026-09-03 08:00:00	1	\N	\N	\N	\N	1	\N	\N	\N	14200.50	22.10	0.30	-57.00	99.80	2026-09-07 09:25:55.264533	\N	\N	\N
204	2026-09-09 06:36:15.648342	1	Kampala Central Tower Hub	Central	Kampala	Macro Tower	1	Router	Cisco	ASR1001-X	15000.00	30.00	1.00	-60.00	99.00	2026-09-09 06:38:59.377947	\N	\N	\N
\.


--
-- Data for Name: silver_network_health; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.silver_network_health (measurement_id, measured_at, site_id, site_name, region, district, site_type, equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id, inserted_at) FROM stdin;
2	2026-08-28 09:00:00	6	Site 6	Region	District	Macro	1	Radio	Manufacturer	Model	16820.750	27.100	0.60	-59.10	99.70	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
3	2026-08-28 08:00:00	6	Site 6	Region	District	Macro	2	Radio	Manufacturer	Model	8240.300	18.400	0.20	-52.40	99.90	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
4	2026-08-28 09:00:00	6	Site 6	Region	District	Macro	2	Radio	Manufacturer	Model	9015.800	21.200	0.30	-53.10	99.80	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
5	2026-08-28 08:00:00	7	Site 7	Region	District	Macro	3	Radio	Manufacturer	Model	11240.600	35.800	1.20	-63.50	98.90	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
6	2026-08-28 09:00:00	7	Site 7	Region	District	Macro	3	Radio	Manufacturer	Model	12450.200	39.400	1.80	-64.20	98.50	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
7	2026-08-28 08:00:00	7	Site 7	Region	District	Macro	4	Radio	Manufacturer	Model	9850.400	12.600	0.30	-45.20	99.70	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
8	2026-08-28 09:00:00	7	Site 7	Region	District	Macro	4	Radio	Manufacturer	Model	10240.700	14.800	0.40	-46.10	99.60	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
9	2026-08-28 08:00:00	8	Site 8	Region	District	Macro	5	Radio	Manufacturer	Model	7350.800	42.500	2.40	-69.30	97.80	Warning	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
10	2026-08-28 09:00:00	8	Site 8	Region	District	Macro	5	Radio	Manufacturer	Model	7680.400	48.200	3.10	-70.40	96.90	Warning	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
11	2026-08-28 08:00:00	9	Site 9	Region	District	Macro	6	Radio	Manufacturer	Model	6420.300	55.600	4.20	-72.10	96.40	Warning	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
12	2026-08-28 09:00:00	9	Site 9	Region	District	Macro	6	Radio	Manufacturer	Model	6180.900	61.300	5.10	-73.50	95.80	Critical	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
13	2026-08-28 08:00:00	10	Site 10	Region	District	Macro	7	Radio	Manufacturer	Model	4280.500	72.400	6.30	-78.20	94.70	Critical	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
14	2026-08-28 09:00:00	10	Site 10	Region	District	Macro	7	Radio	Manufacturer	Model	3910.200	81.700	7.80	-80.10	93.60	Critical	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
15	2026-08-28 08:00:00	12	Site 12	Region	District	Macro	8	Radio	Manufacturer	Model	8760.400	31.200	0.90	-61.40	98.70	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
16	2026-08-28 09:00:00	12	Site 12	Region	District	Macro	8	Radio	Manufacturer	Model	9240.800	34.500	1.10	-62.20	98.40	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
17	2026-08-01 08:00:00	1	Site 1	Region	District	Macro	1	Radio	Manufacturer	Model	1000.000	20.000	0.50	-60.00	99.90	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
19	2026-08-30 08:30:22.922971	6	Site 6	Region	District	Macro	1	Radio	Manufacturer	Model	18500.500	35.200	1.10	-62.50	98.80	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
20	2026-08-30 09:59:10.396175	1	Site 1	Region	District	Macro	1	Radio	Manufacturer	Model	22000.000	31.500	0.70	-60.50	99.10	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
23	2026-08-31 06:00:00	1	Site 1	Region	District	Macro	1	Radio	Manufacturer	Model	12500.500	24.500	0.40	-59.50	99.80	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
24	2026-08-31 06:00:00	6	Site 6	Region	District	Macro	2	Radio	Manufacturer	Model	14200.200	21.300	0.30	-54.20	99.90	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
25	2026-08-31 06:00:00	7	Site 7	Region	District	Macro	3	Radio	Manufacturer	Model	10800.750	28.400	0.80	-56.70	99.30	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
26	2026-08-31 06:00:00	8	Site 8	Region	District	Macro	4	Radio	Manufacturer	Model	7200.400	42.200	2.10	-68.40	97.80	Warning	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
27	2026-08-31 06:00:00	9	Site 9	Region	District	Macro	5	Radio	Manufacturer	Model	6100.600	55.100	4.20	-71.50	96.40	Warning	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
28	2026-08-31 06:00:00	10	Site 10	Region	District	Macro	6	Radio	Manufacturer	Model	3900.250	73.600	6.50	-78.20	93.80	Critical	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
29	2026-08-31 06:00:00	12	Site 12	Region	District	Macro	7	Radio	Manufacturer	Model	8700.900	34.700	1.20	-63.10	98.20	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
86	2026-08-31 07:00:00	12	Site 12	Region	District	Macro	8	Radio	Manufacturer	Model	9500.750	29.400	0.90	-62.30	98.70	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
103	2026-08-31 11:00:00	6	Site 6	Region	District	Macro	2	Radio	Manufacturer	Model	16500.250	19.200	0.15	-51.40	99.90	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
113	2026-08-31 12:00:00	6	Site 6	Region	District	Macro	2	Radio	Manufacturer	Model	18500.750	21.400	0.25	-53.10	99.10	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
114	2026-09-01 08:47:44.741623	1	Site 1	Region	District	Macro	1	Radio	Manufacturer	Model	15000.000	25.000	0.50	-60.00	99.50	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
116	2026-09-02 09:31:38.83634	1	Site 1	Region	District	Macro	1	Radio	Manufacturer	Model	12000.000	25.000	0.50	-60.00	99.50	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
117	2026-09-02 08:00:00	1	Site 1	Region	District	Macro	1	Radio	Manufacturer	Model	12500.500	24.500	0.40	-59.50	99.70	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
118	2026-09-02 08:05:00	2	Site 2	Region	District	Macro	2	Radio	Manufacturer	Model	9800.200	19.800	0.20	-52.00	99.90	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
119	2026-09-02 08:10:00	3	Site 3	Region	District	Macro	3	Radio	Manufacturer	Model	11200.750	35.600	1.20	-64.00	98.90	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
120	2026-09-02 08:15:00	4	Site 4	Region	District	Macro	4	Radio	Manufacturer	Model	15400.300	15.200	0.30	-45.50	99.80	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
121	2026-09-02 08:20:00	6	Site 6	Region	District	Macro	5	Radio	Manufacturer	Model	18750.900	34.800	1.00	-62.20	98.90	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
122	2026-09-02 08:25:00	6	Site 6	Region	District	Macro	2	Radio	Manufacturer	Model	6200.400	59.100	4.80	-73.10	95.90	Warning	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
123	2026-09-02 08:30:00	6	Site 6	Region	District	Macro	2	Radio	Manufacturer	Model	4100.600	76.800	7.10	-79.00	94.00	Critical	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
124	2026-09-02 08:35:00	4	Site 4	Region	District	Macro	4	Radio	Manufacturer	Model	9100.250	31.500	0.90	-61.30	98.60	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
149	2026-09-03 08:00:00	1	Site 1	Region	District	Macro	1	Radio	Manufacturer	Model	14200.500	22.100	0.30	-57.00	99.80	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
1	2026-08-28 08:00:00	6	Site 6	Region	District	Macro	1	Radio	Manufacturer	Model	15240.500	24.300	0.40	-58.20	99.90	Healthy	2026-09-07 09:33:04.360163	3	113	2026-09-07 09:33:04.360163
204	2026-09-09 06:36:15.648342	1	Kampala Central Tower Hub	Central	Kampala	Macro Tower	1	Router	Cisco	ASR1001-X	15000.000	30.000	1.00	-60.00	99.00	Healthy	2026-09-09 06:38:59.402042	3	122	2026-09-09 06:38:59.402042
\.


--
-- Data for Name: sites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sites (site_id, site_name, region, district, latitude, longitude, site_type, status) FROM stdin;
1	Kampala Central Tower Hub	Central	Kampala	0.313600	32.581100	Macro Tower	Active
2	Gulu Main Base Cell	Northern	Gulu	2.774500	32.299000	Micro Cell	Active
3	Mbarara Business District	Western	Mbarara	-0.606700	30.655200	Rooftop Hub	Active
4	Jinja Industrial Overlook	Eastern	Jinja	0.424400	33.204300	Macro Tower	Active
5	Entebbe Airport Gateway	Central	Wakiso	0.051500	32.443500	Data Center	Active
6	Entebbe Central	Central	Wakiso	0.051200	32.463700	Macro Tower	Active
7	Mbale East	Eastern	Mbale	1.080600	34.175000	Macro Tower	Active
8	Masaka South	Central	Masaka	-0.333800	31.734100	Macro Tower	Active
9	Arua North	West Nile	Arua	3.029000	30.910000	Macro Tower	Active
10	Kabale Rural	Western	Kabale	-1.248600	29.989900	Micro Cell	Active
12	Soroti Central	Eastern	Soroti	1.715000	33.611000	Macro Tower	Active
\.


--
-- Data for Name: source_batches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.source_batches (batch_id, source_name, file_name, file_checksum, records_read, records_inserted, records_rejected, status, started_at, completed_at, error_message) FROM stdin;
1	network_measurements	network_measurements.csv	625184ed6bfa0df417425f034ce1e67492c71d547a642db8241d44b7b5581772	8	0	0	SUCCESS	2026-08-31 10:14:33.72127	2026-08-31 10:14:33.758984	\N
2	network_measurements	network_measurements.csv	c6eccf565cb436e372e6fc6804f40928f092e064165724836b6649534c7a177a	9	1	0	SUCCESS	2026-08-31 13:08:29.315123	2026-08-31 13:08:29.37259	\N
3	network_measurements	network_measurements.csv	cf363c4879f648f5e9f348f4297b478707baca093a8c5cb9edf5db4fe31b2564	10	1	0	SUCCESS	2026-08-31 13:10:50.44995	2026-08-31 13:10:50.492542	\N
\.


--
-- Data for Name: transformation_runs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.transformation_runs (transformation_run_id, run_id, layer, transformation_name, started_at, completed_at, status, records_processed, error_message) FROM stdin;
1	84	SILVER	silver_measurements	2026-09-04 09:24:41.882126	2026-09-04 09:24:41.906398	SUCCESS	0	\N
2	84	GOLD	gold_transformations	2026-09-04 09:24:41.911459	2026-09-04 09:24:41.923356	FAILED	0	(sqlalchemy.exc.InvalidRequestError) A value is required for bind parameter 'availability_pct'\n[SQL: \n    INSERT INTO gold_site_daily_performance (\n        site_id, site_name, region, district, measurement_date,\n        measurement_count, avg_traffic_mb, avg_latency_ms,\n        avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct,\n        updated_at\n    )\n    VALUES (\n        %(site_id)s, %(site_name)s, %(region)s, %(district)s, %(measurement_date)s,\n        %(measurement_count)s, %(avg_traffic_mb)s, %(avg_latency_ms)s,\n        %(avg_packet_loss_pct)s, %(avg_signal_strength_dbm)s, %(availability_pct)s,\n        CURRENT_TIMESTAMP\n    )\n    ON CONFLICT (site_id, measurement_date) \n    DO UPDATE SET\n        site_name = EXCLUDED.site_name,\n        region = EXCLUDED.region,\n        district = EXCLUDED.district,\n        measurement_count = EXCLUDED.measurement_count,\n        avg_traffic_mb = EXCLUDED.avg_traffic_mb,\n        avg_latency_ms = EXCLUDED.avg_latency_ms,\n        avg_packet_loss_pct = EXCLUDED.avg_packet_loss_pct,\n        avg_signal_strength_dbm = EXCLUDED.avg_signal_strength_dbm,\n        avg_availability_pct = EXCLUDED.avg_availability_pct,\n        updated_at = CURRENT_TIMESTAMP;\n    ]\n[parameters: [{'site_id': 6, 'site_name': 'Entebbe Central', 'region': 'Central', 'district': 'Wakiso', 'measurement_date': datetime.date(2026, 8, 31), 'measurement ... (64 characters truncated) ... ms': Decimal('20.63'), 'avg_packet_loss_pct': Decimal('0.23'), 'avg_signal_strength_dbm': Decimal('-52.90'), 'avg_availability_pct': Decimal('99.63')}]]\n(Background on this error at: https://sqlalche.me/e/20/cd3x)
3	85	SILVER	silver_measurements	2026-09-04 09:24:51.129667	2026-09-04 09:24:51.150471	SUCCESS	0	\N
4	85	GOLD	gold_transformations	2026-09-04 09:24:51.154178	2026-09-04 09:24:51.16634	FAILED	0	(sqlalchemy.exc.InvalidRequestError) A value is required for bind parameter 'availability_pct'\n[SQL: \n    INSERT INTO gold_site_daily_performance (\n        site_id, site_name, region, district, measurement_date,\n        measurement_count, avg_traffic_mb, avg_latency_ms,\n        avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct,\n        updated_at\n    )\n    VALUES (\n        %(site_id)s, %(site_name)s, %(region)s, %(district)s, %(measurement_date)s,\n        %(measurement_count)s, %(avg_traffic_mb)s, %(avg_latency_ms)s,\n        %(avg_packet_loss_pct)s, %(avg_signal_strength_dbm)s, %(availability_pct)s,\n        CURRENT_TIMESTAMP\n    )\n    ON CONFLICT (site_id, measurement_date) \n    DO UPDATE SET\n        site_name = EXCLUDED.site_name,\n        region = EXCLUDED.region,\n        district = EXCLUDED.district,\n        measurement_count = EXCLUDED.measurement_count,\n        avg_traffic_mb = EXCLUDED.avg_traffic_mb,\n        avg_latency_ms = EXCLUDED.avg_latency_ms,\n        avg_packet_loss_pct = EXCLUDED.avg_packet_loss_pct,\n        avg_signal_strength_dbm = EXCLUDED.avg_signal_strength_dbm,\n        avg_availability_pct = EXCLUDED.avg_availability_pct,\n        updated_at = CURRENT_TIMESTAMP;\n    ]\n[parameters: [{'site_id': 6, 'site_name': 'Entebbe Central', 'region': 'Central', 'district': 'Wakiso', 'measurement_date': datetime.date(2026, 8, 31), 'measurement ... (64 characters truncated) ... ms': Decimal('20.63'), 'avg_packet_loss_pct': Decimal('0.23'), 'avg_signal_strength_dbm': Decimal('-52.90'), 'avg_availability_pct': Decimal('99.63')}]]\n(Background on this error at: https://sqlalche.me/e/20/cd3x)
5	86	SILVER	silver_measurements	2026-09-04 09:26:50.920856	2026-09-04 09:26:50.943959	SUCCESS	0	\N
6	86	GOLD	gold_transformations	2026-09-04 09:26:50.94793	2026-09-04 09:26:50.979593	SUCCESS	9	\N
7	87	SILVER	silver_measurements	2026-09-04 09:29:02.137672	2026-09-04 09:29:02.15985	SUCCESS	0	\N
8	87	GOLD	gold_transformations	2026-09-04 09:29:02.16487	2026-09-04 09:29:02.192928	SUCCESS	9	\N
9	88	SILVER	silver_measurements	2026-09-04 09:50:14.147849	2026-09-04 09:50:14.172758	SUCCESS	0	\N
10	88	GOLD	gold_transformations	2026-09-04 09:50:14.176496	2026-09-04 09:50:14.207718	SUCCESS	9	\N
11	89	SILVER	silver_measurements	2026-09-04 09:53:18.132867	2026-09-04 09:53:18.156165	SUCCESS	0	\N
12	89	GOLD	gold_transformations	2026-09-04 09:53:18.159885	2026-09-04 09:53:18.188655	SUCCESS	9	\N
13	90	SILVER	silver_measurements	2026-09-04 11:19:54.011023	2026-09-04 11:19:54.046197	SUCCESS	0	\N
14	90	GOLD	gold_transformations	2026-09-04 11:19:54.051073	2026-09-04 11:19:54.086014	SUCCESS	9	\N
15	91	SILVER	silver_measurements	2026-09-04 11:47:32.385334	2026-09-04 11:47:32.411538	SUCCESS	0	\N
16	91	GOLD	gold_transformations	2026-09-04 11:47:32.41628	2026-09-04 11:47:32.447816	SUCCESS	9	\N
17	92	SILVER	silver_measurements	2026-09-04 11:50:29.654777	2026-09-04 11:50:29.680776	SUCCESS	0	\N
18	92	GOLD	gold_transformations	2026-09-04 11:50:29.685532	2026-09-04 11:50:29.720363	SUCCESS	9	\N
19	93	SILVER	silver_measurements	2026-09-04 11:52:39.636083	2026-09-04 11:52:39.661871	SUCCESS	0	\N
20	93	GOLD	gold_transformations	2026-09-04 11:52:39.666404	2026-09-04 11:52:39.696862	SUCCESS	9	\N
21	94	SILVER	silver_measurements	2026-09-06 07:36:02.778587	2026-09-06 07:36:02.813931	SUCCESS	0	\N
22	94	GOLD	gold_transformations	2026-09-06 07:36:02.817102	2026-09-06 07:36:02.850878	SUCCESS	9	\N
23	98	SILVER	silver_measurements	2026-09-07 07:17:08.997177	2026-09-07 07:17:09.025341	SUCCESS	0	\N
24	98	GOLD	gold_transformations	2026-09-07 07:17:09.034417	2026-09-07 07:17:09.084465	SUCCESS	9	\N
25	99	SILVER	silver_measurements	2026-09-07 07:42:04.457723	2026-09-07 07:42:04.48277	SUCCESS	0	\N
26	99	GOLD	gold_transformations	2026-09-07 07:42:04.490239	2026-09-07 07:42:04.52373	SUCCESS	9	\N
27	100	SILVER	silver_measurements	2026-09-07 07:54:38.447258	2026-09-07 07:54:38.471713	SUCCESS	0	\N
28	100	GOLD	gold_transformations	2026-09-07 07:54:38.509669	2026-09-07 07:54:38.548351	SUCCESS	9	\N
29	101	SILVER	silver_measurements	2026-09-07 08:42:58.438307	2026-09-07 08:42:58.464424	SUCCESS	0	\N
30	101	GOLD	gold_transformations	2026-09-07 08:42:58.500285	2026-09-07 08:42:58.532947	SUCCESS	9	\N
31	102	SILVER	silver_measurements	2026-09-07 08:58:41.938336	2026-09-07 08:58:41.970351	SUCCESS	0	\N
32	102	GOLD	gold_transformations	2026-09-07 08:58:42.00487	2026-09-07 08:58:42.039061	SUCCESS	9	\N
33	103	SILVER	silver_measurements	2026-09-07 09:01:48.397682	2026-09-07 09:01:48.421745	SUCCESS	0	\N
34	103	GOLD	gold_transformations	2026-09-07 09:01:48.59949	2026-09-07 09:01:48.642053	SUCCESS	9	\N
35	106	GOLD	gold_transformations	2026-09-07 09:27:40.350898	2026-09-07 09:27:40.398561	FAILED	0	(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "gold_equipment_health_pkey"\nDETAIL:  Key (equipment_id)=(2) already exists.\n\n[SQL: \n    TRUNCATE TABLE gold_equipment_health;\n    INSERT INTO gold_equipment_health (\n        equipment_id, equipment_type, manufacturer, model, measurement_count,\n        avg_latency_ms, avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct,\n        health_status, record_count, updated_at\n    )\n    SELECT\n        equipment_id, equipment_type, manufacturer, model, COUNT(*) AS measurement_count,\n        ROUND(AVG(latency_ms), 2) AS avg_latency_ms,\n        ROUND(AVG(packet_loss_pct), 2) AS avg_packet_loss_pct,\n        ROUND(AVG(signal_strength_dbm), 2) AS avg_signal_strength_dbm,\n        ROUND(AVG(availability_pct), 2) AS avg_availability_pct,\n        CASE\n            WHEN AVG(availability_pct) < 95 OR AVG(packet_loss_pct) > 5 OR AVG(latency_ms) > 70 THEN 'Critical'\n            WHEN AVG(availability_pct) < 98 OR AVG(packet_loss_pct) > 2 OR AVG(latency_ms) > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END AS health_status,\n        COUNT(*) AS record_count,\n        CURRENT_TIMESTAMP\n    FROM silver_measurements\n    GROUP BY equipment_id, equipment_type, manufacturer, model;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/gkpj)
36	107	SILVER	silver_measurements	2026-09-07 09:28:19.113641	2026-09-07 09:28:19.146937	FAILED	0	(sqlalchemy.exc.InvalidRequestError) A value is required for bind parameter 'run_id'\n[SQL: \n    INSERT INTO silver_measurements (\n        measurement_id, source_record_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at, batch_id, run_id\n    )\n    SELECT\n        m.measurement_id, m.source_record_id, m.measured_at, m.site_id, s.site_name, s.region, s.district, s.site_type,\n        m.equipment_id, e.equipment_type, e.manufacturer, e.model, m.traffic_mb, m.latency_ms,\n        m.packet_loss_pct, m.signal_strength_dbm, m.availability_pct,\n        COALESCE(m.ingested_at, CURRENT_TIMESTAMP), m.batch_id, %(run_id)s\n    FROM measurements m\n    JOIN sites s ON m.site_id = s.site_id\n    JOIN equipment e ON m.equipment_id = e.equipment_id\n    WHERE m.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/cd3x)
37	108	SILVER	silver_measurements	2026-09-07 09:28:26.500057	2026-09-07 09:28:26.518707	FAILED	0	(sqlalchemy.exc.InvalidRequestError) A value is required for bind parameter 'run_id'\n[SQL: \n    INSERT INTO silver_measurements (\n        measurement_id, source_record_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at, batch_id, run_id\n    )\n    SELECT\n        m.measurement_id, m.source_record_id, m.measured_at, m.site_id, s.site_name, s.region, s.district, s.site_type,\n        m.equipment_id, e.equipment_type, e.manufacturer, e.model, m.traffic_mb, m.latency_ms,\n        m.packet_loss_pct, m.signal_strength_dbm, m.availability_pct,\n        COALESCE(m.ingested_at, CURRENT_TIMESTAMP), m.batch_id, %(run_id)s\n    FROM measurements m\n    JOIN sites s ON m.site_id = s.site_id\n    JOIN equipment e ON m.equipment_id = e.equipment_id\n    WHERE m.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/cd3x)
38	109	SILVER	silver_measurements	2026-09-07 09:29:32.951048	2026-09-07 09:29:32.986857	FAILED	0	(psycopg2.errors.UndefinedColumn) column "site_name" of relation "silver_network_health" does not exist\nLINE 3:         measurement_id, measured_at, site_id, site_name, reg...\n                                                      ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id\n    )\n    SELECT\n        sm.measurement_id, sm.measured_at, sm.site_id, sm.site_name, sm.region, sm.district, sm.site_type,\n        sm.equipment_id, sm.equipment_type, sm.manufacturer, sm.model, sm.traffic_mb, sm.latency_ms,\n        sm.packet_loss_pct, sm.signal_strength_dbm, sm.availability_pct,\n        CASE\n            WHEN sm.availability_pct < 95 OR sm.packet_loss_pct > 5 OR sm.latency_ms > 70 THEN 'Critical'\n            WHEN sm.availability_pct < 98 OR sm.packet_loss_pct > 2 OR sm.latency_ms > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END,\n        sm.ingested_at, sm.batch_id, %(run_id)s\n    FROM silver_measurements sm\n    WHERE sm.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n[parameters: {'run_id': 109, 'batch_id': 3}]\n(Background on this error at: https://sqlalche.me/e/20/f405)
39	110	SILVER	silver_measurements	2026-09-07 09:30:29.78714	2026-09-07 09:30:29.811397	FAILED	0	(psycopg2.errors.UndefinedColumn) column "site_name" of relation "silver_network_health" does not exist\nLINE 3:         measurement_id, measured_at, site_id, site_name, reg...\n                                                      ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id\n    )\n    SELECT\n        sm.measurement_id, sm.measured_at, sm.site_id, sm.site_name, sm.region, sm.district, sm.site_type,\n        sm.equipment_id, sm.equipment_type, sm.manufacturer, sm.model, sm.traffic_mb, sm.latency_ms,\n        sm.packet_loss_pct, sm.signal_strength_dbm, sm.availability_pct,\n        CASE\n            WHEN sm.availability_pct < 95 OR sm.packet_loss_pct > 5 OR sm.latency_ms > 70 THEN 'Critical'\n            WHEN sm.availability_pct < 98 OR sm.packet_loss_pct > 2 OR sm.latency_ms > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END,\n        sm.ingested_at, sm.batch_id, %(run_id)s\n    FROM silver_measurements sm\n    WHERE sm.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n[parameters: {'run_id': 110, 'batch_id': 3}]\n(Background on this error at: https://sqlalche.me/e/20/f405)
40	111	SILVER	silver_measurements	2026-09-07 09:31:03.479071	2026-09-07 09:31:03.504062	FAILED	0	(psycopg2.errors.UndefinedColumn) column "site_name" of relation "silver_network_health" does not exist\nLINE 3:         measurement_id, measured_at, site_id, site_name, reg...\n                                                      ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id\n    )\n    SELECT\n        sm.measurement_id, sm.measured_at, sm.site_id, sm.site_name, sm.region, sm.district, sm.site_type,\n        sm.equipment_id, sm.equipment_type, sm.manufacturer, sm.model, sm.traffic_mb, sm.latency_ms,\n        sm.packet_loss_pct, sm.signal_strength_dbm, sm.availability_pct,\n        CASE\n            WHEN sm.availability_pct < 95 OR sm.packet_loss_pct > 5 OR sm.latency_ms > 70 THEN 'Critical'\n            WHEN sm.availability_pct < 98 OR sm.packet_loss_pct > 2 OR sm.latency_ms > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END,\n        sm.ingested_at, sm.batch_id, %(run_id)s\n    FROM silver_measurements sm\n    WHERE sm.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n[parameters: {'run_id': 111, 'batch_id': 3}]\n(Background on this error at: https://sqlalche.me/e/20/f405)
41	112	SILVER	silver_measurements	2026-09-07 09:31:12.960411	2026-09-07 09:31:12.982668	FAILED	0	(psycopg2.errors.UndefinedColumn) column "site_name" of relation "silver_network_health" does not exist\nLINE 3:         measurement_id, measured_at, site_id, site_name, reg...\n                                                      ^\n\n[SQL: \n    INSERT INTO silver_network_health (\n        measurement_id, measured_at, site_id, site_name, region, district, site_type,\n        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,\n        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id\n    )\n    SELECT\n        sm.measurement_id, sm.measured_at, sm.site_id, sm.site_name, sm.region, sm.district, sm.site_type,\n        sm.equipment_id, sm.equipment_type, sm.manufacturer, sm.model, sm.traffic_mb, sm.latency_ms,\n        sm.packet_loss_pct, sm.signal_strength_dbm, sm.availability_pct,\n        CASE\n            WHEN sm.availability_pct < 95 OR sm.packet_loss_pct > 5 OR sm.latency_ms > 70 THEN 'Critical'\n            WHEN sm.availability_pct < 98 OR sm.packet_loss_pct > 2 OR sm.latency_ms > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END,\n        sm.ingested_at, sm.batch_id, %(run_id)s\n    FROM silver_measurements sm\n    WHERE sm.batch_id = %(batch_id)s\n    ON CONFLICT (measurement_id) DO NOTHING;\n    ]\n[parameters: {'run_id': 112, 'batch_id': 3}]\n(Background on this error at: https://sqlalche.me/e/20/f405)
42	113	GOLD	gold_transformations	2026-09-07 09:33:04.368784	2026-09-07 09:33:04.413443	FAILED	0	(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "gold_equipment_health_pkey"\nDETAIL:  Key (equipment_id)=(2) already exists.\n\n[SQL: \n    TRUNCATE TABLE gold_equipment_health;\n    INSERT INTO gold_equipment_health (\n        equipment_id, equipment_type, manufacturer, model, measurement_count,\n        avg_latency_ms, avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct,\n        health_status, record_count, updated_at\n    )\n    SELECT\n        equipment_id, equipment_type, manufacturer, model, COUNT(*) AS measurement_count,\n        ROUND(AVG(latency_ms), 2) AS avg_latency_ms,\n        ROUND(AVG(packet_loss_pct), 2) AS avg_packet_loss_pct,\n        ROUND(AVG(signal_strength_dbm), 2) AS avg_signal_strength_dbm,\n        ROUND(AVG(availability_pct), 2) AS avg_availability_pct,\n        CASE\n            WHEN AVG(availability_pct) < 95 OR AVG(packet_loss_pct) > 5 OR AVG(latency_ms) > 70 THEN 'Critical'\n            WHEN AVG(availability_pct) < 98 OR AVG(packet_loss_pct) > 2 OR AVG(latency_ms) > 40 THEN 'Warning'\n            ELSE 'Healthy'\n        END AS health_status,\n        COUNT(*) AS record_count,\n        CURRENT_TIMESTAMP\n    FROM silver_measurements\n    GROUP BY equipment_id, equipment_type, manufacturer, model;\n    ]\n(Background on this error at: https://sqlalche.me/e/20/gkpj)
\.


--
-- Name: data_lineage_lineage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.data_lineage_lineage_id_seq', 2, true);


--
-- Name: data_quality_results_quality_result_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.data_quality_results_quality_result_id_seq', 609, true);


--
-- Name: equipment_equipment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_equipment_id_seq', 26, true);


--
-- Name: incidents_incident_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.incidents_incident_id_seq', 8, true);


--
-- Name: ingestion_batches_batch_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ingestion_batches_batch_id_seq', 1, false);


--
-- Name: measurements_measurement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.measurements_measurement_id_seq', 204, true);


--
-- Name: pipeline_lineage_lineage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pipeline_lineage_lineage_id_seq', 38, true);


--
-- Name: pipeline_runs_run_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pipeline_runs_run_id_seq', 149, true);


--
-- Name: pipeline_stage_runs_stage_run_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pipeline_stage_runs_stage_run_id_seq', 50, true);


--
-- Name: raw_measurements_raw_measurement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.raw_measurements_raw_measurement_id_seq', 43, true);


--
-- Name: rejected_measurements_rejection_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rejected_measurements_rejection_id_seq', 1, false);


--
-- Name: sites_site_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sites_site_id_seq', 12, true);


--
-- Name: source_batches_batch_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.source_batches_batch_id_seq', 3, true);


--
-- Name: transformation_runs_transformation_run_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.transformation_runs_transformation_run_id_seq', 42, true);


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
-- Name: rejected_measurements rejected_measurements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rejected_measurements
    ADD CONSTRAINT rejected_measurements_pkey PRIMARY KEY (rejection_id);


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
-- Name: raw_measurements uq_raw_measurement_source; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.raw_measurements
    ADD CONSTRAINT uq_raw_measurement_source UNIQUE (measurement_id, source_file);


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
-- Name: ingestion_batches fk_ingestion_pipeline_run; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingestion_batches
    ADD CONSTRAINT fk_ingestion_pipeline_run FOREIGN KEY (pipeline_run_id) REFERENCES public.pipeline_runs(run_id) ON DELETE CASCADE;


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
-- Name: raw_measurements fk_raw_ingestion_run; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.raw_measurements
    ADD CONSTRAINT fk_raw_ingestion_run FOREIGN KEY (ingestion_run_id) REFERENCES public.pipeline_runs(run_id);


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

\unrestrict F1iqCZVdvdMeXSaCKjfE0hFocMOaCepjPe5W2EPVaEcIUNAWknU2N2aN63RIEOt

