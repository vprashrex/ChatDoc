from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.processes.connectors.local import (
    LocalIndexerConfig,
    LocalDownloaderConfig,
    LocalConnectionConfig,
    LocalUploaderConfig

)

from langchain_community.embeddings import GPT4AllEmbeddings

from unstructured_ingest.v2.processes.partitioner import PartitionerConfig
from unstructured_ingest.v2.processes.chunker import ChunkerConfig
#imports
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

from unstructured.partition.pdf import partition_pdf
import uuid
import shutil
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.schema.document import Document
from langchain.storage import InMemoryStore
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from unstructured.staging.base import elements_from_json
from dotenv import load_dotenv

load_dotenv()


class Embedding:
    def __init__(self,user_id:str):
        self.input_dir = f"data/input/{user_id}/"
        self.output_dir = f"data/output/{user_id}/"
        self.collection_name = f"{user_id}_collection"
        self.presist_path = f"embedding_db/{user_id}_db"
        
        Pipeline.from_configs(
            context=ProcessorConfig(),
            indexer_config=LocalIndexerConfig(input_path=self.input_dir),
            downloader_config=LocalDownloaderConfig(),
            source_connection_config=LocalConnectionConfig(),
            partitioner_config=PartitionerConfig(
                partition_by_api=False,
                strategy="fast",
                additional_partition_args={
                    "split_pdf_page": True,
                    "split_pdf_concurrency_level": 15,
                    "chunking_strategy":"by_title",
                    "max_characters":4000,
                    "new_after_n_chars":3800,
                    "combine_text_under_n_chars":2000,
                    },
                ),
            uploader_config=LocalUploaderConfig(output_dir=self.output_dir)
        ).run()

        self.vectorstore = Chroma(collection_name=self.collection_name, embedding_function=NVIDIAEmbeddings(
          model="nvidia/nv-embed-v1",
          api_key=os.getenv("NVIDIA_API_KEY"),
          truncate="NONE"
        ),persist_directory=self.presist_path,)

        store = InMemoryStore()
        self.id_key = "doc_id"
        self.retriever = MultiVectorRetriever(vectorstore=self.vectorstore, docstore=store, id_key=self.id_key)
        self.load_process_file(self.output_dir)
        self.save_vector()
        self.delete_file(self.input_dir,self.output_dir)

    def delete_file(self,input_dir,output_dir):
        shutil.rmtree(os.path.abspath(input_dir), ignore_errors=True)
        shutil.rmtree(os.path.abspath(output_dir), ignore_errors=True)

    def load_process_file(self,output_dir):
        elements = []
        for filename in os.listdir(output_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(os.path.abspath(output_dir), filename)
                try:
                    elements.extend(elements_from_json(filename=file_path))
                except IOError:
                    print(f"Error: Could not read file {filename}.")
        text_elements = []
        for element in elements:
            if 'CompositeElement' in str(type(element)):
                text_elements.append(element)
        self.text_elements = [i.text for i in text_elements]
        
    

    def save_vector(self):
        doc_ids = [str(uuid.uuid4()) for _ in self.text_elements]
        summary_docs = [
                Document(page_content=s, metadata={self.id_key: doc_ids[i]})
                for i, s in enumerate(self.text_elements)
            ]

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=300)
        all_splits_pypdf = text_splitter.split_documents(summary_docs)
        print("processing retriever .....")
        self.retriever.vectorstore.add_documents(all_splits_pypdf)
        self.retriever.docstore.mset(list(zip(doc_ids, self.text_elements)))