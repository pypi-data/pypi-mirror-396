
from .spread import Spread, InlineSpread, RenderTypes


#########  TAG SPREADS  #########
#################################

def get_spread(tag = None):
	if tag == '@byline':
		return BylineTag(tag)
	elif tag == '@imports':
		return ImportsTag(tag)
	elif tag == '@class':
		return ClassTag(tag)
	elif tag == '@method':
		return MethodTag(tag)
	elif tag in ['@return', '@returns']:
		return ReturnTag(tag)
	elif tag in ['@deflist', '@params', '@constants', '@attributes', '@exceptions']:
		return DeflistTag(tag)
	elif tag in ['@h1','@h2','@h3','@h4','@m1','@m2','@m3','@m4']:
		return HeaderTag(tag)
	elif tag == '@table':
		return TableTag(tag)
	elif tag == '@hr':
		return HrTag(tag)
	elif tag == '@br':
		return BrTag(tag)
	elif tag == '@codeblock':
		return CodeblockTag(tag)
	elif tag == '@literal':
		return LiteralTag(tag)
	elif tag == '@note':
		return NoteTag(tag)
	elif tag in ['@bulleted', '@non-bulleted', '@numbered']:
		return ListTag(tag)
	elif tag == '@image':
		return ImageTag(tag)
	else:
		return ParagraphTag()


class ParagraphTag(InlineSpread):
	pass


class BylineTag(InlineSpread):

	def add_text(self, text, render_type = RenderTypes.HTML, preserve_linebreaks = False):
		text = super().make_render_safe(text, render_type)
		self.text += text + '\n'

	def render(self, index, render_type = RenderTypes.HTML):
		result = ''
		if render_type == RenderTypes.HTML:
			result += '<div id="{}" class="k-byline">\n'.format(index)
			for line in self.text.splitlines():
				result += '<div class="k-byline-line">{}</div>\n'.format(self.render_text(line))
			result += '</div>'
		elif render_type == RenderTypes.MARKDOWN:
			for line in self.text.splitlines():
				result += '> * {}\n'.format(self.render_text(line, render_type))
			result += '\n'
		return result


class ImportsTag(Spread):

	def add_text(self, text, render_type = RenderTypes.HTML, preserve_linebreaks = False):
		text = super().make_render_safe(text, render_type)
		self.text += text + '\n'

	def render(self, index, render_type = RenderTypes.HTML):
		result = ''
		if render_type == RenderTypes.HTML:
			result += '<div id="{}" class="k-imports">\nImports:\n'.format(index)
			for line in self.text.splitlines():
				result += '<div class="k-imports-line">{}</div>\n'.format(line)
			result += '</div>'
		elif render_type == RenderTypes.MARKDOWN:
			result += '**Imports:**\n\n'
			for line in self.text.splitlines():
				result += '* ```{}```\n'.format(line)
			result += '\n'
		return result


class ClassTag(Spread):

	def render(self, index, render_type = RenderTypes.HTML):
		if render_type == RenderTypes.HTML:
			return '<div id="{}" class="k-class">{}</div>'.format(index, self.text)
		elif render_type == RenderTypes.MARKDOWN:
			return '## ```{}```\n\n'.format(self.text)
		return ''


class MethodTag(Spread):

	def render(self, index, render_type = RenderTypes.HTML):
		if render_type == RenderTypes.HTML:
			return'<div id="{}" class="k-method">{}</div>'.format(index, self.text)
		elif render_type == RenderTypes.MARKDOWN:
			return '#### ```{}```\n'.format(self.text)
		return ''


class HeaderTag(Spread):

	def __init__(self, tag = None):
		self.text = ''
		self.type = tag
		self.tag = tag

	def render(self, index, render_type = RenderTypes.HTML):
		tag_type = self.tag[1:]
		if render_type == RenderTypes.HTML:
			return '<div id="{}" class="k-{}">{}</div>'.format(index, tag_type, self.text)
		elif render_type == RenderTypes.MARKDOWN:
			tag_str = '#'*int(tag_type[1:])
			return '{} {}\n'.format(tag_str, self.text)
		return ''


class TableTag(InlineSpread):

	def add_text(self, text, render_type = RenderTypes.HTML, preserve_linebreaks = False):
		self.text += self.make_render_safe(text, render_type) + '\n'

	def render_html_row(self, line):
		result = ''
		if len(line) > 2 and line[:3] == '---':
			self.header = False
		else:
			cells = line.split('|')
			result += '<tr>'
			for cell in cells:
				cell = cell.strip()
				if self.header:
					result += '<th>{}</th>'.format(self.render_text(cell, RenderTypes.HTML))
				else:
					result += '<td>{}</td>'.format(self.render_text(cell, RenderTypes.HTML))
			result += '</tr>\n'
		return result

	def render_markdown_row(self, line):
		result = ''
		if len(line) > 2 and line[:3] == '---':
			self.header = False
			for i in range(self.num_cells):
				result += '|---'
			result += '|\n'
		else:
			cells = line.split('|')
			self.num_cells = len(cells)
			for cell in cells:
				cell = cell.strip()
				result += '| ' + self.render_text(cell, RenderTypes.MARKDOWN) + ' '
			result += '|\n'
		return result

	def render(self, index, render_type = RenderTypes.HTML):
		self.header = True
		self.num_cells = 0
		result = ''
		if render_type == RenderTypes.HTML:
			result += '<table class="k-table">\n'
			for line in self.text.splitlines():
				result += self.render_html_row(line)
			result += '</table>\n'
		elif render_type == RenderTypes.MARKDOWN:
			header = True
			self.num_cells = 0
			for line in self.text.splitlines():
				result += self.render_markdown_row(line)
			result += '\n'
		return result


class HrTag(Spread):

	def render(self, index, render_type = RenderTypes.HTML):
		if render_type == RenderTypes.HTML:
			return '<hr />\n'
		elif render_type == RenderTypes.MARKDOWN:
			return '----------------------------------------\n'
		return ''


class BrTag(Spread):

	def render(self, index, render_type = RenderTypes.HTML):
		if render_type == RenderTypes.HTML:
			return '<div class="k-break"></div>\n'
		elif render_type == RenderTypes.MARKDOWN:
			return '\n\n'
		return ''


class CodeblockTag(Spread):

	def add_text(self, text, render_type = RenderTypes.HTML, preserve_linebreaks = False):
		if render_type == RenderTypes.HTML:
			text = self.make_render_safe(text, render_type)
		self.text += text

	def render(self, index, render_type = RenderTypes.HTML):
		if render_type == RenderTypes.HTML:
			return '<div id="{}" class="k-codeblock">{}</div>'.format(index, self.text)
		elif render_type == RenderTypes.MARKDOWN:
			return '```\n{}\n```\n\n'.format(self.text)
		return ''


class LiteralTag(Spread):

	def add_text(self, text, render_type = RenderTypes.HTML, preserve_linebreaks = False):
		self.text += text

	def render(self, index, render_type = RenderTypes.HTML):
		result = ''
		if render_type == RenderTypes.HTML:
			text = self.text
			for line in text.splitlines():
				result += '{}<br/>\n'.format(line)
		elif render_type == RenderTypes.MARKDOWN:
			result = '{}\n\n'.format(self.text)
		return result


class NoteTag(InlineSpread):

	def render(self, index, render_type = RenderTypes.HTML):
		safe_text = self.render_text(self.text, render_type)
		if render_type == RenderTypes.HTML:
			return '<table id="{}" class="k-note"><tr><td class="k-note-note">NOTE:</td><td>{}</td></tr></table>'.format(index, safe_text)
		elif render_type == RenderTypes.MARKDOWN:
			return '**NOTE:** {}\n\n'.format(safe_text)
		return ''


class ReturnTag(InlineSpread):

	def render(self, index, render_type = RenderTypes.HTML):
		safe_text = self.render_text(self.text, render_type)
		if render_type == RenderTypes.HTML:
			return '<div id="{}" class="k-return">Returns:<div class="k-return_desc">{}</div></div>'.format(index, safe_text)
		elif render_type == RenderTypes.MARKDOWN:
			return '**Returns:** {}\n\n'.format(safe_text)
		return ''


class DeflistTag(InlineSpread):

	def __init__(self, tag = None):
		self.text = ''
		self.type = tag
		self.tag = tag
		self.title = ''
		self.table_class = 'def'
		if tag == '@params':
			self.title = 'Parameters:'
			self.table_class = 'params'
		elif tag == '@attributes':
			self.title = 'Attributes:'
			self.table_class = 'attributes'
		elif tag == '@exceptions':
			self.title = 'Exceptions:'
			self.table_class = 'exceptions'
		elif tag == '@constants':
			self.title = 'Constants:'
			self.table_class = 'constants'

	def add_text(self, text, render_type = RenderTypes.HTML, preserve_linebreaks = False):
		text = self.make_render_safe(text, render_type)
		if ':' in text:
			self.text += '\n'
		else:
			self.text += ' '
		if preserve_linebreaks:
			self.text += '@'
		self.text += text

	def render(self, index, render_type = RenderTypes.HTML):
		result = ''
		if render_type == RenderTypes.HTML:
			result += '<div id="{}" class="k-params">{}<table class="k-{}">\n'.format(index, self.title, self.table_class)
			for line in self.text.splitlines():
				splits = line.split(':', 1)
				if len(splits) == 2:
					item = splits[0].strip()
					desc = self.render_text(splits[1].strip())
					result += '<tr><td class="k-var_name">{}</td><td class="k-var_desc">{}</td></tr>\n'.format(item, desc)
			result += '</table></div>'
		elif render_type == RenderTypes.MARKDOWN:
			if self.title:
				result += '**{}**\n\n'.format(self.title)
			for line in self.text.splitlines():
				splits = line.split(':', 1)
				if len(splits) == 2:
					item = splits[0].strip()
					desc = self.render_text(splits[1].strip(), render_type)
					result += '* ```{}```: {}\n'.format(item, desc)
			result += '\n'
		return result


class ListTag(InlineSpread):

	LIST_TAGS = {
		'@non-bulleted': {
			'html': 'ul',
			'md': '- ',
			'mark': '-',
		},
		'@bulleted': {
			'html': 'ul',
			'md': '* ',
			'mark': '*',
		},
		'@numbered': {
			'html': 'ol',
			'md': '1 ',
			'mark': '#',
		},
	}

	def __init__(self, tag = None):
		self.text = ''
		self.type = tag
		self.tag = tag

	def add_text(self, text, render_type = RenderTypes.HTML, preserve_linebreaks = False):
		text = self.make_render_safe(text, render_type)
		if text[0] in ['-', '*', '#']:
			self.text += '\n'
		else:
			self.text += ' '
		if preserve_linebreaks:
			self.text += '@'
		self.text += text

	def is_list_level(self, check_level, line):
		return len(line) > check_level and line[:check_level+1] == (self.mark*check_level) + ' '

	def render_html_list(self, check_level, line):
		result = ''
		if self.is_list_level(check_level, line):
			if self.level > check_level:
				# close the list
				for i in range(self.level, check_level, -1):
					result += '</{}>\n'.format(self.htmltag)
			elif self.level < check_level:
				result += '<{}>\n'.format(self.htmltag)
			self.level = check_level
			outstr = self.render_text(line[check_level+1:], RenderTypes.HTML)
			result += '<li>{}</li>\n'.format(outstr)
		return result

	def render_markdown_list(self, check_level, line):
		if self.is_list_level(check_level, line):
			return '  '*(check_level-1) + self.mdtag + self.render_text(line[check_level+1:], RenderTypes.MARKDOWN) + '\n'
		return ''

	def render(self, index, render_type = RenderTypes.HTML):
		result = ''
		self.htmltag = self.LIST_TAGS[self.tag]['html']
		self.mdtag = self.LIST_TAGS[self.tag]['md']
		self.mark = self.LIST_TAGS[self.tag]['mark']
		list_type = self.tag[1:]
		self.level = 1
		if render_type == RenderTypes.HTML:
			result += '<{} id="{}" class="k-{}">\n'.format(self.htmltag, index, list_type)
			for line in self.text.splitlines():
				result += self.render_html_list(1, line)
				result += self.render_html_list(2, line)
				result += self.render_html_list(3, line)
				result += self.render_html_list(4, line)
			# cleanup
			for i in range(self.level, 0, -1):
				result += '</{}>\n'.format(self.htmltag)
		elif render_type == RenderTypes.MARKDOWN:
			for line in self.text.splitlines():
				result += self.render_markdown_list(1, line)
				result += self.render_markdown_list(2, line)
				result += self.render_markdown_list(3, line)
				result += self.render_markdown_list(4, line)
			result += '\n'
		return result


class ImageTag(Spread):

	def __init__(self, tag = None):
		self.type = tag
		self.text = ''
		self.src = ''
		self.style = ''

	def add_text(self, text, render_type = RenderTypes.HTML, preserve_linebreaks = False):
		self.text = self.make_render_safe(text, render_type)
		textsplit = self.text.split()
		for item in textsplit:
			if '=' in item:
				key, val = item.split('=', 1)
				self.add_style(key, val)
			else:
				self.src = item

	def add_style(self, key, val):
		if key not in ['height', 'width']:
			return
		self.style += '{}:{};'.format(key, val)

	def render(self, index, render_type = RenderTypes.HTML):
		if render_type == RenderTypes.HTML:
			return'<img class="k-image" src="{}" style="{}" />'.format(self.src, self.style)
		elif render_type == RenderTypes.MARKDOWN:
			return '![]({})\n'.format(self.src)
		return ''





