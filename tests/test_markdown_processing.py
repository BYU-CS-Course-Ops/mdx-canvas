from bs4 import BeautifulSoup

from mdxcanvas.text_processing.jinja_processing import _read_md_table
from mdxcanvas.text_processing.markdown_processing import process_markdown


def test_process_markdown():
    text = """
    # baz
    <div>
    **foo**
    <div>*bar*</div>
    <special>**nope**</special>
    </div>
    <quiz><description>This is **bold**</description></quiz>
    <div>Click <a src='foo'>here</a>.</div>
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
    <div>Click <a src='foo'>here</a>.</div>
    """
    assert BeautifulSoup(xml, 'html.parser').prettify() \
           == BeautifulSoup(expected, 'html.parser').prettify()


def test_markdown_data():
    text = '''
    # Foo
    | Key | Value |
    |-----|-------|
    | k1  | v1    |
    | k2  | v2    |
    
    ### Long
    blah blah blah
    
    ## Bar
    
    | b1 | b2 |
    |----|----|
    |  1 |  a |
    |  2 |  b |
    
    ## Baz
    
    | z1 | z2 |
    |----|----|
    |  1 |  c |
    |  2 |  d |
    
    # Foobar
    
    | a | b | c |
    |---|---|---|
    | 1 | 2 | 3 |
    
    '''
    data = _read_md_table(text)

    assert data == [
        {
            'Title': 'Foo',
            'k1': 'v1',
            'k2': 'v2',
            'Long': '<p>blah blah blah</p>',
            'Bar': [
                {'b1': '1', 'b2': 'a'},
                {'b1': '2', 'b2': 'b'}
            ],
            'Baz': [
                {'z1': '1', 'z2': 'c'},
                {'z1': '2', 'z2': 'd'}
            ]
        },
        {
            'Title': 'Foobar',
            'a': '1',
            'b': '2',
            'c': '3'
        }
    ]


