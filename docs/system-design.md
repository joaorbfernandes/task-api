# TM System Design

## Overview

TM is a Task Manager API built as a backend engineering project.

The goal is to keep the product small and clear while evolving the internal architecture in a professional way.

## Focus

The project focuses on:

- task CRUD operations
- request validation
- testing
- architecture refactoring
- domain and persistence separation
- layered backend structure

## Core Domain

The system is currently centred on `Task`.

The domain is responsible for task behaviour and business rules.

This includes decisions such as:

- task lifecycle
- state changes
- editability rules
- domain-level consistency

Other entities such as comments or users may be introduced later, but they are not part of the current core scope.

## Architecture

The current structure is:

```text
routers
↓
services
↓
domain
↓
repositories
↓
in-memory storage
```

Responsibilities are separated as follows:
- routers handle HTTP concerns
- services orchestrate application behaviour
- repositories handle persistence
- domain entities hold business rules

## Roadmap

- EPIC-01 Core Task API
- EPIC-02 Architecture Refactor
- EPIC-03 Persistence Layer
- EPIC-04 Authentication and Ownership
- EPIC-05 Comments and Basic Collaboration
- EPIC-06 Production Readiness