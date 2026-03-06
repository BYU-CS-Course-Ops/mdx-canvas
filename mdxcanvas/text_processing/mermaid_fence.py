from html import escape


def make_mermaid_fence_shortcut():
    """
    Create a fence formatter that converts ```mermaid``` blocks to <mermaid> tags.

    This provides backward compatibility for fence-style mermaid blocks
    while using the new tag-based preprocessor system.
    """
    def mermaid_fence_format(source, language, css_class, options, md, **kwargs):
        # Build extra attributes from {: .class key="value" } syntax
        classes = kwargs.get('classes', [])
        attrs = dict(kwargs.get('attrs', {}))

        if css_class and css_class not in classes:
            classes.insert(0, css_class)

        attr_parts = []
        if classes:
            class_value = ' '.join(classes)
            attr_parts.append(f'class="{escape(class_value, quote=True)}"')

        # Pass through custom key/value attributes to the <mermaid> tag.
        for key, value in attrs.items():
            attr_parts.append(f'{key}="{escape(str(value), quote=True)}"')

        extra_attrs = (' ' + ' '.join(attr_parts)) if attr_parts else ''

        # Return a <mermaid> tag that will be processed by the tag preprocessor
        return f'<mermaid{extra_attrs}>\n{source}\n</mermaid>'

    return mermaid_fence_format
