<p align="center">
	<img src="./asset/logo.png" alt="Web Video Compress logo" width="200" height="200">
</p>

<h1 align="center">Web Video Compress</h1>

<p align="center">
	<strong>Compress videos with a web UI!</strong>
</p>

## 🚀 Overview

Welcome to **Web Video Compress**! This program allows you to compress videos using a simple web interface. It is designed to be user-friendly and efficient, making it easy for anyone to compress their videos without any technical knowledge.

## 🎨 Features

- **Dark Theme**: The program features a sleek dark theme that is easy on the eyes and provides a modern look.
- **Video Grid**: The program displays a grid of videos, allowing users to easily view all of the videos they have uploaded.
- **Cache**: The program caches the videos' metadata, so users can quickly resume compression where they left off.

## 🛠️ Installation

To get started with the program, follow the steps below:

1. **Clone the Repository**
```sh
git clone https://github.com/321BadgerCode/web_video_compress.git
cd ./web_video_compress/
```

<details>

<summary>📦 Dependencies</summary>

- **FFMpeg**: The program requires FFmpeg to be installed on your system. You can download it from the [FFmpeg website](https://www.ffmpeg.org/download.html).

</details>

## 📈 Usage

To use the program, there is only **one** step!

1. **Run the program**
```sh
python ./app.py
```

<details>

<summary>💻 Command Line Arguments</summary>

**Command Line Arguments**:
|	**Argument**		|	**Description**			|	**Default**	|
|	:---:			|	:---:				|	:---:		|
|	`-h & --help`		|	Help menu			|			|
|	`--no-gpu`		|	Disable GPU acceleration	|	False		|
|	`--cq`			|	Set the compression quality	|	65		|
|	`--no-overwrite`	|	Disable overwriting files	|	False		|

</details>

## 📜 License

[LICENSE](./LICENSE)