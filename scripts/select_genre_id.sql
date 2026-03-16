SELECT id, name, description
FROM public.genre_genre
WHERE name = %s
ORDER BY id ASC
LIMIT 1;