#!/bin/bash
celery -A app.celery_worker.app worker --loglevel DEBUG -E --concurrency=2 --without-gossip --without-mingle
