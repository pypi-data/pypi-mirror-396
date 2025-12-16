"""
Bulk CSV processing for phone verification
"""

import csv
from collections.abc import Iterable, Iterator, Sequence
from io import StringIO

from aws_lambda_powertools import Logger

from .models import PhoneVerification
from .verifier import PhoneVerifier

logger = Logger()


class BulkProcessor:
    """Process CSV files for bulk phone verification"""

    def __init__(self, verifier: PhoneVerifier):
        self.verifier = verifier

    def process_csv(self, csv_text: str, phone_column: str = "phone") -> list[PhoneVerification]:
        """
        Process CSV text content.
        Returns list of verification results.
        """
        results = []

        try:
            # Use StringIO to parse CSV text
            csv_file = StringIO(csv_text)
            reader = csv.DictReader(csv_file)

            # Find phone column (case-insensitive)
            headers = reader.fieldnames or []
            phone_col = self._find_phone_column(headers, phone_column)

            if not phone_col:
                raise ValueError(f"Phone column '{phone_column}' not found in CSV")

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                try:
                    phone = row.get(phone_col, "").strip()
                    if not phone:
                        logger.warning(f"Empty phone at row {row_num}")
                        continue

                    # Verify phone
                    result = self.verifier.verify(phone)
                    results.append(result)

                    # Log progress every 100 rows
                    if len(results) % 100 == 0:
                        logger.info(f"Processed {len(results)} phones")

                except ValueError as e:
                    logger.warning(f"Invalid phone at row {row_num}: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing row {row_num}: {str(e)}")
                    continue

            logger.info(f"Completed processing {len(results)} valid phones")

        except Exception as e:
            logger.error(f"CSV processing failed: {str(e)}")
            raise

        return results

    def _find_phone_column(self, headers: list[str] | Sequence[str], preferred: str) -> str | None:
        """Find phone column in headers (case-insensitive)"""
        # First try exact match
        for header in headers:
            if header.lower() == preferred.lower():
                return header

        # Common phone column names
        phone_patterns = [
            "phone",
            "phone_number",
            "phonenumber",
            "mobile",
            "cell",
            "telephone",
            "tel",
            "number",
            "contact",
        ]

        for header in headers:
            header_lower = header.lower()
            for pattern in phone_patterns:
                if pattern in header_lower:
                    logger.info(f"Using column '{header}' as phone column")
                    return header

        return None

    def generate_results_csv(self, original_csv_text: str, results: list[PhoneVerification]) -> str:
        """
        Generate CSV with original data plus verification results.
        Adds columns: line_type, dnc, cached
        Returns CSV text string.
        """
        # Create lookup dict
        results_map = {r.phone_number: r for r in results}

        # Parse original CSV
        input_file = StringIO(original_csv_text)
        reader = csv.DictReader(input_file)
        headers = list(reader.fieldnames or [])

        # Add new columns
        output_headers = headers + ["line_type", "dnc", "cached"]

        # Create output CSV in memory
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=output_headers)
        writer.writeheader()

        phone_col = self._find_phone_column(headers, "phone")

        for row in reader:
            phone = row.get(phone_col, "").strip()

            # Try to normalize for lookup
            try:
                normalized = self.verifier.normalize_phone(phone)
                if normalized in results_map:
                    result = results_map[normalized]
                    row["line_type"] = result.line_type.value
                    row["dnc"] = "true" if result.dnc else "false"
                    row["cached"] = "true" if result.cached else "false"
                else:
                    row["line_type"] = "unknown"
                    row["dnc"] = ""
                    row["cached"] = ""
            except Exception:
                row["line_type"] = "invalid"
                row["dnc"] = ""
                row["cached"] = ""

            writer.writerow(row)

        # Return CSV text
        return output.getvalue()

    def process_csv_stream(
        self, lines: Iterable[str], phone_column: str = "phone", batch_size: int = 100
    ) -> Iterator[list[PhoneVerification]]:
        """
        Process CSV lines as a stream, yielding batches of results.
        Memory-efficient for large files.

        Args:
            lines: Iterator of CSV lines (including header)
            phone_column: Column name containing phone numbers
            batch_size: Number of results to accumulate before yielding

        Yields:
            Batches of PhoneVerification results
        """
        lines_list = list(lines)  # Need to iterate twice - once for headers, once for data

        if not lines_list:
            logger.error("Empty CSV stream")
            return

        # Parse header
        header_line = lines_list[0]
        reader = csv.DictReader(StringIO(header_line))
        headers = reader.fieldnames or []
        phone_col = self._find_phone_column(headers, phone_column)

        if not phone_col:
            raise ValueError(f"Phone column '{phone_column}' not found in CSV")

        batch = []
        row_num = 2  # Start at 2 (header is 1)
        total_processed = 0

        # Process data lines
        for line in lines_list[1:]:
            if not line.strip():
                continue

            try:
                # Parse single line
                row = next(csv.DictReader(StringIO(line), fieldnames=headers))
                phone = row.get(phone_col, "").strip()

                if not phone:
                    logger.warning(f"Empty phone at row {row_num}")
                    row_num += 1
                    continue

                # Verify phone
                result = self.verifier.verify(phone)
                batch.append(result)
                total_processed += 1

                # Yield batch when full
                if len(batch) >= batch_size:
                    logger.info(
                        f"Processed batch of {len(batch)} phones (total: {total_processed})"
                    )
                    yield batch
                    batch = []

            except ValueError as e:
                logger.warning(f"Invalid phone at row {row_num}: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing row {row_num}: {str(e)}")
            finally:
                row_num += 1

        # Yield remaining results
        if batch:
            logger.info(f"Processed final batch of {len(batch)} phones (total: {total_processed})")
            yield batch

        logger.info(f"Stream processing completed. Total processed: {total_processed}")

    def generate_results_csv_stream(
        self,
        original_lines: Iterable[str],
        results_stream: Iterator[list[PhoneVerification]],
        phone_column: str = "phone",
    ) -> Iterator[str]:
        """
        Generate CSV results as a stream, line by line.
        Memory-efficient for large files.

        Args:
            original_lines: Iterator of original CSV lines
            results_stream: Iterator of batched PhoneVerification results
            phone_column: Column name containing phone numbers

        Yields:
            CSV lines with verification results added
        """
        lines_iter = iter(original_lines)

        # Read and yield modified header
        try:
            header_line = next(lines_iter)
            reader = csv.DictReader(StringIO(header_line))
            headers = list(reader.fieldnames or [])

            # Add new columns
            output_headers = headers + ["line_type", "dnc", "cached"]
            yield ",".join(output_headers) + "\n"

            phone_col = self._find_phone_column(headers, phone_column)

        except StopIteration:
            return

        # Build results lookup from stream
        results_map = {}
        for batch in results_stream:
            for result in batch:
                results_map[result.phone_number] = result

        # Reset lines iterator
        lines_iter = iter(original_lines)
        next(lines_iter)  # Skip header

        # Process and yield data lines
        for line in lines_iter:
            if not line.strip():
                continue

            row = next(csv.DictReader(StringIO(line), fieldnames=headers))
            phone = row.get(phone_col, "").strip()

            # Add verification results
            try:
                normalized = self.verifier.normalize_phone(phone)
                if normalized in results_map:
                    result = results_map[normalized]
                    row["line_type"] = result.line_type.value
                    row["dnc"] = "true" if result.dnc else "false"
                    row["cached"] = "true" if result.cached else "false"
                else:
                    row["line_type"] = "unknown"
                    row["dnc"] = ""
                    row["cached"] = ""
            except Exception:
                row["line_type"] = "invalid"
                row["dnc"] = ""
                row["cached"] = ""

            # Write row
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=output_headers)
            writer.writerow(row)
            yield output.getvalue()
