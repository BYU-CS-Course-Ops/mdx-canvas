from bs4 import BeautifulSoup

from mdxcanvas.markdown_processing import process_markdown


def test_process_markdown():
    text = """
    # baz
    <div>
    **foo**
    <div>*bar*</div>
    <special>**nope**</special>
    </div>
    <quiz><description>This is **bold**</description></quiz>
    """

    xml = process_markdown(text, ['special'])

    expected = """
    <h1>baz</h1>
    <div>
    <p><strong>foo</strong></p>
    <div><p><em>bar</em></p></div>
    <special>**nope**</special>
    </div>
    <quiz><description><p>This is <strong>bold</strong></p></description></quiz>
    """

    assert BeautifulSoup(xml, 'html.parser').prettify() \
           == BeautifulSoup(expected, 'html.parser').prettify()
