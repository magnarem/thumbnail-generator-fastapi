#!/bin/bash
celery --broker=redis://localhost:6379/0 flower --port=5432
