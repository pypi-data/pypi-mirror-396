from JUSU.core import Div, H1, P, Button, Img, Ul, Li, Input, JusuError, UnknownAttributeError, EmptyTagError
import os


def test_basic_rendering(tmp_path):
	header = H1("Hello")
	para = P("This is a paragraph.")
	btn = Button("Click", onclick="alert('ok')", cls="btn")
	img = Img(src="https://example.com/image.png", alt="an image")
	page = Div(header, para, btn, img, cls="main")
	html = page.render(pretty=False)
	assert "<h1" in html
	assert "<p>" in html
	assert "onclick='alert'" or "onclick=" in html or "onclick" in html


def test_self_closing_and_wrapping():
	u = Ul("Item 1", "Item 2")
	out = u.render(pretty=False)
	assert "<li>" in out
	# Img must be self closing and not accept children
	try:
		Img("child")
		assert False, "Img should not accept children"
	except JusuError:
		pass
	# Input must be self-closing and not accept children
	try:
		Input("child")
		assert False, "Input should not accept children"
	except JusuError:
		pass


def test_attribute_validation_and_empty_errors():
	# Invalid attribute name passed via expansion
	try:
		Div("X", **{"bad$name": "x"})
		assert False, "Invalid attribute name should raise"
	except UnknownAttributeError:
		pass

	# Empty div should raise
	try:
		Div()
		assert False, "EmptyTagError expected"
	except EmptyTagError:
		pass


def test_render_to_file(tmp_path):
	header = H1("File test")
	page = Div(header, cls="wrap")
	out = tmp_path / "out.html"
	page.render_to_file(str(out))
	assert out.exists()
	content = out.read_text(encoding="utf-8")
	assert "<!DOCTYPE html>" in content


def test_style_dict_and_cls_mapping():
	# Support passing style as dict and mapping 'cls' to class attribute
	p = P("Styled paragraph", cls="lead", style={"color": "red", "font-weight": "bold"})
	html = p.render(pretty=False)
	assert 'class="lead"' in html
	assert 'style="color: red; font-weight: bold"' in html
