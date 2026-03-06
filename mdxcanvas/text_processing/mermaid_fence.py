def make_mermaid_fence_shortcut():
    """
    Create a fence formatter that converts ```mermaid``` blocks to <mermaid> tags.

    This provides backward compatibility for fence-style mermaid blocks
    while using the new tag-based preprocessor system.
    """
    def mermaid_fence_format(source, language, css_class, options, md, **kwargs):
        # Build extra attributes from {: .class #id key="value" } syntax
        classes = kwargs.get('classes', [])
        id_value = kwargs.get('id_value', '')
        attrs = dict(kwargs.get('attrs', {}))

        if css_class and css_class not in classes:
            classes.insert(0, css_class)

        attr_parts = []
        if classes:
            attr_parts.append(f'class="{" ".join(classes)}"')
        if id_value:
            attr_parts.append(f'id="{id_value}"')
        if 'alt' in attrs:
            attr_parts.append(f'alt="{attrs["alt"]}"')

        extra_attrs = (' ' + ' '.join(attr_parts)) if attr_parts else ''

        # Return a <mermaid> tag that will be processed by the tag preprocessor
        return f'<mermaid{extra_attrs}>\n{source}\n</mermaid>'

    return mermaid_fence_format
