"""
Pintes Demo.

This file (and only this demo.py file) is under CC0
"""
import pintes

# Create a new Pint object
root = pintes.CreatePint()

# Give the page a title (this shows up in the tab)
root.retitle_page('Pintes Demo')

# ...and give it an icon. (called a favicon)
root.add_favicon('favicon.ico')

# Let's add some metadata to the page. This is useful for search engines.
root.add_metadata('author', 'Formuna')
# This is equivalent to
# <meta name="author" content="Formuna">

# This is equivalent to <meta name="description" content="A Pintes demo">
root.add_metadata('description', 'A Pintes demo') 

# Create a h1 tag with the header function (the default for level is 1, the largest)
root.create.header('Hello, World!', level=1)

# You can use the p(aragraph) function to generate a paragraph element.
root.create.p('This is a paragraph tag')

# Creating an anchor tag can't be done with the `create()` function for now.
# Instead, use `create_anchor()`.
root.create.a('Click me!', 'https://example.com')

# Creating a div is fairly easy, since it's just creating another Pint.
divRoot = pintes.CreatePint()

# Adding a paragraph inside the div is the same as adding a paragraph to the root,
# except you use the divRoot instead of the root.
divRoot.create.header('This is in a div tag!', level=2)
divRoot.create.p('This is also inside a div tag!')

# If you export now, the div will not be show up since it is a different Pint.
# In order to merge them, you need to use `merge_pints()` function.
root.pint_merge(divRoot)
# ^ This will merge the divRoot into the root Pint.
# It is recommended to write this right before exporting.

# Before we export, let's add some CSS to the page.
# If you have a CSS file,
# Use Python's built-in file reading functions to pipe
# the file contents to `add_css()`.
css_file_contents = open('demo.css', 'r').read()
root.add_css(css_file_contents)

# Let's also create a p tag with a class, and some CSS to go with it.
# Remember that not specifying the `tag` parameter will
# default to a paragraph tag.
root.create_custom('This is a stylized paragraph with a class.', className='demo-class')
root.create_custom('This is a centered paragraph with a class.', className='centered')

# Let's add an image to the page.
# It's recommended to write a small description in the `alt` parameter incase
# the image doesn't load or a screen reader is used.
# The `width` and `height` parameters internally lead to the `style` attribute
# of the image tag, so you can use any CSS units such as px, em, %, etc.
# Or you could just use CSS and give the image a class. Here we use the `width`
# and `height` parameters to make the image smaller.
root.create_image('./image-demo.png', alt='IMG Demo', width='25%', height='25%')  # noqa: E501

# Let's add some JavaScript to the page using multi-line strings.
# The `position` parameter is optional and defaults to 'bottom'.
js = """
console.log("Hello, World!")
console.warn("This is a warning!")
console.error("This is an error!")
alert("Hello user! This alert was made with JavaScript in Pintes!")
"""
root.add_js(js, position='bottom')

# What about unordered lists and ordered lists? Glad you (didn't) ask!
# Creating a list is the same as creating a div tag, except you specify the `tag` parameter in `pint_merge()`.
ulRoot = pintes.CreatePint()
ulRoot.create.header('This is in an unordered list.', level=2)
ulRoot.create_custom('This is a `li` tag inside an unordered list.', tag='li')
ulRoot.create_custom('This is another `li` tag inside an unordered list.', tag='li')
ulRoot.create_custom('Pintes is cool.', tag='li')
# Now we merge the unordered list into the root Pint with the `tag` parameter set to 'ul'.
root.pint_merge(ulRoot, tag='ul')

# What if you have a tag you want to use, but it's a self-closing tag such as <br/> or <hr/>?
# You can use the `selfClosing` parameter in `create()` to create self-closing tags.
# Note that if you specify text in a self-closing tag, it will raise a ValueError.
root.create_custom(selfClosing=True, tag='hr')
root.create_custom('Hey!')

# Now, to export the code you've made to an HTML file.
root.export_to_html_file('demo.html')
# This will overwrite the file if it already exists.
# You can also use `export_to_html()` to export to a string instead of a file,
# which is useful for debugging or PyWebview.
#export = root.export_to_html()
#print(export)
