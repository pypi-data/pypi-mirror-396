from typing import Dict, List, Set, Optional, Any
from .prophecy_dataframe import ProphecyDataFrame
import logging
import uuid

logger = logging.getLogger(__name__)


class Workflow:
    
    def __init__(self):
        self.process_pdfs: Dict[str, ProphecyDataFrame] = {}

    def create_pdf(self, gem_name: str) -> ProphecyDataFrame:
        logger.info(f"Gem '{gem_name}' not in workflow, creating new ProphecyDataFrame")
        pdf = ProphecyDataFrame.create(gem_name, consumer_count=1, is_pyspark_gem=False)
        unique_id = uuid.uuid4()
        gem_name_random = f"gem_name-{unique_id}"
        self.process_pdfs[gem_name_random] = pdf
        return self.process_pdfs.get(gem_name_random)

    def close_all(self) -> None:
        for process_name, pdf in self.process_pdfs.items():
            try:
                pdf.close()
            except Exception as e:
                print(f"Warning: Failed to close PDF for {process_name}: {e}")

        self.process_pdfs = {}
