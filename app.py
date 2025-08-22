import os
import time
import argparse
from flask import Flask, render_template, request, jsonify
import helper
from helper import VIDEO_DIR

app = Flask(__name__)

VID_FILETYPES = (".mp4", ".mkv", ".avi", ".mov", ".webm", "vob", "wmv", "flv", "mpg")

recursive = False
videos = []
progress = 0
rate = 0
start_time = 0

@app.route("/set_recursive", methods=["POST"])
def set_recursive():
	global recursive
	data = request.get_json()
	recursive = data.get("recursive", False)
	return jsonify(status="done")

@app.route('/')
def index():
	global videos
	videos = []
	total_size = 0

	for root, dirs, files in os.walk(VIDEO_DIR):
		for file in files:
			if file.lower().endswith(VID_FILETYPES):
				path = os.path.join(root, file)
				rel_path = os.path.relpath(path, VIDEO_DIR)
				info = helper.get_video_info(path)
				if info:
					info["rel_path"] = rel_path
					info["compressed"] = helper.compressed_cache.get(rel_path, False)
					videos.append(info)
					total_size += info["size"]
		if not recursive:
			break

	return render_template("index.html", videos=videos, total_size=total_size)

@app.route("/compress", methods=["POST"])
def compress():
	global progress
	global rate
	global start_time

	start_time = time.time()

	for video in videos:
		rel_path = video["rel_path"]
		if video["compressed"]:
			continue
		helper.compress_video(os.path.join(VIDEO_DIR, rel_path))
		progress = len(helper.compressed_cache) / len(videos)

	return jsonify(status="done")

@app.route("/get_progress", methods=["GET"])
def get_progress():
	global rate
	global start_time

	if not helper.compressed_cache:
		video = videos[0]["rel_path"]
		rel_path = video.split('.')[0] + "_compressed." + video.split('.')[-1]
		size = os.path.getsize(os.path.join(VIDEO_DIR, rel_path)) // (1024 * 1024)
		elapsed_time = time.time() - start_time
		rate = size / elapsed_time if elapsed_time > 0 else 0
	else:
		last_video = list(helper.compressed_cache.keys())[-1]
		rate = os.path.getsize(os.path.join(VIDEO_DIR, last_video)) // (1024 * 1024) / helper.compressed_cache[last_video]["compression_time"]
	return jsonify(progress=progress, rate=rate, video_amt=len(videos))

if __name__ == "__main__":
	# Get arguments
	parser = argparse.ArgumentParser(description="Video Compression Tool")
	parser.add_argument("--no-gpu", action="store_true", help="Don't use GPU for compression")
	parser.add_argument("--cq", type=int, default=helper.compression_quality, help="Compression quality (0-100)")
	parser.add_argument("--no-overwrite", action="store_true", help="Don't overwrite original files with compressed files")
	args = parser.parse_args()
	if args.cq < 0 or args.cq > 100:
		raise ValueError("Compression quality must be between 0 and 100")
	helper.is_gpu_accelerated = not args.no_gpu
	helper.compression_quality = args.cq
	helper.is_overwrite = not args.no_overwrite
	helper.h265_encoder = helper.detect_h265_encoder()

	# Clear out /static/thumbnails
	if os.path.exists("static/thumbnails") and len(os.listdir("static/thumbnails")) == len(helper.compressed_cache):
		for file in os.listdir("static/thumbnails"):
			os.remove(os.path.join("static/thumbnails", file))
	else:
		os.makedirs("static/thumbnails")

	# Create /videos directory if it doesn't exist
	if not os.path.exists(VIDEO_DIR):
		os.makedirs(VIDEO_DIR)

	# Run Flask app
	app.run(debug=True)