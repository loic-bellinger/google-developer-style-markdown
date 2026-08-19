---
title: "Mathematical notation"
source: https://developers.google.com/style/mathematical-notation
---

# Mathematical notation

This page describes how to format common mathematical notation such as
exponents, expressions, equations, operators, and variables in
documentation. Formatting best practices can help ensure that your
documentation is compatible with assistive technologies and
renders accurately.

For general information about using and formatting numbers, see
[Numbers](https://developers.google.com/style/numbers).

**Note:** This page includes examples of formatting in HTML
and Markdown in standard text. If you're using a third-party tool to display
complex math, follow that tool's formatting guidance to ensure that your
mathematical markup displays correct.

## Use HTML entities for mathematical symbols

In general, use HTML entities for mathematical symbols instead of keyboard
symbols. The following table lists entities for symbols that are common in
arithmetic and algebra. For the plus sign (`+`), equals sign
(`=`), and division sign (`/`), you can use
their keyboard equivalents.

| Symbol | Markup | Description |
|---|---|---|
| + | Use the keyboard symbol. | Plus sign |
| − | `&minus;` | Minus sign |
| × | `&times;` | Multiplication sign Alternatively, you can use the dot operator `∙` (`&#8729;`) or asterisk operator `*` (`&#42;`) to match the UI. Don't use an asterisk (`*`) to indicate multiplication in text. You can indicate multiplication by omitting the multiplication symbol if doing so doesn't create ambiguity---for example, instead of *a* × *b*, you can write *ab*. |
| / | Use the keyboard symbol. | Division sign |
| = | Use the keyboard symbol. | Equals sign |
| ≠ | `&ne;` | Not equal to |
| ± | `&plusmn;` | Plus-minus sign |
| ∓ | `&mnplus;` | Minus-plus sign |
| \< | `&lt;` | Less than sign |
| \> | `&gt;` | Greater than sign |
| ≈ | `&asymp;` | Approximately equal to |
| ≉ | `&nap;` | Not approximately equal to |
| ≅ | `&cong;` | Congruent to |
| ≤ | `&le;` | Less than or equal to |
| ≥ | `&ge;` | Greater than or equal to |
| ≡ | `&equiv;` | Identical to |
| ≢ | `&nequiv;` | Not identical to |
| √ | `&radic;` | Square root |
| ∑ | `&sum;` | N-ary summation |

## Format mathematical notation

The following sections provide formatting for common math-related notation.

### Operators

To ensure accessibility and accurate HTML syntax, use
[HTML entities](https://developers.google.com/style/mathematical-notation#html-entities)
instead of keyboard symbols for operators. For example, use
`&minus;` instead of a hyphen (`-`).

Include a non-breaking space (`&nbsp;`) on both sides
of operators within a single expression, equation, or
statement.

Don't italicize operators.

Recommended: *a* − *b*

To render *a* − *b*, use the following markup:

- **HTML:** `<i>a</i>&nbsp;&minus;&nbsp;<i>b</i>`
- **Markdown:** `_a_&nbsp;&minus;&nbsp;_b_`

### Variables

Italicize variables.

Recommended: *x* ≠ *y*

Recommended: *x*^*y*^

Recommended: *y*~*i*~

To render *x* ≠ *y*, use the following markup:

- **HTML:** `<i>x</i>&nbsp;&ne;&nbsp;<i>y</i>`
- **Markdown:** `_x_&nbsp;&ne;&nbsp;_y_`

### Expressions and equations

Include short expressions and equations inline with your text.

Include a non-breaking space (`&nbsp;`) between components
such as operators and variables so that the expression or equation renders on
the same line.

When an expression or equation creates an awkward line break, consider
placing it on its own line.

Recommended: The equation
that describes a linear trend line is
*y* = *a* + *bx*.

Recommended: The equation
that describes a polynomial trend line, where the order is *o*, is the
following:  

*y* = *a* + *b* × *x* + ... + *k* × *x*^*o*^

To render *y* = *a* + *bx*, use the
following markup:

- **HTML:** `<i>y</i>&nbsp;&=&nbsp;<i>a</i>&nbsp;+&nbsp;<i>bx</i>`
- **Markdown:** `_y_&nbsp;&=&nbsp;_a_&nbsp;+&nbsp;_bx_`

### Fractions

<br />

Express fractions as decimal numbers, when possible.

If you must express fractions as words, connect the numerator and
denominator with a hyphen unless one of them is already hyphenated.

<br />

Recommended: 0.02

Recommended: one and one-half

Recommended: three-sevenths

Recommended: three seventy-fourths

### Exponents and subscripts

Use
[standard mathematical notation](https://wikipedia.org/wiki/Exponentiation).
Don't put a space between the base and the exponent.

To render exponents, use the HTML `<sup>` tag. Don't use the
keyboard caret symbol (`^`) to indicate an exponent.

To render subscripts, use the HTML `<sub>` tag.

Recommended: 2^3^

Recommended: *x*^*y*^

Recommended: *y*~*i*~

Not recommended: 2\^3

To render 2^3^, use the following markup in HTML and Markdown:
`2<sup>3</sup>`

## Notation as words

In general, you can use mathematical notation in place of words in running
text. For example, in a sentence, you might use the statement
*x* ≠ *y* instead of writing "*x* is not equal to
*y*." If the use of notation instead of words creates ambiguous, grammatically
incorrect, or difficult-to-read text, then use words to convey the
mathematical concept.

Recommended: Check
whether *a* \> *b*.

Recommended: The area
is calculated by multiplying the length by the width.

Not recommended: Check
whether *a* is greater than *b*.

Not recommended: The
area is calculated by multiplying *l* × *w*.

## Tools for complex or multiline equations

The methods described on this page that use HTML entities and tags are suitable for most common
mathematical notation. However, for more complex, multiline equations, or formulas that are
difficult to represent clearly with standard HTML, consider using [diagrams,
other images](https://developers.google.com/style/images), or a dedicated math rendering tool to support comprehension. Images and diagrams
like pie charts or bar graphs, in particular, are especially helpful for comparing statistics and
illustrating percentages.

## More resources

- [Numbers](https://developers.google.com/style/numbers)
- [Units of measure](https://developers.google.com/style/units-of-measure)
- [Text-formatting summary](https://developers.google.com/style/text-formatting)
