--
-- PostgreSQL database dump
--

\restrict 4wTBkMjp2lRTPFIWoBEu9w6GOah4jjplPdPxUeRQ9ZwJisOpctC8udDhssPCijt

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.7 (Ubuntu 17.7-3.pgdg24.04+1)

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: grants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.grants (
    id integer NOT NULL,
    name text,
    url text NOT NULL,
    details text,
    button_text text,
    card_body_text text,
    card_body_html text,
    links text[]
);


--
-- Name: grants_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.grants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: grants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.grants_id_seq OWNED BY public.grants.id;


--
-- Name: initiatives; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.initiatives (
    id integer NOT NULL,
    organisation_id integer NOT NULL,
    title text NOT NULL,
    goals text NOT NULL,
    audience text NOT NULL,
    costs bigint,
    stage text NOT NULL,
    demographic text,
    remarks text
);


--
-- Name: initiatives_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.initiatives_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: initiatives_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.initiatives_id_seq OWNED BY public.initiatives.id;


--
-- Name: organisations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.organisations (
    id integer NOT NULL,
    name text NOT NULL,
    mission_and_focus text NOT NULL,
    about_us text NOT NULL,
    remarks text
);


--
-- Name: organisations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.organisations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: organisations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.organisations_id_seq OWNED BY public.organisations.id;


--
-- Name: results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.results (
    grant_id integer NOT NULL,
    initiative_id integer NOT NULL,
    prelim_rating integer NOT NULL,
    grant_description text,
    criteria text[],
    grant_amount text,
    match_rating integer,
    uncertainty_rating integer,
    deadline timestamp without time zone,
    sources text[],
    sponsor_name text,
    sponsor_description text,
    explanations json,
    CONSTRAINT check_match_rating CHECK (((match_rating >= 0) AND (match_rating <= 100))),
    CONSTRAINT check_prelim_rating CHECK (((prelim_rating >= 0) AND (prelim_rating <= 100))),
    CONSTRAINT check_uncertainty_rating CHECK (((uncertainty_rating >= 0) AND (uncertainty_rating <= 100)))
);


--
-- Name: grants id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grants ALTER COLUMN id SET DEFAULT nextval('public.grants_id_seq'::regclass);


--
-- Name: initiatives id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.initiatives ALTER COLUMN id SET DEFAULT nextval('public.initiatives_id_seq'::regclass);


--
-- Name: organisations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organisations ALTER COLUMN id SET DEFAULT nextval('public.organisations_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
220d0e6a4bc0
\.


--
-- Data for Name: grants; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.grants (id, name, url, details, button_text, card_body_text, card_body_html, links) FROM stdin;
\.


--
-- Data for Name: initiatives; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.initiatives (id, organisation_id, title, goals, audience, costs, stage, demographic, remarks) FROM stdin;
2	1	Hua Mei Training Academy	Capacity Building: To build and enhance the capacity of the community-based eldercare service sector.\n\nStandards Improvement: To raise industry standards and competencies through structured, competency-based training roadmaps.\n\nEmpowerment: To educate the public on optimizing the benefits of longevity and supporting the "ageing in place" philosophy.\n\nSocial Impact: To impact community change and foster age-friendly values and practices across society.	Eldercare Professionals: Healthcare practitioners and entry-level staff within the eldercare industry.\n\nFamily Caregivers & Volunteers: Individuals providing informal care to seniors.\n\nThe General Public: Specifically pre-retirees and seniors looking to manage their own longevity.\n\nCommercial & Community Partners: Corporate clients and special interest groups interested in age-friendly practices.	250000	NIL	\N	\N
4	1	ILC Singapore	Promote Wellbeing: To promote the wellbeing of older people and contribute to national development.\n\nResearch and Policy: To initiate research and forge collaborations that inform policy and facilitate policy-action translation.\n\nEffective Practice: To promote quality, effective practice in eldercare within Singapore and the region.\n\nLongevity Solutions: To help societies address longevity and population ageing through research and action as part of a global alliance.\n\nCommunity Innovation: To find innovative approaches to population ageing issues, such as financial security for women and self-care for elders.	Older Persons: Specifically elders in Singapore and the region who benefit from improved wellbeing and self-care programs.\n\nOlder Women: A specific focus group addressed through financial education programs due to their higher life expectancy and financial vulnerability.\n\nPolicy Makers & Public Service: Beneficiaries of evidence-based research and report briefings that influence national policy.\n\nEldercare Practitioners & Academia: Stakeholders who utilize the center's research and participate in conferences/roundtables to improve practice.\n\nThe Community & Enterprise: Local organizations and businesses that benefit from "joining the dots" between geriatric services and societal opportunities in longevity.	50000	NIL	\N	\N
5	1	Community for Successful Ageing (ComSA)	Integrated Care System: To forge a community-wide, integrated system of comprehensive programs and services that promotes health and wellbeing over the life course.\n\nAgeing in Place: To enable older persons to age in place by aligning medical care with psychological, emotional, and spiritual wellness.\n\nCombating "The Three Plagues": To address isolation, loneliness, and boredom—the three plagues that commonly beset older people—through social connectedness and meaningful engagement.\n\nOptimizing Longevity: To optimize opportunities in longevity and improve quality of life by recognizing the continuing potential of older persons rather than just their past contributions.\n\nCatalyzing Community Action: To catalyze community action and build an "elder-friendly neighbourhood" (specifically starting in Whampoa)	Older Persons (Seniors): Specifically those in the Whampoa catchment area (approx. 7,400 residents above 60), including those who are healthy, frail, or at "high risk" of isolation.\n\nThe "Sandwich" Generation & Caregivers: Families who need a supportive environment to help look after their ageing relatives.\n\nThe Local Community: Residents of all ages who benefit from an inclusive, intergenerational environment.\n\nPolicymakers & Urban Planners: ComSA aims to demonstrate a "replicable model" that pulls together urban planning and healthcare policy for national adoption.	4000000	NIL	\N	\N
6	1	Hua Mei Centre for Successful Ageing (HMCSA)	One-Stop Primary Healthcare: To operate as a "first-stop" primary healthcare provider delivering team-managed medical, social, and psycho-emotional care.\n\nHolistic Optimization: To enable individuals to optimize their health and wellbeing across the life course, rather than just treating acute illness.\n\nAgeing in Place: To support adults in ageing at home and in the community for as long as possible.\n\nSelf-Mastery: To encourage self-care and self-mastery by providing training and information at the client's own pace.\n\nCare Continuum: To engage clients in active health promotion and preventive healthcare through to disease management and end-of-life care.	Mature Adults (40+): Adults aged 40 years and above living in the community who want to manage their longevity early.\n\nSeniors with Complex Needs: Elders (typically 60+) with multiple chronic medical conditions or physical frailty who require integrated care.\n\nCaregivers: Family members who need support, guidance, and training to look after their ageing loved ones.\n\nHome-Bound Elders: Individuals who cannot leave their homes and require mobile clinic services.	300000	NIL	\N	\N
\.


--
-- Data for Name: organisations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.organisations (id, name, mission_and_focus, about_us, remarks) FROM stdin;
1	Tsao Foundation	Mission:\nTo advance a positive transformation of the ageing experience, we seek mindset and systemic change by implementing innovation in community-based eldercare, training and education, policy-relevant research, collaboration and advocacy\n\nVision:\nOur vision is of an inclusive society for all ages that optimises the opportunities in longevity and strengthens inter-generational solidarity.\n\n\nValues:\nOur approaches and programme models to improve the quality of life of older persons and enabling the dividends of longevity to reach all ages are guided by INNOVATION.\n\nIn the PURSUIT of EXCELLENCE, we place our programme innovations to the test and strive to maintain the highest service standards.\n\nAs a CATALYST for CONSTRUCTIVE CHANGE, we promote research on issues in ageing, build collaborative platforms for understanding and action and engage in advocacy.	Longevity, so hard won, is not all about cost, burden and problem. An Institution of Public Character (IPC), the Tsao Foundation is dedicated to transforming the experience of longevity for it to be an actualisation of our full potential for growth, health and fulfillment in a society for all ages.\n\nEstablished in 1993 as a non-profit family foundation, our efforts have first focused on promoting successful ageing, and active ageing framed by the World Health Organization.  \n\nTowards that end, for more than two decades, Tsao Foundation has pioneered approaches to ageing and eldercare across a range of disciplines to empower mature adults to master their own ageing journey over their life course in terms of self-care, growth and development.\n\nThe Tsao Foundation is a non-profit organization dedicated to improving the quality of life of older persons in an inclusive society that can embrace both the challenges and opportunities of population ageing. Our community-based programmes and services give older people access to quality integrated medical and pycho-social care in their homes and communities. Our scholarly research as well as dialogue and collaboration with community, academia and public service agencies address critical population ageing issues at both national and policy levels; and our professional and community training and education programmes empower eldercare colleagues, older persons, caregivers and the public with practical help and knowledge.\n\nWe have a strong belief that older people - regardless of their conditions- are capable of leading a full life provided that they have access to sufficient care and support, and are given opportunities to participate in mainstream society.\n\nWe began our work in 1993 and since then have developed innovative and duplicable care models for community-based aged care services. We are among the earliest champion for ageing in place - a long term eldercare proposition for optimal well-being and resource utilization in the community. 	Below are some of our major achievements for the past 19 years:\n\n1\nIn 1993, we launched Singapore’s first team-managed primary healthcare care service for home-bound and at risk elders – the Hua Mei Mobile Clinic. It now includes an end-of-life care practice.\n \t \n2\nIn 1995, we set up a training centre dedicated to raising professional skills in community aged care, and empowering older people, caregivers and volunteers with essential information and skills. We were the first to develop eldercare training courses. In 2008, this training centre was transformed into Hua Mei Training Academy with a CET accreditation from WDA.\n \t \n3\nIn 1995, we initiated an Experts’ Series programme, the first platform for bringing together international experts and distinguished scholars on policy issues related to ageing in Singapore. Some of the distinguished scholars we have invited include Dr. Robert N. Butler (US), Dr. James Birren (US), Her Baroness Sally Greengross (UK), to name a few.\n \t \n4\nIn 1996, we set up the Hua Mei Acupuncture and TCM Centre, which offers Traditional Chinese Medicine (TCM) treatment of acute and chronic conditions that adheres to World Health Organization (WHO) standards.\n \t \n5\nIn 1996, we opened the Hua Mei Seniors’ Clinic, which was a WHO pilot site for developing an aged-friendly primary healthcare clinic, and which provides health management over the life course for adults aged 40 and above.\n \t \n6\nIn 1998, we started the Hua Mei Care Management Service, a pilot project in Singapore uniquely employing a team of nursing and social work-trained case managers to set up care systems for frail and at-risk older persons.\n \t \n7\nIn 2006, we established in cooperation with the Singapore Council of Women’s Organization (SCWO) the first drop in centre for older women, called WINGS or Women’s Initiative for Ageing Successfully.\n \t \n8\nIn 2009, we formally launched the Hua Mei Centre for Successful Ageing (HMCSA), which is an integrated collective of the various community aged care service models that we have pioneered since 1993.\n \t \n9\nIn 2009, we started the Coaching & Counseling programme targeting older persons who are depressed and caregivers who are stressed and need emotional support.\n \t \n10\nIn 2009, we established the Tsao Foundation Ageing Research Initiative in collaboration with the Faculty of Arts and Social Sciences at NUS to spearhead our foray into research on ageing.\n \t \n11\nIn 2010, we played an instrumental role in the development of a medical record system for community health services (IngoT).\n \t \n12\nIn 2011, we launched the International Longevity Centre Singapore, which grew from the Foundation’s Interagency Collaboration Division and seeks to expand its predecessor’s work in policy support through undertaking research and stakeholder platforms.\n \t \n13\nIn the same year, we launched SCOPE or the Self Care on Health of Older People in Singapore, which seeks to increase the understanding and ability of mildly disabled and healthy older persons to care for themselves. Its effectiveness is the subject of a randomized control trial.\n \t \n14\nIn 2011, WECARE (Working to enhance the care and resilience of elders) was launched to demonstrate (through a randomized control trial) that with appropriate intervention and support, elders at risk can optimize their functional and cognitive potential to remain independent and age well in the community.\n \t \n15\nIn 2011, we launched EPICC - a team-managed, centre-based integrated healthcare service for frail and at-risk elders, giving them an alternative option to nursing home care. Modelled on the American PACE, it is a 36-month demonstration project with a randomized control trail to test its effectiveness in achieving a set of health and social-psycho outcomes.
\.


--
-- Data for Name: results; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.results (grant_id, initiative_id, prelim_rating, grant_description, criteria, grant_amount, match_rating, uncertainty_rating, deadline, sources, sponsor_name, sponsor_description, explanations) FROM stdin;
\.


--
-- Name: grants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.grants_id_seq', 1, false);


--
-- Name: initiatives_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.initiatives_id_seq', 1, false);


--
-- Name: organisations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.organisations_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: grants grants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grants
    ADD CONSTRAINT grants_pkey PRIMARY KEY (id);


--
-- Name: initiatives initiatives_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.initiatives
    ADD CONSTRAINT initiatives_pkey PRIMARY KEY (id);


--
-- Name: organisations organisations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organisations
    ADD CONSTRAINT organisations_pkey PRIMARY KEY (id);


--
-- Name: results results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_pkey PRIMARY KEY (grant_id, initiative_id);


--
-- Name: initiatives initiatives_organisation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.initiatives
    ADD CONSTRAINT initiatives_organisation_id_fkey FOREIGN KEY (organisation_id) REFERENCES public.organisations(id);


--
-- Name: results results_grant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_grant_id_fkey FOREIGN KEY (grant_id) REFERENCES public.grants(id);


--
-- Name: results results_initiative_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_initiative_id_fkey FOREIGN KEY (initiative_id) REFERENCES public.initiatives(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 4wTBkMjp2lRTPFIWoBEu9w6GOah4jjplPdPxUeRQ9ZwJisOpctC8udDhssPCijt

