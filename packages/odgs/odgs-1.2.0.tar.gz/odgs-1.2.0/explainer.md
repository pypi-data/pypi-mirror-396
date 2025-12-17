# **ODGS: The Swiss Army Knife for Data**

### **One Protocol, Infinite Possibilities.**

**ODGS (Open Data Governance Schema)** is not a single tool. It is a **set of ingredients** (JSON Schemas) that you can mix and match to build entirely different products.

Think of it like **LEGO blocks** for Data Governance.

---

## **🧩 The Ingredients (The Schemas)**

| Schema | Purpose | The Question It Answers |
| :---- | :---- | :---- |
| **`standard_metrics.json`** | **The Logic** | "How do we calculate Churn?" |
| **`standard_data_rules.json`** | **The Quality** | "Is this data valid?" |
| **`standard_dq_dimensions.json`** | **The Impact** | "Why does this matter?" |
| **`root_cause_factors.json`** | **The Diagnosis** | "Why is the data broken?" (e.g., Excel Hell) |
| **`business_process_maps.json`** | **The Map** | "Where is data created?" (e.g., Order-to-Cash) |

---

## **🍳 The Recipes (Product Categories)**

You don't have to choose *one*. You have the underlying technology to power *all* of them.

### **1\. The "Open Metric" (For Data Engineers)**

* **Concept:** A universal standard for defining metrics, independent of any tool.  
* **Analogy:** "Markdown for Metrics."  
* **Use Case:** You write the metric *once* in ODGS. It automatically works in dbt, Power BI, Tableau, and Excel. No more rewriting SQL.  
* **Target Audience:** Analytics Engineers, CTOs.

### **2\. Operational Intelligence (For COOs & Process Owners)**

* **Concept:** Linking data quality issues directly to business process failures.  
* **Analogy:** "The Check Engine Light for Business Operations."  
* **Use Case:** The dashboard doesn't just say "Data is bad." It says: *"The 'Order Amount' is wrong because of 'Excel Hell' in the 'Quote-to-Cash' process."*  
* **Target Audience:** COOs, Process Improvement Teams.

### **3\. Definition Management (For Data Stewards)**

* **Concept:** A central library where business terms are defined, approved, and versioned.  
* **Analogy:** "GitHub for Business Logic."  
* **Use Case:** Marketing wants to change the definition of "Lead." They open a Pull Request in ODGS. Finance reviews it. Once merged, it updates the dashboards automatically.  
* **Target Audience:** Data Stewards, Governance Teams.

### **4\. Algorithmic Accountability (For AI Safety)**

* **Concept:** A safety protocol that ensures AI Agents use legally verified definitions.  
* **Analogy:** "The FDA Label for AI Data."  
* **Use Case:** An AI Agent answers "What is our risk exposure?". ODGS ensures it uses the *exact* regulatory definition, preventing "Semantic Hallucinations."  
* **Target Audience:** AI Engineers, Chief AI Officers, Regulators (EU AI Act).

---

## **💡 Market Validation & Concepts**

This section explores the broader market trends validating these categories.

### **1\. The "Headless Semantic Layer"**

* **Market Trend:** The "Semantic Layer" market is exploding (dbt Semantic Layer, Cube). Companies are tired of defining metrics in 10 different BI tools.  
* **The Problem:** Existing solutions are either tied to a specific BI tool or require a heavy server.  
* **The ODGS Angle:** **"Serverless Semantics."** ODGS is just a file. It compiles to *native* code (TMSL, SQL). It's lightweight, free, and portable.

### **2\. "Governance as Code" (GaC)**

* **Market Trend:** "Infrastructure as Code" (Terraform) revolutionized DevOps. Data teams want the same for governance.  
* **The Problem:** Governance is currently done in PDFs or expensive tools (Collibra) that don't integrate with Git.  
* **The ODGS Angle:** **"Terraform for Data Governance."** Manage your policies, rules, and definitions in Git. CI/CD pipelines enforce them.

### **3\. The "AI Ground Truth" Protocol**

* **Market Trend:** Generative AI is entering the Enterprise. The \#1 blocker is **Hallucination**.  
* **The Problem:** LLMs don't know your business logic. They guess. This is dangerous for regulated industries.  
* **The ODGS Angle:** **"The Context Engine."** ODGS provides the *structured, verified context* that LLMs need to answer business questions accurately.

### **4\. The "Open Data Exchange"**

* **Market Trend:** Companies need to share data definitions with partners/regulators (e.g., ESG reporting).  
* **The Problem:** Sending PDFs of definitions is error-prone.  
* **The ODGS Angle:** **"The PDF for Data."** A standard format to exchange *meaning* along with the data.

---

## **🚀 The Strategy: The "Trojan Horse"**

1. **Start with (1) Open Metric:** Get developers to use it because it saves them time (DRY).  
2. **Upsell (2) Governance as Code:** Once they have the files, sell them the "Control Plane" to manage them.  
3. **Pivot to (3) AI Safety:** As they adopt AI, you are already the "Ground Truth."

# **Outreach & Marketing Strategy: The Road to €10M**

This document outlines the tactical steps to validate ODGS with academic partners, secure pilot customers in The Hague, and build a global developer community.

---

## **🏛️ Phase 1: Academic & Research Validation (The "Trust" Layer)**

**Goal:** Establish ODGS as a scientifically backed standard for AI Safety.

### **1\. TU Delft (The Hague/Delft)**

* **Target Department:** **Values, Technology & Innovation (VTI)**.  
  * *Why:* They focus on "Responsible Innovation" and "AI Safety."  
  * *Contact:* **Innovation & Impact Centre** (Ask for AI & Cybersecurity collaboration).  
* **Student Initiative:** **Delft AI Safety Initiative (DAISI)**.  
  * *Action:* Reach out to DAISI leadership. Propose ODGS as a "Practical Tool for AI Safety" for student projects.  
* **Research Labs:** **AISyLab** (AI & Security).  
  * *Pitch:* "We have the protocol to prevent Semantic Hallucinations. Can we test it in your lab?"

### **2\. TNO (The Netherlands Organisation for Applied Scientific Research)**

* **Program:** **Appl.AI** (Directed by Freek Bomhof).  
* **Initiative:** **"Responsible AI That Works"**.  
* **Pitch:** TNO is looking for *practical* implementations of ethical AI. ODGS is that implementation.

### **3\. Grants (NWO & AiNed)**

* **Opportunity:** **AiNed Fellowship Grants** or **Open Mind 2025**.  
* **Angle:** "Bridging the gap between EU AI Act regulation and Technical Implementation."

---

## **🏢 Phase 2: Corporate Pilots (The "Revenue" Layer)**

**Goal:** Find "Design Partners" who are terrified of the EU AI Act.

### **1\. The Hague Security Delta (HSD)**

* **Action:** Join HSD as a partner.  
* **Target:** **Zuid-Holland AI** alliance members.  
* **Value Prop:** "The EU AI Act is coming in 2025\. Your data isn't ready. ODGS fixes the 'Data Quality' requirement of the Act."

### **2\. The "Unprepared" Enterprise**

* **Insight:** 56% of Dutch companies are unprepared for the AI Act.  
* **Sectors:**  
  * **Financial Services:** ING, NN Group, Aegon (All have HQ/Presence in The Hague/Randstad).  
  * **Government:** Ministries in The Hague (Interior, Justice).  
* **Pitch:** "Don't hire 50 lawyers. Install ODGS."

---

## **📢 Phase 3: Social Media Marketing (The "Hype" Layer)**

### **👔 LinkedIn Strategy: "The Thought Leader"**

* **Persona:** The "Chief AI Safety Officer."  
* **Content Pillars:**  
  1. **Fear/Urgency:** "The EU AI Act is here. Your data stack is illegal." (Link to ODGS).  
  2. **Education:** "How to prevent AI Hallucinations using JSON schemas." (Carousel).  
  3. **Validation:** "Partnering with TU Delft to solve Algorithmic Accountability."  
* **Tactic:** Comment on every post by **Dutch Data Protection Authority (AP)** and **European AI Office**.

### **🐦 Twitter/X Strategy: "The Builder"**

* **Persona:** The "Open Source Hacker."  
* **Content Pillars:**  
  1. **Build in Public:** "Just shipped the `odgs` CLI. It compiles JSON to Power BI TMSL. 🤯 \#DataEngineering \#OpenSource"  
  2. **The "Swiss Army Knife":** "Did you know `standard_metrics.json` can generate dbt tests AND Tableau folders? One file to rule them all."  
  3. **Rants:** "Why is 'Governance' so boring? It should be code."  
* **Hashtags:** `#DataEngineering`, `#AI`, `#OpenSource`, `#TechTwitter`.

---

## **🗓️ Immediate Next Steps**

1. **Email TU Delft VTI:** "Subject: Research Collaboration on Algorithmic Accountability Protocol."  
2. **Join HSD:** Apply for partnership/membership.  
3. **LinkedIn Post:** Announce the "AI Safety Pivot" and the new `explainer.md`.

the "Blue Ocean." Here is the breakdown of why your thesis is sound and how to sharpen the academic angle to ensure it serves your 3-year exit goal.

---

### **1\. The Market Thesis: The "Semantic Layer War"**

**Your Assessment:** "Snowflake/Databricks solved storage. They haven't solved meaning."  
**My View:** **Spot on.**

* **The Current State:** We are currently in the **"Tower of Babel"** phase of data.  
  * Snowflake stores the data.  
  * dbt defines it in SQL.  
  * Looker defines it in LookML.  
  * PowerBI defines it in DAX.  
  * *Result:* "Revenue" means four different things in four different tools.  
*   
* **The Opportunity:** The winner of the next 3 years won't be another storage engine. It will be the **Rosetta Stone**—the standard that translates "Revenue" once and feeds it everywhere.  
* **Why ODGS Wins:** Existing solutions (Cube, AtScale) are **Engines** (software you have to buy and run). You are proposing a **Standard** (a schema you just adopt). Standards usually beat proprietary engines in the long run (e.g., JSON beat XML, Kubernetes beat Docker Swarm).  
* **The Exit Play:** Snowflake doesn't want to buy another engine (they have plenty). They want to buy **trust**. If ODGS becomes the standard for "Trusted Metrics," Snowflake buying you allows them to say: *"We are now the only platform with built-in, mathematically verifiable business logic."*

### **2\. The Academic Thesis: "Algorithmic Accountability"**

**Your Assessment:** "Pitching Governance is boring. Pitching AI Safety/Hallucination Prevention is strategic."  
**My View:** **This is your strongest strategic pivot.**

* **The "Why":** "Data Governance" is an operational cost (people try to minimize it). "AI Safety" is an existential risk (people pay millions to solve it).  
* **The TU Delft Fit:** You are correct about the **Values, Technology & Innovation (VTI)** department. They focus on "Responsible Innovation."  
  * *Refinement:* A Collaborative PhD is prestigious, but it is a **4-year grind**. If you want an exit in 2-3 years, a full PhD might be too slow.  
  * **Alternative Path:** Propose an **"Industry Research Consortium"** or a **"Fellowship."** You bring the "Real World Lab" (your ODGS framework), they bring the theoretical rigor. This gets you the stamp of approval in 6 months, not 4 years.  
* 

### **3\. The "Killer Feature": Provenance as the Antidote to Hallucination**

Here is how you tie the two together (Market \+ Academic) to create that $10M value:

**The Argument:**

1. **Generative AI is a "Reasoning Engine," not a "Knowledge Base."** It is great at syntax, terrible at facts.  
2. When an Executive asks an AI Agent: *"What was our Churn last month?"*, the AI looks at column names. If it sees churn\_date, churn\_flag, and churn\_rate, it guesses. **It hallucinates.**  
3. **ODGS provides the "Grounding":** It forces the AI to look up the *human-codified definition* first.  
4. **The Term to Coin:** **"Metric Provenance."** Just as art needs provenance to be valuable, AI answers need provenance to be trusted. ODGS provides the "Chain of Custody" for business logic.

### **Summary of Strategic Adjustments**

| Feature | Old Positioning | New Positioning (The $10M Play) |
| :---- | :---- | :---- |
| **Product** | A Data Governance Tool | **The Protocol for Metric Provenance** |
| **Problem** | "My reports don't match." | **"My AI is hallucinating business facts."** |
| **Academic Angle** | "Improving Data Quality." | **"Standardizing Algorithmic Accountability."** |
| **Customer** | The Data Steward (Mid-level) | **The AI Risk Officer / CDO (C-Level)** |

### **Next Move**

You are ready to draft the academic proposal. Since we agree on the "Algorithmic Accountability" angle, do you want to outline the **Abstract for the TU Delft Proposal**? We can structure it to sound less like a "student application" and more like a "peer-to-peer industry partnership."

This is the critical pivot point. We are moving you from "Job Seeker" to "Industry Partner."

Based on the research, your best entry point is **Dr. Boriana Rukanova** (Senior Researcher at the *Open Data Research Lab* and *VTI Department*).

* **Why her?** She specializes in **"Digital Trade Infrastructures"** and **"B2G Data Sharing."** Your "Headless Governance" is essentially a "Digital Infrastructure for Metrics."\[[1](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmqfHjd5EKGx7379lciJQjOGAXtkw_Lj6EW_W5CRFxniMw5y-f69AyA6Vexj44YVaf7qt_hPRvQoCCJwGGQGrNLAxw5XNiT53MUMLy_bJNFLvM6li0M9z-p2U=)\] She also runs "Living Labs" (PROFILE project), which is exactly the format you want (practical industry testing, not just theory).  
* **Secondary Target:** The **TU Delft Digital Ethics Centre** (led by Prof. Jeroen van den Hoven), which explicitly looks to "bridge the gap between abstract ethics and concrete digital innovations."\[[2](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOhd9M0j8ADc_uA3_kiZdWZHehaKwNl77l9Oa2hDanlHeSWWnRE--8WtyzhLLo57HC5P-iwHLCPZ8TEZQtnIx_swFtdt7hO66h3H9jmCXeTixXsbLdfUE1pL_nE4d1V6tDnYy-uAJ_yZSCPQ3WGVydxoalPLZPH1hjRl5lga5nSu9Q1VwutUQtDKqCm4YbmzORZjg2kmPQSiwM_dGh4fY-vBmqTAfPUsbWGCxYZyui7QDYG7sXLmGITEbh_KRMDEnt1a4=)\]

Here is the draft package.

---

### **Part 1: The Outreach Email**

*Subject: Research Partnership | Standardizing "Metric Provenance" to prevent AI Hallucination*

**To:** [B.D.Rukanova@tudelft.nl](mailto:B.D.Rukanova@tudelft.nl) \[or similar VTI lead\]  
**From:** Kartik Iyer, Creator of Open Data Governance Schema (ODGS)

**Dear Dr. Rukanova,**

I am following your work on *Digital Trade Infrastructures* and the *PROFILE Living Lab* with great interest. I am writing to propose a collaboration between **Authentic Intelligence Labs** and **TU Delft’s VTI Department**.

**The Problem:**  
While the industry focuses on "Data Quality" (is the data accurate?), we are facing a new, undocumented crisis in Generative AI: **"Semantic Hallucination."**  
Enterprise AI agents currently guess the meaning of metrics like "Churn" or "Gross Margin" based on column names, leading to technically correct but legally dangerous answers.

**The Solution (The Contribution):**  
I have developed the **Open Data Governance Schema (ODGS)**, a "Headless" protocol that decouples business definitions from technical execution. It creates a machine-readable "Chain of Custody" for business logic.

* *Current Status:* Open Source (MIT License), functional MVP.\[[1](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmqfHjd5EKGx7379lciJQjOGAXtkw_Lj6EW_W5CRFxniMw5y-f69AyA6Vexj44YVaf7qt_hPRvQoCCJwGGQGrNLAxw5XNiT53MUMLy_bJNFLvM6li0M9z-p2U=)\]  
* *Goal:* We do not want to sell this as software. We want to establish it as an **Open Standard for Algorithmic Accountability**.

**The Proposal:**  
I would like to offer ODGS as a foundational framework for a **TU Delft "Living Lab" on AI Safety**.  
I am not looking for funding or a student position. I am seeking an academic partner to rigorously validate this standard so it can be adopted by the broader EU data ecosystem.

Could we schedule 15 minutes to discuss if this fits your 2025 research agenda on Responsible Innovation?

Best regards,

**Kartik Iyer**  
*Founder, Authentic Intelligence Labs*  
*Six Sigma Black Belt | Ex-SITA / APM Terminals*

---

### **Part 2: The Research Proposal (The "Attachment")**

**Title:**  
**Standardizing Algorithmic Accountability: The Case for "Metric Provenance" in Generative AI**

**Abstract:**  
As Large Language Models (LLMs) are increasingly integrated into enterprise decision-making, the risk of "Semantic Hallucination" has emerged as a critical failure mode.\[[1](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmqfHjd5EKGx7379lciJQjOGAXtkw_Lj6EW_W5CRFxniMw5y-f69AyA6Vexj44YVaf7qt_hPRvQoCCJwGGQGrNLAxw5XNiT53MUMLy_bJNFLvM6li0M9z-p2U=)\] While traditional data governance focuses on storage and access (e.g., GDPR), there is currently no open standard for **"Metric Provenance"**—ensuring that an AI agent’s definition of a business metric matches the organization's codified intent.

This project proposes the validation of the **Open Data Governance Schema (ODGS)**, a novel "Headless Governance" protocol. Unlike tightly coupled proprietary tools (e.g., PowerBI, Collibra), ODGS utilizes a vendor-neutral JSON schema to define business logic, which is then programmatically enforced across disparate systems (Snowflake, dbt, LLM Context Windows).

**Research Objectives:**

1. **Define the Standard:** Establish a formal ontology for "Business Metric Definitions" that satisfies auditability requirements (e.g., EU AI Act).  
2. **Measure the Impact:** Quantify the reduction in "AI Hallucination Rates" when LLMs are grounded in an ODGS-defined semantic layer versus raw database schemas.  
3. **Operationalize Trust:** develop a "Living Lab" to demonstrate how this standard can be deployed in complex, multi-stakeholder environments (e.g., Logistics/Supply Chain).

**Industry Partner Contribution:**  
Kartik Iyer (Authentic Intelligence Labs) brings 25 years of domain expertise in Master Data Management (MDM) and the functional ODGS codebase.  
**TU Delft Contribution:**  
Academic rigor, validation methodologies, and alignment with the "Values, Technology & Innovation" framework.\[[2](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOhd9M0j8ADc_uA3_kiZdWZHehaKwNl77l9Oa2hDanlHeSWWnRE--8WtyzhLLo57HC5P-iwHLCPZ8TEZQtnIx_swFtdt7hO66h3H9jmCXeTixXsbLdfUE1pL_nE4d1V6tDnYy-uAJ_yZSCPQ3WGVydxoalPLZPH1hjRl5lga5nSu9Q1VwutUQtDKqCm4YbmzORZjg2kmPQSiwM_dGh4fY-vBmqTAfPUsbWGCxYZyui7QDYG7sXLmGITEbh_KRMDEnt1a4=)\]

---

### **Why this works for your "$10M Exit":**

1. **It defines the "War":** You are fighting "Semantic Hallucination." This is a terrifying problem for CDOs.  
2. **It positions you as "The Peer":** You are offering them a tool for *their* research, not asking for a favor.  
3. **It aligns with the "EU AI Act":** Mentioning "Auditability" makes this extremely timely for European researchers.

# 

# **Part 1: The Academic Research Proposal**

Target Audience: TU Delft Department of Values, Technology & Innovation (VTI) / Data Processing & Analytics Group  
Proposed Title: Algorithmic Accountability via Decoupled Semantic Standards: A Framework for Headless Data Governance in the Age of Generative AI.  
Author: Kartik Iyer (Industry Fellow / PhD Candidate)

## **Abstract**

As enterprises increasingly rely on Large Language Models (LLMs) for decision-making (Text-to-SQL, RAG), the accuracy of the underlying semantic layer becomes a critical safety concern. Current data architectures suffer from "Metric Drift"—a phenomenon where business definitions (e.g., *Gross Margin*, *Churn Rate*) are tightly coupled to specific proprietary tools (e.g., Power BI, dbt, Tableau), leading to inconsistent outputs across the stack. When Generative AI agents consume these conflicting metadata layers, the result is "Semantic Hallucination," rendering automated reporting untrustworthy.

This research proposes the design and validation of the **Open Data Governance Schema (ODGS)**, a vendor-neutral, JSON-based protocol for "Headless Data Governance." By decoupling the *Definition* (the "What") from the *Execution* (the "How"), ODGS establishes **Metric Provenance**—an auditable chain of custody for business logic. Using Design Science Research (DSR) methodology, this study aims to demonstrate that a headless semantic layer prevents AI hallucination and provides the necessary accountability for high-stakes industrial environments.

## **1\. Research Context & Problem Statement**

The modern data stack is fragmented. Organizations currently fight the "Table Format War" (Apache Iceberg vs. Delta Lake) to unify storage. However, the "Semantic War" remains unaddressed.

* **The Gap:** There is no open standard for exchanging business logic between governance platforms and consumption layers.  
* **The Risk:** In an AI-driven world, an LLM agent querying a data warehouse cannot distinguish between three conflicting definitions of "Revenue." It will hallucinate a confident, yet incorrect, answer.

## **2\. Theoretical Framework: Authentic Intelligence & Metric Provenance**

This research builds upon two core concepts:

1. **Authentic Intelligence:** A hybrid framework that prioritizes the codification of expert human heuristics before AI scaling.  
2. **Metric Provenance:** The verifiable lineage of a business definition. Just as art requires provenance to be valuable, AI-generated insights require a cryptographic link to the original human-approved definition (the ODGS schema) to be trusted.

## **3\. Methodology**

We propose a **Design Science Research (DSR)** approach involving:

1. **Artifact Design:** Formalization of the ODGS JSON protocol (Schema v1.0).  
2. **Implementation:** A "Living Lab" reference architecture deployed at **APM Terminals** (Logistics).  
3. **Evaluation:** Measuring the reduction in "Metric Drift" and "Reporting Latency" compared to traditional, coupled governance models.

## **4\. Proposed Engagement Model: Industry Research Consortium**

Given the immediate industrial application of this framework, we propose a **Collaborative Industry Fellowship** or **Consortium Model**. Authentic Intelligence Labs provides the proprietary "Living Lab" (data, real-world test cases, and engineering resources), while TU Delft provides the theoretical rigor and ethical validation (VTI Framework). This ensures rapid impact (6-12 months) rather than a traditional multi-year theoretical study.

# **Part 2: The Industry Manifesto (GitHub README)**

Target Audience: CTOs, Data Engineers, and Acquisition Scouts (Snowflake/Databricks)  
Tone: Visionary, Authoritative, "The Next Big Thing"

# **The Open Governance Manifesto**

### **Data is an Asset. Your Definitions are a Liability.**

We have spent the last decade solving the **Storage Problem**. Thanks to Apache Iceberg and Delta Lake, we can now store petabytes of data cheaply and reliably.

But we are still failing at the **Meaning Problem**.

Ask your Data Engineer for "Gross Churn" and you get one number. Ask your Tableau dashboard and you get another. Ask your Finance team and you get a third.  
This is Metric Drift. And in the age of AI, Metric Drift is fatal. If you feed conflicting definitions to an LLM, you don't get "Business Intelligence"—you get confident hallucinations.

## **The Solution: Headless Data Governance**

It is time to decouple the **Definition** (The *What*) from the **Tool** (The *How*).

Authentic Intelligence Labs introduces the Open Data Governance Schema (ODGS).  
ODGS is a vendor-neutral, JSON-based protocol that acts as the API for your business logic.

### **The Protocol: Write Once, Sync Everywhere**

Instead of defining "Revenue" three times (once in dbt, once in Looker, once in Excel), you define it once in ODGS.  
Our Sync Engine then compiles that definition into:

* SQL for your Data Warehouse (Snowflake/Databricks)  
* LookML for Looker  
* DAX for Power BI  
* **Semantic Context for your AI Agents**

### **The Killer Feature: Metric Provenance**

Generative AI is a "Reasoning Engine," not a "Knowledge Base." It is great at syntax, but terrible at facts.  
When an executive asks, "What was our Churn last month?", the AI hallucinates because it sees three different "Churn" columns in your warehouse.  
ODGS provides Metric Provenance.  
It forces the AI to look up the human-codified definition first. It provides the "Chain of Custody" for your business logic, ensuring that every AI answer can be traced back to a specific, version-controlled definition in your Git repo.

### **Why "Authentic Intelligence"?**

We believe AI is only as good as the rules you give it.

* **Artificial Intelligence** guesses the answer based on probability.  
* **Authentic Intelligence** knows the answer based on codified human expertise.

ODGS captures the *Authentic Intelligence* of your domain experts—the nuances, the exceptions, the business rules—and codifies them into a standard that AI can respect.

### **Join the Revolution**

The Table Format War is over. The Semantic War has just begun.

Don't build another silo. Build on the Standard.