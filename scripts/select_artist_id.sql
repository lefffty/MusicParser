SELECT id, username, description, avatar
FROM public.artist_artist
WHERE username = %s
ORDER BY id ASC
LIMIT 1;