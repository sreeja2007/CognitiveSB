from celery import Celery

def make_celery():
    return Celery(
        "shadowbyte",
        broker="redis://localhost:6379/0",
        backend="redis://localhost:6379/0",
        include=["tasks"],
    )

celery = make_celery()
