UPDATE artist_artist aa 
SET avatar = %(avatar)s
WHERE aa.id = %(artist_id)s;