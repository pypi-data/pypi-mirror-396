# Comprehensive File-by-File Analysis

> ⚠️ **Note:** This is a comprehensive 3,500+ line analysis document (76KB).
> For a summary, see [recommendations.md](recommendations.md).
> This detailed analysis is useful for reference but may be overwhelming for most users.

**Analysis Date:** 2025-10-30
**Total Files:** 103
**Comparison:** Our Library vs leading alternatives

---

## Executive Summary

- **EXCELLENT:** 2 files (1.9%)
- **GOOD:** 33 files (32.0%)
- **ACCEPTABLE:** 23 files (22.3%)
- **MODERATE_BLOAT:** 2 files (1.9%)
- **TEXT_QUALITY_ISSUE:** 35 files (34.0%)
- **SIGNIFICANT_LOSS:** 2 files (1.9%)

### By Category

**forms:** 10 files, avg size ratio: 0.87×

**mixed:** 89 files, avg size ratio: 1.32×

**technical:** 4 files, avg size ratio: 0.98×

---

## ⚠️ Issues Requiring Attention

### forms/irs_f1040.md

**Rating:** `SIGNIFICANT_LOSS`

**Issue:** Output is 11.6× smaller (possible content loss)

**Metrics:**
- Our size: 17,395 bytes
- established PDF library size: 200,972 bytes
- Ratio: 0.09×
- Bold sections: 209 vs 3294
- Garbled patterns: 175 vs 0
- Form fields: 0 vs 0
- Content similarity: 2.2%

**Our output preview:**
```
# Extracted from: irs_f1040.pdf

**Pages:** 2

---

## Form Fields

*This document contains 141 form fields:*

### Text Fields

| Field Name | Value |
|------------|-------|
| topmostSubform[0].Page1[
```

**established PDF library output preview:**
```
|1040<br>Department of the Treasury—Internal Revenue Service Form<br>U.S. Individual Income Tax Return|Col2|Col3|Col4|Col5|2024|Col7|OMB No. 1545-0074|Col9|Col10|Col11|Col12|IRS Use Only—Do not write 
```

---

### mixed/TYLWGSX5OYKE27DHTQXUJTBMKMHMKY3B.md

**Rating:** `SIGNIFICANT_LOSS`

**Issue:** Output is 23.0× smaller (possible content loss)

**Metrics:**
- Our size: 77 bytes
- established PDF library size: 1,768 bytes
- Ratio: 0.04×
- Bold sections: 1 vs 6
- Garbled patterns: 1 vs 0
- Form fields: 0 vs 0
- Content similarity: 4.2%

**Our output preview:**
```
# Extracted from: TYLWGSX5OYKE27DHTQXUJTBMKMHMKY3B.pdf

**Pages:** 1

---
```

**established PDF library output preview:**
```
# **Attachment 3** **PWSs with a History of Significant Non-Compliance in Tennessee** **FY1997 – FY2000**

**PWSID** **Name** **Means of Achievement**

0000115 Clarksburg Utility District 3 TCR violat
```

---

### mixed/GOCYUTJWJZBXHIUSFYG3LVX5SG6HPEVV.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 47 potential garbled text patterns

**Metrics:**
- Our size: 6,768 bytes
- established PDF library size: 6,759 bytes
- Ratio: 1.00×
- Bold sections: 48 vs 17
- Garbled patterns: 47 vs 0
- Form fields: 0 vs 0
- Content similarity: 39.6%

**Our output preview:**
```
# Extracted from: GOCYUTJWJZBXHIUSFYG3LVX5SG6HPEVV.pdf

**Pages:** 2

---

---

---

---

---

China
Linking U.S. Businesses to
Global Infrastructure Opportunities 
w w w . u s t d a . g o v
The U.S. 
```

**established PDF library output preview:**
```
# China

### Linking U.S. Businesses to Global Infrastructure Opportunities

#### w w w. u s t d a . g o v

The U.S. Trade and Development Agency helps companies create U.S. jobs through the export of
```

---

### forms/irs_f8821.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 57 potential garbled text patterns

**Metrics:**
- Our size: 6,145 bytes
- established PDF library size: 6,133 bytes
- Ratio: 1.00×
- Bold sections: 45 vs 34
- Garbled patterns: 57 vs 0
- Form fields: 0 vs 0
- Content similarity: 2.6%

**Our output preview:**
```
# Extracted from: irs_f8821.pdf

**Pages:** 1

---

## Form Fields

*This document contains 45 form fields:*

### Text Fields

| Field Name | Value |
|------------|-------|
| topmostSubform[0].Page1[0
```

**established PDF library output preview:**
```
|8821<br>Form<br>(Rev. January 2021)<br>Department of the Treasury<br>Internal Revenue Service|Tax Information Authorization<br>▶ Go to www.irs.gov/Form8821 for instructions and the latest information
```

---

### mixed/D4CM47RUIGRB3ELSBVH4KECQCVU7DJZF.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 20 potential garbled text patterns

**Metrics:**
- Our size: 5,203 bytes
- established PDF library size: 5,191 bytes
- Ratio: 1.00×
- Bold sections: 13 vs 10
- Garbled patterns: 20 vs 0
- Form fields: 0 vs 0
- Content similarity: 61.2%

**Our output preview:**
```
# Extracted from: D4CM47RUIGRB3ELSBVH4KECQCVU7DJZF.pdf

**Pages:** 3

---

---

---

---

---

AMENDED IN  ASSEMBL Y A UGUST 16, 2010
AMENDED IN  ASSEMBL Y A UGUST 2, 2010
AMENDED IN  ASSEMBL Y JUNE 2
```

**established PDF library output preview:**
```
AMENDED IN ASSEMBLY AUGUST 16, 2010


AMENDED IN ASSEMBLY AUGUST 2, 2010


AMENDED IN ASSEMBLY JUNE 24, 2010


AMENDED IN SENATE MARCH 23, 2010

# **SENATE BILL No. 1450**


**Introduced by Senator Si
```

---

### mixed/S6RR7MFG2QJUDGJSWOXXSMWFJOHAB3YU.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 64 potential garbled text patterns

**Metrics:**
- Our size: 21,443 bytes
- established PDF library size: 21,539 bytes
- Ratio: 1.00×
- Bold sections: 60 vs 45
- Garbled patterns: 64 vs 1
- Form fields: 0 vs 0
- Content similarity: 26.8%

**Our output preview:**
```
# Extracted from: S6RR7MFG2QJUDGJSWOXXSMWFJOHAB3YU.pdf

**Pages:** 13

---

---

---

---

---

---

---

---

---

---

---

**UNITED  STATES  ENVIRONMENTAL  PROTECTION  A** **GENCY**
**REGION  8**
*
```

**established PDF library output preview:**
```
**UNITED STATES ENVIRONMENTAL PROTECTION AGENCY**


**REGION 8**
**999 18** **[TH]** **STREET - SUITE 300**


**DENVER, CO  80202-2466**
**http://www.epa.gov/region08**


**June 14, 2004**
Ref: 8MO



```

---

### mixed/ELS4P7L7AQO4WFSJVMCLQZ4HLOQIHFZU.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 38 potential garbled text patterns

**Metrics:**
- Our size: 23,712 bytes
- established PDF library size: 23,603 bytes
- Ratio: 1.00×
- Bold sections: 36 vs 34
- Garbled patterns: 38 vs 7
- Form fields: 0 vs 0
- Content similarity: 74.3%

**Our output preview:**
```
# Extracted from: ELS4P7L7AQO4WFSJVMCLQZ4HLOQIHFZU.pdf

**Pages:** 8

---

---

---

**Comptroller of the Currency**
**Administrator of National Banks**
Washington, D.C.  20219
**Corporate Decision #9
```

**established PDF library output preview:**
```
**Comptroller of the Currency**
**Administrator of National Banks**


Washington, D.C. 20219

# **Corporate Decision #97-72** **August 1997**


**DECISION OF THE OFFICE OF THE COMPTROLLER OF THE CURRE
```

---

### mixed/XMW6SGXOJREQ4QRTL4QUIV76ZB4733MN.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 12 potential garbled text patterns

**Metrics:**
- Our size: 44,539 bytes
- established PDF library size: 44,320 bytes
- Ratio: 1.00×
- Bold sections: 404 vs 405
- Garbled patterns: 12 vs 2
- Form fields: 0 vs 0
- Content similarity: 72.4%

**Our output preview:**
```
# Extracted from: XMW6SGXOJREQ4QRTL4QUIV76ZB4733MN.pdf

**Pages:** 14

---

---

---

---

---

**Table of Contents**
**16.04.14 - Rules Governing the Low Income Home Energy Assistance Program**
000. 
```

**established PDF library output preview:**
```
## **_Table of Contents_**

**16.04.14 - Rules Governing the Low Income Home Energy Assistance Program**


000. Legal Authority. .......................................................................
```

---

### mixed/7GB7EXTYK2SHE3R3CBCOYKLOQT4CMEAF.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 24 potential garbled text patterns

**Metrics:**
- Our size: 31,518 bytes
- established PDF library size: 31,315 bytes
- Ratio: 1.01×
- Bold sections: 499 vs 457
- Garbled patterns: 24 vs 23
- Form fields: 0 vs 0
- Content similarity: 66.2%

**Our output preview:**
```
# Extracted from: 7GB7EXTYK2SHE3R3CBCOYKLOQT4CMEAF.pdf

**Pages:** 14

---

---

---

 
 
 
 
 
**PUBLIC DISCLOSURE**  
 
 
JUNE 23, 2004 
 
 
COMMUNITY REINVESTMENT ACT PERFORMANCE EVALUATION 
 
 
BA
```

**established PDF library output preview:**
```
**PUBLIC DISCLOSURE**


JUNE 23, 2004


COMMUNITY REINVESTMENT ACT PERFORMANCE EVALUATION


BARRE SAVINGS BANK


90148


56 COMMON STREET
BARRE, MASSACHUSETTS 01005


DIVISION OF BANKS

ONE SOUTH STAT
```

---

### mixed/MH3FFNRFQM4LT55ID7VX657NKPCRUB67.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 97 potential garbled text patterns

**Metrics:**
- Our size: 54,298 bytes
- established PDF library size: 53,244 bytes
- Ratio: 1.02×
- Bold sections: 192 vs 153
- Garbled patterns: 97 vs 2
- Form fields: 0 vs 0
- Content similarity: 64.4%

**Our output preview:**
```
# Extracted from: MH3FFNRFQM4LT55ID7VX657NKPCRUB67.pdf

**Pages:** 24

---

---

** **
 
**MOC MONTHLY REPORT ** **P**
** **
**East Side Access (MTACC-ESA) Project **
Metropolitan Transportation Autho
```

**established PDF library output preview:**
```
**PMOC MONTHLY REPORT**


**East Side Access (MTACC-ESA) Project**


Metropolitan Transportation Authority


New York, New York


Report Period August 1 to August 31, 2013


PMOC Contract No. DTFT60-0
```

---

### mixed/7A3MBRLFC6OU5KGMFIDEQPUOQTROBYUS.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 45 potential garbled text patterns

**Metrics:**
- Our size: 14,377 bytes
- established PDF library size: 14,071 bytes
- Ratio: 1.02×
- Bold sections: 35 vs 21
- Garbled patterns: 45 vs 4
- Form fields: 0 vs 0
- Content similarity: 56.6%

**Our output preview:**
```
# Extracted from: 7A3MBRLFC6OU5KGMFIDEQPUOQTROBYUS.pdf

**Pages:** 6

---

---

---

---

 
Department of Pesticide Regulation ** **
       
 
 
Arnold Schwarzenegger 
 
Mary-Ann Warmerdam 
Director 

```

**established PDF library output preview:**
```
# Department of Pesticide Regulation

Mary-Ann Warmerdam
_Director_


**DEPARTMENT OF PESTICIDE REGULATION**

**PESTICIDE REGISTRATION AND EVALUATION COMMITTEE**



Arnold Schwarzenegger
_Governor_



```

---

### forms/irs_fw2.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 487 potential garbled text patterns

**Metrics:**
- Our size: 43,192 bytes
- established PDF library size: 44,615 bytes
- Ratio: 0.97×
- Bold sections: 373 vs 801
- Garbled patterns: 487 vs 1
- Form fields: 0 vs 0
- Content similarity: 4.4%

**Our output preview:**
```
# Extracted from: irs_fw2.pdf

**Pages:** 11

---

## Form Fields

*This document contains 272 form fields:*

### Text Fields

| Field Name | Value |
|------------|-------|
| topmostSubform[0].CopyA[0
```

**established PDF library output preview:**
```
## **Attention:**

### You may file Forms W-2 and W-3 electronically on the SSA’s Employer - W 2 Filing Instructions and Information web page, which is also accessible at www.socialsecurity.gov/employ
```

---

### mixed/HGJIJLL3ZVEO2ISTFZSKH53BIC2K3UYX.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 60 potential garbled text patterns

**Metrics:**
- Our size: 29,048 bytes
- established PDF library size: 28,139 bytes
- Ratio: 1.03×
- Bold sections: 79 vs 28
- Garbled patterns: 60 vs 0
- Form fields: 0 vs 0
- Content similarity: 4.4%

**Our output preview:**
```
# Extracted from: HGJIJLL3ZVEO2ISTFZSKH53BIC2K3UYX.pdf

**Pages:** 9

---

 
2. In the first year, the modificnaitnigo,n , anodp erunning  tohfe facility will 
generate between 2,290 and 2,960 jobes  
```

**established PDF library output preview:**
```
EXECUTIVE OFFICE OF THE PRESIDENT

COUNCIL OF ECONOMIC ADVISERS

WASHINGTON, D.C.

This technical memo describes the likely economic impacts on the local economy of the
purchase and modification of th
```

---

### mixed/45W73IZ4UHYYGASU2Y4JO6Q7SC56OPTI.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 15 potential garbled text patterns

**Metrics:**
- Our size: 8,560 bytes
- established PDF library size: 8,287 bytes
- Ratio: 1.03×
- Bold sections: 16 vs 12
- Garbled patterns: 15 vs 1
- Form fields: 0 vs 0
- Content similarity: 80.6%

**Our output preview:**
```
# Extracted from: 45W73IZ4UHYYGASU2Y4JO6Q7SC56OPTI.pdf

**Pages:** 2

---

Administration oWfilliam J. Clinton, 19/9F5eb. 27 325
today who represent the strong partnership
in disaster response between
```

**established PDF library output preview:**
```
_Administration of William J. Clinton, 1995 / Feb. 27_ 325



today who represent the strong partnership
in disaster response between the Red Cross
and AmeriCorps, our national service program. Johnny
```

---

### forms/irs_fw9.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 42 potential garbled text patterns

**Metrics:**
- Our size: 40,716 bytes
- established PDF library size: 42,302 bytes
- Ratio: 0.96×
- Bold sections: 213 vs 139
- Garbled patterns: 42 vs 3
- Form fields: 0 vs 0
- Content similarity: 3.6%

**Our output preview:**
```
# Extracted from: irs_fw9.pdf

**Pages:** 6

---

## Form Fields

*This document contains 23 form fields:*

### Text Fields

| Field Name | Value |
|------------|-------|
| topmostSubform[0].Page1[0].
```

**established PDF library output preview:**
```
# Form  W-9 Request for Taxpayer
## (Rev. March 2024) Identification Number and Certification

Department of the Treasury
Internal Revenue Service **Go to** _**www.irs.gov/FormW9**_ **for instructions
```

---

### mixed/LCFQJGJLCOJ56B3YM3XIPRJ7DFUQPTDG.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 241 potential garbled text patterns

**Metrics:**
- Our size: 225,743 bytes
- established PDF library size: 216,395 bytes
- Ratio: 1.04×
- Bold sections: 776 vs 405
- Garbled patterns: 241 vs 21
- Form fields: 0 vs 0
- Content similarity: 16.8%

**Our output preview:**
```
# Extracted from: LCFQJGJLCOJ56B3YM3XIPRJ7DFUQPTDG.pdf

**Pages:** 106

---

---

---

The U.S-.Swiss Safe Harbor Guide to SCeelrft-ificat ion                               U.S. Department ofc eC omme
```

**established PDF library output preview:**
```
## U.S.-Swiss Safe Harbor Framework

# A Guide to Self-Certification

The U.S.-Swiss Safe Harbor Guide to Self-Certification U.S. Department of Commerce


### Table of Contents

Introduction. . . . . 
```

---

### technical/arxiv_2312.17533.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 71 potential garbled text patterns

**Metrics:**
- Our size: 32,364 bytes
- established PDF library size: 33,920 bytes
- Ratio: 0.95×
- Bold sections: 1 vs 67
- Garbled patterns: 71 vs 1
- Form fields: 0 vs 0
- Content similarity: 74.1%

**Our output preview:**
```
# Extracted from: arxiv_2312.17533.pdf

**Pages:** 17

---

Void Shape Identifcation in a 2D Point Distribution
Netzer Moriya
1 Abstract
We introduce a new approach for identifying and characterizing 
```

**established PDF library output preview:**
```
## Void Shape Identification in a 2D Point Distribution

### Netzer Moriya **1 Abstract**

We introduce a new approach for identifying and characterizing voids within two-dimensional
(2D) point distri
```

---

### mixed/2Z5VOQ6G6CMR5GMVSAAXULXHXTMJPTM2.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 177 potential garbled text patterns

**Metrics:**
- Our size: 400,626 bytes
- established PDF library size: 381,726 bytes
- Ratio: 1.05×
- Bold sections: 2024 vs 1561
- Garbled patterns: 177 vs 6
- Form fields: 0 vs 0
- Content similarity: 2.2%

**Our output preview:**
```
# Extracted from: 2Z5VOQ6G6CMR5GMVSAAXULXHXTMJPTM2.pdf

**Pages:** 174

---

---

---

---

---

Department of Energy
FY 2007 Congressional 
Budget Request
Other defense activities
Security & Safety P
```

**established PDF library output preview:**
```
**Other Defense Activities**


**Safeguards and Security Crosscut**


**Other Defense Activities**


**Safeguards and Security Crosscut**


**Volume 2**


**Table of Contents**


Page
Appropriation Ac
```

---

### technical/arxiv_2312.00001.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 81 potential garbled text patterns

**Metrics:**
- Our size: 51,509 bytes
- established PDF library size: 55,242 bytes
- Ratio: 0.93×
- Bold sections: 1 vs 105
- Garbled patterns: 81 vs 1
- Form fields: 0 vs 0
- Content similarity: 85.3%

**Our output preview:**
```
# Extracted from: arxiv_2312.00001.pdf

**Pages:** 22

---

ON RANDOM PAIRWISE COMPARISONS MATRICES AND
THEIR GEOMETRY.
JEAN-PIERRE MAGNOT
Abstract. We describe a framework for random pairwise compari
```

**established PDF library output preview:**
```
**ON RANDOM PAIRWISE COMPARISONS MATRICES AND**

**THEIR GEOMETRY.**


JEAN-PIERRE MAGNOT


Abstract. We describe a framework for random pairwise comparisons
matrices, inspired by selected constructio
```

---

### mixed/AJXUPPG2S5WLMN76I434ABJTFQFTSFSO.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 15 potential garbled text patterns

**Metrics:**
- Our size: 4,941 bytes
- established PDF library size: 4,611 bytes
- Ratio: 1.07×
- Bold sections: 39 vs 35
- Garbled patterns: 15 vs 2
- Form fields: 0 vs 0
- Content similarity: 62.3%

**Our output preview:**
```
# Extracted from: AJXUPPG2S5WLMN76I434ABJTFQFTSFSO.pdf

**Pages:** 4

---

** REAL ESTATE BOARD  **
** **
**AGENDA **
** **
**Thursday, May 14, 2009 - 9:00 a.m. **
**2**
**nd**
** Floor **
**Departmen
```

**established PDF library output preview:**
```
**REAL ESTATE BOARD**


**AGENDA**


**Thursday, May 14, 2009 - 9:00 a.m.**

**2** **[nd]** **Floor**

**Department of Professional and Occupational Regulation**

**9960 Mayland Drive**
**Richmond, Vi
```

---

### mixed/SE6VNMZC7SS4KLSVUOXM3QR4FK2WJHWZ.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 83 potential garbled text patterns

**Metrics:**
- Our size: 29,686 bytes
- established PDF library size: 32,205 bytes
- Ratio: 0.92×
- Bold sections: 204 vs 343
- Garbled patterns: 83 vs 2
- Form fields: 0 vs 0
- Content similarity: 34.8%

**Our output preview:**
```
# Extracted from: SE6VNMZC7SS4KLSVUOXM3QR4FK2WJHWZ.pdf

**Pages:** 13

---

---

---

---

Trust and
Agency
Funds —
Federal

---

---

---

---

---

---

---

---

---

---

---

---

---

---

State
```

**established PDF library output preview:**
```
_State of California • Budgetary/Legal Basis Annual Report_

## **Nongovernmental Cost Funds** **Trust and Agency Funds – Federal** **Balance Sheet**


**June 30, 2001**
(Amounts in thousands)


**ASS
```

---

### mixed/MM3LE7UZACMNXBDXA5FM6MTGBLZG7N4W.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 63 potential garbled text patterns

**Metrics:**
- Our size: 104,524 bytes
- established PDF library size: 96,623 bytes
- Ratio: 1.08×
- Bold sections: 1314 vs 632
- Garbled patterns: 63 vs 2
- Form fields: 0 vs 0
- Content similarity: 28.2%

**Our output preview:**
```
# Extracted from: MM3LE7UZACMNXBDXA5FM6MTGBLZG7N4W.pdf

**Pages:** 28

---

---

---

---

---

---

**CÓMO**
**COSTEAR SUS**
**ESTUDIOS**
**SUPERIORES**
**2012–13 Guía sobre la ayuda federal para est
```

**established PDF library output preview:**
```
**Sitios web útiles e información de contacto**






                                   

                                   

                                   

                                   
```

---

### mixed/YPNQXE4XMRDK6YTLK3B44PDTF4TYHBNY.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 11 potential garbled text patterns

**Metrics:**
- Our size: 11,422 bytes
- established PDF library size: 10,374 bytes
- Ratio: 1.10×
- Bold sections: 138 vs 106
- Garbled patterns: 11 vs 1
- Form fields: 0 vs 0
- Content similarity: 39.6%

**Our output preview:**
```
# Extracted from: YPNQXE4XMRDK6YTLK3B44PDTF4TYHBNY.pdf

**Pages:** 6

---

---

---

---

 
STATE OF CALIFORNIA — THE RESOURCES AGENCY                                ARNOLD SCHWARZENEGGER,G overno r 

```

**established PDF library output preview:**
```
STATE OF CALIFORNIA — THE RESOURCES AGENCY ARNOLD SCHWARZENEGGER, _Governor_
**CALIFORNIA ENERGY COMMISSION**

1516 Ninth Street
Sacramento, California 95814

Main website: www.energy.ca.gov

## **Not
```

---

### mixed/MMSNF4WV7XLHQFKEQYKHHH7GJPPQJQ7U.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 82 potential garbled text patterns

**Metrics:**
- Our size: 16,207 bytes
- established PDF library size: 14,704 bytes
- Ratio: 1.10×
- Bold sections: 22 vs 5
- Garbled patterns: 82 vs 39
- Form fields: 0 vs 0
- Content similarity: 10.0%

**Our output preview:**
```
# Extracted from: MMSNF4WV7XLHQFKEQYKHHH7GJPPQJQ7U.pdf

**Pages:** 39

---

---

---

---

---

LaThuile Italy / David Fi,n lFeeyrmilab / March 2007             Slide  1
Liquid Argon TPC R&D Update
(a
```

**established PDF library output preview:**
```
###### Liquid Argon TPC R&D Update (a Fermilab perspective) • Massive LAr Detector Paradigms • Technical Efforts at Fermilab

LaThuile Italy / David Finley, Fermilab / March 2007 Slide 1


#### Massiv
```

---

### forms/irs_f4506t.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 30 potential garbled text patterns

**Metrics:**
- Our size: 19,597 bytes
- established PDF library size: 17,771 bytes
- Ratio: 1.10×
- Bold sections: 125 vs 100
- Garbled patterns: 30 vs 0
- Form fields: 0 vs 0
- Content similarity: 2.8%

**Our output preview:**
```
# Extracted from: irs_f4506t.pdf

**Pages:** 2

---

## Form Fields

*This document contains 29 form fields:*

### Text Fields

| Field Name | Value |
|------------|-------|
| topmostSubform[0].Page1[
```

**established PDF library output preview:**
```
## Form  4506-T



(April 2025) OMB No. 1545-1872



Department of the Treasury
Internal Revenue Service



Request for Transcript of Tax Return
**Do not sign this form unless all applicable lines hav
```

---

### mixed/7WOCAN6T6B5JRJB4C5LAIHLE6ERU2V22.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 14 potential garbled text patterns

**Metrics:**
- Our size: 9,490 bytes
- established PDF library size: 10,757 bytes
- Ratio: 0.88×
- Bold sections: 87 vs 66
- Garbled patterns: 14 vs 15
- Form fields: 0 vs 0
- Content similarity: 2.2%

**Our output preview:**
```
# Extracted from: 7WOCAN6T6B5JRJB4C5LAIHLE6ERU2V22.pdf

**Pages:** 2

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

                      U n i t e d   S t a t e s   Depar
```

**established PDF library output preview:**
```
United States Department of Agriculture
National Agricultural Statistics Service
# **Southern Region News Release** **Broiler Hatcher** **y**


**Cooperating with the Alabama Department of Agriculture
```

---

### forms/irs_f1040v.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 15 potential garbled text patterns

**Metrics:**
- Our size: 8,651 bytes
- established PDF library size: 10,128 bytes
- Ratio: 0.85×
- Bold sections: 59 vs 76
- Garbled patterns: 15 vs 0
- Form fields: 0 vs 0
- Content similarity: 2.0%

**Our output preview:**
```
# Extracted from: irs_f1040v.pdf

**Pages:** 2

---

## Form Fields

*This document contains 15 form fields:*

### Text Fields

| Field Name | Value |
|------------|-------|
| topmostSubform[0].Page1[
```

**established PDF library output preview:**
```
# **2024 Form 1040-V**



Department of the Treasury
**Internal Revenue Service**



**What Is Form 1040-V?**

It’s a statement you send with your check or money order for
any balance due on the “Amou
```

---

### forms/irs_fw4.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 31 potential garbled text patterns

**Metrics:**
- Our size: 24,506 bytes
- established PDF library size: 29,093 bytes
- Ratio: 0.84×
- Bold sections: 169 vs 194
- Garbled patterns: 31 vs 0
- Form fields: 0 vs 0
- Content similarity: 1.4%

**Our output preview:**
```
# Extracted from: irs_fw4.pdf

**Pages:** 4

---

## Form Fields

*This document contains 29 form fields:*

### Text Fields

| Field Name | Value |
|------------|-------|
| topmostSubform[0].Page1[0].
```

**established PDF library output preview:**
```
|W-4<br>Form<br>Department of the Treasury<br>Internal Revenue Service|Col2|Employee’s Withholding Certificate<br>Complete Form W-4 so that your employer can withhold the correct federal income tax fr
```

---

### mixed/KMELIR3DJDUFB52NSPC42LSIU6OOD77U.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 11 potential garbled text patterns

**Metrics:**
- Our size: 5,007 bytes
- established PDF library size: 5,949 bytes
- Ratio: 0.84×
- Bold sections: 32 vs 17
- Garbled patterns: 11 vs 9
- Form fields: 0 vs 0
- Content similarity: 1.4%

**Our output preview:**
```
# Extracted from: KMELIR3DJDUFB52NSPC42LSIU6OOD77U.pdf

**Pages:** 3

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---


```

**established PDF library output preview:**
```
|Col1|Southeast Region<br>Protected Resources Division|Col3|
|---|---|---|
|<br> <br>**Southeast Region**<br>**(Texas through North Carolina, Puerto Rico, and the U.S. Virgin Islands)**<br>**Threatene
```

---

### forms/irs_f1099msc.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 253 potential garbled text patterns

**Metrics:**
- Our size: 19,997 bytes
- established PDF library size: 26,878 bytes
- Ratio: 0.74×
- Bold sections: 160 vs 161
- Garbled patterns: 253 vs 3
- Form fields: 0 vs 0
- Content similarity: 1.8%

**Our output preview:**
```
# Extracted from: irs_f1099msc.pdf

**Pages:** 6

---

## Form Fields

*This document contains 119 form fields:*

### Text Fields

| Field Name | Value |
|------------|-------|
| topmostSubform[0].Cop
```

**established PDF library output preview:**
```
# **Attention:**

Copy A of this form is provided for informational purposes only. Copy A appears in red,
similar to the official IRS form. The official printed version of Copy A of this IRS form is
s
```

---

### mixed/QRJ42GGGA52M42R57XTGIQONYKAKWVG5.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 134 potential garbled text patterns

**Metrics:**
- Our size: 18,573 bytes
- established PDF library size: 14,594 bytes
- Ratio: 1.27×
- Bold sections: 1232 vs 103
- Garbled patterns: 134 vs 0
- Form fields: 0 vs 0
- Content similarity: 3.2%

**Our output preview:**
```
# Extracted from: QRJ42GGGA52M42R57XTGIQONYKAKWVG5.pdf

**Pages:** 7

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

T  **S**Ta
```

**established PDF library output preview:**
```
# **Special Education School District Data Profile for 2008-09**

The Special Education School District Data Profile is prepared in accordance with the requirement of the Individuals with Disabilities
```

---

### mixed/XIUQD2OYDIFIKQY5T5AHYPEFOP4XZFS7.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 36 potential garbled text patterns

**Metrics:**
- Our size: 56,547 bytes
- established PDF library size: 39,160 bytes
- Ratio: 1.44×
- Bold sections: 1 vs 0
- Garbled patterns: 36 vs 28
- Form fields: 0 vs 0
- Content similarity: 74.4%

**Our output preview:**
```
# Extracted from: XIUQD2OYDIFIKQY5T5AHYPEFOP4XZFS7.pdf

**Pages:** 6

---

Census 2000, Summary File 1 General Profile 1: PERSONS BY RACE, AGE, & SEX; HOUSEHOLDS AND FAMILIES BY RACE AND BY TYPE      
```

**established PDF library output preview:**
```
Census 2000, Summary File 1 General Profile 1: PERSONS BY RACE, AGE, & SEX; HOUSEHOLDS AND FAMILIES BY RACE AND BY TYPE             Gen-1
Area Name: Farmington town                                    
```

---

### forms/irs_f1040es.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 310 potential garbled text patterns

**Metrics:**
- Our size: 85,574 bytes
- established PDF library size: 157,920 bytes
- Ratio: 0.54×
- Bold sections: 2434 vs 1096
- Garbled patterns: 310 vs 1
- Form fields: 0 vs 0
- Content similarity: 1.8%

**Our output preview:**
```
# Extracted from: irs_f1040es.pdf

**Pages:** 12

---

## Form Fields

*This document contains 117 form fields:*

### Text Fields

| Field Name | Value |
|------------|-------|
| topmostSubform[0].Pag
```

**established PDF library output preview:**
```
# **2025**
### **Form 1040-ES**

**Estimated Tax for Individuals**


**Purpose of This Package**
Use Form 1040-ES to figure and pay your estimated tax
for 2025.


Estimated tax is the method used to p
```

---

### mixed/UFTWPHWPAMA7G4B6F5SMUFNA3HU6H5UW.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 34 potential garbled text patterns

**Metrics:**
- Our size: 7,381 bytes
- established PDF library size: 4,643 bytes
- Ratio: 1.59×
- Bold sections: 37 vs 15
- Garbled patterns: 34 vs 11
- Form fields: 0 vs 0
- Content similarity: 4.0%

**Our output preview:**
```
# Extracted from: UFTWPHWPAMA7G4B6F5SMUFNA3HU6H5UW.pdf

**Pages:** 3

---

## Form Fields

*This document contains 86 form fields:*

### Text Fields

| Field Name | Value |
|------------|-------|
| Pe
```

**established PDF library output preview:**
```
**UNITED STATES DISTRICT COURT**

**DISTRICT OF SOUTH CAROLINA**


**Application for Mediators**


_Please complete the entire application, using additional paper if necessary. You may also attach a r
```

---

### forms/irs_f2848.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 193 potential garbled text patterns

**Metrics:**
- Our size: 14,441 bytes
- established PDF library size: 9,068 bytes
- Ratio: 1.59×
- Bold sections: 79 vs 55
- Garbled patterns: 193 vs 0
- Form fields: 0 vs 0
- Content similarity: 2.0%

**Our output preview:**
```
# Extracted from: irs_f2848.pdf

**Pages:** 2

---

## Form Fields

*This document contains 92 form fields:*

### Text Fields

| Field Name | Value |
|------------|-------|
| topmostSubform[0].Page1[0
```

**established PDF library output preview:**
```
|2848<br>Form<br>(Rev. January 2021)<br>Department of the Treasury<br>Internal Revenue Service|Power of Attorney<br>and Declaration of Representative<br>▶ Go to www.irs.gov/Form2848 for instructions a
```

---

### mixed/YBTLDNWUYL3SLS4NVMFEB3OFUWOZBLA7.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 452 potential garbled text patterns

**Metrics:**
- Our size: 57,096 bytes
- established PDF library size: 33,141 bytes
- Ratio: 1.72×
- Bold sections: 199 vs 38
- Garbled patterns: 452 vs 0
- Form fields: 0 vs 0
- Content similarity: 3.2%

**Our output preview:**
```
# Extracted from: YBTLDNWUYL3SLS4NVMFEB3OFUWOZBLA7.pdf

**Pages:** 19

---

Grades **6-8**
Telephone **(631) 893-3290**
Principal **BERNADETTE BURNS**
School ID **58-05-09-03-0011**
**DISTRICT**
**WES
```

**established PDF library output preview:**
```
### This School’s Report Card

The New York State School Report Card is an important part
of the Board of Regents effort to raise learning standards for all
students. It provides information to the pu
```

---

### mixed/SESP5SOLQQMFWGNYXPD3UCI2KCA6PHQO.md

**Rating:** `TEXT_QUALITY_ISSUE`

**Issue:** Contains 34 potential garbled text patterns

**Metrics:**
- Our size: 5,255 bytes
- established PDF library size: 2,220 bytes
- Ratio: 2.37×
- Bold sections: 208 vs 4
- Garbled patterns: 34 vs 0
- Form fields: 0 vs 0
- Content similarity: 3.0%

**Our output preview:**
```
# Extracted from: SESP5SOLQQMFWGNYXPD3UCI2KCA6PHQO.pdf

**Pages:** 1

---

---

---

**(p)**
[Millions of U.S. Dollars]
3% 3%  2r1% 8% 10% 4%9 % 0% 1r%  1r8%8% 8% 5% 9% 7%5% 10% 6% 5r%  3r%8% 6% 8% 8%
```

**established PDF library output preview:**
```
**U.S. TRAVEL AND TOURISM BALANCE OF TRADE: European Union**
**Receipts (Exports) and Payments (Imports)**
**2007-2016** **[(p)]**


[Millions of U.S. Dollars]





(p) Preliminary, subject to future 
```

---

## ✅ Excellent Quality Files

These files show near-perfect matching with leading alternatives:

| File | Size Ratio | Bold Ratio | Similarity |
|------|-----------|-----------|------------|
| mixed/YE5PQJ6NUYA6UOWHADZIVVMCINU4AYZF.md | 1.00× | 1.13× | 19.2% |
| mixed/WZRQHWEXEG24SJPSEOEVB6FMPU6DA4VU.md | 1.00× | 1.50× | 77.1% |
| mixed/Z42OE7PSGVKK54B3J2LWZ4THMYJIJHGJ.md | 1.01× | 1.05× | 1.4% |
| mixed/P7ZED35W7LHI6YLKM5TVSLOQVACYSHHM.md | 1.01× | 1.33× | 79.3% |
| mixed/EMMM5FRYBCPVBLVU4RY6OFEKZFWM2KIJ.md | 0.99× | 0.80× | 75.0% |
| mixed/SEVNFYZBX7VQEWEG5SQQTFZK24PCUDFU.md | 1.01× | 0.00× | 4.4% |
| mixed/WSP5DEW3S4BVQYFWKEFDC3HDLMRK3UT2.md | 1.02× | 0.44× | 72.2% |
| mixed/NM76DD2NN5OG5VHK5TQMZV3OO3T6UDAK.md | 1.02× | 1.03× | 61.0% |
| mixed/WXR2YY3TSXGUNVC2VECKTVIJO7PMECRS.md | 1.02× | 1.02× | 35.4% |
| mixed/CTMYRF75O3COU6UV5KWIFEF6TLJF4REJ.md | 1.03× | 4.00× | 61.0% |
| mixed/YS6AIKVZKRRKLU2JGEBFS3PO665RXHWI.md | 1.03× | 0.75× | 27.4% |
| mixed/YQZG4CHDFUMUUDUEO2IY3GSWB4YCIKJI.md | 0.97× | 1.61× | 66.2% |
| mixed/7N6KRBZIEFV4F5QLLW3GBF6LKNNWSWVB.md | 0.97× | 1.33× | 2.6% |
| mixed/RHW47KIVYBR2WPS44NNXESVQHKWOOXXD.md | 1.03× | 0.83× | 73.0% |
| technical/arxiv_2401.00001.md | 0.96× | 0.02× | 64.1% |
| mixed/H7U4KMXPQKUBDKIPQQRC6ETJZEZR3OCZ.md | 1.04× | 1.25× | 12.2% |
| mixed/TW5273JZ43VOQUCL7FRZ2N6STHYBBCQ4.md | 1.04× | 0.00× | 3.2% |
| mixed/HNBALTFDCV5YCQB772EJLOZGFV3JQLXS.md | 1.04× | 0.00× | 19.4% |
| mixed/NFLMOWBSAYHS4IFKAY5KSXU64BTAEZJ3.md | 1.04× | 0.00× | 2.0% |
| mixed/AYZVGVPYWC6TNBDO76IU7PON3RZ22WQP.md | 1.04× | 1.05× | 53.8% |

---

## 📋 Complete File Analysis

Sorted by quality rating (worst to best):

### 🟠 forms/irs_f1040.md

**Quality:** `SIGNIFICANT_LOSS` - Output is 11.6× smaller (possible content loss)

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 17,395 bytes | 200,972 bytes | 0.09× |
| **Bold Sections** | 209 | 3294 | 0.06× |
| **Lines** | 399 | 207 | 1.93× |
| **BR Tags** | 0 | 18019 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.2% |

---

### 🟠 mixed/TYLWGSX5OYKE27DHTQXUJTBMKMHMKY3B.md

**Quality:** `SIGNIFICANT_LOSS` - Output is 23.0× smaller (possible content loss)

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 77 bytes | 1,768 bytes | 0.04× |
| **Bold Sections** | 1 | 6 | 0.17× |
| **Lines** | 8 | 38 | 0.21× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 4.2% |

---

### 🟡 mixed/GOCYUTJWJZBXHIUSFYG3LVX5SG6HPEVV.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 47 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 6,768 bytes | 6,759 bytes | 1.00× |
| **Bold Sections** | 48 | 17 | 2.82× |
| **Lines** | 141 | 172 | 0.82× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 39.6% |

---

### 🟡 forms/irs_f8821.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 57 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 6,145 bytes | 6,133 bytes | 1.00× |
| **Bold Sections** | 45 | 34 | 1.32× |
| **Lines** | 130 | 101 | 1.29× |
| **BR Tags** | 0 | 135 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.6% |

---

### 🟡 mixed/D4CM47RUIGRB3ELSBVH4KECQCVU7DJZF.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 20 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 5,203 bytes | 5,191 bytes | 1.00× |
| **Bold Sections** | 13 | 10 | 1.30× |
| **Lines** | 126 | 228 | 0.55× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 61.2% |

---

### 🟡 mixed/S6RR7MFG2QJUDGJSWOXXSMWFJOHAB3YU.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 64 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 21,443 bytes | 21,539 bytes | 1.00× |
| **Bold Sections** | 60 | 45 | 1.33× |
| **Lines** | 371 | 817 | 0.45× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 26.8% |

---

### 🟡 mixed/ELS4P7L7AQO4WFSJVMCLQZ4HLOQIHFZU.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 38 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 23,712 bytes | 23,603 bytes | 1.00× |
| **Bold Sections** | 36 | 34 | 1.06× |
| **Lines** | 327 | 397 | 0.82× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 74.3% |

---

### 🟡 mixed/XMW6SGXOJREQ4QRTL4QUIV76ZB4733MN.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 12 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 44,539 bytes | 44,320 bytes | 1.00× |
| **Bold Sections** | 404 | 405 | 1.00× |
| **Lines** | 872 | 1,137 | 0.77× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 72.4% |

---

### 🟡 mixed/7GB7EXTYK2SHE3R3CBCOYKLOQT4CMEAF.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 24 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 31,518 bytes | 31,315 bytes | 1.01× |
| **Bold Sections** | 499 | 457 | 1.09× |
| **Lines** | 831 | 723 | 1.15× |
| **BR Tags** | 0 | 173 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 66.2% |

---

### 🟡 mixed/MH3FFNRFQM4LT55ID7VX657NKPCRUB67.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 97 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 54,298 bytes | 53,244 bytes | 1.02× |
| **Bold Sections** | 192 | 153 | 1.25× |
| **Lines** | 836 | 1,197 | 0.70× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 64.4% |

---

### 🟡 mixed/7A3MBRLFC6OU5KGMFIDEQPUOQTROBYUS.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 45 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 14,377 bytes | 14,071 bytes | 1.02× |
| **Bold Sections** | 35 | 21 | 1.67× |
| **Lines** | 294 | 282 | 1.04× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 56.6% |

---

### 🟡 forms/irs_fw2.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 487 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 43,192 bytes | 44,615 bytes | 0.97× |
| **Bold Sections** | 373 | 801 | 0.47× |
| **Lines** | 702 | 514 | 1.37× |
| **BR Tags** | 0 | 618 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 4.4% |

---

### 🟡 mixed/HGJIJLL3ZVEO2ISTFZSKH53BIC2K3UYX.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 60 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 29,048 bytes | 28,139 bytes | 1.03× |
| **Bold Sections** | 79 | 28 | 2.82× |
| **Lines** | 517 | 444 | 1.16× |
| **BR Tags** | 0 | 80 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 4.4% |

---

### 🟡 mixed/45W73IZ4UHYYGASU2Y4JO6Q7SC56OPTI.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 15 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 8,560 bytes | 8,287 bytes | 1.03× |
| **Bold Sections** | 16 | 12 | 1.33× |
| **Lines** | 163 | 204 | 0.80× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 80.6% |

---

### 🟡 forms/irs_fw9.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 42 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 40,716 bytes | 42,302 bytes | 0.96× |
| **Bold Sections** | 213 | 139 | 1.53× |
| **Lines** | 672 | 968 | 0.69× |
| **BR Tags** | 0 | 176 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 3.6% |

---

### 🟡 mixed/LCFQJGJLCOJ56B3YM3XIPRJ7DFUQPTDG.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 241 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 225,743 bytes | 216,395 bytes | 1.04× |
| **Bold Sections** | 776 | 405 | 1.92× |
| **Lines** | 4,137 | 4,899 | 0.84× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 16.8% |

---

### 🟡 technical/arxiv_2312.17533.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 71 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 32,364 bytes | 33,920 bytes | 0.95× |
| **Bold Sections** | 1 | 67 | 0.01× |
| **Lines** | 625 | 824 | 0.76× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 74.1% |

---

### 🟡 mixed/2Z5VOQ6G6CMR5GMVSAAXULXHXTMJPTM2.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 177 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 400,626 bytes | 381,726 bytes | 1.05× |
| **Bold Sections** | 2024 | 1561 | 1.30× |
| **Lines** | 5,874 | 8,523 | 0.69× |
| **BR Tags** | 0 | 37 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.2% |

---

### 🟡 technical/arxiv_2312.00001.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 81 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 51,509 bytes | 55,242 bytes | 0.93× |
| **Bold Sections** | 1 | 105 | 0.01× |
| **Lines** | 1,430 | 1,551 | 0.92× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 85.3% |

---

### 🟡 mixed/AJXUPPG2S5WLMN76I434ABJTFQFTSFSO.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 15 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 4,941 bytes | 4,611 bytes | 1.07× |
| **Bold Sections** | 39 | 35 | 1.11× |
| **Lines** | 168 | 217 | 0.77× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 62.3% |

---

### 🟡 mixed/SE6VNMZC7SS4KLSVUOXM3QR4FK2WJHWZ.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 83 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 29,686 bytes | 32,205 bytes | 0.92× |
| **Bold Sections** | 204 | 343 | 0.59× |
| **Lines** | 700 | 3,424 | 0.20× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 34.8% |

---

### 🟡 mixed/MM3LE7UZACMNXBDXA5FM6MTGBLZG7N4W.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 63 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 104,524 bytes | 96,623 bytes | 1.08× |
| **Bold Sections** | 1314 | 632 | 2.08× |
| **Lines** | 1,959 | 2,753 | 0.71× |
| **BR Tags** | 0 | 147 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 28.2% |

---

### 🟡 mixed/YPNQXE4XMRDK6YTLK3B44PDTF4TYHBNY.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 11 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 11,422 bytes | 10,374 bytes | 1.10× |
| **Bold Sections** | 138 | 106 | 1.30× |
| **Lines** | 438 | 405 | 1.08× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 39.6% |

---

### 🟡 mixed/MMSNF4WV7XLHQFKEQYKHHH7GJPPQJQ7U.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 82 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 16,207 bytes | 14,704 bytes | 1.10× |
| **Bold Sections** | 22 | 5 | 4.40× |
| **Lines** | 795 | 789 | 1.01× |
| **BR Tags** | 0 | 54 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 10.0% |

---

### 🟡 forms/irs_f4506t.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 30 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 19,597 bytes | 17,771 bytes | 1.10× |
| **Bold Sections** | 125 | 100 | 1.25× |
| **Lines** | 345 | 572 | 0.60× |
| **BR Tags** | 0 | 3 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.8% |

---

### 🟡 mixed/7WOCAN6T6B5JRJB4C5LAIHLE6ERU2V22.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 14 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 9,490 bytes | 10,757 bytes | 0.88× |
| **Bold Sections** | 87 | 66 | 1.32× |
| **Lines** | 198 | 276 | 0.72× |
| **BR Tags** | 0 | 528 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.2% |

---

### 🟡 forms/irs_f1040v.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 15 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 8,651 bytes | 10,128 bytes | 0.85× |
| **Bold Sections** | 59 | 76 | 0.78× |
| **Lines** | 192 | 237 | 0.81× |
| **BR Tags** | 0 | 51 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.0% |

---

### 🟡 forms/irs_fw4.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 31 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 24,506 bytes | 29,093 bytes | 0.84× |
| **Bold Sections** | 169 | 194 | 0.87× |
| **Lines** | 435 | 537 | 0.81× |
| **BR Tags** | 0 | 673 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 1.4% |

---

### 🟡 mixed/KMELIR3DJDUFB52NSPC42LSIU6OOD77U.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 11 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 5,007 bytes | 5,949 bytes | 0.84× |
| **Bold Sections** | 32 | 17 | 1.88× |
| **Lines** | 201 | 105 | 1.91× |
| **BR Tags** | 0 | 12 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 1.4% |

---

### 🟡 forms/irs_f1099msc.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 253 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 19,997 bytes | 26,878 bytes | 0.74× |
| **Bold Sections** | 160 | 161 | 0.99× |
| **Lines** | 401 | 209 | 1.92× |
| **BR Tags** | 0 | 354 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 1.8% |

---

### 🟡 mixed/QRJ42GGGA52M42R57XTGIQONYKAKWVG5.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 134 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 18,573 bytes | 14,594 bytes | 1.27× |
| **Bold Sections** | 1232 | 103 | 11.90× |
| **Lines** | 402 | 307 | 1.31× |
| **BR Tags** | 0 | 79 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 3.2% |

---

### 🟡 mixed/XIUQD2OYDIFIKQY5T5AHYPEFOP4XZFS7.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 36 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 56,547 bytes | 39,160 bytes | 1.44× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 390 | 408 | 0.96× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 74.4% |

---

### 🟡 forms/irs_f1040es.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 310 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 85,574 bytes | 157,920 bytes | 0.54× |
| **Bold Sections** | 2434 | 1096 | 2.22× |
| **Lines** | 1,007 | 1,355 | 0.74× |
| **BR Tags** | 0 | 7745 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 1.8% |

---

### 🟡 mixed/UFTWPHWPAMA7G4B6F5SMUFNA3HU6H5UW.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 34 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 7,381 bytes | 4,643 bytes | 1.59× |
| **Bold Sections** | 37 | 15 | 2.47× |
| **Lines** | 265 | 179 | 1.48× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 4.0% |

---

### 🟡 forms/irs_f2848.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 193 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 14,441 bytes | 9,068 bytes | 1.59× |
| **Bold Sections** | 79 | 55 | 1.44× |
| **Lines** | 243 | 211 | 1.15× |
| **BR Tags** | 0 | 68 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.0% |

---

### 🟡 mixed/YBTLDNWUYL3SLS4NVMFEB3OFUWOZBLA7.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 452 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 57,096 bytes | 33,141 bytes | 1.72× |
| **Bold Sections** | 199 | 38 | 5.24× |
| **Lines** | 2,770 | 1,911 | 1.45× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 3.2% |

---

### 🟡 mixed/SESP5SOLQQMFWGNYXPD3UCI2KCA6PHQO.md

**Quality:** `TEXT_QUALITY_ISSUE` - Contains 34 potential garbled text patterns

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 5,255 bytes | 2,220 bytes | 2.37× |
| **Bold Sections** | 208 | 4 | 52.00× |
| **Lines** | 38 | 42 | 0.90× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 3.0% |

---

### 🟡 mixed/D2FRDPDTXJKVTJKEBESWUWBYZDJRBNAI.md

**Quality:** `MODERATE_BLOAT` - Output is 5.8× larger

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 560 bytes | 96 bytes | 5.83× |
| **Bold Sections** | 77 | 1 | 77.00× |
| **Lines** | 14 | 10 | 1.40× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 5.1% |

---

### 🟡 mixed/KTCXROTYIAYW34ZFMVAKRU5FQFD3D7XQ.md

**Quality:** `MODERATE_BLOAT` - Output is 7.0× larger

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 429 bytes | 61 bytes | 7.03× |
| **Bold Sections** | 7 | 0 | 0.00× |
| **Lines** | 21 | 8 | 2.62× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 17.4% |

---

### 🟢 mixed/AGA4FFOUY3VW5J6OAKHFGWZ6TS4KYOF7.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 2,286 bytes | 3,007 bytes | 0.76× |
| **Bold Sections** | 181 | 206 | 0.88× |
| **Lines** | 235 | 39 | 6.03× |
| **BR Tags** | 0 | 156 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.8% |

---

### 🟢 mixed/ZZLARWOCNXAHCS25AGWDA2UPFRV3G6TU.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 2,908 bytes | 2,297 bytes | 1.27× |
| **Bold Sections** | 75 | 3 | 25.00× |
| **Lines** | 89 | 94 | 0.95× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 3.6% |

---

### 🟢 mixed/L3YHCAZRLQVYA7O4G6SG5BQHUREJTYQO.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 970 bytes | 1,404 bytes | 0.69× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 120 | 116 | 1.03× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 16.4% |

---

### 🟢 mixed/WYIDAT7X2DXYMKGRFAXDEAA2EJF23GRQ.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 7,830 bytes | 5,896 bytes | 1.33× |
| **Bold Sections** | 353 | 38 | 9.29× |
| **Lines** | 142 | 125 | 1.14× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 29.4% |

---

### 🟢 mixed/RLGNJP7L3BZWPR6KCTTN5I4DIPFSCP3L.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 195,886 bytes | 147,177 bytes | 1.33× |
| **Bold Sections** | 1 | 33 | 0.03× |
| **Lines** | 6,403 | 7,188 | 0.89× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.0% |

---

### 🟢 mixed/QIYEVQGJUXO4R45CCFYLL65JS6FERSNA.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 7,630 bytes | 12,054 bytes | 0.63× |
| **Bold Sections** | 99 | 87 | 1.14× |
| **Lines** | 117 | 144 | 0.81× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 66.2% |

---

### 🟢 mixed/YE54VY55FNS7H3IOPRHQYVOD2RJJW3DT.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 1,217 bytes | 863 bytes | 1.41× |
| **Bold Sections** | 37 | 11 | 3.36× |
| **Lines** | 61 | 34 | 1.79× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 45.5% |

---

### 🟢 mixed/22ZOCVPAF2GSGXR357RM7UT4Z22RS2LH.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 490 bytes | 342 bytes | 1.43× |
| **Bold Sections** | 20 | 18 | 1.11× |
| **Lines** | 38 | 38 | 1.00× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 12.1% |

---

### 🟢 mixed/EIR7WZL6LLXE7N7TX5ZY4QKXPPZEISPQ.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 3,119 bytes | 2,054 bytes | 1.52× |
| **Bold Sections** | 18 | 17 | 1.06× |
| **Lines** | 147 | 54 | 2.72× |
| **BR Tags** | 0 | 35 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.2% |

---

### 🟢 mixed/AI27TP7D5YR3E23YDKFKVE27DDUEN5TU.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 1,821 bytes | 1,111 bytes | 1.64× |
| **Bold Sections** | 137 | 3 | 45.67× |
| **Lines** | 37 | 34 | 1.09× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 5.0% |

---

### 🟢 mixed/7DHC66NNE4RHBN7MNVPKSCN6E2GFRS2Z.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 7,518 bytes | 3,719 bytes | 2.02× |
| **Bold Sections** | 81 | 2 | 40.50× |
| **Lines** | 68 | 66 | 1.03× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.6% |

---

### 🟢 mixed/BI5TFHTLJDOJCIYTD6D2PM5OBALKZ4QX.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 757 bytes | 368 bytes | 2.06× |
| **Bold Sections** | 70 | 7 | 10.00× |
| **Lines** | 18 | 19 | 0.95× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 6.2% |

---

### 🟢 mixed/AHJAUKMSCN4OI3FPBHSLQVQSDTKBIHI3.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 1,615 bytes | 770 bytes | 2.10× |
| **Bold Sections** | 30 | 1 | 30.00× |
| **Lines** | 28 | 23 | 1.22× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 1.6% |

---

### 🟢 mixed/5PFVA6CO2FP66IJYJJ4YMWOLK5EHRCCD.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 9,745 bytes | 4,537 bytes | 2.15× |
| **Bold Sections** | 182 | 3 | 60.67× |
| **Lines** | 83 | 85 | 0.98× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 1.2% |

---

### 🟢 mixed/QRWUEJ3NLZCZOXL2HTG2KMRCA6O42IG5.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 6,407 bytes | 2,839 bytes | 2.26× |
| **Bold Sections** | 159 | 3 | 53.00× |
| **Lines** | 77 | 64 | 1.20× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 0.8% |

---

### 🟢 mixed/T7NO5D5YLX4V5I7FBDQDAIXPBCLNAO7X.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 638 bytes | 275 bytes | 2.32× |
| **Bold Sections** | 11 | 1 | 11.00× |
| **Lines** | 21 | 17 | 1.24× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 3.4% |

---

### 🟢 mixed/WFMYY4FTQ2IYW3TPG7G5H6OJVMS2B2YD.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 14,081 bytes | 5,850 bytes | 2.41× |
| **Bold Sections** | 731 | 19 | 38.47× |
| **Lines** | 99 | 119 | 0.83× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.2% |

---

### 🟢 mixed/JPJ5MCDTMBPXA7YEZNO5KXTSWXWYNDW5.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 11,849 bytes | 4,919 bytes | 2.41× |
| **Bold Sections** | 533 | 10 | 53.30× |
| **Lines** | 81 | 110 | 0.74× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 0.2% |

---

### 🟢 mixed/JWCODRHRIROHXHNEQP5VHTLJBBM5SBWX.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 3,204 bytes | 1,297 bytes | 2.47× |
| **Bold Sections** | 162 | 4 | 40.50× |
| **Lines** | 48 | 42 | 1.14× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 1.6% |

---

### 🟢 mixed/OIBFL53UO6KGYL6PN27JMGWOJKWD62FK.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 1,579 bytes | 639 bytes | 2.47× |
| **Bold Sections** | 143 | 13 | 11.00× |
| **Lines** | 28 | 29 | 0.97× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 1.6% |

---

### 🟢 mixed/QPGEM6DY42HDRLY6OQFDPEFDUSW43ITT.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 3,606 bytes | 1,411 bytes | 2.56× |
| **Bold Sections** | 202 | 4 | 50.50× |
| **Lines** | 38 | 40 | 0.95× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.4% |

---

### 🟢 mixed/M3JC5LYIW5JUNGMUE4FIXGDYFEUABDJK.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 1,310 bytes | 505 bytes | 2.59× |
| **Bold Sections** | 58 | 1 | 58.00× |
| **Lines** | 20 | 15 | 1.33× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.0% |

---

### 🟢 mixed/THLKZHEPHTVPUJNWQ3L62RDZOIKMHE6X.md

**Quality:** `ACCEPTABLE` - Acceptable output quality

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 7,053 bytes | 2,443 bytes | 2.89× |
| **Bold Sections** | 543 | 7 | 77.57× |
| **Lines** | 59 | 61 | 0.97× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.2% |

---

### ✅ mixed/YE5PQJ6NUYA6UOWHADZIVVMCINU4AYZF.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 9,339 bytes | 9,335 bytes | 1.00× |
| **Bold Sections** | 52 | 46 | 1.13× |
| **Lines** | 258 | 329 | 0.78× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 19.2% |

---

### ✅ mixed/WZRQHWEXEG24SJPSEOEVB6FMPU6DA4VU.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 10,873 bytes | 10,888 bytes | 1.00× |
| **Bold Sections** | 33 | 22 | 1.50× |
| **Lines** | 190 | 294 | 0.65× |
| **BR Tags** | 0 | 5 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 77.1% |

---

### ✅ mixed/Z42OE7PSGVKK54B3J2LWZ4THMYJIJHGJ.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 9,215 bytes | 9,164 bytes | 1.01× |
| **Bold Sections** | 45 | 43 | 1.05× |
| **Lines** | 168 | 250 | 0.67× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 1.4% |

---

### ✅ mixed/P7ZED35W7LHI6YLKM5TVSLOQVACYSHHM.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 2,173 bytes | 2,156 bytes | 1.01× |
| **Bold Sections** | 4 | 3 | 1.33× |
| **Lines** | 96 | 151 | 0.64× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 79.3% |

---

### ✅ mixed/EMMM5FRYBCPVBLVU4RY6OFEKZFWM2KIJ.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 13,403 bytes | 13,569 bytes | 0.99× |
| **Bold Sections** | 20 | 25 | 0.80× |
| **Lines** | 181 | 254 | 0.71× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 75.0% |

---

### ✅ mixed/SEVNFYZBX7VQEWEG5SQQTFZK24PCUDFU.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 6,270 bytes | 6,187 bytes | 1.01× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 205 | 169 | 1.21× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 4.4% |

---

### ✅ mixed/WSP5DEW3S4BVQYFWKEFDC3HDLMRK3UT2.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 795 bytes | 777 bytes | 1.02× |
| **Bold Sections** | 4 | 9 | 0.44× |
| **Lines** | 17 | 35 | 0.49× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 72.2% |

---

### ✅ mixed/NM76DD2NN5OG5VHK5TQMZV3OO3T6UDAK.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 6,746 bytes | 6,584 bytes | 1.02× |
| **Bold Sections** | 30 | 29 | 1.03× |
| **Lines** | 168 | 248 | 0.68× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 61.0% |

---

### ✅ mixed/WXR2YY3TSXGUNVC2VECKTVIJO7PMECRS.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 6,602 bytes | 6,438 bytes | 1.02× |
| **Bold Sections** | 52 | 51 | 1.02× |
| **Lines** | 179 | 269 | 0.67× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 35.4% |

---

### ✅ mixed/CTMYRF75O3COU6UV5KWIFEF6TLJF4REJ.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 12,271 bytes | 11,949 bytes | 1.03× |
| **Bold Sections** | 20 | 5 | 4.00× |
| **Lines** | 188 | 321 | 0.59× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 61.0% |

---

### ✅ mixed/YS6AIKVZKRRKLU2JGEBFS3PO665RXHWI.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 18,283 bytes | 17,739 bytes | 1.03× |
| **Bold Sections** | 6 | 8 | 0.75× |
| **Lines** | 321 | 433 | 0.74× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 27.4% |

---

### ✅ mixed/YQZG4CHDFUMUUDUEO2IY3GSWB4YCIKJI.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 10,638 bytes | 10,973 bytes | 0.97× |
| **Bold Sections** | 82 | 51 | 1.61× |
| **Lines** | 291 | 251 | 1.16× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 66.2% |

---

### ✅ mixed/7N6KRBZIEFV4F5QLLW3GBF6LKNNWSWVB.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 18,213 bytes | 18,814 bytes | 0.97× |
| **Bold Sections** | 12 | 9 | 1.33× |
| **Lines** | 366 | 929 | 0.39× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.6% |

---

### ✅ mixed/RHW47KIVYBR2WPS44NNXESVQHKWOOXXD.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 1,725 bytes | 1,668 bytes | 1.03× |
| **Bold Sections** | 10 | 12 | 0.83× |
| **Lines** | 37 | 70 | 0.53× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 73.0% |

---

### ✅ technical/arxiv_2401.00001.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 27,174 bytes | 28,178 bytes | 0.96× |
| **Bold Sections** | 1 | 50 | 0.02× |
| **Lines** | 691 | 644 | 1.07× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 64.1% |

---

### ✅ mixed/H7U4KMXPQKUBDKIPQQRC6ETJZEZR3OCZ.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 16,269 bytes | 15,685 bytes | 1.04× |
| **Bold Sections** | 10 | 8 | 1.25× |
| **Lines** | 439 | 630 | 0.70× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 12.2% |

---

### ✅ mixed/TW5273JZ43VOQUCL7FRZ2N6STHYBBCQ4.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 2,563 bytes | 2,469 bytes | 1.04× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 76 | 59 | 1.29× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 3.2% |

---

### ✅ mixed/HNBALTFDCV5YCQB772EJLOZGFV3JQLXS.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 2,800 bytes | 2,694 bytes | 1.04× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 240 | 156 | 1.54× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 19.4% |

---

### ✅ mixed/NFLMOWBSAYHS4IFKAY5KSXU64BTAEZJ3.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 3,142 bytes | 3,010 bytes | 1.04× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 105 | 61 | 1.72× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.0% |

---

### ✅ mixed/AYZVGVPYWC6TNBDO76IU7PON3RZ22WQP.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 4,283 bytes | 4,098 bytes | 1.04× |
| **Bold Sections** | 20 | 19 | 1.05× |
| **Lines** | 144 | 131 | 1.10× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 53.8% |

---

### ✅ mixed/EHKVBSEBX33HSCZP2YGBOAAGM4WPMRL2.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 11,134 bytes | 10,633 bytes | 1.05× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 354 | 279 | 1.27× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 1.0% |

---

### ✅ mixed/F5H4P3SVLYMD7CM2HIICOSAGODB6N3JT.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 4,524 bytes | 4,303 bytes | 1.05× |
| **Bold Sections** | 20 | 19 | 1.05× |
| **Lines** | 247 | 181 | 1.36× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 25.2% |

---

### ✅ mixed/DTUUL6SJCKWTMKUHW4EBFNTNIZCMIM2H.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 37,733 bytes | 35,760 bytes | 1.05× |
| **Bold Sections** | 60 | 29 | 2.07× |
| **Lines** | 593 | 1,137 | 0.52× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 70.2% |

---

### ✅ mixed/UZ24VCW32BGC524CZI3QWY7LKJJXZ2ZZ.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 14,200 bytes | 15,099 bytes | 0.94× |
| **Bold Sections** | 47 | 68 | 0.69× |
| **Lines** | 498 | 1,307 | 0.38× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 63.7% |

---

### ✅ mixed/TTIW4RPBGSA7VUIZ6FAJFB3VIYGDENLI.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 1,071 bytes | 1,009 bytes | 1.06× |
| **Bold Sections** | 1 | 26 | 0.04× |
| **Lines** | 137 | 49 | 2.80× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.8% |

---

### ✅ mixed/CT6O4FXETQ2ABBLKKRWK5E344XQA73C3.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 1,228 bytes | 1,153 bytes | 1.06× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 44 | 35 | 1.26× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 2.0% |

---

### ✅ mixed/AJUCXMX47JIFDGYJLPX5YLA7W3N4IXSV.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 975 bytes | 915 bytes | 1.07× |
| **Bold Sections** | 10 | 7 | 1.43× |
| **Lines** | 38 | 50 | 0.76× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 63.3% |

---

### ✅ mixed/46KXLWATPXX7EE6CIIN3H4KUPVN3RX75.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 2,602 bytes | 2,410 bytes | 1.08× |
| **Bold Sections** | 7 | 3 | 2.33× |
| **Lines** | 115 | 104 | 1.11× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 41.6% |

---

### ✅ technical/arxiv_2401.00002.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 23,221 bytes | 21,349 bytes | 1.09× |
| **Bold Sections** | 1 | 6 | 0.17× |
| **Lines** | 453 | 549 | 0.83× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 72.2% |

---

### ✅ mixed/WT4PUCQSO7JLM6FV4HZDJ6DN4ZGWFL7U.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 881 bytes | 809 bytes | 1.09× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 30 | 22 | 1.36× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 3.4% |

---

### ✅ mixed/W5VHS6JXL2IZQKOADSVN6J2JWZPNWVC6.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 846 bytes | 763 bytes | 1.11× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 48 | 29 | 1.66× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 5.4% |

---

### ✅ mixed/HPXULDFI3DAZ3V2NZOHYUGUY5SLS4AHU.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 728 bytes | 650 bytes | 1.12× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 23 | 19 | 1.21× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 8.0% |

---

### ✅ mixed/GGYFXPMKQD267PXVZ3L2TK46IIHHSV7V.md

**Quality:** `GOOD` - Good match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 1,855 bytes | 1,652 bytes | 1.12× |
| **Bold Sections** | 20 | 42 | 0.48× |
| **Lines** | 46 | 53 | 0.87× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 78.8% |

---

### ⭐ mixed/SGU5XQOYWHC2ADXS74XA3FLWFRGL5RDW.md

**Quality:** `EXCELLENT` - Near-perfect match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 4,029 bytes | 3,998 bytes | 1.01× |
| **Bold Sections** | 4 | 5 | 0.80× |
| **Lines** | 111 | 130 | 0.85× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 82.8% |

---

### ⭐ mixed/XYUJKKMUXDLLC6JTCXEWHK5ZMNSTPHF6.md

**Quality:** `EXCELLENT` - Near-perfect match with reference

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 3,694 bytes | 3,613 bytes | 1.02× |
| **Bold Sections** | 13 | 31 | 0.42× |
| **Lines** | 113 | 139 | 0.81× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 83.0% |

---

### ❓ mixed/5JWNPTKTIAPTHTEGVKW7WVNBDBKQMRJO.md

**Quality:** `EMPTY_FILE` - Our output is empty

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 93 bytes | 0 bytes | 0.00× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 24 | 0 | 24.00× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 0.0% |

---

### ❓ mixed/D45G6SVN7QZSMYJOJGWLKE3MJ6DHTYY5.md

**Quality:** `EMPTY_FILE` - Our output is empty

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 98 bytes | 0 bytes | 0.00× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 28 | 0 | 28.00× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 0.0% |

---

### ❓ mixed/OW26QBLLEQRZH5PWHLAQGVI427SWTZUM.md

**Quality:** `EMPTY_FILE` - Our output is empty

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 79 bytes | 0 bytes | 0.00× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 10 | 0 | 10.00× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 0.0% |

---

### ❓ mixed/QJRUY4FRCDHXZJT5ZAWKMADAMAQUP5R6.md

**Quality:** `EMPTY_FILE` - Our output is empty

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 79 bytes | 0 bytes | 0.00× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 10 | 0 | 10.00× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 0.0% |

---

### ❓ mixed/WXURHXHVCOCL3XIN4PFUPT2OGYFIXYR5.md

**Quality:** `EMPTY_FILE` - Our output is empty

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 96 bytes | 0 bytes | 0.00× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 26 | 0 | 26.00× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 0.0% |

---

### ❓ mixed/ZC2ELDSYWFVOJZRXTLERXVM7UMXWCWZN.md

**Quality:** `EMPTY_FILE` - Our output is empty

| Metric | Our Library | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Size** | 77 bytes | 0 bytes | 0.00× |
| **Bold Sections** | 1 | 0 | 0.00× |
| **Lines** | 8 | 0 | 8.00× |
| **BR Tags** | 0 | 0 | - |
| **Form Fields** | 0 | 0 | - |
| **Similarity** | - | - | 0.0% |

---

