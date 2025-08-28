from django.core.management.base import BaseCommand
from nextrag.rag_pipeline import build_and_save_vectorstore

class Command(BaseCommand):
    help = "Update vector store with all PDFs in the knowledge base."

    # Build or Update the vector store
    def handle(self, *args, **kwargs):
        build_and_save_vectorstore()
        self.stdout.write(self.style.SUCCESS("Knowledge base successfully updated."))
