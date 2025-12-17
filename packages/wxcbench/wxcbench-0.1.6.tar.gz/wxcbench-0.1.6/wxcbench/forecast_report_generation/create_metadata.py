"""
Create Metadata Module

Creates a metadata CSV file that pairs HRRR weather data files with their
corresponding forecast discussions for machine learning training.
"""

import os
from pathlib import Path
from typing import Optional
import pandas as pd

from wxcbench.forecast_report_generation.config import DEFAULT_METADATA_OUTPUT_FILE


def create_metadata(
    image_dir: str,
    caption_dir: str,
    output_file: Optional[str] = None
) -> pd.DataFrame:
    """
    Create a metadata CSV file by matching HRRR images with their captions.
    
    This function processes a directory of HRRR files (.grib2) and corresponding
    caption files (.csv), and generates a single metadata file in CSV format
    suitable for machine learning training.
    
    Parameters
    ----------
    image_dir : str
        Path to the directory containing HRRR image files (.grib2)
    caption_dir : str
        Path to the directory containing caption files (.csv)
    output_file : str, optional
        Path to save the generated metadata CSV file.
        If None, uses default from config (default: None)
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing the metadata with columns: file_name, text
        
    Examples
    --------
    >>> import wxcbench.forecast_report_generation as frg
    >>> df = frg.create_metadata(
    ...     image_dir="hrrr",
    ...     caption_dir="csv_reports",
    ...     output_file="metadata.csv"
    ... )
    """
    if output_file is None:
        output_file = DEFAULT_METADATA_OUTPUT_FILE
    
    metadata_rows = []
    
    # Verify directories exist
    image_path = Path(image_dir)
    caption_path = Path(caption_dir)
    
    if not image_path.is_dir():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    if not caption_path.is_dir():
        raise FileNotFoundError(f"Caption directory not found: {caption_dir}")
    
    # Process each image file
    for filename in os.listdir(image_dir):
        if filename.endswith(".grib2"):
            # Generate the corresponding caption file name
            # HRRR filename format: hrrr.YYYYMMDD.tHHZ.wrfDATATYPEfFF.grib2
            # Caption filename format: YYYYMMDD.csv
            parts = filename.split(".")
            if len(parts) >= 2:
                date_part = parts[1]  # YYYYMMDD
                label_filename = f"{date_part}.csv"
            else:
                continue
            
            label_path = caption_path / label_filename
            
            # Check if caption file exists
            if not label_path.is_file():
                continue
            
            try:
                # Read the caption file
                caption_df = pd.read_csv(label_path, index_col=0)
                
                # Extract discussion text
                if "discussion" in caption_df.columns:
                    caption = caption_df.iloc[0]["discussion"].strip()
                else:
                    # Try to get first column if "discussion" doesn't exist
                    caption = str(caption_df.iloc[0, 0]).strip()
                
                # Save metadata
                metadata_rows.append({
                    "file_name": filename,
                    "text": caption
                })
                
            except Exception as e:
                raise ValueError(f"Error processing caption file {label_path}: {e}")
    
    # Write metadata to output file
    if metadata_rows:
        metadata_df = pd.DataFrame(metadata_rows)
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_df.to_csv(output_file, index=False)
        print(f"Metadata file created: {output_file} with {len(metadata_df)} entries")
        return metadata_df
    else:
        raise ValueError(
            "No metadata was generated. Please check input files and directories."
        )

