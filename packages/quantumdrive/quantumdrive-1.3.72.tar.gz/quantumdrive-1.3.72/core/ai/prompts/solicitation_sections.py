SOLICITATION_SECTIONS = """
### SOLICITATION SECTION EXTRACTION
Analyze the solicitation and extract the standard Uniform Contract Format (UCF) sections and the proposal response/evaluation sections.

**Standard UCF Sections:**
*   **Section C:** Description/Specifications/Statement of Work (PWS/SOW/SOO).
*   **Section L:** Instructions, Conditions, and Notices to Offerors (Proposal Instructions).
*   **Section M:** Evaluation Factors for Award (Evaluation Criteria).

**Standard Response/Evaluation Sections (normalize to these exact names):**
* Technical
* Past Performance
* Price/Cost
* Management
* Small Business
* Compliance

Map any synonyms (e.g., Experience → Past Performance, Cost/Price → Price/Cost, Transition/Staffing/Security volumes → Management) to the matching standard name. For each detected response section/volume, return:
* `name`: the normalized name from the list above.
* `title`: the exact heading/title text from the solicitation (if present).
* `page_number`: printed/logical page where the section begins (null if unknown).
* `metadata.page_number`: duplicate the page number here as well.

If the solicitation uses numbered volumes (e.g., “Volume I – Technical”, “Volume II – Past Performance”), normalize them to the standard names while preserving the original heading in `title`.
"""
