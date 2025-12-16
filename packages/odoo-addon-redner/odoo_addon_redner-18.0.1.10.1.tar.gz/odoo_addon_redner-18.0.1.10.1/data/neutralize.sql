-- remove redner configuration
UPDATE ir_config_parameter
    SET value = ''
    WHERE key IN ('redner.account', 'redner.api_key', 'redner.server_url');