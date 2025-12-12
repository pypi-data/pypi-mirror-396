ALTER TABLE {schema}.{prefix}route ADD COLUMN weight INTEGER DEFAULT 10000;

COMMENT ON COLUMN {schema}.{prefix}route.weight IS 'How many active jobs can run on route';
