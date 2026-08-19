---
title: "Pluralization"
source: https://developers.google.com/style/pluralization
---

# Pluralization

In general, follow the standard rules for pluralization in US English and use the regular
plural form of a word in most cases. Avoid using *'s* to form a plural to avoid confusing
a plural with a possessive or contraction.

For more information, see [Contractions](https://developers.google.com/style/contractions) and [Possessives](https://developers.google.com/style/possessives).

## Singular and plural

For sentences with long or complex subjects, make sure to use either a plural or singular
appropriately.

Recommended: Confirm that the number of
entries listed in the directory is accurate.

Recommended: The workloads with the
`app: backend` label represent the traffic source.

Not recommended: The efficiency of
algorithms that process data sets depend on memory allocation.

For sentences with more than one subject being connected by *and* or *or*, make sure
to use either a plural and singular appropriately.

Recommended: The request payload and
header information are logged for debugging.

Recommended: Either the API keys or
service account wasn't authenticated.

Not recommended: User authentication and
authorization is processed and handled by the security module.

For consistent style, use a plural after *one or more*, not a singular.

Because *one or more* can express the possibility of one or more outcomes, it's sometimes
helpful to reword the sentence for clarity.

Recommended: If one or more tests fail, a
system warning is triggered.

Recommended: If any one test fails, a
system warning is triggered.

See also [Plurals in parentheses](https://developers.google.com/style/pluralization#plurals-in-parentheses).

Use a singular after *more than one*, not a plural.

Recommended: You can create more than one
instance at a time.

## Plural abbreviations

In general, treat acronyms, initialisms, and other abbreviations as regular words when making
them plural. Avoid using *'s* to form the plural to help distinguish the plural form from the
possessive. For more information, see [Possessives](https://developers.google.com/style/possessives).

Recommended: APIs, SKEs, and IDEs

Not recommended: API's, SKE's, and
IDE's

If the acronym, initialism, or abbreviation ends in *s*, *sh*, *ch*, or
*x*, then add *es*---for example, *OSes*, *DISHes*, *DCCHes*, and
*BMXes*.

> [!NOTE]
> **Note:** Forming a plural using *'s* can be ambiguous or confusing to readers and might cause issues in translation. For more information, see [Write for a global audience](https://developers.google.com/style/translation).

When spelling out a term, make sure that both the spelled-out term and abbreviation match,
with both either being a plural or singular.

Recommended: virtual machines (VMs)

Not recommended: virtual machines (VM)

When using numbers with units of measure, use the singular when spelling out the unit if the
number is one. Otherwise, use the plural form for all other numbers, including zero,
decimal numbers, and numbers greater than one.

Recommended: 0 degrees

Recommended: 0.5 degrees

Recommended: 1 degree

Recommended: 15 degrees

Don't make an abbreviation plural when used as a unit with a number.

Recommended: 64 GB

Not recommended: 64 GBs

> [!NOTE]
> **Note:** Sometimes it can be helpful to spell out *-bit* or *-byte* terms. However, in general, it's not necessary to spell out a unit when used in combination with a specific number.

Make sure to include a space, preferably a nonbreaking space, between the number and
abbreviation. For more information, see [Spaces in units of
measurement](https://developers.google.com/style/units-of-measure#spaces-in-units-of-measurement).

For more information, see [Abbreviations](https://developers.google.com/style/abbreviations).

## Plural product and feature names

In general, don't form a plural or possessive for the trademark of a product, feature, or
company name. For more information, see [Use trademarks only as modifiers](https://developers.google.com/style/trademarks#use-trademarks-only-as-modifiers) and
[Product, feature, and company
names](https://developers.google.com/style/possessives#product,-feature,-and-company-names).

In general, use singular class names. Don't manually make a singular class name plural. Doing
so might cause issues in translation. Instead, add a plural noun after the class name.

Recommended: `Intent` objects
and `Activity` instances

Not recommended: `Intent`s and
`Activity`s

Not recommended: `Intents` and
`Activities`

For more information, see [API reference code
comments](https://developers.google.com/style/api-reference-comments).

## Plurals in parentheses

Don't put optional plurals in parentheses. Instead, use either a plural or singular
construction and keep things consistent throughout your documentation. Choose what is most
appropriate for your documentation and your audience. If it's important in a specific context to
indicate both, use *one or more*.

| Recommended | Not recommended |
|---|---|
| To find your API key, visit the **Credentials** page. | To find your API key(s), visit the **Credentials** page. |
| The value of the parent depends on the values of its children. | The value of the parent depends on the value(s) of its child(ren). |
| You can use a physical linecard, which can contain one or more ports. | You can use a physical linecard, which can contain port(s). |

## Plural pronouns

For information about plural pronouns like *we*, *you*, and *they*, see [Pronouns](https://developers.google.com/style/pronouns) and [Second person and first
person](https://developers.google.com/style/person).
