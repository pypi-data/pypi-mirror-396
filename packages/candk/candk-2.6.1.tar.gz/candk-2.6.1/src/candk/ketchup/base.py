
import os, sys, logging
from pathlib import Path
from datetime import datetime

from .tags import get_spread
from .spread import *


VERSION = '2.6.1'
VERSION_YEAR = '2025'

source_path = Path(__file__).resolve()
source_dir = source_path.parent

STYLESHEET = os.path.join(source_dir, 'style.css')

########  BASE CLASSES  ########
################################

class Document():

	log = logging.getLogger('ketchup')

	def __init__(self, filepath, page_name = None,
					output_name = None, output_dir = None,
					css_file = STYLESHEET,
					render_type = RenderTypes.HTML,
					preserves_linebreaks = False,
					collapse_h1 = False,
					newline_headers = True):
		# config
		self.page_name = page_name
		self.filepath = filepath
		self.output_name = output_name
		self.output_dir = output_dir
		self.css_file = css_file
		self.render_type = render_type
		self.preserves_linebreaks = preserves_linebreaks
		self.collapse_h1 = collapse_h1
		self.newline_headers = newline_headers
		# state
		self.document = []
		self.prev_line = None
		self.prev_spread = None
		self.spread = None
		self.empty_lines = 0


	def add_text(self, text):
		myfile = text.split('\n')
		self.parse_text(myfile)


	def check_for_output_controls(self, line):
		if self.prev_line == '@page' and not self.spread:
			self.page_name = line
		elif self.prev_line == '@file' and not self.spread:
			self.output_name = line
		elif self.prev_line == '@outdir' and not self.spread:
			self.output_dir = line


	def no_spread_or_not_in(self, taglist):
		return (not self.spread or (self.spread and self.spread.type not in taglist))


	def determine_action(self, line):

		if line in KETCHUP_TAGS and self.no_spread_or_not_in(NON_STYLED_TAGS):
			return 'styled_tag'

		elif line == '' and self.no_spread_or_not_in(BLOCK_TAGS):
			return 'empty_line_detected'

		elif line in END_BLOCK_TAGS:
			return 'end_block_tag'

		elif self.spread and self.spread.type in BLOCK_TAGS:
			return 'start_block_tag'

		elif len(line) > 1 and \
				line[0] in FRONTLINE_TAGS and \
				line[1] in FRONTLINE_TAGS + [' '] and \
				self.no_spread_or_not_in(INLINE_ALLOWED):
			return 'frontline_tag'

		elif len(line) > 3 and \
				line[:2] in ['@h', '@m'] and \
				self.no_spread_or_not_in(INLINE_ALLOWED):
			return 'headers_and_markers'

		elif len(line) > 2 and line[:3] == '___':
			return 'horizontal_rule'

		elif self.spread:
			return 'add_to_existing_spread'

		elif self.prev_line not in OUTPUT_CONTROLS:
			return 'header_or_paragraph'

		return None


	def parse_text(self, myfile):
		self.prev_line = None
		self.prev_spread = None
		self.spread = None
		self.empty_lines = 0
		for line in myfile:
			unstripped_line = line
			line = line.strip()

			self.check_for_output_controls(line)
			action_name = self.determine_action(line)
			if action_name:
				action = getattr(self, action_name)
				action(unstripped_line=unstripped_line, line=line)

			self.prev_line = line
		self.add_spread()


	def add_spread(self, end_spread = True, preserve_empty = False):
		if not preserve_empty:
			self.empty_lines = 0
		if self.spread and not self.spread.is_empty():
			self.document.append(self.spread)
			self.prev_spread = self.spread
			if end_spread:
				self.spread = None


	def render(self):
		result = ''
		for i in range(len(self.document)):
			spread = self.document[i]
			result += spread.render(str(i), render_type = self.render_type) + '\n'
		return result


	#-----------------------------
	# TAG PARSING METHODS
	#-----------------------------

	def styled_tag(self, line=None, **kwargs):
		self.add_spread()
		if line not in OUTPUT_CONTROLS:
			self.spread = get_spread(line)
		if self.spread and self.spread.type in ['@hr','@br']:
			self.document.append(self.spread)
			self.spread = None

	def empty_line_detected(self, **kwargs):
		self.add_spread(preserve_empty = True)
		self.empty_lines += 1

	def start_block_tag(self, unstripped_line=None, **kwargs):
		self.empty_lines = 0
		self.spread.add_text(unstripped_line, self.render_type, self.preserves_linebreaks)

	def end_block_tag(self, **kwargs):
		self.add_spread()

	def frontline_tag(self, line=None, **kwargs):
		self.add_spread()
		tag = None
		try:
			tag = FRONTLINE_SPREAD_MAPPINGS[line[0]]
		except:
			self.log.error('{} not a valid list type, defaulting to paragraph tag'.format(tag))

		self.spread = get_spread(tag)
		self.spread.add_text(line, self.render_type, self.preserves_linebreaks)

	def headers_and_markers(self, line=None, **kwargs):
		self.add_spread()
		tag = line[:3]
		self.spread = get_spread(tag)
		text = line[3:].strip()
		self.spread.add_text(text, self.render_type, self.preserves_linebreaks)

	def horizontal_rule(self, **kwargs):
		self.add_spread()
		self.spread = get_spread('@hr')
		self.document.append(self.spread)
		self.prev_spread = self.spread
		self.spread = None

	def add_to_existing_spread(self, line=None, **kwargs):
		self.empty_lines = 0
		self.spread.add_text(line, self.render_type, self.preserves_linebreaks)

	def header_or_paragraph(self, line=None, **kwargs):
		if self.empty_lines == 3 and self.newline_headers:
			self.spread = get_spread('@h1')
		elif self.empty_lines == 2 and self.newline_headers:
			self.spread = get_spread('@h2')
		else:
			self.spread = get_spread()
		self.spread.add_text(line, self.render_type, self.preserves_linebreaks)
		self.empty_lines = 0




class Ketchup(Document):

	NAV_TEMPLATES = {
		'@h1-collapsible': '<details><summary class="k-nav k-nav-header k-nh1 collapsible"><a class="k-a" href="#{}">{}</a></summary>\n',
		'@h1':     '<a class="k-a" href="#{}"><div class="k-nav k-nav-header k-nh1 collapsible">{}</div></a>\n',
		'@h2':     '<a class="k-a" href="#{}"><div class="k-nav k-nav-header k-nh2">{}</div></a>\n',
		'@class':  '<a class="k-a" href="#{}"><div class="k-nav k-nav-class">{}</div></a>\n',
		'@method': '<a class="k-a" href="#{}"><div class="k-nav k-nav-method">{}</div></a>\n',
	}

	HTML_HEADER_TEMPLATE = '''<html><head>
<title>{title}</title>
<style>{css}</style>
</head><body>
<a class="k-a" href=""><div class="k-page-title">{page_name}</div></a>
<div class="k-page">
{navbar}
<div class="k-content">
'''

	HTML_FOOTER_TEMPLATE = '''<div class="k-spacer">Generated {timestamp}</br>
Documentation generated by Ketchup v{version}</br>
Developed by Charles Koch - {copyright_year}</div>
</div></div></body></html>'''

	def translate_filename(self, filepath, sep=os.sep):
		filename, file_ext = os.path.splitext(filepath)
		filename = filename.replace(sep, '.')
		return filename

	def begin(self):
		self.initialize_data()
		fullpath = os.path.abspath(self.filepath)
		self.parse_file(fullpath)
		filename = self.translate_filename(self.filepath)
		result = self.render(self.page_name)
		self.send_to_output(result, self.output_name, self.output_dir)


	def initialize_data(self):
		self.document = []
		filename = self.translate_filename(self.filepath)
		if self.page_name is None:
			self.page_name = filename
		if self.output_name is None:
			self.output_name = filename
		if self.output_dir is None:
			self.output_dir = os.getcwd()

		self.output_dir = os.path.abspath(self.output_dir)


	def parse_file(self, filepath):
		with open(filepath, 'r') as myfile:
			self.parse_text(myfile)


	def minify_css(self, css_file):
		with open(css_file, 'r') as mycss:
			css = mycss.read()
		css = css.strip()
		css = css.replace('\t', '')
		css = css.replace('\n', '')
		return css


	def render_nav_entry(self, i, spread):
		# if we're doing a new @h1,
		# let's end the current collapsible (if there is one)
		# and make a new collapsible section.
		if spread.type == '@h1':
			result = ''
			if self.section is not None and self.collapse_h1:
				result += '</details>\n'
			self.section = i
			if self.collapse_h1:
				result += self.NAV_TEMPLATES['@h1-collapsible'].format(i, spread.text)
				return result

		return self.NAV_TEMPLATES.get(spread.type, '').format(i, spread.text)


	def render_nav(self):
		result = '<div class="k-navbar">\n'
		# add section to track what section we are rendering
		self.section = None
		for i in range(len(self.document)):
			spread = self.document[i]
			result += self.render_nav_entry(i, spread)
		# if we've reached the end, close the <details> tag
		if self.section and self.collapse_h1:
			result += '</details>\n'
		result += '</div>\n'
		return result


	def render_html_head(self, filename):
		data = {
			'title': filename.split('.')[-1],
			'css': self.minify_css(self.css_file),
			'page_name': filename,
			'navbar': self.render_nav(),
		}
		return self.HTML_HEADER_TEMPLATE.format(**data)

	def render_html_footer(self, right_now=None):
		if right_now is None:
			right_now = datetime.now()
		data = {
			'version': VERSION,
			'timestamp': right_now.strftime('%I:%M%p  %d %b %Y'),
			'copyright_year': VERSION_YEAR,
		}
		return self.HTML_FOOTER_TEMPLATE.format(**data)


	def render(self, filename):
		result = ''
		if self.render_type == RenderTypes.HTML:
			result += self.render_html_head(filename)

		for i in range(len(self.document)):
			spread = self.document[i]
			result += spread.render(str(i), render_type = self.render_type) + '\n'

		if self.render_type == RenderTypes.HTML:
			result += self.render_html_footer()
		return result


	def send_to_output(self, text, output_name, output_dir, dryrun = False):
		file_path = os.path.join(output_dir, output_name + '.' + self.render_type)
		with open(file_path, 'w') as outfile:
			outfile.write(text)

