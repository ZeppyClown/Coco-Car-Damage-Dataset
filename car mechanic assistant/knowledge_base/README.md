# RAG Knowledge Base - Car Mechanic Assistant

## Overview
This knowledge base is designed for a Retrieval-Augmented Generation (RAG) system powering a professional car mechanic assistant. The structure prioritizes **practical workshop use** over academic theory.

## Design Principles

1. **Mechanic-first organization** - Folders represent types of mechanical knowledge, not data categories
2. **Real-world focus** - Content emphasizes actual workshop fixes over textbook theory
3. **Quick retrieval** - Structure optimized for fast, relevant document matching
4. **Probability-based** - Causes ranked from most to least likely in practice
5. **Workshop defaults assumed** - No hand-holding, assumes professional context

## Folder Structure

```
knowledge_base/
│
├── 01_vehicle_specs/          # Technical specifications & service data
├── 02_diagnostic_procedures/  # Symptom-based troubleshooting flowcharts
├── 03_fault_codes/            # OBD codes with real-world interpretation
├── 04_repair_procedures/      # Step-by-step repair guides
├── 05_parts_catalog/          # Part cross-references & compatibility
├── 06_diagnostic_software/    # Coding & adaptation procedures
├── 07_paint_codes/            # Color identification & mixing
├── 08_pricing_valuation/      # Labor rates & cost estimation
├── 09_workshop_rules/         # Default assumptions & standards
└── 10_troubleshooting_database/  # Known issues & proven fixes
```

---

## Detailed Folder Descriptions

### **01_vehicle_specs/**
**Purpose:** Quick access to technical specifications for diagnostics and repairs

**Subfolders:**
- `by_make_model/` - Vehicle-specific spec sheets
- `engine_specifications/` - Engine technical data
- `fluid_capacities/` - Oil, coolant, transmission fluid specs
- `torque_specifications/` - Bolt torque values
- `service_intervals/` - Maintenance schedules

**Example files:**
- BMW_E90_328i_2007.md
- BMW_N52_engine_torque_specs.md

**Retrieval use:**
- Query: "Oil capacity for 2007 BMW 328i"
- Returns: Exact specs with part numbers and torque values
- Metadata: `make`, `model`, `year`, `engine_code`, `spec_type`

**Response style:** Direct numbers with units, no explanations unless asked

---

### **02_diagnostic_procedures/**
**Purpose:** Systematic troubleshooting based on symptoms

**Subfolders:**
- `symptom_based/` - Organized by what customer reports ("won't start", "rough idle")
- `system_specific/` - By vehicle system (cooling, electrical, etc.)
- `flowcharts/` - Decision trees for complex diagnostics

**Example files:**
- rough_idle_diagnosis.md
- no_start_cranks_good.md

**Retrieval use:**
- Query: "Car cranks but won't start"
- Returns: Flowchart with probability-ranked causes (60% ignition, 20% fuel, etc.)
- Metadata: `symptom`, `system`, `difficulty`, `tools_required`

**Response style:** Step-by-step logical flow, most likely causes first

---

### **03_fault_codes/**
**Purpose:** Decode DTCs with real-world meaning and common causes

**Subfolders:**
- `obd_generic/` - Standard OBD-II codes (P0xxx, P2xxx)
- `manufacturer_specific/` - Brand-specific codes (BMW, VW, etc.)
- `code_interpretation_guides/` - How to read freeze frame data

**Example files:**
- P0300_random_misfire.md
- BMW_30D8_DME_fault.md

**Retrieval use:**
- Query: "P0300 code meaning"
- Returns: "Random misfire. 60% = ignition coils, 20% = fuel system. Test coils first."
- Metadata: `code`, `manufacturer`, `system`, `severity`, `common_causes`

**Response style:** Real-world probabilities, not just textbook definitions

---

### **04_repair_procedures/**
**Purpose:** Detailed repair instructions with gotchas and time-savers

**Subfolders:**
- `step_by_step_guides/` - Complete repair procedures
- `special_tools_required/` - Jobs needing specific tools
- `common_mistakes/` - What not to do
- `time_estimates/` - Book time vs real time

**Example files:**
- BMW_N54_injector_replacement.md

**Retrieval use:**
- Query: "How to replace N54 fuel injectors"
- Returns: Step-by-step with critical warnings (reverse thread bolts, coding required, etc.)
- Metadata: `component`, `vehicle_family`, `difficulty`, `time_estimate`, `special_tools`

**Response style:** Sequential steps with warnings highlighted

---

### **05_parts_catalog/**
**Purpose:** Part number lookup, cross-referencing, compatibility

**Subfolders:**
- `cross_reference/` - OEM to aftermarket equivalents
- `oem_vs_aftermarket/` - Quality comparisons
- `part_identification/` - Visual identification guides
- `compatibility_matrices/` - Fitment tables

**Example files:**
- spark_plug_cross_reference.md

**Retrieval use:**
- Query: "Spark plugs for BMW N52"
- Returns: "OEM: 12120037607 ($12). Aftermarket: NGK ZGR6STE-13 (exact equivalent, $8)"
- Metadata: `part_type`, `oem_number`, `aftermarket_equivalents`, `compatibility`

**Response style:** Direct part numbers with pricing and notes

---

### **06_diagnostic_software/**
**Purpose:** ECU coding, adaptations, scan tool procedures

**Subfolders:**
- `coding_procedures/` - How to code/adapt modules
- `adaptation_values/` - Reset and relearn procedures
- `software_versions/` - Tool compatibility
- `tool_requirements/` - Which software for which job

**Example files:**
- BMW_INPA_injector_coding.md

**Retrieval use:**
- Query: "How to code BMW injectors with INPA"
- Returns: Step-by-step INPA procedure with screenshots references
- Metadata: `manufacturer`, `system`, `software_required`, `procedure_type`

**Response style:** Click-by-click instructions with critical steps highlighted

---

### **07_paint_codes/**
**Purpose:** Color identification and paint matching

**Subfolders:**
- `color_databases/` - Paint code to color name lookups
- `mixing_formulas/` - How to mix custom colors
- `visual_references/` - Photo-based identification

**Example files:**
- BMW_paint_codes.md

**Retrieval use:**
- Query: "BMW paint code 300"
- Returns: "Alpine White III (solid). Common on E90 2006-2013. Where to find code: door jamb"
- Metadata: `manufacturer`, `code`, `color_name`, `type` (metallic/solid)

**Response style:** Code → name → where to find it → notes on matching

---

### **08_pricing_valuation/**
**Purpose:** Generate estimates quickly and accurately

**Subfolders:**
- `labor_rates/` - Book time vs real time for common jobs
- `parts_pricing/` - Typical part cost ranges
- `market_values/` - Vehicle valuation for trades
- `estimate_templates/` - Standard estimate formats

**Example files:**
- common_repair_labor_guide.md

**Retrieval use:**
- Query: "Labor time for timing belt"
- Returns: "4.5-6 hrs book time. Add 1 hr for water pump. Parts $300-500, total $800-1500"
- Metadata: `job_type`, `labor_hours`, `parts_cost`, `region`

**Response style:** Range, not single number. Explain what affects price.

---

### **09_workshop_rules/**
**Purpose:** Default assumptions so Claude doesn't ask obvious questions

**Subfolders:**
- `standard_procedures/` - How we do things
- `safety_protocols/` - Non-negotiable safety rules
- `quality_standards/` - OEM vs aftermarket policies
- `default_assumptions/` - What to assume unless told otherwise

**Example files:**
- workshop_standards.md

**Retrieval use:**
- **Auto-loaded with every query** for context awareness
- Query: "Recommend brake pads"
- Returns: "OEM or quality aftermarket (shop standard for safety parts). Options: OEM $120, Akebono $85"
- Metadata: `priority: always_loaded`, `override_allowed`

**Response style:** Assumes workshop defaults, mentions them naturally

**Example defaults:**
- Use OEM parts for safety-critical components
- Synthetic oil for turbos
- Don't reuse stretch bolts
- Check for TSBs before diagnosing

---

### **10_troubleshooting_database/**
**Purpose:** Known issues with proven fixes (the "I've seen this before" folder)

**Subfolders:**
- `known_issues/` - Common failures by make/model/engine
- `recalls_tsbs/` - Factory bulletins and recalls
- `real_world_fixes/` - What actually works vs theory

**Example files:**
- BMW_N54_HPFP_failure.md
- Honda_VTC_actuator_rattle.md

**Retrieval use:**
- Query: "BMW N54 hard start when hot"
- Returns: "Classic HPFP failure. 60% failure rate by 80k miles. Fix: Replace HPFP + LPFP ($650-1900)"
- Metadata: `make`, `model`, `symptom`, `failure_rate`, `confirmed_fix`

**Response style:** "This is a known issue. Here's the proven fix."

---

## Metadata Schema

Each document includes JSON metadata for vector database indexing:

```json
{
  "content": "Document text...",
  "metadata": {
    "folder": "03_fault_codes",
    "make": "BMW",
    "model": "E90",
    "year_range": "2006-2013",
    "engine": "N52",
    "category": "diagnostic",
    "urgency": "medium",
    "tools_required": ["scan_tool", "multimeter"],
    "difficulty": "intermediate",
    "time_estimate_hrs": 2.5,
    "cost_range": "$200-500",
    "last_updated": "2024-12-15"
  }
}
```

**Key metadata fields:**
- `make`, `model`, `year_range`, `engine` - Vehicle identification
- `category` - Document type (diagnostic, repair, spec, etc.)
- `symptom` - What customer reports
- `difficulty` - Skill level required
- `tools_required` - Special tools needed
- `time_estimate_hrs` - Realistic time estimate
- `cost_range` - Parts + labor estimate
- `urgency` - How soon it needs fixing

---

## Retrieval Strategy

### **Query Flow:**
1. **User query arrives** → Extract vehicle info + symptom/task
2. **Load workshop_rules/** → Auto-inject defaults as context
3. **Primary retrieval** → Match to most relevant folder(s)
4. **Cross-reference** → Pull related docs from 2-3 folders
5. **Prioritize known issues** → Folder 10 ranks higher than generic
6. **Format response** → Direct, actionable, no fluff

### **Example Multi-Folder Query:**
```
User: "2008 BMW 328i rough idle, P0300 code"

Retrieval:
- 03_fault_codes/P0300_random_misfire.md
- 02_diagnostic_procedures/rough_idle_diagnosis.md
- 10_troubleshooting_database/BMW_N52_ignition_coil_failures.md
- 05_parts_catalog/ignition_coil_cross_reference.md

Response:
"P0300 = random misfire. On N52 engines, 60% = ignition coils failing.
Quick test: Swap coil 2 with coil 4, clear codes, test drive.
If code moves to P0304 → bad coil.
Replace all 6 coils + plugs if >60k miles.
Parts: Coils $120-360 (set), Plugs $40-80. Labor: 1.5 hrs."
```

---

## Content Guidelines

### **Writing Style:**
- **Direct** - No preamble, get to the point
- **Practical** - Real-world fixes, not theory
- **Probability-based** - Most likely causes first
- **Workshop tone** - Assumes professional mechanic context

### **What to Include:**
- Probability percentages (60% ignition, 20% fuel)
- Part numbers when available
- Common mistakes/gotchas
- Time estimates (book vs real)
- Cost ranges
- Special tools needed

### **What to Avoid:**
- Academic explanations
- Overly cautious disclaimers
- Listing every possible cause equally
- Assuming customer is doing the work (assume pro mechanic)

---

## Expanding the Knowledge Base

### **Adding New Documents:**

1. **Choose correct folder** based on document type
2. **Use consistent naming**:
   - Make_Model_Year_Issue.md
   - Code_P0300_description.md
   - Component_replacement_procedure.md

3. **Include metadata block** at end of every document

4. **Follow real-world structure**:
   - Symptoms first
   - Most likely causes first
   - Quick tests before complex diagnostics
   - Common mistakes section
   - Cost breakdown

5. **Cross-reference related docs**:
   - Link to related codes
   - Reference repair procedures
   - Point to known issues

---

## File Count by Folder

Current example files:
- 01_vehicle_specs: 2 files
- 02_diagnostic_procedures: 2 files
- 03_fault_codes: 2 files
- 04_repair_procedures: 1 file
- 05_parts_catalog: 1 file
- 06_diagnostic_software: 1 file
- 07_paint_codes: 1 file
- 08_pricing_valuation: 1 file
- 09_workshop_rules: 1 file
- 10_troubleshooting_database: 2 files

**Total: 14 example files**

These are templates. Expand with:
- More makes/models
- More common issues
- More fault codes
- More repair procedures

---

## Usage with RAG System

### **Document Chunking:**
- Chunk by section (marked with ## headers)
- Keep related info together (don't split mid-procedure)
- Typical chunk size: 500-1000 tokens

### **Vector Embeddings:**
- Embed both content and metadata
- Weight technical terms heavily (part numbers, codes, symptoms)
- Weight known issues higher than generic diagnostics

### **Retrieval:**
- Top-k = 5-10 documents
- Re-rank by relevance score
- Prioritize folder 10 (known issues) and folder 09 (workshop rules)

### **Response Generation:**
- Cite folder numbers in responses (e.g., "Per workshop standards (09/)")
- Include part numbers and costs when available
- Provide ranges, not single values
- Rank causes by probability

---

## Maintenance

**Update frequency:**
- Workshop rules: As policies change
- Known issues: When new patterns emerge
- Pricing: Quarterly (parts prices fluctuate)
- Specs: As new models released
- Codes: When new DTCs discovered

**Version control:**
- Track `last_updated` in metadata
- Archive old revisions
- Document major changes

---

## License & Usage

This knowledge base structure is designed for professional automotive workshop use.

**Content should be:**
- Accurate (verify with factory service info)
- Tested (proven in real workshop environment)
- Up-to-date (check for TSBs and recalls)
- Legally compliant (respect copyrights on factory service data)

---

## Contact

For questions about this knowledge base structure or to contribute content, contact your workshop manager.

**Remember:** This is a living document. Update it as you learn new patterns and fixes in the shop.
