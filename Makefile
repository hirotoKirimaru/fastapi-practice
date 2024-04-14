server:
	rye run uvicorn src.main:app --host 0.0.0.0 --reload

production:
	rye run gunicorn src.main:app --workers 4

#worker:
#	rye run
