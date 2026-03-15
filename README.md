# legal-llm-claim-eval
## Overview
This repository contains a small experiment exploring whether a large language model (LLM) can correctly determine whether a reference excerpt discloses a patent claim limitation.

The goal is to explore failure modes in LLM-assisted legal analytis, particularly the gap between semantic similarity and legal disclosure.

## Dataset
The dataset consists of a small set of examples containing:
* a patent claim limitation
* a reference excerpt
* a ground truth table indicating whether the excerpt discloses the limitation

The dataset is intentionally small and designed to illustrated evaluation stucture rather than provide a comprehensive benchmarkk.

## Example Dataset Entries
| claim _ limitation | reference_excerpt | human_review |
| :--- | :--- | :--- |
| trasnmitting a signal | the device sends a wireless message to a remote receiver | discloses |
| encrypting data | the system compresses files before storage | does not disclose |
| storing credentials | user credentials are saved in memory for later authentication | discloses |
| generating a secure token | the server creates a random session identifier | partially discloses | 


## Method
The script prompts an LLM with:
* a claim limitation
* a reference excerpt

The model is  asked to classify whether the excerpt:
* discloses the limitation
* partially discloses the limitation
* does not disclose the limitation

Predictions are compared against the ground truth labels.

## Goal
The goal of this  experiment is to explore how LLMs perform on legal reasoning tasks where plausible language overlap does not necessarily correspond to legal disclosure.

## Notes
This repository contains a small prototype exploring how LLM outputs can be evaluated on legal reasoning tasks.
