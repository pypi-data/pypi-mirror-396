"""
Sevk Markup Renderer
Converts Sevk markup to email-compatible HTML using regex-based parsing (like Node.js)
"""

import re
import html
import math
from typing import Dict, List, Tuple, Optional, Callable


class FontConfig:
    """Font configuration"""
    def __init__(self, id: str = "", name: str = "", url: str = ""):
        self.id = id
        self.name = name
        self.url = url


class EmailHeadSettings:
    """Head settings for email generation"""
    def __init__(self):
        self.title: str = ""
        self.preview_text: str = ""
        self.styles: str = ""
        self.fonts: List[FontConfig] = []


class ParsedEmailContent:
    """Parsed email content"""
    def __init__(self):
        self.body: str = ""
        self.head_settings: EmailHeadSettings = EmailHeadSettings()


def generate_email_from_markup(html_content: str, head_settings: Optional[EmailHeadSettings] = None) -> str:
    """Generate email HTML from Sevk markup"""
    if head_settings is not None:
        content_to_process = html_content
        settings = head_settings
    else:
        parsed = parse_email_html(html_content)
        content_to_process = parsed.body
        settings = parsed.head_settings

    normalized = _normalize_markup(content_to_process)
    processed = _process_markup(normalized)

    # Build head content
    title_tag = f"<title>{settings.title}</title>" if settings.title else ""
    font_links = _generate_font_links(settings.fonts)
    custom_styles = f'<style type="text/css">{settings.styles}</style>' if settings.styles else ""
    preview_text = f'<div style="display:none;font-size:1px;color:#ffffff;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">{settings.preview_text}</div>' if settings.preview_text else ""

    return f'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en" dir="ltr">
<head>
<meta content="text/html; charset=UTF-8" http-equiv="Content-Type"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
{title_tag}
{font_links}
{custom_styles}
</head>
<body style="margin:0;padding:0;font-family:ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;background-color:#ffffff">
{preview_text}
{processed}
</body>
</html>'''


def _normalize_markup(content: str) -> str:
    """Normalize markup by wrapping if needed"""
    result = content

    # Replace <link> with <sevk-link>
    if '<link' in result:
        result = re.sub(r'<link\s+href=', '<sevk-link href=', result, flags=re.IGNORECASE)
        result = result.replace('</link>', '</sevk-link>')

    if '<sevk-email' not in result and '<email' not in result and '<mail' not in result:
        result = f"<mail><body>{result}</body></mail>"

    return result


def _generate_font_links(fonts: List[FontConfig]) -> str:
    """Generate font link tags"""
    return '\n'.join([f'<link href="{f.url}" rel="stylesheet" type="text/css" />' for f in fonts])


def parse_email_html(content: str) -> ParsedEmailContent:
    """Parse email HTML and extract head settings"""
    if '<email>' in content or '<email ' in content or '<mail>' in content or '<mail ' in content:
        return _parse_sevk_markup(content)

    result = ParsedEmailContent()
    result.body = content
    return result


def _parse_sevk_markup(content: str) -> ParsedEmailContent:
    """Parse Sevk markup format"""
    head_settings = EmailHeadSettings()

    # Extract title
    title_match = re.search(r'<title[^>]*>([\s\S]*?)</title>', content, re.IGNORECASE)
    if title_match:
        head_settings.title = title_match.group(1).strip()

    # Extract preview
    preview_match = re.search(r'<preview[^>]*>([\s\S]*?)</preview>', content, re.IGNORECASE)
    if preview_match:
        head_settings.preview_text = preview_match.group(1).strip()

    # Extract styles
    style_match = re.search(r'<style[^>]*>([\s\S]*?)</style>', content, re.IGNORECASE)
    if style_match:
        head_settings.styles = style_match.group(1).strip()

    # Extract fonts
    font_pattern = r'<font[^>]*name=["\']([^"\']*)["\'][^>]*url=["\']([^"\']*)["\'][^>]*/?\s*>'
    for i, match in enumerate(re.finditer(font_pattern, content, re.IGNORECASE)):
        head_settings.fonts.append(FontConfig(
            id=f"font-{i}",
            name=match.group(1),
            url=match.group(2)
        ))

    # Extract body
    body_match = re.search(r'<body[^>]*>([\s\S]*?)</body>', content, re.IGNORECASE)
    if body_match:
        body = body_match.group(1).strip()
    else:
        body = content
        patterns = [
            r'<email[^>]*>', r'</email>',
            r'<mail[^>]*>', r'</mail>',
            r'<head[^>]*>[\s\S]*?</head>',
            r'<title[^>]*>[\s\S]*?</title>',
            r'<preview[^>]*>[\s\S]*?</preview>',
            r'<style[^>]*>[\s\S]*?</style>',
            r'<font[^>]*>[\s\S]*?</font>',
            r'<font[^>]*/?>',
        ]
        for pattern in patterns:
            body = re.sub(pattern, '', body, flags=re.IGNORECASE)
        body = body.strip()

    result = ParsedEmailContent()
    result.body = body
    result.head_settings = head_settings
    return result


def _process_markup(content: str) -> str:
    """Process markup using regex-based parsing (like Node.js)"""
    result = content

    # Process section tags
    result = _process_tag(result, 'section', lambda attrs, inner:
        f'''<table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="{_style_to_string(_extract_all_style_attributes(attrs))}">
<tbody>
<tr>
<td>{inner}</td>
</tr>
</tbody>
</table>''')

    # Process row tags
    result = _process_tag(result, 'row', lambda attrs, inner:
        f'''<table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="{_style_to_string(_extract_all_style_attributes(attrs))}">
<tbody style="width:100%">
<tr style="width:100%">{inner}</tr>
</tbody>
</table>''')

    # Process column tags
    result = _process_tag(result, 'column', lambda attrs, inner:
        f'<td style="{_style_to_string(_extract_all_style_attributes(attrs))}">{inner}</td>')

    # Process container tags
    result = _process_tag(result, 'container', lambda attrs, inner:
        f'''<table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="{_style_to_string(_extract_all_style_attributes(attrs))}">
<tbody>
<tr style="width:100%">
<td>{inner}</td>
</tr>
</tbody>
</table>''')

    # Process heading tags
    def process_heading(attrs: Dict[str, str], inner: str) -> str:
        level = attrs.get('level', '1')
        style = _extract_all_style_attributes(attrs)
        return f'<h{level} style="{_style_to_string(style)}">{inner}</h{level}>'
    result = _process_tag(result, 'heading', process_heading)

    # Process paragraph tags
    result = _process_tag(result, 'paragraph', lambda attrs, inner:
        f'<p style="{_style_to_string(_extract_all_style_attributes(attrs))}">{inner}</p>')

    # Process text tags
    result = _process_tag(result, 'text', lambda attrs, inner:
        f'<span style="{_style_to_string(_extract_all_style_attributes(attrs))}">{inner}</span>')

    # Process button tags with MSO compatibility
    result = _process_tag(result, 'button', _process_button)

    # Process image tags
    def replace_image(match):
        attrs = _parse_attributes(match.group(1) or '')
        src = attrs.get('src', '')
        alt = attrs.get('alt', '')
        width = attrs.get('width')
        height = attrs.get('height')

        style = _extract_all_style_attributes(attrs)
        if 'outline' not in style:
            style['outline'] = 'none'
        if 'border' not in style:
            style['border'] = 'none'
        if 'text-decoration' not in style:
            style['text-decoration'] = 'none'

        style_str = _style_to_string(style)
        width_attr = f' width="{width}"' if width else ''
        height_attr = f' height="{height}"' if height else ''

        return f'<img src="{src}" alt="{alt}"{width_attr}{height_attr} style="{style_str}" />'

    result = re.sub(r'<image([^>]*)/?>',  replace_image, result, flags=re.IGNORECASE)

    # Process divider tags
    def replace_divider(match):
        attrs = _parse_attributes(match.group(1) or '')
        style = _extract_all_style_attributes(attrs)
        style_str = _style_to_string(style)
        class_attr = attrs.get('class') or attrs.get('className')
        class_str = f' class="{class_attr}"' if class_attr else ''
        return f'<hr style="{style_str}"{class_str} />'

    result = re.sub(r'<divider([^>]*)/?>',  replace_divider, result, flags=re.IGNORECASE)

    # Process link tags
    def process_link(attrs: Dict[str, str], inner: str) -> str:
        href = attrs.get('href', '#')
        target = attrs.get('target', '_blank')
        style = _extract_all_style_attributes(attrs)
        return f'<a href="{href}" target="{target}" style="{_style_to_string(style)}">{inner}</a>'
    result = _process_tag(result, 'sevk-link', process_link)

    # Process list tags
    def process_list(attrs: Dict[str, str], inner: str) -> str:
        list_type = attrs.get('type', 'unordered')
        tag = 'ol' if list_type == 'ordered' else 'ul'
        style = _extract_all_style_attributes(attrs)
        if 'list-style-type' in attrs:
            style['list-style-type'] = attrs['list-style-type']
        style_str = _style_to_string(style)
        class_attr = attrs.get('class') or attrs.get('className')
        class_str = f' class="{class_attr}"' if class_attr else ''
        return f'<{tag} style="{style_str}"{class_str}>{inner}</{tag}>'
    result = _process_tag(result, 'list', process_list)

    # Process list item tags
    def process_li(attrs: Dict[str, str], inner: str) -> str:
        style = _extract_all_style_attributes(attrs)
        style_str = _style_to_string(style)
        class_attr = attrs.get('class') or attrs.get('className')
        class_str = f' class="{class_attr}"' if class_attr else ''
        return f'<li style="{style_str}"{class_str}>{inner}</li>'
    result = _process_tag(result, 'li', process_li)

    # Process codeblock tags
    def process_codeblock(attrs: Dict[str, str], inner: str) -> str:
        style = _extract_all_style_attributes(attrs)
        if 'width' not in style:
            style['width'] = '100%'
        if 'box-sizing' not in style:
            style['box-sizing'] = 'border-box'
        style_str = _style_to_string(style)
        escaped = inner.replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre style="{style_str}"><code>{escaped}</code></pre>'
    result = _process_tag(result, 'codeblock', process_codeblock)

    # Clean up wrapper tags
    wrapper_patterns = [
        r'<sevk-email[^>]*>', r'</sevk-email>',
        r'<sevk-body[^>]*>', r'</sevk-body>',
        r'<email[^>]*>', r'</email>',
        r'<mail[^>]*>', r'</mail>',
        r'<body[^>]*>', r'</body>',
    ]
    for pattern in wrapper_patterns:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)

    return result.strip()


def _process_button(attrs: Dict[str, str], inner: str) -> str:
    """Process button with MSO compatibility (like Node.js)"""
    href = attrs.get('href', '#')
    style = _extract_all_style_attributes(attrs)

    # Parse padding
    padding_top, padding_right, padding_bottom, padding_left = _parse_padding(style)

    y = padding_top + padding_bottom
    text_raise = _px_to_pt(y)

    pl_font_width, pl_space_count = _compute_font_width_and_space_count(padding_left)
    pr_font_width, pr_space_count = _compute_font_width_and_space_count(padding_right)

    button_style = {
        'line-height': '100%',
        'text-decoration': 'none',
        'display': 'inline-block',
        'max-width': '100%',
        'mso-padding-alt': '0px',
    }

    # Merge with extracted styles
    button_style.update(style)

    # Override padding with parsed values
    button_style['padding-top'] = f'{padding_top}px'
    button_style['padding-right'] = f'{padding_right}px'
    button_style['padding-bottom'] = f'{padding_bottom}px'
    button_style['padding-left'] = f'{padding_left}px'

    style_str = _style_to_string(button_style)

    left_mso_spaces = '&#8202;' * pl_space_count
    right_mso_spaces = '&#8202;' * pr_space_count

    return f'<a href="{href}" target="_blank" style="{style_str}"><!--[if mso]><i style="mso-font-width:{round(pl_font_width * 100)}%;mso-text-raise:{text_raise}" hidden>{left_mso_spaces}</i><![endif]--><span style="max-width:100%;display:inline-block;line-height:120%;mso-padding-alt:0px;mso-text-raise:{_px_to_pt(padding_bottom)}">{inner}</span><!--[if mso]><i style="mso-font-width:{round(pr_font_width * 100)}%" hidden>{right_mso_spaces}&#8203;</i><![endif]--></a>'


def _parse_padding(style: Dict[str, str]) -> Tuple[int, int, int, int]:
    """Parse padding values from style"""
    if 'padding' in style:
        parts = style['padding'].split()
        if len(parts) == 1:
            val = _parse_px(parts[0])
            return val, val, val, val
        elif len(parts) == 2:
            vertical = _parse_px(parts[0])
            horizontal = _parse_px(parts[1])
            return vertical, horizontal, vertical, horizontal
        elif len(parts) == 4:
            return _parse_px(parts[0]), _parse_px(parts[1]), _parse_px(parts[2]), _parse_px(parts[3])

    return (
        _parse_px(style.get('padding-top', '0')),
        _parse_px(style.get('padding-right', '0')),
        _parse_px(style.get('padding-bottom', '0')),
        _parse_px(style.get('padding-left', '0')),
    )


def _parse_px(s: str) -> int:
    """Parse px value"""
    return int(s.replace('px', '')) if s else 0


def _px_to_pt(px: int) -> int:
    """Convert px to pt for MSO"""
    return (px * 3) // 4


def _compute_font_width_and_space_count(expected_width: int) -> Tuple[float, int]:
    """Compute font width and space count for MSO padding"""
    if expected_width == 0:
        return 0, 0

    smallest_space_count = 0
    max_font_width = 5.0

    while True:
        if smallest_space_count > 0:
            required_font_width = expected_width / smallest_space_count / 2.0
        else:
            required_font_width = math.inf

        if required_font_width <= max_font_width:
            return required_font_width, smallest_space_count
        smallest_space_count += 1


def _process_tag(content: str, tag_name: str, processor: Callable[[Dict[str, str], str], str]) -> str:
    """Process a tag with regex-based parsing"""
    result = content
    open_pattern = f'<{tag_name}([^>]*)>'
    close_tag = f'</{tag_name}>'
    open_tag_start = f'<{tag_name}'

    max_iterations = 10000
    iterations = 0

    while iterations < max_iterations:
        iterations += 1

        # Find all opening tags
        matches = list(re.finditer(open_pattern, result, re.IGNORECASE))
        if not matches:
            break

        processed = False

        # Find the innermost tag (one that has no nested same tags)
        for i in range(len(matches) - 1, -1, -1):
            match = matches[i]
            start = match.start()
            inner_start = match.end()
            attrs_str = match.group(1)

            # Find the next close tag after this opening tag
            close_pos = result.lower().find(close_tag.lower(), inner_start)
            if close_pos == -1:
                continue

            inner = result[inner_start:close_pos]

            # Check if there's another opening tag inside
            if open_tag_start.lower() in inner.lower():
                # This tag has nested same tags, skip it
                continue

            # This is an innermost tag, process it
            attrs = _parse_attributes(attrs_str)
            replacement = processor(attrs, inner)
            end = close_pos + len(close_tag)

            result = result[:start] + replacement + result[end:]
            processed = True
            break

        if not processed:
            break

    return result


def _parse_attributes(attrs_str: str) -> Dict[str, str]:
    """Parse attributes from an attribute string"""
    attrs = {}
    for match in re.finditer(r'([\w-]+)=["\']([^"\']*)["\']', attrs_str):
        attrs[match.group(1)] = match.group(2)
    return attrs


def _extract_all_style_attributes(attrs: Dict[str, str]) -> Dict[str, str]:
    """Extract all style attributes from element attributes (like Node.js extractStyleAttributes)"""
    style = {}

    # Typography attributes
    if 'text-color' in attrs:
        style['color'] = attrs['text-color']
    elif 'color' in attrs:
        style['color'] = attrs['color']
    if 'background-color' in attrs:
        style['background-color'] = attrs['background-color']
    if 'font-size' in attrs:
        style['font-size'] = attrs['font-size']
    if 'font-family' in attrs:
        style['font-family'] = attrs['font-family']
    if 'font-weight' in attrs:
        style['font-weight'] = attrs['font-weight']
    if 'line-height' in attrs:
        style['line-height'] = attrs['line-height']
    if 'text-align' in attrs:
        style['text-align'] = attrs['text-align']
    if 'text-decoration' in attrs:
        style['text-decoration'] = attrs['text-decoration']

    # Dimensions
    if 'width' in attrs:
        style['width'] = attrs['width']
    if 'height' in attrs:
        style['height'] = attrs['height']
    if 'max-width' in attrs:
        style['max-width'] = attrs['max-width']
    if 'min-height' in attrs:
        style['min-height'] = attrs['min-height']

    # Spacing - Padding
    if 'padding' in attrs:
        style['padding'] = attrs['padding']
    else:
        if 'padding-top' in attrs:
            style['padding-top'] = attrs['padding-top']
        if 'padding-right' in attrs:
            style['padding-right'] = attrs['padding-right']
        if 'padding-bottom' in attrs:
            style['padding-bottom'] = attrs['padding-bottom']
        if 'padding-left' in attrs:
            style['padding-left'] = attrs['padding-left']

    # Spacing - Margin
    if 'margin' in attrs:
        style['margin'] = attrs['margin']
    else:
        if 'margin-top' in attrs:
            style['margin-top'] = attrs['margin-top']
        if 'margin-right' in attrs:
            style['margin-right'] = attrs['margin-right']
        if 'margin-bottom' in attrs:
            style['margin-bottom'] = attrs['margin-bottom']
        if 'margin-left' in attrs:
            style['margin-left'] = attrs['margin-left']

    # Borders
    if 'border' in attrs:
        style['border'] = attrs['border']
    else:
        if 'border-top' in attrs:
            style['border-top'] = attrs['border-top']
        if 'border-right' in attrs:
            style['border-right'] = attrs['border-right']
        if 'border-bottom' in attrs:
            style['border-bottom'] = attrs['border-bottom']
        if 'border-left' in attrs:
            style['border-left'] = attrs['border-left']
        if 'border-color' in attrs:
            style['border-color'] = attrs['border-color']
        if 'border-width' in attrs:
            style['border-width'] = attrs['border-width']
        if 'border-style' in attrs:
            style['border-style'] = attrs['border-style']

    # Border Radius
    if 'border-radius' in attrs:
        style['border-radius'] = attrs['border-radius']
    else:
        if 'border-top-left-radius' in attrs:
            style['border-top-left-radius'] = attrs['border-top-left-radius']
        if 'border-top-right-radius' in attrs:
            style['border-top-right-radius'] = attrs['border-top-right-radius']
        if 'border-bottom-left-radius' in attrs:
            style['border-bottom-left-radius'] = attrs['border-bottom-left-radius']
        if 'border-bottom-right-radius' in attrs:
            style['border-bottom-right-radius'] = attrs['border-bottom-right-radius']

    return style


def _style_to_string(style: Dict[str, str]) -> str:
    """Convert style dict to inline style string"""
    return ';'.join([f'{k}:{v}' for k, v in style.items()])


def render(markup: str) -> str:
    """
    Render Sevk markup to email-compatible HTML

    Args:
        markup: The Sevk markup to render

    Returns:
        The rendered HTML string
    """
    return generate_email_from_markup(markup)


class Renderer:
    """Renderer class for compatibility"""

    def render(self, markup: str) -> str:
        """Render Sevk markup to email-compatible HTML"""
        return generate_email_from_markup(markup)
