-- Script de correction pour la base de données YakTaa

-- Renommer la colonne 'id' en 'shop_id'
ALTER TABLE shops RENAME COLUMN id TO shop_id;

