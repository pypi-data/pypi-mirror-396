from typing import Dict, List

from ...enums import LogCode, UploadStatus
from ..base import DataUnitStrategy


class SingleDataUnitStrategy(DataUnitStrategy):
    """Single data unit generation strategy."""

    def __init__(self, context):
        self.context = context

    def generate(self, uploaded_files: List[Dict], batch_size: int) -> List[Dict]:
        """Generate data units individually."""
        client = self.context.client
        generated_data_units = []

        for uploaded_file in uploaded_files:
            try:
                # Create data unit for single file (batch of 1)
                created_data_units = client.create_data_units([uploaded_file])
                generated_data_units.extend(created_data_units)

            except Exception as e:
                self.context.run.log_message_with_code(LogCode.DATA_UNIT_BATCH_FAILED, str(e))
                # Log failed data unit
                self.context.run.log_data_unit(None, UploadStatus.FAILED, data_unit_meta=None)

        return generated_data_units
