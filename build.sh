(
	python breeder/gen.py ;
	python logo/gen.py
	) | ffmpeg -r $(json fps <params.json) -loglevel quiet \
		-s $(json width <params.json | tr '\n' x ; json height <params.json) \
		-f rawvideo -pixel_format rgb24 -i - -an -vcodec libx264 -y /tmp/concat.mkv
