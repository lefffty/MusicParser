SELECT id, name, duration
FROM public.song_song
WHERE name = %s
ORDER BY id ASC
LIMIT 1;