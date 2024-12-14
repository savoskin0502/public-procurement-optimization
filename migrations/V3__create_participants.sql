CREATE TABLE public.gz_participant (
    participant_id BIGINT PRIMARY KEY
    , bin VARCHAR(12)
    , iin VARCHAR(12)
    , registration_date TIMESTAMP
    , creation_date INT
    , website TEXT
    , country_name TEXT
    , kato_list TEXT
    , is_quazi INT
    , is_customer INT
    , is_organizer INT
    , is_national_company INT
    , ref_kopf_code TEXT
    , is_association_with_disabilities INT
    , registration_year INT
    , is_resident INT
    , is_supplier INT
    , supplier_type TEXT
    , krp_code TEXT
    , branches TEXT
    , parent_company TEXT
    , oked_list TEXT
    , kse_code TEXT
    , is_world_company INT
    , is_state_monopoly INT
    , is_natural_monopoly INT
    , is_patronymic_producer INT
    , is_patronymic_supplier INT
    , is_small_employer INT
    , is_single_org INT
);

CREATE INDEX idx_participant_id ON gz_participant(participant_id);
