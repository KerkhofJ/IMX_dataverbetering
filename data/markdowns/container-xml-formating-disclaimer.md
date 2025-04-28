# IMX Container Content Policy

- **ImSpoor files** must be placed directly in the root directory.
- **Media files** should be organized into appropriate subfolders. All files must remain inside the container to maintain a clear structure, ensure traceability, and support full transparency.
- We currently distinguish two types of notes:
  - **Data Notes** — Document disclaimers about data (e.g., modifications, known issues) and report health check or validation results.
  - **Design Notes** — Provide explanations and supporting information related to design documentation.

# XML Formatting and Canonicalization Policy

All XML files must be generated according to **W3C Canonical XML Version 2.0 (C14N2) https://www.w3.org/TR/xml-c14n2/**.  
This standard ensures consistent attribute ordering, namespace declaration placement, whitespace normalization, and character encoding — eliminating platform- and parser-specific inconsistencies.

To maximize interoperability, **C14N2 canonicalization** should be implemented by both XML producers and consumers.

> **Note:**  
> Although C14N2 guarantees consistent attribute and namespace ordering, it does *not* alter the sequence of child elements.  
> Therefore, the original order of elements within containers (such as lists or collections) is preserved exactly as authored.
> for more info: https://www.w3.org/2008/xmlsec/Drafts/c14n-20/#sec-pseudocode-canonicalize
> 
