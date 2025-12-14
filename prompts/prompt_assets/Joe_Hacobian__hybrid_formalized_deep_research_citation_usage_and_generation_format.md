## Citation Style Instructions (Hybrid, Strict)

When generating research reports, literature reviews, or analytical documents, follow this exact citation format.

### IN-TEXT CITATIONS (MANDATORY)
1. Cite sources using **monotonically incremented superscript integers**, e.g. `text¹`.
2. Do **not** use parentheses, brackets, author names, or years in the text.
3. Each **new source introduced** increments the counter by one.
4. Multiple citations appear as independent superscripts: `… phenomena¹ ² ³`.
5. Superscripts must be **Unicode superscripts** (¹ ² ³ …), not plain numbers.

### `# Cited Sources` (MANDATORY)
At the end of the document, include a `# Cited Sources` section.

**Global rules**
- Sources must be listed in **chronological order of appearance in the text** (first cited = 1, next new source = 2, etc.).
- **Every** in-text superscript must correspond to **exactly one** entry in `# Cited Sources`, and **every** entry must be cited at least once.
- Do **not** collapse ranges. Do **not** use `et al.` List authors as shown by the source.
- Do **not** fabricate bibliographic fields. If a field is unknown, omit it (do not invent volume/issue/pages).
- URLs must be real, accessible, and point to the cited content.

### SOURCE TYPE SELECTION (CONDITIONAL LOGIC)
For each cited item, choose exactly one of the following formats:

#### Type A — Academic / formal publications (journals, conference proceedings, standards, books, chapters)
Use **Type A** only when the source is a formal publication (peer-reviewed journal, conference proceedings, official standard/spec, book, book chapter, academic report).

**Type A — Journal / proceedings**
`<index>. <AuthorLast>, <Initials>., <AuthorLast>, <Initials>., & <AuthorLast>, <Initials>. (<Year>). <Title in sentence case>. *<Journal or Source>*, *<VolumeNumber>* (<IssueNumber>), <PageRange>.`

Rules:
- Title must be sentence case.
- Journal/source must be italicized.
- Volume number must be italicized.
- Issue number in parentheses immediately after volume.
- Page range follows a comma.
- If volume/issue/pages are not available, **omit those fields** (do not invent them).

**Type A — Book**
`<index>. <AuthorLast>, <Initials>. (<Year>). <Title in sentence case>. *<Publisher>*.`

**Type A — Chapter**
`<index>. <AuthorLast>, <Initials>. (<Year>). <Chapter title in sentence case>. In <EditorLast>, <Initials>. & <EditorLast>, <Initials>. (Eds.), <Book title in sentence case> (pp. xx–yy). *<Publisher>*.`

**Type A — Standard / specification / charter (if treated as formal publication)**
`<index>. <OrgName>. (<Year>). <Title in sentence case>. *<Publishing organization>*.`

#### Type B — Web sources (press releases, blog posts, policies/ToS, documentation pages, GitHub, forum posts, news articles, videos)
Use **Type B** for any source that is primarily a web page or online publication.

**Type B — Web**
`<index>. <AuthorOrOrg>. (<Best-effort Year-Month-Day or Year>). <Title in sentence case>. *<Website or Publisher>*. <URL>.`

Rules:
- Use the best-known publication date. If only a year is known, use the year.
- Title must be sentence case.
- Website/publisher must be italicized.
- URL must be included.
- If the author is unknown, use the organization or site name as `<AuthorOrOrg>`.
- If the page is undated and no reliable date is available, use `(n.d.)`.

#### Type B — YouTube / video
`<index>. <ChannelOrCreator>. (<Best-effort Year-Month-Day or Year>). <Video title in sentence case> [Video]. *YouTube*. <URL>.`

### QUALITY CONTROL (MANDATORY)
Before finalizing, perform an internal citation audit:
- Count the number of unique sources cited in the text = N.
- Ensure `# Cited Sources` contains exactly N entries.
- Ensure the highest superscript index equals N.
- Ensure there are no gaps or duplicate indices.

### OUTPUT REQUIREMENT
All citations must obey **this hybrid format exactly**.  
Do not output a plan. Do not ask questions. Produce the report and its `# Cited Sources` in one pass.
