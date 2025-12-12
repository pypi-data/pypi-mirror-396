import sys, os, re, getopt, logging, glob

HELP = """corndog -frmhv -s <path or file> -o <path> -n <name> -x <ext> -X <pattern>

-f	Export results to a single file. By default the name of the file is
	'Corndog_out.txt' unless a different name and extension are provided via the
	-n and/or -x options.

-r	Parse files in subdirectories as well as the starting directory.

-m	Export results to multiple files, with each file corresponding to a source
	file. The files are named the same as the source file with the subfolders
	prepended by hyphens (-) and the extension '.txt'. The names cannot be set
	with the -n option, but the xtension can be changed with the -x option.

-h	Display the help. This will also display if any invalid options are given.

-s	The starting point for the parsing. By default the starting point is the
	current working directory. If a filename is given as the starting point,
	only that file will be parsed instead of the entire directory.

-o	The path for the output file. By default the output directory is the current
	working directory.

-n	Give the output file a specific name.

-x	Give the output file(s) a specific file extension.

-X  A file glob pattern which identifies files to exclude from parsing.
    Excluded files will not be read at all by Corndog.
    This option can be used multiple times to exclude several patterns.

-v  "Verbose": send warnings and errors to stderr to give more detailed
    feedback of the parsing and rendering.
    Use multiple v's to set the verbosity level (-v, -vv, or -vvv).
"""

STREAM = 'stream'
SINGLE_FILE = 'single file'
ONE_TO_ONE = 'one to one'

class FileType:

	def __init__(self, ext, comments=[''], ignores=[], replaces=[]):
		self.ext = ext
		self.comments = comments
		self.ignores = ignores
		self.replaces = replaces

FILE_TYPES = {
	'.py': FileType('.py', 
			comments=['#','"""', "'''"],
			ignores =['#'],
			replaces=['//','"""', "'''"]),

	'.java': FileType('.java', 
			comments=['//', '/**',  '/*'],
			ignores =['*'],
			replaces=['//', '/**', '/*','*/']),

	'.sql': FileType('.sql', 
			comments=['--', '/**', '/*'],
			ignores =['*'],
			replaces=['//','--', '/**', '/*','*/']),

	'.xml': FileType('.xml', 
			comments=['<!--'],
			ignores =[],
			replaces=['//', '<!--', '-->']),

	'.html': FileType('.html', 
			comments=['<!--'],
			ignores =[],
			replaces=['//','<!--', '-->']),

	'.php': FileType('.php', 
			comments=['<!--', '//', '#'],
			ignores =['#'],
			replaces=['//','<!--', '-->']),

	'.ftl': FileType('.ftl', 
			comments=['<!--'],
			ignores =[],
			replaces=['//','<!--', '-->']),

	'.js': FileType('.js', 
			comments=['/**', '/*', '//'],
			ignores =['*'],
			replaces=['//', '/**', '/*', '*/']),

	'.ts': FileType('.ts', 
			comments=['/**', '/*', '//'],
			ignores =['*'],
			replaces=['//', '/**', '/*', '*/']),

	'.css': FileType('.css', 
			comments=['/**', '/*'],
			ignores =['*'],
			replaces=['//', '/**', '/*', '*/']),

	'.c': FileType('.c', 
			comments=['/*'],
			ignores =['*'],
			replaces=['//', '/**', '/*', '*/']),

	'.cpp': FileType('.cpp', 
			comments=['/**', '/*'],
			ignores =['*'],
			replaces=['//', '/**', '/*', '*/']),

	'.sh': FileType('.sh', 
			comments=['#'],
			ignores =['#'],
			replaces=['//']),

	'.bat': FileType('.bat', 
			comments=['::', 'REM ', 'rem '],
			ignores =['::'],
			replaces=['::', 'REM ', 'rem ']),

	'.txt': FileType('.txt', 
			comments=[''],
			ignores =[],
			replaces=['//']),

	'.properties': FileType('.properties', 
			comments=['#', '!'],
			ignores =['#', '!'],
			replaces=['//']),

	'.kp': FileType('.kp', 
			comments=[''],
			ignores =[],
			replaces=['//']),

	'.tas': FileType('.tas', 
			comments=[':CD ', ':CM '],
			ignores =[],
			replaces=['//',':CD ', ':CM ']),

	'.vue': FileType('.vue', 
			comments=['<!--', '/**', '/*', '//'],
			ignores =['*'],
			replaces=['<!--', '-->', '//', '/**', '/*', '*/']),

	'.toml': FileType('.toml', 
			comments=['#'],
			ignores =['#'],
			replaces=['//']),

	'.yml': FileType('.yml', 
			comments=['#'],
			ignores =['#'],
			replaces=['//']),

	'.yaml': FileType('.yaml', 
			comments=['#'],
			ignores =['#'],
			replaces=['//']),

	'.conf': FileType('.conf', 
			comments=['#'],
			ignores =['#'],
			replaces=['//']),

	'.ini': FileType('.ini', 
			comments=[';'],
			ignores =[';'],
			replaces=['//']),
}

class Corndog():

	log = logging.getLogger('corndog')

	def __init__(self, start_point = None, search_subs = False, output = STREAM,
					output_name = 'Conrdog_out', output_ext = '.txt',
					output_dir = None, excludes = []):
		self._configure(start_point, search_subs, output, output_name,
							output_ext, output_dir, excludes)


	def _configure(self, start_point, search_subs, output, output_name,
						output_ext, output_dir, excludes):
		self.start_point = start_point
		self.search_subs = search_subs
		self.output = output
		self.output_name = output_name
		self.output_ext = output_ext
		self.output_dir = output_dir
		self.final_text = ''
		self.original_start = self.start_point
		self.excludes = excludes
		self._exclude_paths = []


	def initialize_data(self):
		if self.start_point is None:
			self.start_point = os.getcwd()
		self.start_point = os.path.abspath(self.start_point)
		self.original_start = self.start_point

		# if start_point is a file, we need to set the start point to the directory itself
		if self._hack_is_file(self.start_point):
			self.start_point = os.path.dirname(self.start_point)

		if self.output_dir is None:
			self.output_dir = self.start_point
		self.output_dir = os.path.abspath(self.output_dir)

		# we need to do this because Python 3.9 does not have the
		# root_dir argument for glob.iglob() *sigh*.
		prev_dir = os.getcwd()
		os.chdir(self.start_point)

		self._exclude_paths = []
		for pattern in self.excludes:
			for path in glob.iglob(pattern, recursive=True):
				full_path = os.path.abspath(path)
				self._exclude_paths.append(full_path)

		os.chdir(prev_dir)


	def _hack_is_file(self, path):
		"""Yes, I know this is super hacky, but it only
		causes issues if a directory has a . in the name
		"""
		splitstr = path.split('.')
		if len(splitstr) == 1:
			# No . found, must not be a file
			return False
		return True


	def begin(self):
		self.initialize_data()

		if self._hack_is_file(self.original_start):
			# if it's a file, just parse it and output it
			os.chdir(self.start_point)
			if not self.matches_excludes(self.original_start):
				text = self.parse_file(self.original_start)
				self.send_to_output(text, self.output, self.output_name, self.output_ext, self.output_dir)
		else:
			self.final_text = ''
			self._search_dir(self.start_point, first_dir = True)
			if self.output == SINGLE_FILE:
				self.send_to_output(self.final_text, self.output, self.output_name, self.output_ext, self.output_dir)


	def matches_excludes(self, filepath):
		if filepath in self._exclude_paths:
			self.log.warning('{} matches an exclude pattern, skipping'.format(filepath))
			return True
		return False


	def _search_dir(self, root, first_dir = False, prev_name = ''):
		os.chdir(root)
		if not first_dir:
			dirname = prev_name + os.path.basename(root) + '-'
		else:
			dirname = ''
		for entry in sorted(os.listdir(root)):
			full_path = os.path.abspath(entry)
			if self.matches_excludes(full_path):
				continue
			if os.path.isfile(entry):
				text = self.parse_file(full_path)
				filename, file_ext = os.path.splitext(entry)
				file_ext = file_ext.lower()
				filename = dirname + filename
				if text != '' and text is not None:
					if self.output == ONE_TO_ONE or self.output == STREAM:
						self.send_to_output(text, self.output, filename, self.output_ext, self.output_dir)
					else:
						self.final_text += text + '\n'
			elif os.path.isdir(entry) and self.search_subs:
				self._search_dir(full_path, prev_name = dirname)
				os.chdir(root)

	@classmethod
	def send_to_output(cls, text, output, output_name = 'Corndog_out', output_ext = '.txt', output_dir = None):
		if output_dir is None:
			output_dir = os.getcwd()
		file_path = os.path.join(output_dir, output_name + output_ext)
		cls.log.info('SEND TO: ' + file_path)
		if output == STREAM:
			print(text)
		elif output == SINGLE_FILE or output == ONE_TO_ONE:
			with open(file_path, 'w') as outfile:
				outfile.write(text)


	@classmethod
	def capture_text(cls, line, file_ext):
		# set correct comment markers
		ignores = ' \t' + ''.join(FILE_TYPES[file_ext].ignores)
		line = line.lstrip(ignores)

		if line.strip() == '':
			return '\n'

		if file_ext == '.tas' and len(line) > 3 and line[:4] not in FILE_TYPES['.tas'].comments:
			# must be in a TaskBuilder file
			# can only read comment sections
			cls.log.error('Only comments (:CD or :CM nodes) can be parsed from .tas files')
			return '\n'

		for mark in FILE_TYPES[file_ext].replaces:
			line = line.replace(mark, '')
		line = line.replace('-==', '\n')

		if line.strip() == '':
			return '\n'
		
		return line

	@classmethod
	def parse_file(cls, filepath):
		cls.log.info('READING: ' + filepath)
		start_fetch = False
		result = ''
		# determine file type (via the extension)
		myname, file_ext = os.path.splitext(filepath)
		file_ext = file_ext.lower()
		if file_ext not in FILE_TYPES.keys():
			# uh oh! we got a file that is not supported!
			cls.log.warning('File Type {} Not Supported'.format(file_ext))
			return result
		elif file_ext == '.tas':
			cls.log.warning('DEPRECATED: TaskBuilder file support will be removed in a future version of Corndog')

		# read the file
		lookers = ['-==']
		with open(filepath, 'r') as myfile:
			for line in myfile:
				if not start_fetch:
					# if we haven't started a fetch, check if we should
					for looker in lookers:
						if looker in line:
							start_fetch = True

				if start_fetch:
					newstr = cls.capture_text(line, file_ext)
					result += newstr

					if newstr == '\n':
						# empty line, stop fetching
						start_fetch = False

		if result.strip() != '':
			result += '\n'

		return result



def main():

	showhelp = False
	optlist = []
	try:
		optlist, args = getopt.gnu_getopt(sys.argv[1:], 'fmrhvn:x:X:o:s:')
	except getopt.GetoptError:
		showhelp = True

	loglevel = 41 #minimum log level for CRITICAL
	cd = Corndog()

	for o, arg in optlist:
		if o == '-r':
			cd.search_subs = True
		if o == '-m':
			cd.output = ONE_TO_ONE
		if o == '-f':
			cd.output = SINGLE_FILE
		if o == '-h':
			showhelp = True
		if o == '-n':
			cd.output_name = arg
		if o == '-x':
			cd.output_ext = arg
		if o == '-X':
			cd.excludes.append(arg)
		if o == '-o':
			cd.output_dir = arg
		if o == '-s':
			cd.start_point = arg
		if o == '-v':
			loglevel -= 11

	if showhelp:
		print(HELP)
		return

	# adjust the logging level
	# if it's too low, bump it back up to DEBUG
	if loglevel <= logging.NOTSET:
		loglevel = logging.DEBUG

	logging.basicConfig(stream=sys.stderr, level=loglevel)

	cd.begin()

if __name__ == '__main__':
	main()








