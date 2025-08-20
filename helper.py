import os
import time
import subprocess
import json
import torch

VIDEO_DIR = "videos"
CACHE_FILE = "cache.json"
GPU_H265_ENCODER_MAP = {
	"NVIDIA": "hevc_nvenc",
	"AMD Radeon": "hevc_amf",
	"Intel": "hevc_qsv",
	"default": "libx265"
}

if os.path.exists(CACHE_FILE):
	with open(CACHE_FILE, 'r') as f:
		compressed_cache = json.load(f)
else:
	compressed_cache = {}
is_gpu_accelerated = True
compression_quality = 65
is_overwrite = True
h265_encoder = "libx265"

def detect_h265_encoder():
	if not torch.cuda.is_available() or not is_gpu_accelerated:
		return GPU_H265_ENCODER_MAP["default"]

	gpu_name = torch.cuda.get_device_name().strip()

	for name, encoder in GPU_H265_ENCODER_MAP.items():
		if name in gpu_name:
			return encoder

	return GPU_H265_ENCODER_MAP["default"]

def get_video_info(path):
	cmd = [
		"ffprobe", "-v", "error",
		"-select_streams", "v:0",
		"-show_entries", "format=duration:stream=nb_frames,r_frame_rate",
		"-of", "json", path
	]
	result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	info = json.loads(result.stdout)
	duration = float(info["format"]["duration"])
	size = os.path.getsize(path)
	thumbnail = generate_thumbnail(path)
	return {
		"filename": os.path.basename(path),
		"duration": f"{int(duration // 60)}:{int(duration % 60):02}",
		"size": size,
		"thumbnail": thumbnail
	}

def generate_thumbnail(path):
	thumb_name = os.path.basename(path) + ".jpg"
	thumb_path = os.path.join("static", "thumbnails", thumb_name)
	if not os.path.exists(thumb_path):
		subprocess.run([
			"ffmpeg", "-i", path,
			"-vf", "thumbnail,scale=320:-1",
			"-frames:v", "1", thumb_path, "-y"
		])
	return thumb_path

def save_cache(compressed_cache):
	with open(CACHE_FILE, "w") as f:
		json.dump(compressed_cache, f, indent=4)

def compress_video(path):
	global compressed_cache
	output_path = os.path.splitext(path)[0] + "_compressed.mp4"
	cmd = []
	if h265_encoder == "libx265":
		cmd = [
			"ffmpeg", "-i", path,
			"-c:a", "copy",
			"-c:v", h265_encoder,
			"-preset", "fast",
			"-crf", str(int(51 * (compression_quality / 100))),
			output_path, "-y"
		]
	else:
		cmd = [
			"ffmpeg", "-i", path,
			"-c:a", "copy",
			"-c:v", h265_encoder,
			"-preset", "p1",
			"-cq", str(int(63 * (compression_quality / 100))),
			output_path, "-y"
		]
	try:
		start_time = time.time()
		subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		elapsed_time = time.time() - start_time
		compression_percent = (os.path.getsize(path) - os.path.getsize(output_path)) / os.path.getsize(path) * 100
		compressed_cache[os.path.relpath(path, VIDEO_DIR)] = {
			"compressed": True,
			"compression_percent": compression_percent,
			"compression_time": elapsed_time
		}
		save_cache(compressed_cache)
		if is_overwrite:
			os.replace(output_path, path)
		return True
	except Exception as e:
		print(f"Compression failed for {path}: {e}")
		return False