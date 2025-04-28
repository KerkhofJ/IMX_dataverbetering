# XML Formatting & Canonicalization Disclaimer

The XML content of the Signaling Design is produced and verified using the W3C Canonical XML Version 2.0 (C14N2) method—specifically via the Python **lxml** library’s built-in C14N2 support. 

Adopting this approach ensures:

- **Deterministic Output**  
  Attribute order, namespace declarations, whitespace normalization, and character encoding are applied consistently, eliminating platform- or parser-dependent variations.

- **Robust Signature Verification**  
  Any changes to element order, namespace prefixes, or whitespace outside the canonicalization rules will invalidate digital signatures or lead to parsing discrepancies.

- **Standards-Compliant Handling of Comments & Processing Instructions**  
  Comments and processing instructions are included or omitted strictly per the C14N2 specification.

---

## Recommendation

To achieve the highest level of interoperability and security, we strongly encourage all XML producers and consumers to adopt the **C14N2 canonicalization workflow**. 
This practice minimizes integration issues and maximizes fidelity in signed or exchanged XML documents.
