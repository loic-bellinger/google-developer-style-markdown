---
title: "Inclusive language"
source: https://developers.google.com/style/inclusive-documentation
---

> [!NOTE]
> **Note**: This document includes references to potentially disrespectful or offensive terms. These terms are listed here to provide usage guidance and alternative terms.

When you write developer documentation with inclusivity and diversity in mind,
you help ensure that the content is more precise and clear for all readers.
Avoid any kind of idiomatic or figurative language that can be misinterpreted or
distracting.

This page is not an exhaustive reference, but provides some general guidelines
and examples that illustrate some best practices for writing inclusive
documentation.

For other writing best practices, see the following resources:

- [Write for a global audience](https://developers.google.com/style/translation)
- [Write accessible documentation](https://developers.google.com/style/accessibility)
- [Voice and tone](https://developers.google.com/style/tone)

## Avoid unnecessarily gendered language

Be mindful of the
[pronouns](https://developers.google.com/style/pronouns#gender-neutral-pronouns)
that are used in narrative
examples, and be aware of other possible sources of gendered language.

| Recommended | Not recommended |
|---|---|
| Equipment installation takes around 16 person-hours to complete. | Equipment installation takes around 16 man-hours to complete. |
| Build AI that benefits humanity. | Build AI that benefits mankind. |

## Avoid figurative language

Use simple language and terminology that's precise and clear for all of your
audiences:

- Avoid idiomatic or figurative language that can be misunderstood, distracting, or difficult for translation.
- Avoid [jargon](https://developers.google.com/style/jargon).
- Use terms that are established industry standards and widely understood by the target audience.

When you try to achieve a [friendly and conversational
tone](https://developers.google.com/style/tone), you might mistakenly use figurative language. Figurative language can
come in the form of figures of speech and other turns of phrase. Be attentive to
your word choice, especially when you aim for an informal tone.

Don't use metaphors, and don't use a term in a metaphorical sense
([use words in their primary sense](https://developers.google.com/style/translation#use-words-in-their-primary-sense)).
For example, avoid using the metaphor of *pets versus cattle* when you
compare on-premises or stateful systems with stateless cloud systems.

For guidance about specific terms, see the
[Word list](https://developers.google.com/style/word-list).

### Avoid ableist language

Ableist language includes
words or phrases such as *crazy*, *insane*, *blind to* or
*blind eye to*, *cripple*, *dumb*, and others. Choose a more
accurate or alternative word, depending on the context.

| Recommended | Not recommended |
|---|---|
| Before launch, give everything a final check for completeness and clarity. | Before launch, give everything a final sanity-check. |
| There are some baffling outliers in the data. | There are some crazy outliers in the data. |
| It slows down the service, causing a poor user experience until the queue clears. | It cripples the service, causing a poor user experience until the queue clears. |
| Replace the placeholder in this example with the appropriate value. | Replace the [dummy variable](https://developers.google.com/style/word-list#dummy-variable) in this example with the appropriate value. |

### Avoid graphic or metaphorical language

Avoid unnecessarily graphic or metaphorical language, when you can use a more
precise term.

For example, instead of
*[STONITH](https://developers.google.com/style/word-list#stonith)*, use specific terms to
describe the process that's used to stop an errant node. If you need to mention a term
such as *STONITH*, you can mention it once when you first explain the
relevant feature, and phrase it in a way that de-emphasizes the term.

Recommended:
This approach might require you to fence failed nodes.

Sometimes okay:
This approach might require you to fence failed nodes (sometimes referred to
as *STONITH*).

Always use the most precise and well-understood terms for your context.
In some contexts, an industry-established term has a specific technical meaning
that doesn't have an accurate synonym or alternative. For examples, see the word
list entries for [terminate](https://developers.google.com/style/word-list#terminate) and
[execute](https://developers.google.com/style/word-list#execute).

| Recommended | Not recommended |
|---|---|
| If the connection doesn't respond, check for errors. | If the connection hangs, check for errors. |
| Point to **File** , and then click **New**. | Hover over **File** , and hit **New**. |

For guidance about specific terms, see the
[Word list](https://developers.google.com/style/word-list).

## Write diverse and inclusive examples

Write documentation for a
[global audience](https://developers.google.com/style/translation#be-inclusive).
Use diverse names, genders, ages, and locations in examples. Keep the following
advice in mind:

- Follow our [gender-neutral
  pronoun](https://developers.google.com/style/pronouns#gender-neutral-pronouns) guidance.
- Avoid being too culturally specific to the US. Be mindful when referring to specific holidays (see also the word list entry for [*the holidays*](https://developers.google.com/style/word-list#holiday)), cultural practices, sports, and figures of speech.
- In examples, [choose a diverse set of names](https://developers.google.com/style/examples#example-person-names) to help reflect our global audience. For guidelines about fictional people, see [Further notes about example people](https://developers.google.com/style/examples#further-notes-about-example-people).
- When writing about older adults, avoid terms and figures of speech such as *the elderly*, *the aged*, *seniors*, *senior citizens*, or *80 years young*. Instead, use terms such as *older adults* or *aging population*, or mention the person's relative age or relationship to the other people in your example when those details are relevant.

## Write about features and users in inclusive ways

Avoid referring to people in divisive ways. For example, instead of referring
to people as *native speakers* or *non-native speakers* of English, consider
whether your document needs to discuss this at all, and revise it
to discuss the feature in terms that are relevant to anyone regardless of what
languages they know.

Avoid using socially charged terms for technical concepts where possible. For
example, avoid terms such as [blacklist](https://developers.google.com/style/word-list#blacklist) and
[native](https://developers.google.com/style/word-list#native) feature, and don't use terms like
[first-class
citizen](https://wikipedia.org/wiki/First-class_citizen), even though such terms might still be widely used.

### Replace or write around non-inclusive terms

This section contains guidance about how to replace or write around a non-inclusive term. If a
term is well established in the industry and replacing it could cause confusion, see
[Replace established terms](https://developers.google.com/style/inclusive-documentation#replace). If a term occurs in code samples or keywords, see
[Write around non-inclusive code terms](https://developers.google.com/style/inclusive-documentation#write-around). For information about avoiding
non-inclusive jargon, see [Jargon](https://developers.google.com/style/jargon).

#### Replace established terms

Many non-inclusive terms are in wide use in the industry, such as *whitelist*. If replacing
an established term could cause confusion for readers, you can directly refer to the non-inclusive
term on the first use, and put it in parentheses. Then use the inclusive, replacement term
throughout the rest of the document.

Recommended: To make sure that administrators
get the notification, add them to an allowlist (sometimes called a *whitelist*). Anyone who
isn't on the allowlist is blocked ...

Recommended: In this model, a Jenkins
controller (master) handles HTTP requests. The Jenkins controller is designed to ...

Recommended: In cloud architecture, servers
are treated as commodities (sometimes described by using the metaphor *cattle, not pets*).
In many cases, instead of directly replacing a word, you can rewrite to improve the clarity of a sentence. For example, instead of replacing the verb *whitelist* with *allowlist*, try rewriting the sentence.

Recommended: You can allow requests from a
range of IP addresses by entering a CIDR block instead of a single address in the field.

Not recommended: You can allowlist a range of
IP addresses by entering a CIDR block instead of a single address in the field.

#### Write around non-inclusive code terms

In some cases, non-inclusive terms are embedded in code (or similar) as names or keywords, and
you can't simply ignore those terms and use different terminology. What you can do, however, is
*minimize* your use of the term (hence avoid propagating it as a term of art), while still
providing clear documentation to your readers. Don't use a non-inclusive name or keyword unless it's
in code font.

Following are scenarios for writing around non-inclusive terms that occur in code and keywords.

One scenario is if you're documenting an existing system in which an entity is already named
by using a non-inclusive term. For example, there might be a configuration file that includes the
following cluster name:

```
apiVersion: v1
kind: Config
preferences: {}

clusters:
- cluster:
  name: master
- cluster:
  name: replica-1
```

Another scenario is if your documentation includes a non-inclusive term that's an established
keyword, such as the keyword `SLAVE` in dialects of SQL:

```
START SLAVE UNTIL SQL_AFTER_MTS_GAPS;
```

The first time that you refer to a code item that uses a non-inclusive term, you can directly
refer to that term, but format it in code font, and put it in parentheses if possible.

Recommended: The configuration file helps you
create a parent node (which is named `master` in the file).

Recommended: Start the replica by using the
`START SLAVE` statement.

In subsequent mentions, use the preferred term (*parent node*, *replica*). If it's
necessary to refer to the entity name or keyword, continue doing so only with code formatting.

## Avoid bias and harm when discussing
disability and accessibility

Many developers create products with accessibility and disability in mind.
When documenting these features, and when writing about people with
disabilities or about accessibility, work to eliminate unintentional bias and
harm. Take the time to educate yourself about the ways that the communities that you're
writing about prefer to be identified and described before writing about them in
your documentation.

Some general guidelines in this area include the following:

- Don't describe people without disabilities as *normal* or *healthy*. This contributes to othering and alienation of people with disabilities by implying that they are abnormal or sick. Instead, use terms such as *nondisabled person*, *sighted person*, *hearing person*, *person without disabilities*, or *neurotypical person*.
- Research the ways that the people in the communities that you're writing about
  prefer to be identified and use the terms that they prefer. In many cases, avoid
  terms that remove personhood or that define people by their disability. For
  example, avoid terms such as *the disabled* or *a quadriplegic*.
  Instead, use terms such as *people with disabilities* or *a quadriplegic person*.

  However, many members of some communities prefer *identity-first language*---for
  example, that preference is common in autistic, blind, and Deaf communities. Capitalization of
  identities also can vary (for some perspectives, visit
  [Identity-First Language](https://autisticadvocacy.org/about-asan/identity-first-language/)
  and
  [Self-Identification
  in the Deaf Community](https://www.verywellhealth.com/deaf-culture-big-d-small-d-1046233)). Whenever possible, research and choose terms
  that respect the ways that people in the communities identify.
- Use *see* to refer to links and cross-references. For more information, see [see](https://developers.google.com/style/word-list#see).
- Avoid terms that reflect or project feelings and judgments about a person's disability, such as *victim of*, *suffering from*, or *wheelchair-bound*. Instead, use neutral terms such as *experiencing*, *living with*, or *uses a wheelchair*.
- Avoid euphemisms or patronizing terms such as *physically challenged*, *special*, *differently abled*, or *handi-capable*.
