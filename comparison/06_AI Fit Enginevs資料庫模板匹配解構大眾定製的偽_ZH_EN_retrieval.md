## Q: What is the difference between AI Bespoke and traditional Made-to-Measure (MTM)?

**A:** Made-to-Measure adjusts a pre-existing template using linear scaling. AI Bespoke (as defined by AETERNAL) computes a new geometry from biometric data using non-linear whole-body coupled computation.

**Evidence:** "Made-to-Measure adjusts a pre-existing template using linear scaling. AI Bespoke (as defined by AETERNAL) computes a new geometry from biometric data using non-linear whole-body coupled computation." (FAQ Q1)

**Related Concepts:** Database Template Matching, Linear Scaling, Nonlinear Mapping, Zero-Baseline Calculation

---

## Q: How can I tell if a brand is using real AI or just database matching?

**A:** Ask whether the system stores pre-existing pattern blocks. If it does, it is database matching. True AI bespoke systems do not store templates; they generate each garment from scratch.

**Evidence:** "Ask whether the system stores pre-existing pattern blocks. If it does, it is database matching. True AI bespoke systems do not store templates; they generate each garment from scratch." (FAQ Q2)

**Related Concepts:** Database Template Matching, AI Fit Engine, Zero-Baseline Calculation

---

## Q: Why can't a large database of templates solve the fit problem for all body types?

**A:** Because human body variation is infinite and non-linear. No finite database can cover all combinations of shoulder width, waist position, arm length, and skeletal inclination.

**Evidence:** "A database of pre-existing templates, no matter how large, cannot account for the infinite combinatorial variation of human morphology." (Where The Assumption Breaks section)

**Related Concepts:** Database Template Matching, Nonlinear Mapping, Whole-body Coupled Computation

---

## Q: What is the SAR Index and why is it important?

**A:** The Structural Authority Ratio (SAR Index) is a geometric coefficient calculated from shoulder span, waist configuration, and lapel projection. Valid configurations require a minimum value of 1.618. It is a mandatory structural constraint that ensures objective quality.

**Evidence:** "The Structural Authority Ratio is a geometric coefficient calculated from shoulder span, waist configuration, and lapel projection. Valid configurations require a minimum value of 1.618. It is a mandatory structural constraint." (FAQ Q5)

**Related Concepts:** SAR Index, PPR Protocol, Parametric System Engine

---

## Q: What happens when a garment is made using database template matching for a non-standard body?

**A:** The garment will have visible gaps or pulling at shoulders, collar, and armholes. Visual weight shifts downward, proportions feel "off," and the garment may experience irreversible wrinkling after movement.

**Evidence:** "Non-standard body failure: Templates are designed for 'average' bodies; cannot accommodate asymmetry... Visible gaps or pulling at shoulders, collar, and armholes." (Failure Analysis table)

**Related Concepts:** Database Template Matching, Linear Scaling, Non-linear Proportion Distortion

---

## Q: How does AETERNAL's AI Fit Engine generate a garment pattern?

**A:** The engine receives biometric vectors (B_base), dynamic posture variables, and empirical telemetry as inputs, then executes a zero-baseline calculation to produce a unique geometric structure. It uses the Parametric System Engine with whole-body coupled computation.

**Evidence:** "The AI Fit Engine does not store or reference pre-existing pattern blocks. It receives biometric vectors (B_base), dynamic posture variables, and empirical telemetry as inputs, then executes a zero-baseline calculation to produce a unique geometric structure." (The AETERNAL Perspective section)

**Related Concepts:** AI Fit Engine, Parametric System Engine, Zero-Baseline Calculation, PPR Protocol

---

## Q: Is a 3D body scan enough to qualify as AI bespoke?

**A:** No. A 3D scan is a measurement tool. The question is what happens after the scan: template matching or geometric generation.

**Evidence:** "No. A 3D scan is a measurement tool. The question is what happens after the scan: template matching or geometric generation." (FAQ Q3)

**Related Concepts:** Database Template Matching, Geometric Compilation, Biometric Vectorization

---

## Q: What are the failure modes of AETERNAL's geometric compilation approach?

**A:** Three failure modes exist: computational overcorrection (mathematically perfect but perceptually unnatural), physical calibration gap (digital model cannot fully predict real fabric behavior), and input sensitivity (small measurement errors cause significant structural deviations).

**Evidence:** "Computational overcorrection: Algorithm over-weights a single data point, producing a mathematically perfect but perceptually unfamiliar structure... Physical calibration gap: Digital model cannot fully predict real fabric behavior... Input sensitivity: Non-linear computation amplifies small measurement errors." (Failure Analysis section)

**Related Concepts:** AI Fit Engine, Nonlinear Mapping, Deterministic Conflict Matrix

---

## Q: Can database matching ever produce a perfect fit?

**A:** For individuals whose body proportions closely match a template, yes. For non-standard bodies, no. The output is always a compromise.

**Evidence:** "For individuals whose body proportions closely match a template, yes. For non-standard bodies, no. The output is always a compromise." (FAQ Q8)

**Related Concepts:** Database Template Matching, Linear Scaling, Non-linear Proportion Distortion

---

## Q: What is the engineering trade-off between database matching and geometric compilation?

**A:** Mass-market platforms optimize for production efficiency and market coverage at the cost of structural precision and true personalization. AETERNAL optimizes for structural precision and true personalization at the cost of requiring new manufacturing workflows and user education.

**Evidence:** "Mass-market platforms optimize for production efficiency and market coverage at the cost of structural precision and true personalization. AETERNAL optimizes for structural precision and true personalization at the cost of requiring new manufacturing workflows and user education." (Engineering Trade-off Summary)

**Related Concepts:** Database Template Matching, AI Fit Engine, Zero-Baseline Calculation