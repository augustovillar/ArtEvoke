/* Charset/engine padrão */

/*  ===================== */
/*  Tabela: Patient */
/*  ===================== */
CREATE TABLE IF NOT EXISTS Patient (
    id                CHAR(36)      NOT NULL,
    email             VARCHAR(100)  NOT NULL,
    password          VARCHAR(255)  NULL,
    name              VARCHAR(100) NOT NULL,
    date_of_birth     DATE NULL,
    education_level   VARCHAR(50) NULL,
    occupation        VARCHAR(100) NULL,
    diseases          TEXT,
    medications       TEXT,
    visual_impairment BOOLEAN       NOT NULL DEFAULT FALSE,
    hearing_impairment BOOLEAN      NOT NULL DEFAULT FALSE,
    household_income  DECIMAL(10,2)          CHECK (household_income IS NULL OR household_income >= 0),
    ethnicity         VARCHAR(50),
    status            ENUM('pending','active') NOT NULL DEFAULT 'pending',
    code              CHAR(4)       NULL,
    created_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_patient PRIMARY KEY (id),
    CONSTRAINT uq_patient_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*  ===================== */
/*  Tabela: Doctor */
/*  ===================== */
CREATE TABLE IF NOT EXISTS Doctor (
    id               CHAR(36)      NOT NULL,
    email            VARCHAR(100)  NOT NULL,
    password         VARCHAR(255)  NOT NULL,
    name             VARCHAR(100) NOT NULL,
    date_of_birth    DATE NOT NULL,
    specialization   VARCHAR(100) NOT NULL,
    created_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_doctor PRIMARY KEY (id),
    CONSTRAINT uq_doctor_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*  ========================================= */
/*  Tabela de junção: PatientDoctor (N:N) */
/*  ========================================= */
CREATE TABLE IF NOT EXISTS PatientDoctor (
    patient_id  CHAR(36)    NOT NULL,
    doctor_id   CHAR(36)    NOT NULL,
    started_at  DATE,
    ended_at    DATE,
    created_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_patient_doctor PRIMARY KEY (patient_id, doctor_id),
    CONSTRAINT fk_pd_patient
        FOREIGN KEY (patient_id) REFERENCES Patient (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_pd_doctor
        FOREIGN KEY (doctor_id)  REFERENCES Doctor  (id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS SemArt (
    id                      CHAR(36)   NOT NULL,
    image_file              CHAR(36),
    description             TEXT,
    artist_name             VARCHAR(100),
    title                   VARCHAR(255),
    technique               VARCHAR(100),
    date                    VARCHAR(50),
    type                    VARCHAR(50),
    art_school              VARCHAR(50),
    description_generated   TEXT,
    CONSTRAINT pk_semart PRIMARY KEY (id),
    KEY idx_semart_artist_name (artist_name),
    KEY idx_semart_type (type),
    KEY idx_semart_art_school (art_school)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



CREATE TABLE IF NOT EXISTS Ipiranga (
    id                      CHAR(36)    NOT NULL,
    external_id             CHAR(36),
    image_file              VARCHAR(200),
    inventory_code          VARCHAR(20),
    title                   VARCHAR(500),
    description             TEXT,
    type                    VARCHAR(50),
    artist_name             VARCHAR(100),
    location                VARCHAR(50),
    date                    VARCHAR(50),
    period                  VARCHAR(20),
    technique               VARCHAR(100),
    height                  VARCHAR(8),
    width                   VARCHAR(8),
    color                   VARCHAR(20),
    history                 TEXT,
    collection_alt_name     TEXT,
    description_generated   TEXT,
    CONSTRAINT pk_ipiranga PRIMARY KEY (id),
    KEY idx_ipiranga_type (type),
    KEY idx_ipiranga_inventory_code (inventory_code),
    KEY idx_ipiranga_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS WikiArt (
    id                      CHAR(36)    NOT NULL,
    image_file              VARCHAR(160),
    artist_name             VARCHAR(100),
    type                    VARCHAR(100),
    description             TEXT,
    width                   VARCHAR(8),
    height                  VARCHAR(8),
    description_generated   TEXT,
    CONSTRAINT pk_wikiart PRIMARY KEY (id),
    KEY idx_wikiart_artist_name (artist_name),
    KEY idx_wikiart_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS CatalogItem (
  id           CHAR(36) NOT NULL,
  ipiranga_id  CHAR(36) NULL,
  wikiart_id   CHAR(36) NULL,
  semart_id    CHAR(36) NULL,

  /* armazenado diretamente (e indexável sem stress) */
  source ENUM('ipiranga','wikiart','semart') NOT NULL,

  CONSTRAINT pk_catalogitem PRIMARY KEY (id),
  CONSTRAINT fk_ci_ipiranga FOREIGN KEY (ipiranga_id) REFERENCES Ipiranga(id) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_ci_wikiart FOREIGN KEY (wikiart_id) REFERENCES WikiArt(id)  ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_ci_semart FOREIGN KEY (semart_id) REFERENCES SemArt(id)   ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


/*  ====================================================== */
/*  Art Exploration */
/*  ====================================================== */
CREATE TABLE IF NOT EXISTS ArtExploration (
  id              CHAR(36)    NOT NULL,
  patient_id      CHAR(36)    NOT NULL,
  story_generated TEXT        NOT NULL,
  dataset         ENUM('ipiranga', 'wikiart','semart') NOT NULL,
  language        ENUM('en','pt') NOT NULL,
  correct_option_0 CHAR(100)  NULL,
  correct_option_1 CHAR(100)  NULL,
  correct_option_2 CHAR(100)  NULL,
  correct_option_3 CHAR(100)  NULL,
  created_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_art_exploration PRIMARY KEY (id),
  CONSTRAINT fk_artexp_patient FOREIGN KEY (patient_id) REFERENCES Patient(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  INDEX idx_artexp_patient (patient_id),
  INDEX idx_artexp_dataset (dataset),
  INDEX idx_artexp_language (language)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*  Lista ordenada de imagens (obras) ligadas a um ArtExploration */
/*  image_id: ID da obra na sua tabela/serviço de catálogo (quando existir, pode virar FK) */
CREATE TABLE IF NOT EXISTS Images (
    id                 CHAR(36)   NOT NULL,
    art_exploration_id CHAR(36)   NOT NULL,
    catalog_id         CHAR(36)   NOT NULL,
    display_order      TINYINT NOT NULL,
    CONSTRAINT pk_images PRIMARY KEY (id),
    CONSTRAINT fk_images_artexp FOREIGN KEY (art_exploration_id) REFERENCES ArtExploration(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_images_catalog FOREIGN KEY (catalog_id) REFERENCES CatalogItem(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*  ====================================================== */
/*  3) Memory Reconstruction */
/*  ====================================================== */
CREATE TABLE IF NOT EXISTS MemoryReconstruction (
    id                    CHAR(36)   NOT NULL,
    patient_id            CHAR(36)   NOT NULL,
    story                 TEXT NOT NULL,
    dataset               ENUM('ipiranga', 'wikiart', 'semart') NOT NULL,   
    language              ENUM('en','pt') NOT NULL,
    segmentation_strategy ENUM('conservative','broader') NOT NULL,
    created_at            TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_memrec PRIMARY KEY (id),
    CONSTRAINT fk_memrec_patient FOREIGN KEY (patient_id) REFERENCES Patient(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*  Seções da história com até 6 imagens + favorita */
/*  image*_id/fav_image_id: IDs de obras no seu catálogo (podem virar FKs futuramente) */
CREATE TABLE IF NOT EXISTS Sections (
  id                       CHAR(36)  NOT NULL,
  memory_reconstruction_id CHAR(36)  NOT NULL,
  section_content          TEXT      NOT NULL,
  display_order            TINYINT   NOT NULL,
  image1_id                CHAR(36)  NOT NULL,
  image2_id                CHAR(36)  NOT NULL,
  image3_id                CHAR(36)  NOT NULL,
  image4_id                CHAR(36)  NOT NULL,
  image5_id                CHAR(36)  NOT NULL,
  image6_id                CHAR(36)  NOT NULL,
  fav_image_id             CHAR(36)  NULL,
  CONSTRAINT pk_sections PRIMARY KEY (id),
  KEY idx_sections_memrec (memory_reconstruction_id),
  UNIQUE KEY uq_sections_memrec_order (memory_reconstruction_id, display_order),
  CONSTRAINT fk_sections_memrec FOREIGN KEY (memory_reconstruction_id) REFERENCES MemoryReconstruction(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_sections_image1 FOREIGN KEY (image1_id) REFERENCES CatalogItem(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_sections_image2 FOREIGN KEY (image2_id) REFERENCES CatalogItem(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_sections_image3 FOREIGN KEY (image3_id) REFERENCES CatalogItem(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_sections_image4 FOREIGN KEY (image4_id) REFERENCES CatalogItem(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_sections_image5 FOREIGN KEY (image5_id) REFERENCES CatalogItem(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_sections_image6 FOREIGN KEY (image6_id) REFERENCES CatalogItem(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_sections_imagefav FOREIGN KEY (fav_image_id) REFERENCES CatalogItem(id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


/*  ===================== */
/*  Tabela: Session */
/*  ===================== */
CREATE TABLE IF NOT EXISTS `Session` (
  id                        CHAR(36)  NOT NULL,
  patient_id                CHAR(36)  NOT NULL,
  doctor_id                 CHAR(36)  NOT NULL,
  memory_reconstruction_id  CHAR(36)  NULL,  -- ID created when activity is saved
  art_exploration_id        CHAR(36)  NULL,  -- ID created when activity is saved
  mode ENUM('art_exploration','memory_reconstruction') NOT NULL,
  interruption_time         SMALLINT  NOT NULL DEFAULT 10 CHECK (interruption_time BETWEEN 1 AND 300),
  status ENUM('pending','in_progress','in_evaluation','completed') NOT NULL DEFAULT 'pending',
  started_at DATE NULL,
  ended_at   DATE NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_session PRIMARY KEY (id),
  KEY idx_session_patient (patient_id),
  KEY idx_session_doctor (doctor_id),
  KEY idx_session_mr (memory_reconstruction_id),
  KEY idx_session_ae (art_exploration_id),
  KEY idx_session_mode (mode),
  CONSTRAINT fk_session_patient FOREIGN KEY (patient_id) REFERENCES Patient(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_session_doctor FOREIGN KEY (doctor_id)  REFERENCES Doctor(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;






/*  ====================== */
/*  PreEvaluation */
/*  ====================== */
CREATE TABLE IF NOT EXISTS PreEvaluation (
  id                     CHAR(36)    NOT NULL,
  session_id             CHAR(36)    NOT NULL,
  meds_changes           VARCHAR(100) NULL,     
  alone                  BOOLEAN      NULL,   
  any_recent_conditions  VARCHAR(100) NULL,   
  created_at             TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_pre_evaluation PRIMARY KEY (id),
  CONSTRAINT uq_pre_session UNIQUE (session_id),
  CONSTRAINT fk_pre_session
    FOREIGN KEY (session_id) REFERENCES Session(id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*  ====================== */
/*  PosEvaluation */
CREATE TABLE IF NOT EXISTS PosEvaluation (
  id          CHAR(36)  NOT NULL,
  session_id  CHAR(36)  NOT NULL,
  experience  SMALLINT  NULL CHECK (experience BETWEEN 0 AND 10),
  difficulty  SMALLINT  NULL CHECK (difficulty BETWEEN 0 AND 10),
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_pos_evaluation PRIMARY KEY (id),
  CONSTRAINT uq_pos_session UNIQUE (session_id),
  CONSTRAINT fk_pos_session
    FOREIGN KEY (session_id) REFERENCES Session(id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


/*  ====================================================== */
/*  Evaluation Questions */
/*  ====================================================== */

/*  ====================== */
/*  Evaluation */
/*  ====================== */
CREATE TABLE IF NOT EXISTS Evaluation (
  id          CHAR(36)  NOT NULL,
  session_id  CHAR(36)  NOT NULL,
  mode        ENUM('art_exploration','memory_reconstruction') NOT NULL,
  current_step SMALLINT NOT NULL DEFAULT 0,
  number_steps SMALLINT NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_evaluation PRIMARY KEY (id),
  CONSTRAINT fk_eval_session
    FOREIGN KEY (session_id) REFERENCES Session(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_eval_session (session_id),
  INDEX idx_eval_mode (mode),
  INDEX idx_current_step (current_step)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


/*  ====================== */
/*  SelectImageQuestion */
/*  ====================== */
CREATE TABLE IF NOT EXISTS SelectImageQuestion (
  id                   CHAR(36)  NOT NULL,
  eval_id              CHAR(36)  NOT NULL,
  elapsed_time         TIME      NULL,
  image_selected_id    CHAR(36)  NULL,
  section_id           CHAR(36)  NULL,
  image_distractor_0_id CHAR(36) NULL,
  image_distractor_1_id CHAR(36) NULL,
  created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_select_image_question PRIMARY KEY (id),
  CONSTRAINT fk_siq_eval
    FOREIGN KEY (eval_id) REFERENCES Evaluation(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_siq_section
    FOREIGN KEY (section_id) REFERENCES Sections(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_siq_selected
    FOREIGN KEY (image_selected_id) REFERENCES CatalogItem(id)
      ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_siq_distractor0
    FOREIGN KEY (image_distractor_0_id) REFERENCES CatalogItem(id)
      ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_siq_distractor1
    FOREIGN KEY (image_distractor_1_id) REFERENCES CatalogItem(id)
      ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX idx_siq_eval (eval_id),
  INDEX idx_siq_section (section_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*  ====================== */
/*  StoryOpenQuestion */
/*  ====================== */
CREATE TABLE IF NOT EXISTS StoryOpenQuestion (
  id           CHAR(36)  NOT NULL,
  eval_id      CHAR(36)  NOT NULL,
  elapsed_time TIME      NULL,
  text         TEXT      NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_story_open_question PRIMARY KEY (id),
  CONSTRAINT fk_soq_eval
    FOREIGN KEY (eval_id) REFERENCES Evaluation(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_soq_eval (eval_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*  ====================== */
/*  ChronologicalOrderQuestion */
/*  ====================== */
CREATE TABLE IF NOT EXISTS ChronologicalOrderQuestion (
  id                CHAR(36)     NOT NULL,
  eval_id           CHAR(36)     NOT NULL,
  elapsed_time      TIME         NULL,
  selected_option_0 VARCHAR(100)    NULL,
  selected_option_1 VARCHAR(100)    NULL,
  selected_option_2 VARCHAR(100)    NULL,
  selected_option_3 VARCHAR(100)    NULL,
  created_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_chronological_order_question PRIMARY KEY (id),
  CONSTRAINT fk_coq_eval
    FOREIGN KEY (eval_id) REFERENCES Evaluation(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_coq_eval (eval_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*  ====================== */
/*  ObjectiveQuestion */
/*  ====================== */
CREATE TABLE IF NOT EXISTS ObjectiveQuestion (
  id              CHAR(36)  NOT NULL,
  eval_id         CHAR(36)  NOT NULL,
  elapsed_time    TIME      NULL,
  type            ENUM('period','environment', 'emotion') NOT NULL,
  option_0        CHAR(100) NULL,
  option_1        CHAR(100) NULL,
  option_2        CHAR(100) NULL,
  option_3        CHAR(100) NULL,
  option_4        CHAR(100) NULL,
  selected_option CHAR(100) NULL,
  correct_option  CHAR(100) NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_objective_question PRIMARY KEY (id),
  CONSTRAINT fk_oq_eval
    FOREIGN KEY (eval_id) REFERENCES Evaluation(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_oq_eval (eval_id),
  INDEX idx_oq_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;