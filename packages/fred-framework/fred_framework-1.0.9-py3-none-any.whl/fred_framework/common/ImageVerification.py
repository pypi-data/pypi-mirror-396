#!/usr/bin/env python3  
# -*- coding: utf-8 -*-  

import os
import random
import string
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageFont, ImageDraw


class ImageVerification:
	"""
		@desc:  图形验证码
	"""
	width = 150
	height = 60
	num = 4
	fontsize = 36
	line_num = 4  # 干扰线密度
	bg_color = (0, 0, 0, 0)
	
	def rand_color(self):
		"""生成用于绘制字符串的随机颜色(可以随意指定0-255之间的数字)"""
		red = random.randint(0, 255)
		green = random.randint(0, 255)
		blue = random.randint(0, 255)
		return red, green, blue
	
	def gen_text(self):
		"""生成4位随机字符串"""
		# sample 用于从一个大的列表或字符串中，随机取得N个字符，来构建出一个子列表
		new_str = string.ascii_letters.replace("o", "").replace("O", "") + string.digits.replace("0", "")
		list = random.sample(new_str, self.num)
		return ''.join(list)
	
	# 获取字体（使用fonts目录中的字体文件）
	def get_font(self):
		"""
		获取字体对象，优先使用包内fonts目录中的字体文件，如果不存在则尝试系统字体，最后使用PIL默认字体
		支持通过 self.fontsize 动态调整字体大小
		使用包内资源定位方式，适合pip包安装后的使用场景
		"""
		# 获取当前文件所在目录（包内路径）
		current_file = Path(__file__).resolve()
		# 从 common 目录向上到 fred_framework 目录，然后定位 fonts 目录
		package_root = current_file.parent.parent  # common -> fred_framework
		font_path = package_root / 'fonts' / 'NotoSansSC-VariableFont_wght.ttf'
		
		# 如果字体文件存在，使用该字体
		if font_path.exists():
			try:
				return ImageFont.truetype(str(font_path), self.fontsize)
			except Exception:
				pass  # 如果加载失败，继续尝试其他字体
		
		# 尝试加载系统字体（支持指定大小）
		system_fonts = [
			'/System/Library/Fonts/Helvetica.ttc',  # macOS
			'/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
			'C:/Windows/Fonts/arial.ttf',  # Windows
			'C:/Windows/Fonts/msyh.ttc',  # Windows 微软雅黑
		]
		
		for sys_font in system_fonts:
			if os.path.exists(sys_font):
				try:
					return ImageFont.truetype(sys_font, self.fontsize)
				except Exception:
					continue
		
		# 如果所有字体都加载失败，使用默认字体（注意：默认字体不支持大小参数）
		# 但为了保持一致性，我们仍然返回默认字体
		default_font = ImageFont.load_default()
		# 注意：ImageFont.load_default() 不支持字体大小参数
		# 如果需要支持字体大小，必须使用 truetype 字体
		return default_font
	
	def draw_lines(self, draw, num, width, height):
		"""
		绘制干扰线
		:param draw: 图片对象
		:param num: 干扰线数量
		:param width: 图片的宽
		:param height: 图片的高
		:return:
		"""
		for num in range(num):
			x1 = random.randint(0, int(round(width / 2)))
			y1 = random.randint(0, int(round(height / 2)))
			x2 = random.randint(0, width)
			y2 = random.randint(int(round(height / 2)), height)
			draw.line(((x1, y1), (x2, y2)), fill=self.rand_color(), width=2)
	
	def draw_verify_code(self):
		"""绘制验证码图片"""
		code = self.gen_text()
		width, height = self.width, self.height  # 设定图片大小，可根据实际需求调整
		im = Image.new('RGBA', (width, height), self.bg_color)  # 创建图片对象，并设定背景色为白色'#54D8A5'
		draw = ImageDraw.Draw(im)  # 新建ImageDraw对象
		# 获取字体对象（在循环外只加载一次，提高性能）
		font = self.get_font()
		# 绘制字符串
		for i in range(self.num):
			x = random.randint(0, 3) + self.fontsize * i
			y = height / 10 + random.randint(-3, 3)
			fill = self.rand_color()
			text = code[i]
			draw.text((x, y), text=text, fill=fill, font=font, stroke_width=1, stroke_fill=self.rand_color())  #
		self.draw_lines(draw, self.line_num, width, height)  # 绘制干扰线
		
		# im.show()  # 如需临时调试，可以直接将生成的图片显示出来
		out = BytesIO()
		im.save(out, "png")
		out.seek(0)
		return out, code
