# ==================================================================== #
# File name: video.py
# Author: Long H. Pham and Duong N.-N. Tran
# Date created: 03/28/2021
#
# Video IO operations.
# ==================================================================== #
import os
from typing import Optional
from typing import Tuple

import cv2
import numpy as np

from tss.ops import image_channel_last
from tss.ops import resize_image_cv2
from tss.utils import data_dir
from tss.utils import is_video_file
from tss.utils import is_video_stream
from tss.utils import printe


# MARK: - VideoReader

class VideoReader(object):
	"""Video Reader.
	
	Attributes:
		dataset (string, optional):
			The name of the dataset to work on.
		file (string, optional):
			The video file or image folder. By default, assume all video are put inside ``aicity2021/video/``.
		stream (string, optional):
			If we run directly with the input stream, ``stream`` must be of some value.
			By default ``null`` means run with video file defined in ``path``.
		dims (tuple):
			Input size as [C, H, W]. This is also used to reshape the input.
		frame_rate (int):
			The frame rate of the video.
		batch_size (int, Optional):
			Number of samples in one forward & backward pass.
		cap (VideoCapture):
			The VideoCapture object from OpenCV.
		num_frames (int):
			Total number of frames in the video.
		frame_idx (int):
			The current frame index.
	"""
	
	# MARK: Magic Functions
	
	def __init__(
		self,
		dataset   : Optional[str] = None,
		file      : Optional[str] = None,
		stream    : Optional[str] = None,
		dims      : Tuple[int, int, int] = (3, 1920, 1080),
		frame_rate: float         = 10,
		batch_size: Optional[int] = 1,
		**kwargs
	):
		super().__init__(**kwargs)
		self.dataset    = dataset
		self.file       = file
		self.stream     = stream
		self.dims       = dims
		self.frame_rate = frame_rate
		self.batch_size = batch_size
		self.cap        = None
		self.num_frames = -1
		self.frame_idx  = 0
		
		# TODO: Setup stream
		if self.stream:
			self.create_online_stream()
		elif self.file:
			self.create_video_stream()
		
		if self.cap is None:
			printe("Error when reading input stream or video file")
			raise IOError
	
	def __len__(self):
		""" Get the len of video.
		
		Returns:
			(int):
				>0 if the offline video
				-1 if the online video
		"""
		return self.num_frames  # number of frame, [>0 : video, -1 : online_stream]
	
	def __iter__(self):
		""" The returns an iterator from them.
		
		Returns:
			self (VideoInputStream):
				For definition __next__ below
		"""
		self.frame_idx = 0
		return self
	
	def __next__(self):
		""" The next iterator for capture video 
			e.g.:
				>>> video_stream = VideoReader("cam_1.mp4")
				>>> for image, frame_idx in enumerate(video_stream):
		
		Returns:
			frame_indexes (list):
				The list of image indexes in the video.
			images (list):
				The list of np.array images from OpenCV.
		"""
		if self.frame_idx >= self.num_frames:
			raise StopIteration
		else:
			frame_indexes = []
			images        = []
			
			for i in range(self.batch_size):
				self.frame_idx += 1
				if self.frame_idx >= self.num_frames:
					break
				ret_val, image = self.cap.read()
				frame_indexes.append(self.frame_idx)
				images.append(image)
				
			return frame_indexes, np.array(images)
	
	def __del__(self):
		""" Close the reading stream.
		"""
		self.close_stream()
		
	# MARK: Setup
	
	def create_online_stream(self):
		""" Create the capture for online camera
				stream_pipe = 'rtsp://192.168.1.64/1'  # IP camera
				stream_pipe = 'rtsp://username:password@192.168.1.64/1'  # IP camera with login
				stream_pipe = 'http://wmccpinetop.axiscam.net/mjpg/video.mjpg'  # IP golf camera
		Returns:
			cap (VideoCapture):
				The object VideoCapture of OpenCV.
			num_frames (int): =-1
				The online camera doesnt have number of frame.
		"""
		if is_video_stream(stream=self.stream):
			self.cap = cv2.VideoCapture(self.stream)  # stream
			self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.batch_size)  # set buffer (batch) size
		else:
			printe(f"{self.stream} is not a corrected stream format.")
			raise FileNotFoundError
		
	def create_video_stream(self):
		""" Create the capture for video

		Returns:
			cap (VideoCapture):
				The object VideoCapture of OpenCV.
			num_frames (int):
				The total of frame in this video.
		"""
		# TODO: Get path to video file
		video_file = os.path.join(data_dir, self.dataset, "video", self.file)
		if is_video_file(file=video_file):
			self.cap        = cv2.VideoCapture(video_file)
			self.num_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
		else:
			printe(f"Video file not found or wrong file type at {video_file}.")
			raise FileNotFoundError
			
	def close_stream(self):
		"""Release the current video capture.
		"""
		if self.cap:
			self.cap.release()
	

# MARK: - VideoWriter

class VideoWriter(object):
	"""Video Writer
	
	Attributes:
		output_dir (str):
		
		file (str, optional):
			The video file or image folder. By default, assume all video are put inside ``aicity2021/video/``.
		dims (tuple):
			Input size as [C, H, W]. This is also used to reshape the input aicity2021.
		frame_rate (int):
			The frame rate of the video.
		fourcc (str):
			The file type of video
				# *'MP4V': MP4 -> this type can open on ubuntu
				# *'XVID': AVI
				# *'MJPG': AVI
				# *'WMV1': AVI
	"""
	
	# MARK: Magic Functions
	
	def __init__(
		self,
		output_dir: str,
		file      : Optional[str]        = None,
		dims      : Tuple[int, int, int] = (3, 1920, 1080),
		frame_rate: float                = 10,
		fourcc    : Optional[str]        = "mp4v",
		**kwargs
	):
		super().__init__(**kwargs)
		self.output_dir   = output_dir
		self.file         = file
		self.dims         = dims
		self.frame_rate   = frame_rate
		self.fourcc       = fourcc
		self.video_writer = None
		
		# TODO: Setup video writer
		if self.file:
			self.create_video_writer()
		
		if self.video_writer is None:
			printe("No video writer is defined. Please check again!")
			raise ValueError
		
	def __del__(self):
		""" Close the writing stream
		
		Returns:

		"""
		self.close_video_writer()
		
	# MARK: Setup stream
	
	def create_video_writer(self):
		""" Create the new video writer.
		"""
		video_file        = os.path.join(self.output_dir, self.file)
		fourcc            = cv2.VideoWriter_fourcc(*self.fourcc)
		self.video_writer = cv2.VideoWriter(video_file, fourcc, self.frame_rate, (self.dims[2], self.dims[1]))
			
		if not self.video_writer:
			printe(f"Video file cannot be created at {video_file}.")
			raise FileNotFoundError
		
	def write_frame(self, image: np.ndarray):
		""" Add one frame to writing video.
		
		We have to scale image before write.
		
		Args:
			image (np.ndarray):
				The image for writing of shape [H, W, C].
		"""
		# TODO: Convert to channel last
		image = image_channel_last(image=image)
		image = resize_image_cv2(image=image, size=self.dims[1:3])
		self.video_writer.write(image)
	
	def close_video_writer(self):
		"""Release the current video capture.
		"""
		if self.video_writer:
			self.video_writer.release()