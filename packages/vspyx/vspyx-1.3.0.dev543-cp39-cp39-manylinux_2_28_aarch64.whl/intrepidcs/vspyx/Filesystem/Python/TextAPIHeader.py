import rlcompleter
__completer__ = rlcompleter.Completer(locals())
__disable_pretty_print__ = False
__disable_autocomplete__ = False

def __pretty_print__(obj, max_depth):
	import json
	import numbers

	if __disable_pretty_print__:
		return str(obj)

	def build(obj, current_level, max_depth):

		def strval(x):
			ret = str(x)
			if ret.startswith("vector_"):
				return ret[ret.find('['):]
			return str(x)

		def get_value(val, current_level, max_depth):
			if max_depth >= 0 and current_level >= max_depth:
				return strval(val)
			if isinstance(val, str) or isinstance(val, numbers.Number):
				return strval(val)
			if hasattr(val, "__entries"): #pybind enum
				return strval(val)
			if hasattr(val, "__iter__"):
				return [get_value(x, current_level + 1, max_depth) for x in val if not callable(x)]
			if hasattr(val, "__repr__"):
				return strval(val)
			return build(val, current_level + 1, max_depth)

		def enumerate_dir(obj):
			for item in dir(obj):
				yield item, getattr(obj, item)

		def enumerate_dict(obj):
			for item, value in obj.items():
				yield item, value

		enumerator = enumerate_dir
		if isinstance(obj, dict):
			enumerator = enumerate_dict
		elif hasattr(obj, "__dict__"):
			enumerator = enumerate_dict
			obj = obj.__dict__

		j = {}
		for name, val in enumerator(obj):
			if len(name) >= 2 and name[:2] == '__' or callable(val):
				continue
			j[name] = get_value(val, current_level, max_depth)

		return j if j != {} else strval(obj)

	return json.dumps(build(obj, 0, max_depth), sort_keys=True, indent=2)
