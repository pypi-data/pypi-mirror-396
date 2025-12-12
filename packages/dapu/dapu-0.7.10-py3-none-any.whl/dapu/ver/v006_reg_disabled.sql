UPDATE {schema}.{prefix}registry SET disabled = '' WHERE 1=1;

ALTER TABLE {schema}.{prefix}registry 
    ALTER COLUMN disabled SET DEFAULT '' 
    , ALTER COLUMN disabled SET NOT NULL ;

