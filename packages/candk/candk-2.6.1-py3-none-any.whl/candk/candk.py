import os, sys, getopt, logging
from .corndog import Corndog, STREAM, SINGLE_FILE, ONE_TO_ONE
from .ketchup.base import Ketchup, STYLESHEET, RenderTypes

HELP = """candk -frNbmMhv -p <page_name> -s <path or file> -o <path> -n <name> -c <css file> -x <ext> -X <pattern>

-f	Export results to a single file. By default the name of the file is
	'Corndog_out.txt' unless a different name and extension are provided via the
	-n and/or -x options.

-r	Parse files in subdirectories as well as the starting directory.

-m	Export results to multiple files, with each file corresponding to a source
	file. The files are named the same as the source file with the subfolders
	prepended by hyphens (-) and the extension '.txt'. The names cannot be set
	with the -n option, but the extension can be changed with the -x option.

-h	Display the help. This will also display if any invalid options are given.

-s	The starting point for the parsing. By default the starting point is the
	current working directory. If a filename is given as the starting point,
	only that file will be parsed instead of the entire directory.

-o	The path for the output file. By default the output directory is the current
	working directory.

-n	Give the output file a specific name.

-x	Give the output file(s) a specific file extension.

-M  Export to Markdown (.md) rather than HTML (.html)

-c  Replaces the default CSS with the stylesheet specified.

-N  Level 1 headers in the navigation sidebar are rendered as collapsible
    elements, to save space when the document is exceptionally large.

-b  Disable creating headers from empty newlines

-p	Give the page a name. If the name has periods, the HTML title will be only
	the right-most portion, but the full page_name will display on the page
	itself. NOTE: If the -m flag is used, all resulting files will use
	the same page name.

-X  A file glob pattern which identifies files to exclude from parsing.
    Excluded files will not be read at all by Corndog.
    This option can be used multiple times to exclude several patterns.

-v  "Verbose": send warnings and errors to stderr to give more detailed
    feedback of the parsing and rendering.
    Use multiple v's to set the verbosity level (-v, -vv, or -vvv).
"""

class CorndogWithKetchup(Corndog):

	def __init__(self, start_point = None, search_subs = False,
					output = STREAM, output_name = 'Conrdog_out',
					output_ext = '.txt', output_dir = None,
					css_file = STYLESHEET, collapse_h1 = False,
					newline_headers = True, page_name = None,
					render_type = RenderTypes.HTML,
					excludes = []):
		super().__init__(start_point = start_point, search_subs = search_subs,
							output = output, output_name = output_name, 
							output_ext = output_ext, output_dir = output_dir,
							excludes = excludes)
		self.css_file = css_file
		self.collapse_h1 = collapse_h1
		self.render_type = render_type
		self.newline_headers = newline_headers
		self.page_name = page_name

	def send_to_output(self, text, output, output_name = 'Corndog_out', output_ext = '.txt', output_dir = None):
		output_name = output_name.replace('-', '.')
		super().send_to_output(text, output, output_name = output_name, output_ext = '.kp', output_dir = output_dir)
		filename = output_name + output_ext
		file = os.path.join(output_dir, filename)
		prev_dir = os.getcwd()
		os.chdir(output_dir)
		kp = Ketchup(filename, page_name = self.page_name,
						output_dir = output_dir,
						css_file = self.css_file, 
						collapse_h1 = self.collapse_h1,
						newline_headers = self.newline_headers,
						render_type = self.render_type)
		kp.begin()
		os.remove(filename)
		os.chdir(prev_dir)


def main():

	showhelp = False
	optlist = []
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'fmbNrMhvX:n:o:s:c:p:')
	except getopt.GetoptError:
		showhelp = True

	loglevel = 41 #minimum log level for CRITICAL
	cd = CorndogWithKetchup(output_ext = '.kp', output = ONE_TO_ONE)

	for o, arg in optlist:
		if o == '-r':
			cd.search_subs = True
		if o == '-M':
			cd.render_type = RenderTypes.MARKDOWN
		if o == '-m':
			cd.output = ONE_TO_ONE
		if o == '-f':
			cd.output = SINGLE_FILE
		if o == '-N':
			cd.collapse_h1 = True
		if o == '-h':
			showhelp = True
		if o == '-n':
			cd.output_name = arg
		if o == '-o':
			cd.output_dir = arg
		if o == '-s':
			cd.start_point = arg
		if o == '-c':
			cd.css_file = arg
		if o == '-b':
			cd.newline_headers = False
		if o == '-p':
			cd.page_name = arg
		if o == '-X':
			cd.excludes.append(arg)
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