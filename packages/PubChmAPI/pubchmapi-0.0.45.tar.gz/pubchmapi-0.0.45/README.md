# PubChmAPI Library

## Overview

### Introduction

The **PubChmAPI** Python package simplifies interaction with the PubChem database via the PUG-REST API. Unlike traditional wrappers with hard-coded functions, PubChmAPI uses dynamic metaprogramming to generate endpoints, ensuring full coverage of the PubChem schema. It handles URL generation, automatic batching, and throttling to provide a seamless data retrieval experience.



---

## Naming Convention

Functions in **PubChmAPI** follow a strict semantic naming convention to eliminate ambiguity:

`domain_identifier_get_operation_option`

* **Domain:** The primary database being queried (e.g., `compound`, `substance`, `assay`, `gene`).
* **Identifier:** The input type provided (e.g., `cid`, `name`, `smiles`, `geneid`).
* **Operation:** The specific data to retrieve (e.g., `properties`, `aids`, `synonyms`).
* **Option (Optional):** Filters or variants (e.g., `active`, `inactive`, `2d`).

---

## Functions

### Compound Property Functions (By Name)

Retrieve calculated properties using a compound name (e.g., "Aspirin").
**Format:** `compound_name_get_[Property](identifier)`

* **compound_name_get_Title**(*identifier*)
* **compound_name_get_MolecularFormula**(*identifier*)
* **compound_name_get_MolecularWeight**(*identifier*)
* **compound_name_get_CanonicalSMILES**(*identifier*)
* **compound_name_get_IsomericSMILES**(*identifier*)
* **compound_name_get_InChI**(*identifier*)
* **compound_name_get_InChIKey**(*identifier*)
* **compound_name_get_IUPACName**(*identifier*)
* **compound_name_get_XLogP**(*identifier*)
* **compound_name_get_ExactMass**(*identifier*)
* **compound_name_get_MonoisotopicMass**(*identifier*)
* **compound_name_get_TPSA**(*identifier*)
* **compound_name_get_Complexity**(*identifier*)
* **compound_name_get_Charge**(*identifier*)
* **compound_name_get_HBondDonorCount**(*identifier*)
* **compound_name_get_HBondAcceptorCount**(*identifier*)
* **compound_name_get_RotatableBondCount**(*identifier*)
* **compound_name_get_HeavyAtomCount**(*identifier*)
* **compound_name_get_IsotopeAtomCount**(*identifier*)
* **compound_name_get_AtomStereoCount**(*identifier*)
* **compound_name_get_DefinedAtomStereoCount**(*identifier*)
* **compound_name_get_UndefinedAtomStereoCount**(*identifier*)
* **compound_name_get_BondStereoCount**(*identifier*)
* **compound_name_get_DefinedBondStereoCount**(*identifier*)
* **compound_name_get_UndefinedBondStereoCount**(*identifier*)
* **compound_name_get_CovalentUnitCount**(*identifier*)
* **compound_name_get_Volume3D**(*identifier*)
* **compound_name_get_ConformerModelRMSD3D**(*identifier*)
* **compound_name_get_EffectiveRotorCount3D**(*identifier*)
* **compound_name_get_ConformerCount3D**(*identifier*)
* **compound_name_get_Fingerprint2D**(*identifier*)
* **compound_name_get_FeatureCount3D**(*identifier*)
* **compound_name_get_FeatureAcceptorCount3D**(*identifier*)
* **compound_name_get_FeatureDonorCount3D**(*identifier*)
* **compound_name_get_FeatureAnionCount3D**(*identifier*)
* **compound_name_get_FeatureCationCount3D**(*identifier*)
* **compound_name_get_FeatureRingCount3D**(*identifier*)
* **compound_name_get_FeatureHydrophobeCount3D**(*identifier*)
* **compound_name_get_XStericQuadrupole3D**(*identifier*)
* **compound_name_get_YStericQuadrupole3D**(*identifier*)
* **compound_name_get_ZStericQuadrupole3D**(*identifier*)

### Compound CID Functions

Retrieve data using a Compound Identifier (CID).
**Format:** `compound_cid_get_[Operation](identifier)`

#### General & Conversion
* **compound_cid_get_description**(*identifier*)
* **compound_cid_get_synonyms**(*identifier*)
* **compound_cid_get_sids**(*identifier*) *(Get Substance IDs)*
* **compound_cid_get_cids**(*identifier*) *(Self-retrieval/Verification)*
* **compound_cid_get_conformers**(*identifier*)

#### Images
* **compound_cid_get_png**(*identifier*) *(Default)*
* **compound_cid_get_png_2d**(*identifier*)
* **compound_cid_get_png_3d**(*identifier*)

#### Assays (Biological Activity)
* **compound_cid_get_aids**(*identifier*) *(All associated Assays)*
* **compound_cid_get_aids_active**(*identifier*) *(Only Active Assays)*
* **compound_cid_get_aids_inactive**(*identifier*) *(Only Inactive Assays)*
* **compound_cid_get_assaysummary**(*identifier*)

#### Structural & Isotopic Variants
* **compound_cid_get_cids_same_isotopes**(*identifier*)
* **compound_cid_get_cids_same_connectivity**(*identifier*)
* **compound_cid_get_cids_same_tautomer**(*identifier*)
* **compound_cid_get_cids_same_stereo**(*identifier*)
* **compound_cid_get_cids_parent**(*identifier*)
* **compound_cid_get_cids_original**(*identifier*)
* **compound_cid_get_cids_component**(*identifier*)
* **compound_cid_get_cids_preferred**(*identifier*)

#### Properties (Batch)
* **compound_cid_get_all_properties**(*identifier*) *(Retrieves all properties as CSV)*
* **compound_cid_get_properties**(*identifier, properties=[...]*) *(Retrieve specific list)*

> *Note: All single property functions listed under "Compound Name" are also available for CIDs (e.g., `compound_cid_get_MolecularWeight`).*

### Structural Search Functions

Retrieve CIDs based on structural similarity or substructures.
**Format:** `compound_[Method]_[InputType]_get_cids(identifier)`

* **compound_fastsimilarity_2d_cid_get_cids**(*cid*)
* **compound_fastsubstructure_smiles_get_cids**(*smiles*)
* **compound_fastidentity_smiles_get_cids**(*smiles*)
* **compound_similarity_3d_cid_get_cids**(*cid*)

### Biological Domain Functions

Retrieve data related to proteins, genes, taxonomy, and cell lines.

#### Protein Functions
**Format:** `protein_[Identifier]_get_[Operation]`
* **protein_accession_get_summary**(*accession*)
* **protein_accession_get_aids**(*accession*)
* **protein_gi_get_summary**(*gi*)
* **protein_synonym_get_aids**(*synonym*)

#### Gene Functions
**Format:** `gene_[Identifier]_get_[Operation]`
* **gene_geneid_get_summary**(*geneid*)
* **gene_geneid_get_aids**(*geneid*)
* **gene_genesymbol_get_summary**(*symbol*)
* **gene_genesymbol_get_aids**(*symbol*)

#### Taxonomy Functions
**Format:** `taxonomy_[Identifier]_get_[Operation]`
* **taxonomy_taxid_get_summary**(*taxid*)
* **taxonomy_taxid_get_aids**(*taxid*)
* **taxonomy_synonym_get_aids**(*synonym*)

#### Cell Line Functions
**Format:** `cell_[Identifier]_get_[Operation]`
* **cell_cellacc_get_summary**(*cellacc*)
* **cell_cellacc_get_aids**(*cellacc*)
* **cell_synonym_get_summary**(*synonym*)