import sys, io

class __output_interceptor__(io.BufferedIOBase):
	
	def __init__(self, output_type, old_stream):
		self.old_stream = old_stream
		self.output_type = output_type
		self.buffer = bytearray()

	def close(self):
		if self.old_stream is not None:
			self.old_stream.close()
			self.old_stream = None
		super().close()

	def fileno(self):
		return self.output_type

	def flush(self):
		if self.old_stream is not None:
			self.old_stream.flush()
		if self.output_type == 1 or self.output_type == 2 and '__output__' in globals():
			out = globals()['__output__']
			if out is not None:
				out(self.buffer.decode('UTF-8'))
		self.buffer = bytearray()

	def isatty(self):
		return self.old_stream.isatty() if self.old_stream is not None else False

	def detach(self):
		if self.old_stream is not None:
			self.old_stream.detach()

	def readline(self, size=-1):
		if self.old_stream is not None:
			return self.old_stream.readline(size)
		else:
			return bytes()

	def readlines(self, hint=-1):
		if self.old_stream is not None:
			return self.old_stream.readlines(hint)
		else:
			return []

	def seek(self, offset, whence=io.SEEK_SET):
		if self.old_stream is not None:
			return self.old_stream.seek(offset, whence)
		else:
			return 0

	def seekable(self):
		if self.old_stream is not None:
			return self.old_stream.seekable()
		else:
			return False

	def tell(self):
		if self.old_stream is not None:
			return self.old_stream.tell()
		else:
			return 0

	def truncate(self, size=None):
		if self.old_stream is not None:
			self.old_stream.truncate(size)
		if size is not None:
			self.buffer = self.buffer[0:size]
		return len(self.buffer)

	def read(self, size=-1):
		if self.old_stream is not None:
			self.old_stream.read(size)
		else:
			pass

	def writable(self):
		return not self.closed and (self.output_type == 1 or self.output_type == 2)

	def writelines(self, lines):
		if self.old_stream is not None:
			self.old_stream.writelines(lines)
		super().writelines(lines)

	def read1(self, size=None):
		if self.old_stream is not None:
			return self.old_stream.read1(size)
		else:
			return 0

	def readinto1(self, b):
		if self.old_stream is not None:
			return self.old_stream.readinto1(b)

	def write(self, b):
		if self.old_stream is not None:
			self.old_stream.write(b)
		self.buffer.extend(b)
		return len(b)

sys.stdout = io.TextIOWrapper(__output_interceptor__(1, sys.stdout.buffer if sys.stdout is not None else None), encoding='UTF-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(__output_interceptor__(2, sys.stderr.buffer if sys.stderr is not None else None), encoding='UTF-8', line_buffering=True)
