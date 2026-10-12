"""Read-only checks for content preservation, navigation and local assets.

Run from the repository root: python -X utf8 tests/verify_site.py
"""
from collections import Counter
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = '8b69e0eea7c29f3e75f40d19b5c3bd6caf3a71f1'
PAGES = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
PAGES = [p for p in PAGES if p.endswith('.html')]


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.text = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def text(source):
    return ' '.join(' '.join(Document(source).text).split())


def original_copy(source):
    body = source.split('<article class="article-body">', 1)[1]
    marker = '<h3>15從Line對話到故事</h3>'
    # The legacy export repeats its 16-item navigation exactly three times.
    for _ in range(3):
        body = body.split(marker, 1)[1]
    body = re.split(r'<section class="gallery-section">|<nav class="sequence-nav"', body, maxsplit=1)[0]
    for label in ('Google Sites', 'Report abuse', 'Page details', 'Page updated'):
        body = body.replace('<p>' + label + '</p>', '')
    return text(body)


class WebsiteChecks(unittest.TestCase):
    def test_article_text_is_preserved_after_export_navigation_cleanup(self):
        for page in PAGES:
            with self.subTest(page=page):
                before = subprocess.check_output(['git', 'show', f'{BASE}:{page}'], cwd=ROOT).decode('utf-8')
                after = (ROOT / page).read_text(encoding='utf-8')
                copy = re.search(r'<!-- article-copy:start -->(.*?)<!-- article-copy:end -->', after, re.S)
                self.assertIsNotNone(copy, 'The readable article region must be identifiable')
                self.assertEqual(original_copy(before), text(copy[1]), 'Article text was lost or changed')

    def test_existing_photographs_keep_their_page_and_order(self):
        for page in PAGES:
            with self.subTest(page=page):
                before = subprocess.check_output(['git', 'show', f'{BASE}:{page}'], cwd=ROOT).decode('utf-8')
                after = (ROOT / page).read_text(encoding='utf-8')
                photos = lambda s: [a['src'] for t, a in Document(s).tags if t == 'img' and 'photo-thumb' in a.get('class', '').split()]
                self.assertEqual(photos(before), photos(after))

    def test_every_page_exposes_its_current_location_and_working_local_links(self):
        for page in PAGES:
            with self.subTest(page=page):
                source = (ROOT / page).read_text(encoding='utf-8')
                doc = Document(source)
                current = [a for t, a in doc.tags if a.get('aria-current') == 'page']
                self.assertEqual(len(current), 1)
                self.assertEqual(current[0].get('href'), page)
                self.assertEqual(sum(t == 'h1' for t, a in doc.tags), 1)
                ids = [a['id'] for _, a in doc.tags if 'id' in a]
                self.assertEqual(len(ids), len(set(ids)), 'Duplicate HTML id')
                self.assertTrue(any(t == 'details' and a.get('class') == 'site-menu' for t, a in doc.tags), 'Menu needs a no-JavaScript fallback')
                for tag, attrs in doc.tags:
                    for name in ('src', 'href'):
                        value = attrs.get(name)
                        if not value or value.startswith('#'):
                            continue
                        parsed = urlsplit(unescape(value))
                        if parsed.scheme or parsed.netloc:
                            continue
                        self.assertTrue((ROOT / unquote(parsed.path)).is_file(), f'Missing asset: {value}')

    def test_articles_have_no_sidebar_contents(self):
        for page in PAGES:
            with self.subTest(page=page):
                source = (ROOT / page).read_text(encoding='utf-8')
                self.assertFalse(any('article-toc' in a.get('class', '').split() for _, a in Document(source).tags))

    def test_homepage_gives_a_real_link_to_every_chapter(self):
        source = (ROOT / 'index.html').read_text(encoding='utf-8')
        section = re.search(r'<!-- chapter-index:start -->(.*?)<!-- chapter-index:end -->', source, re.S)
        self.assertIsNotNone(section, 'Homepage needs chapter entry points')
        links = [a.get('href') for t, a in Document(section[1]).tags if t == 'a']
        self.assertEqual(Counter(links), Counter(p for p in PAGES if p != 'index.html'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
