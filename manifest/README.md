# Product Manifest Library

Product manifests define the long-lived product governance for Kaupfjelag Naersveitamanna products.

A manifest answers:

- why the product exists
- who it serves
- who it does not serve
- what it must never become
- which principles guide future engineering, product, governance, and business decisions

A manifest is not marketing copy.

A manifest is not architecture.

A manifest is not implementation.

It is the product's durable decision frame.

## Why Manifests Exist

Kaupfjelag products are expected to grow deliberately. A manifest prevents a product from drifting into whatever is easiest to build, easiest to sell, or fastest to automate.

The manifest gives teams a shared answer to:

- should we build this?
- does this fit the product?
- would this damage trust?
- does this serve the people we claim to serve?
- are we automating a good process, or merely speeding up a poor one?

## Difference From Architecture

Architecture defines how a system is structured.

A product manifest defines why the system deserves to exist and what boundaries must guide architecture.

Architecture can change as technology changes. The manifest should change rarely.

## Difference From Implementation

Implementation is code, configuration, migrations, interfaces, and operations.

A manifest is not a backlog. It does not prescribe classes, tables, routes, UI components, or vendors.

Implementation should be reviewed against the manifest before major work begins.

## When To Update A Manifest

Update a manifest when:

- the product mission changes
- the target audience changes
- a new business model changes incentives
- a product starts serving a materially different use case
- governance boundaries need clarification
- repeated decisions show that the manifest is ambiguous

Do not update a manifest just to justify a feature already chosen.

## New Product Order

Every new Kaupfjelag product should begin in this order:

```text
Product Manifest
↓
Architecture
↓
Governance
↓
Canonical Objects / Domain Model
↓
UX / Product Design
↓
Implementation
```

## Manifest Index

- [Company Manifest](company-manifest.md)
- [Hladvarp Manifest](hladvarp-manifest.md)
- [SecureVault Manifest](securevault-manifest.md)
- [Health Platform Manifest](health-platform-manifest.md)
- [Kaupfjelag Development System Manifest](kaupfjelag-development-system-manifest.md)
