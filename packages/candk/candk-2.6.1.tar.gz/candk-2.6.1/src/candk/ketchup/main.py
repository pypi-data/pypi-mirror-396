
import os, sys, getopt, time, logging

from .base import Ketchup
from .spread import RenderTypes





#########  MAIN SCRIPT  #########
#################################

HELP = '''ketchup <filepath> -hwNmMbv -p <page_name> -n <output_name>
						   -o <output_dir> -c <css_file>

<filepath>  The file to be parsed and transformed into an HTML document.

-h	Display the help. This will also display if any invalid options are given.

-p	Give the page a name. If the name has periods, the HTML title will be only
	the right-most portion, but the full page_name will display on the page
	itself.

-n	Give the output file a specific name.

-o	The path for the output file. By default the output directory is the current
	working directory.

-c  Replaces the default CSS with the stylesheet specified.

-N  Level 1 headers in the navigation sidebar are rendered as collapsible
    elements, to save space when the document is exceptionally large.

-b  Disable creating headers from empty newlines

-m  Export to Markdown (.md) rather than HTML (.html)

-M  Same as -m

-w  "Watch Mode": Runs in a loop, and updates the output file each time it
    detects that the input file has been changed.

-v  "Verbose": send warnings and errors to stderr to give more detailed
    feedback of the parsing and rendering.
    Use multiple v's to set the verbosity level (-v, -vv, or -vvv).
'''

def main():

	showhelp = False
	optlist = []
	try:
		optlist, args = getopt.gnu_getopt(sys.argv[1:], 'hwmbMNvp:n:o:c:')
	except getopt.GetoptError:
		showhelp = True
		print(HELP)
		return

	loglevel = 41 #minimum log level for CRITICAL
	ketchup = None

	try:
		ketchup = Ketchup(sys.argv[1])
	except:
		print('Requires a <filepath> to a ketchup file (file extension .kp)')
		print('Use the -h option for more information.')
		return

	watch_file = False
	last_modified = None

	for o, arg in optlist:
		if o == '-p':
			ketchup.page_name = arg
		if o == '-h':
			showhelp = True
		if o == '-n':
			ketchup.output_name = arg
		if o == '-o':
			ketchup.output_dir = arg
		if o == '-c':
			ketchup.css_file = arg
		if o == '-m' or o == '-M':
			ketchup.render_type = RenderTypes.MARKDOWN
		if o == '-b':
			ketchup.newline_headers = False
		if o == '-N':
			ketchup.collapse_h1 = True
		if o == '-w':
			watch_file = True
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

	if watch_file:
		print('Watching for changes in ' + args[0])
		ketchup.initialize_data()
		full_filepath = os.path.abspath(ketchup.filepath)
		try:
			while(True):
				stat = os.stat(full_filepath)
				modified_time = stat.st_mtime
				if last_modified != modified_time:
					ketchup.begin()
					print('Ketchup render success!')
					last_modified = modified_time
				time.sleep(1)
		except KeyboardInterrupt:
			# stopped the loop, let's exit
			pass
	else:
		ketchup.begin()



if __name__ == '__main__':
	main()




