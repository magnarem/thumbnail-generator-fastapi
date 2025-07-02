# Thumbnail Generator API

This project provides a **FastAPI-based web API** for generating thumbnail images from a **WMS (Web Map Service) resource**. The API allows clients to request a thumbnail by providing a WMS URL and returns a URL where the generated thumbnail can be fetched later. Thumbnail generation is handled asynchronously using **Celery** workers, and thumbnails are served via an external **Nginx** service.

---

## Features

- **FastAPI Web API**:
  - Accepts requests with a WMS URL.
  - Responds with a URL where the generated thumbnail can be fetched. Used for indexing to solr
  - Validates requests and responses using **Pydantic models**.

- **Asynchronous Thumbnail Generation**:
  - Uses **Celery** workers for background processing.
  - Stores thumbnails on disk for retrieval via Nginx.

- **Redis as Broker and Result Backend**:
  - Redis is used as the message broker and result backend for Celery.

- **Scalable and Decoupled Architecture**:
  - API and worker components are independent, allowing horizontal scaling.

---

## Technologies Used

- **FastAPI**: High-performance web framework for building APIs with Python.
- **Pydantic**: Data validation and serialization for request and response models.
- **Celery**: Distributed task queue for background processing.
- **Redis**: Message broker and result backend for Celery.
- **Nginx**: Serves the generated thumbnails (configured separately, not part of this project).
- **Python**: The core language for the application.
- **Docker**: (Optional) For containerized deployment of the API and workers.

---

## Installation

### Prerequisites

Ensure the following are installed on your system:

- Python 3.8+
- Redis server
- (Optional) Docker and Docker Compose

### Clone the Repository

```bash
git clone https://github.com/your-username/thumbnail-generator-api.git
cd thumbnail-generator-ap
