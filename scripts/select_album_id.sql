SELECT id, name, publication_date, cover
FROM public.albums_album
WHERE name = %s
ORDER BY id ASC
LIMIT 1;