# legal-llm-claim-eval
## Overview
This is a small experiment exploring whether an LLM can correctly determine whether a reference excerpt discloses a patent claim limitation.

The goal is to explore failure modes in LLM-assisted legal analytis, particularly the gap between semantic similarity and legal disclosure.

## Dataset
The dataset consists of a small set of examples containing:
* a patent claim limitation
* a reference excerpt
* a ground truth lable indicating whether the excert discloses the limitation

The dataset is intentionally small and designed to illustrated evaluation stucture rather than provide a comprehensive benchmarkk.

## Method
The script prompts an LLM with:
* a claim limitation
* a reference excerpt

The model is basically asked to classify whether the excerpt:
* discloses the limitation
* partially discloses the limitation
* does not disclose it

Predictions are compared against the ground truth labels.

## Goal
The goal of this little experiment is to explore how LLMs perform on legal reasoning tasks, where plausible language overlap does not necessarily correspond to legal disclosure.
