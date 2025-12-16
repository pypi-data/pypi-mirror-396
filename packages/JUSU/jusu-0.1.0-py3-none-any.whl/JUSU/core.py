"""
JUSU - A tiny beginner-friendly HTML builder library

This module provides simple Tag classes to build HTML using plain-English
style Python syntax. The API is intentionally forgiving for beginners:
- strings passed as children are auto-wrapped into paragraphs where sensible
- `cls` maps to the HTML `class` attribute
- `render()` returns HTML string
- `render_to_file()` writes an HTML string to a file

Supported tags: Div, H1, P, Button, Img, Span, Ul, Li, Br, Hr, Input

Usage (demo at bottom):
	page = Div(H1("Hello"), P("Welcome."), Button("Click me", onclick="alert('Hi')"))
	print(page.render())
"""
from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from typing import Any, Iterable, List, MutableMapping, Optional
import os


class JusuError(Exception):
	"""Base class for JUSU errors."""


class UnknownAttributeError(JusuError):
	"""Raised when an attribute is invalid or intentionally forbidden."""


class EmptyTagError(JusuError):
	"""Raised when a non-self-closing tag is created without children."""


def _is_string_like(value: Any) -> bool:
	return isinstance(value, (str,))


def _debug(msg: str) -> None:
	# Lightweight debug helper; keep no-op by default to avoid noisy output.
	# Developers can monkeypatch or override during debugging if needed.
	return


@dataclass
class Tag:
	"""Generic HTML tag builder.

	Parameters:
	- name: tag name (e.g. 'div')
	- children: nested string or Tag objects
	- attrs: keyword arguments for attributes (uses 'cls' for class)
	"""

	name: str
	_children: List[Any] = field(default_factory=list)
	_attrs: MutableMapping[str, Any] = field(default_factory=dict)
	self_closing: bool = False
	allow_empty: bool = False

	# A small set of attribute names we specially support mapping for.
	_attr_aliases = {
		"cls": "class",
		"classname": "class",
		# leave 'id', 'style', 'onclick' as-is
	}

	def __init__(self, *children: Any, **attrs: Any) -> None:
		# initialize dataclass fields
		object.__setattr__(self, "name", getattr(self, "name", self.__class__.__name__.lower()))
		object.__setattr__(self, "_children", [])
		object.__setattr__(self, "_attrs", {})

		# Special attribute mapping: accept 'cls' and 'class' (for flexibility)
		for key, value in attrs.items():
			key_str = str(key)
			if key_str in self._attr_aliases:
				key_str = self._attr_aliases[key_str]
			if key_str == "class":
				# `class` is a valid HTML attribute; allow passing via 'cls' or 'class'.
				self._attrs["class"] = value
			else:
				# Allow most attributes but restrict obviously invalid keys.
				if not key_str.replace("-", "").isalnum():
					raise UnknownAttributeError(f"Invalid attribute name: '{key}'.")
				self._attrs[key_str] = value

		# Add children (strings or Tag objects). Auto-wrap strings where sensible.
		for child in children:
			self.add(child)

		# Validation at construction time: non-self-closing tags must not be empty
		if not getattr(self, "self_closing", False) and not getattr(self, "allow_empty", False):
			if len(self._children) == 0:
				raise EmptyTagError(f"Tag <{self.name}> is empty. Add children or use allow_empty=True.")

	def add(self, child: Any) -> Tag:
		"""Add a child (string or Tag) to this tag in a forgiving way.

		- Strings are wrapped in `P` unless this tag expects inline content.
		- Strings under `ul` become `Li` elements.
		- Tag children are added as-is.
		"""
		# Handle None silently
		if child is None:
			return self

		# Allow lists/iterables to be flattened
		if isinstance(child, (list, tuple)):
			for c in child:
				self.add(c)
			return self

		# If child is a string, decide a sensible wrapper
		if _is_string_like(child):
			text = str(child)
			# In a UL, text should be wrapped into LI. For inline tags and
			# text-holding tags like P/H1/Li/Span/Button we insert text directly
			if self.name == "ul":
				self._children.append(Li(text))
			elif self.name in {"span", "button", "p", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
				self._children.append(text)
			else:
				# For block containers like div, wrap plain text into paragraphs
				self._children.append(P(text))
			return self

		# If child is already a Tag, append
		if isinstance(child, Tag):
			self._children.append(child)
			return self

		# Finally, try converting to str and add
		self._children.append(str(child))
		return self

	def _render_attrs(self) -> str:
		"""Render attributes mapping, escaping values appropriately."""
		pieces: List[str] = []
		for k, v in self._attrs.items():
			if v is True:
				pieces.append(f"{k}")
			elif v is False or v is None:
				continue
			else:
				# Accept style as dict for beginner-friendliness
				if k == "style" and isinstance(v, dict):
					style_str = "; ".join(f"{prop}: {val}" for prop, val in v.items())
					pieces.append(f'{k}="{escape(style_str, quote=True)}"')
				else:
					pieces.append(f'{k}="{escape(str(v), quote=True)}"')
		return " " + " ".join(pieces) if pieces else ""

	def render(self, indent: Optional[int] = 0, pretty: bool = True) -> str:
		"""Return the HTML string for this tag, optionally pretty-printed.

		- `indent` indicates number of spaces to indent the current tag.
		- `pretty` when True inserts newlines and indentation for readability.
		"""
		space = " " * (indent or 0)
		nl = "\n" if pretty else ""
		attrs = self._render_attrs()

		if getattr(self, "self_closing", False):
			return f"{space}<{self.name}{attrs} />{nl}"

		if not self._children and not getattr(self, "allow_empty", False):
			# defensive check: if children are absent, we raise the informative error
			raise EmptyTagError(f"Tag <{self.name}> is empty and may be accidental.")

		# render children
		rendered_children: List[str] = []
		for child in self._children:
			if isinstance(child, Tag):
				rendered_children.append(child.render(indent=(indent or 0) + 2, pretty=pretty))
			else:
				# text node - escape HTML
				text = escape(str(child))
				if pretty:
					rendered_children.append(f"{' ' * ((indent or 0) + 2)}{text}{nl}")
				else:
					rendered_children.append(text)

		content = "".join(rendered_children)
		if pretty:
			return f"{space}<{self.name}{attrs}>{nl}{content}{space}</{self.name}>{nl}"
		else:
			return f"<{self.name}{attrs}>{content}</{self.name}>"

	def render_to_file(self, filename: str, pretty: bool = True, doctype: bool = True) -> None:
		"""Write the HTML for this tag to a file.

		By default the rendered file contains a minimal HTML document wrapper
		unless the tag is intended to be used as a fragment. Beginners will
		find a full document more useful by default.
		"""
		body = self.render(pretty=pretty)
		# Small friendly document wrapper for beginners
		head = "<head>\n<meta charset=\"utf-8\">\n</head>\n"
		html_doc = f"<html>\n{head}<body>\n{body}\n</body>\n</html>\n"
		if doctype:
			full = "<!DOCTYPE html>\n" + html_doc
		else:
			full = html_doc

		with open(filename, "w", encoding="utf-8") as fh:
			fh.write(full)


# Tag subclasses (small, readable wrappers)
class Div(Tag):
	name = "div"


class H1(Tag):
	name = "h1"


class P(Tag):
	name = "p"


class Button(Tag):
	name = "button"


class Img(Tag):
	name = "img"
	self_closing = True

	def __init__(self, *children: Any, **attrs: Any) -> None:
		# Img is self-closing; children are not allowed
		if children:
			raise JusuError("Img is a self-closing tag and cannot contain children.")
		super().__init__(**attrs)


class Span(Tag):
	name = "span"
	allow_empty = True


class Ul(Tag):
	name = "ul"


class Li(Tag):
	name = "li"


class Input(Tag):
	name = "input"
	self_closing = True

	def __init__(self, *children: Any, **attrs: Any) -> None:
		if children:
			raise JusuError("Input is a self-closing tag and cannot contain children.")
		super().__init__(**attrs)


class Br(Tag):
	name = "br"
	self_closing = True


class Hr(Tag):
	name = "hr"
	self_closing = True


# Minimal demo (runs when module executed directly)
def _demo():
	header = H1("Welcome to JUSU")
	para = P("A tiny HTML builder for beginners.")
	button = Button("Click me", onclick="alert('Hello from JUSU')", cls="btn")
	image = Img(src="https://via.placeholder.com/150", alt="Demo image")
	page = Div(header, para, button, image, cls="container")
	outfile = os.path.join(os.getcwd(), "jusu_demo.html")
	page.render_to_file(outfile)
	print(f"Demo written to {outfile}")


if __name__ == "__main__":
	_demo()

