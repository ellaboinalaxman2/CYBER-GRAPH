"""Script to generate sample CICIDS2017-like data for Member 3."""

import os
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pandas as pd
    import numpy as np
    from tqdm import tqdm
except ImportError as e:
    print(f"Error: {e}")
    print("Please install required packages: pip install pandas numpy tqdm")
    sys.exit(1)


class CICIDS2017Generator:
    """
    Generates sample CICIDS2017-like data for testing.
    """
    
    # Feature columns (subset for demonstration)
    FEATURE_COLUMNS = [
        'Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
        'Total Length of Fwd Packets', 'Total Length of Bwd Packets', 'Fwd Packet Length Max',
        'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std',
        'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean',
        'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean',
        'Fwd IAT Total', 'Fwd IAT Mean', 'Bwd IAT Total', 'Bwd IAT Mean',
        'Fwd PSH Flags', 'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags',
        'Fwd Header Length', 'Bwd Header Length', 'Fwd Packets/s', 'Bwd Packets/s',
        'Min Packet Length', 'Max Packet Length', 'Packet Length Mean',
        'FIN Flag Count', 'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count',
        'ACK Flag Count', 'URG Flag Count', 'CWE Flag Count', 'ECE Flag Count',
        'Down/Up Ratio', 'Average Packet Size', 'Avg Fwd Segment Size',
        'Avg Bwd Segment Size', 'Init_Win_bytes_forward', 'Init_Win_bytes_backward',
        'act_data_pkt_fwd', 'min_seg_size_forward', 'Active Mean', 'Idle Mean',
        'Label'
    ]
    
    LABEL_MAPPING = {
        "BENIGN": 0,
        "BruteForce": 1,
        "DoS": 2,
        "DDoS": 3,
        "PortScan": 4,
        "Bot": 5,
        "Web Attack": 6,
        "Infiltration": 7,
        "Heartbleed": 8,
    }
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the generator.
        
        Args:
            data_dir: Directory to store data
        """
        self.data_dir = Path(data_dir or "data/raw/CICIDS2017")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = print
    
    def generate(self, size: int = 10000) -> bool:
        """
        Generate sample data.
        
        Args:
            size: Number of samples to generate
            
        Returns:
            bool: True if successful
        """
        print(f"Generating {size} sample records...")
        
        np.random.seed(42)
        
        # Generate feature data
        data = []
        labels = []
        
        for _ in tqdm(range(size), desc="Generating samples"):
            row = {}
            
            # Generate random features
            for col in self.FEATURE_COLUMNS[:-1]:  # Exclude Label
                if 'Flag' in col or 'URG' in col or 'PSH' in col:
                    row[col] = np.random.randint(0, 2)
                elif 'Bytes' in col or 'Length' in col:
                    row[col] = np.random.randint(0, 10000)
                elif 'Count' in col or 'Packets' in col:
                    row[col] = np.random.randint(0, 1000)
                elif 'Ratio' in col or 'Rate' in col:
                    row[col] = np.random.uniform(0, 100)
                elif 'Mean' in col or 'Std' in col or 'Max' in col or 'Min' in col:
                    row[col] = np.random.uniform(0, 1000)
                else:
                    row[col] = np.random.uniform(0, 100)
            
            # Assign label
            prob = np.random.random()
            if prob < 0.7:
                label = "BENIGN"
            elif prob < 0.85:
                label = "BruteForce"
            elif prob < 0.92:
                label = "DoS"
            elif prob < 0.96:
                label = "PortScan"
            else:
                label = "DDoS"
            
            row['Label'] = label
            data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to parquet
        output_file = self.data_dir / "cicids_sample.parquet"
        df.to_parquet(output_file)
        
        print(f"Generated {size} samples saved to {output_file}")
        
        # Create metadata
        metadata = {
            "dataset": "CICIDS2017",
            "version": "sample",
            "size": size,
            "features": len(self.FEATURE_COLUMNS) - 1,
            "classes": list(self.LABEL_MAPPING.keys()),
            "class_distribution": df['Label'].value_counts().to_dict(),
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
        
        metadata_file = self.data_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Metadata saved to {metadata_file}")
        
        # Also save as CSV for compatibility
        csv_file = self.data_dir / "cicids_sample.csv"
        df.to_csv(csv_file, index=False)
        print(f"CSV version saved to {csv_file}")
        
        return True
    
    def prepare_for_ml(self) -> pd.DataFrame:
        """
        Prepare the dataset for machine learning.
        
        Returns:
            pd.DataFrame: Prepared data
        """
        input_file = self.data_dir / "cicids_sample.parquet"
        
        if not input_file.exists():
            print(f"Input file not found: {input_file}")
            return None
        
        print(f"Preparing data from {input_file}")
        
        try:
            # Load data
            df = pd.read_parquet(input_file)
            
            # Handle missing values
            df = df.fillna(0)
            
            # Encode labels
            df['Label_Encoded'] = df['Label'].map(self.LABEL_MAPPING)
            
            # Drop rows with unknown labels
            df = df.dropna(subset=['Label_Encoded'])
            
            # Separate features and labels
            feature_cols = [col for col in df.columns if col not in ['Label', 'Label_Encoded']]
            X = df[feature_cols]
            y = df['Label_Encoded']
            
            # Normalize features
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Save prepared data
            prepared_file = self.data_dir / "cicids_prepared.parquet"
            prepared_df = pd.DataFrame(X_scaled, columns=feature_cols)
            prepared_df['Label'] = y.values
            prepared_df.to_parquet(prepared_file)
            
            print(f"Prepared data saved to {prepared_file}")
            print(f"Shape: {prepared_df.shape}")
            print(f"Classes: {prepared_df['Label'].unique()}")
            
            return prepared_df
            
        except Exception as e:
            print(f"Failed to prepare data: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        stats = {
            "data_dir": str(self.data_dir),
            "files": [],
            "total_size_mb": 0,
        }
        
        for file_path in self.data_dir.glob("*"):
            if file_path.is_file():
                stats["files"].append({
                    "name": file_path.name,
                    "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                })
                stats["total_size_mb"] += file_path.stat().st_size / (1024 * 1024)
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        
        # Try to load metadata
        metadata_file = self.data_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                stats["records"] = metadata.get("size", 0)
                stats["classes"] = metadata.get("classes", [])
                stats["features"] = metadata.get("features", 0)
        
        return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate CICIDS2017 sample data")
    parser.add_argument(
        "--sample",
        action="store_true",
        default=True,
        help="Generate sample data"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=10000,
        help="Number of samples to generate"
    )
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="Prepare data for ML after generation"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show dataset statistics"
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = CICIDS2017Generator()
    
    if args.stats:
        stats = generator.get_statistics()
        print("\n=== CICIDS2017 Dataset Statistics ===")
        print(json.dumps(stats, indent=2))
        return 0
    
    # Generate data
    success = generator.generate(size=args.size)
    
    if not success:
        print("Generation failed!")
        return 1
    
    # Prepare for ML
    if args.prepare:
        generator.prepare_for_ml()
    
    # Show statistics
    stats = generator.get_statistics()
    print("\n=== Generation Complete ===")
    print(json.dumps(stats, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())