
KETCHUP_TAGS = ['@byline',		# multiline
				'@imports',		# multiline
				'@class',		# single line
				'@method',		# single line
				'@attributes',	# multiline list
				'@constants',	# multiline list
				'@params',		# multiline list
				'@return',		# single line
				'@returns',		# single line
				'@exceptions',	# multiline list
				'@deflist',		# multiline list
				'@h1','@h2',	# single line
				'@h3','@h4',	# single line
				'@m1','@m2',	# single line
				'@m3','@m4',	# single line
				'@table',		# multiline
				'@hr',			# horizontal rule
				'@br',			# break line
				'@codeblock',	# multiline
				'@endcodeblock',# end tag
				'@codeblockend',# alternate end tag
				'@literal',		# multiline
				'@endliteral',	# end tag
				'@literalend',	# alternate end tag
				'@note',		# single line
				'@page',		# single line
				'@file',		# single line
				'@outdir',		# single line
				'@image',		# single line
				]

FRONTLINE_SPREAD_MAPPINGS = {
				'-': '@non-bulleted',
				'*': '@bulleted',
				'#': '@numbered',
				}

OUTPUT_CONTROLS = ['@page', '@file', '@outdir']
NON_STYLED_TAGS = ['@codeblock', '@literal', '@class', '@method']
BLOCK_TAGS = ['@codeblock', '@literal']
END_BLOCK_TAGS = ['@endcodeblock', '@endliteral', '@codeblockend', '@literalend']
INLINE_ALLOWED = ['@non-bulleted', '@bulleted', '@numbered', '@table', '@class', '@method']
FRONTLINE_TAGS = list(FRONTLINE_SPREAD_MAPPINGS.keys())

# render types
class RenderTypes:
	HTML = 'html'
	MARKDOWN = 'md'


########  BASE SPREAD  ########
###############################

class Spread():

	TEMPLATES = {
		'html': '<div id="{index}" class="k-paragraph">{text}</div>',
		'md':   '\n{text}\n',
	}

	def __init__(self, tag = None):
		self.type = tag
		self.text = ''

	def __str__(self):
		return str(self.type)

	def is_empty(self):
		return (self.text == '' or self.text is None)

	def make_render_safe(self, text, render_type):
		if render_type == RenderTypes.HTML:
			text = text.replace('<', '&lt;')
			text = text.replace('>', '&gt;')
		elif render_type == RenderTypes.MARKDOWN:
			text = text.replace('[', '\\[')
			text = text.replace('+', '\\+')
		return text

	def add_text(self, text, render_type = RenderTypes.HTML, preserve_linebreaks = False):
		self.text += ' ' + self.make_render_safe(text, render_type)

	def render_text(self, text, render_type = RenderTypes.HTML):
		return self.make_render_safe(text, render_type)

	def render(self, index, render_type = RenderTypes.HTML):
		data = { 'index': index, 'text': self.render_text(self.text, render_type) }
		return self.TEMPLATES[render_type].format(**data)


########  INLINE SPREAD  ########
#################################
OPEN = 'open'
CLOSE = 'close'

class InlineSpread(Spread):

	INLINE_TEMPLATES = {
		'code': {
			'open': {
				'html': '<span class="k-code">',
				'md'  : '```',
			},
			'close': {
				'html': '</span> ',
				'md'  : '```',
			},
		},
		'codeline': {
			'open': {
				'html': '<span class="k-code">',
				'md'  : '```',
			},
			'close': {
				'html': '</span>',
				'md'  : '```',
			},
		},
		'link': {
			'open': {
				'html': '<a class="k-link" target="_blank" href="',
				'md'  : '[',
			},
			'close': {
				'html': '">{link_text}</a> ',
				'md'  : '{link_text}]({link_text})',
			},
		},
		'bold': {
			'open': {
				'html': '<strong>',
				'md'  : '**',
			},
			'close': {
				'html': '</strong>',
				'md'  : '**',
			},
		},
		'italic': {
			'open': {
				'html': '<em>',
				'md'  : '_',
			},
			'close': {
				'html': '</em>',
				'md'  : '_',
			},
		},
		'linebreak': {
			'open': {
				'html': '<br />',
				'md'  : '<br />',
			},
			'close': {
				'html': '<br />',
				'md'  : '<br />',
			},
		}
	}

	def initialize_data(self):
		self.disregard_next = False
		self.codeline_start = False
		self.codeline_end = False
		self.link_text = ''
		self.tag = None
		self.bold = False
		self.italic = False

	def add_text(self, text, render_type = RenderTypes.HTML, preserve_linebreaks = False):
		if preserve_linebreaks:
			self.text += '@' + self.make_render_safe(text, render_type)
		else:
			self.text += ' ' + self.make_render_safe(text, render_type)

	def render_text(self, text, render_type = RenderTypes.HTML):
		text = super().render_text(text, render_type)
		return self.render_inline(text, render_type)


	def _render_tag(self, tag, open_or_close, render_type, **kwargs):
		return self.INLINE_TEMPLATES[tag][open_or_close][render_type].format(**kwargs)


	def determine_action(self, i, char, text):

		if self.tag == 'codeline':
			return '_codeline_inside'

		elif char == '/' and (i == 0 or text[i-1] == ' ') and self.tag not in ['code', 'codeline']:
			return '_codeline_open'

		elif char == ' ' and self.tag == 'code':
			return '_code_close'

		elif char == '!' and (i == 0 or text[i-1] == ' ') and self.tag not in ['link']:
			return '_link_open'

		elif char == ' ' and self.tag == 'link':
			return '_link_close'

		elif char == '*' and self.tag is None:
			return '_bold_tag'

		elif char == '_' and self.tag is None:
			return '_italic_tag'

		elif char =='@' and self.tag is None:
			return '_linebreak'

		return '_plain_char'


	def render_inline(self, text, render_type = RenderTypes.HTML):
		result = ''
		self.initialize_data()

		for i in range(len(text)):
			char = text[i]
			if char == '\\':
				self.disregard_next = True
			elif self.disregard_next:
				self.disregard_next = False
				result += char
			else:
				action_name = self.determine_action(i, char, text)
				action = getattr(self, action_name)
				result += action(i, char, text, render_type)

		result += self._inline_cleanup(render_type)
		return result


	def _inline_cleanup(self, render_type):
		result = ''
		if self.tag in ['code','codeline']:
			result += self._render_tag(self.tag, CLOSE, render_type)
		elif self.tag in ['link']:
			result += self._render_tag(self.tag, CLOSE, render_type,
											link_text=self.link_text)
		if self.bold:
			result += self._render_tag('bold', CLOSE, render_type)
		if self.italic:
			result += self._render_tag('italic', CLOSE, render_type)
		return result

	#-----------------------------
	# TAG PARSE AND RENDER METHODS
	#-----------------------------

	def _codeline_inside(self, i, char, text, render_type):
		self.codeline_end = (char == '-' and \
								(i < (len(text)-1) and text[i+1] == '/')) or \
								(self.codeline_end and char == '/')
		if char == '/' and self.codeline_end:
			result = self._render_tag(self.tag, CLOSE, render_type)
			self.codeline_start = False
			self.codeline_end = False
			self.tag = None
			return result
		elif char == '-' and (self.codeline_end or self.codeline_start):
			return ''
		self.codeline_start = False
		self.codeline_end = False
		return char

	def _codeline_open(self, i, char, text, render_type):
		if i < (len(text)-1) and text[i+1] == '-':
			self.tag = 'codeline'
			self.codeline_start = True
		else:
			self.tag = 'code'
		return self._render_tag(self.tag, OPEN, render_type)

	def _code_close(self, i, char, text, render_type):
		result = self._render_tag(self.tag, CLOSE, render_type)
		self.tag = None
		return result

	def _link_open(self, i, char, text, render_type):
		self.tag = 'link'
		self.link_text = ''
		return self._render_tag(self.tag, OPEN, render_type)

	def _link_close(self, i, char, text, render_type):
		result = self._render_tag(self.tag, CLOSE, render_type,
										link_text=self.link_text)
		self.tag = None
		return result

	def _bold_tag(self, i, char, text, render_type):
		if (i < (len(text)-1) and text[i+1] != ' ') and not self.bold:
			self.bold = True
			return self._render_tag('bold', OPEN, render_type)
		elif self.bold:
			self.bold = False
			return self._render_tag('bold', CLOSE, render_type)
		return ''

	def _italic_tag(self, i, char, text, render_type):
		if (i < (len(text)-1) and text[i+1] != ' ') and not self.italic:
			self.italic = True
			return self._render_tag('italic', OPEN, render_type)
		elif self.italic:
			self.italic = False
			return self._render_tag('italic', CLOSE, render_type)
		return ''

	def _linebreak(self, i, char, text, render_type):
		return self._render_tag('linebreak', OPEN, render_type)

	def _plain_char(self, i, char, text, render_type):
		if self.tag == 'link':
			self.link_text += char
		return char


