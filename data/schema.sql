-- Health Dashboard Schema
-- Supports multiple users (person_id = 'AK' | 'RK')

CREATE TABLE IF NOT EXISTS reports (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id   TEXT    NOT NULL,          -- 'AK' or 'RK'
    report_date TEXT    NOT NULL,          -- ISO date: YYYY-MM-DD
    lab_name    TEXT,
    report_type TEXT,                      -- 'CBC', 'MetabolicPanel', 'LipidPanel', etc.
    source_file TEXT    UNIQUE NOT NULL,   -- renamed filename, dedup key
    ingested_at TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS biomarkers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id    INTEGER NOT NULL REFERENCES reports(id),
    name         TEXT    NOT NULL,         -- canonical name e.g. 'Hemoglobin'
    value        REAL,                     -- numeric value (null if qualitative)
    text_value   TEXT,                     -- qualitative result e.g. 'Positive', 'O+', 'Trace'
    unit         TEXT,                     -- canonical unit e.g. 'g/dL'
    ref_low      REAL,
    ref_high     REAL,
    flag         TEXT                      -- 'H', 'L', 'HH', 'LL', or NULL
);

CREATE TABLE IF NOT EXISTS vitals (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id    INTEGER NOT NULL REFERENCES reports(id),
    weight_lbs   REAL,
    height_in    REAL,
    bmi          REAL,
    bp_systolic  INTEGER,
    bp_diastolic INTEGER,
    pulse        INTEGER,
    temperature  REAL      -- °F
);

CREATE INDEX IF NOT EXISTS idx_biomarkers_name      ON biomarkers(name);
CREATE INDEX IF NOT EXISTS idx_biomarkers_report_id ON biomarkers(report_id);
CREATE INDEX IF NOT EXISTS idx_reports_person_date  ON reports(person_id, report_date);
