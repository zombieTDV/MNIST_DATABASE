# mnist_no_bucket.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Iterable, Tuple
import gzip
import os

import numpy as np
from PIL import Image
from tqdm import tqdm

import torch
from torchvision import datasets, transforms

import pyodbc
from config.settings import settings  # giữ cấu hình của bạn

# ---------- ImageRecord ----------
@dataclass
class ImageRecord:
    label: int
    array: np.ndarray  # dtype uint8, shape (28,28)

    def to_bytes(self, compress: bool = True) -> Tuple[bytes, bool]:
        """Trả về (bytes, gz_flag). Lưu raw bytes theo row-major."""
        raw = self.array.tobytes()
        if compress:
            return gzip.compress(raw), True
        return raw, False

    def to_pil(self) -> Image.Image:
        return Image.fromarray(self.array, mode="L")


# ---------- MNISTOrganizer ----------
class MNISTOrganizer:
    def __init__(self, root: str = "./mnist_data", train: bool = True, download: bool = True):
        self.root = root
        self.train = train
        self.download = download
        self._dataset = None
        self._transform = transforms.Compose([transforms.ToTensor()])

    def load_dataset(self):
        if self._dataset is None:
            self._dataset = datasets.MNIST(root=self.root, train=self.train, download=self.download, transform=self._transform)
        return self._dataset

    def iter_records(self):
        ds = self.load_dataset()
        for img_t, lbl in ds:
            arr = img_t.squeeze(0).mul(255).to(torch.uint8).cpu().numpy()
            yield ImageRecord(label=int(lbl), array=arr)

    def group_by_label(self, limit_per_label: Optional[int] = None, labels_only: Optional[Iterable[int]] = None, show_progress: bool = True) -> Dict[int, List[ImageRecord]]:
        """
        Trả về dict: label -> list[ImageRecord].
        - limit_per_label: giới hạn số ảnh mỗi label (None = không giới hạn).
        - labels_only: iterable các label cần gom (None = all 0..9).
        """
        labels_set = set(labels_only) if labels_only is not None else None
        # khởi tạo dict cho 0..9 để đảm bảo key luôn có sẵn
        buckets: Dict[int, List[ImageRecord]] = {i: [] for i in range(10)}
        ds = self.load_dataset()
        total = len(ds)
        it = self.iter_records()
        if show_progress:
            it = tqdm(it, total=total, desc="Grouping MNIST", unit="img")

        for rec in it:
            if labels_set is not None and rec.label not in labels_set:
                continue
            if limit_per_label is not None and len(buckets[rec.label]) >= limit_per_label:
                # kiểm tra tất cả labels (hoặc labels_set) đã đủ không
                keys = labels_set if labels_set is not None else range(10)
                if all(len(buckets[k]) >= limit_per_label for k in keys):
                    break
                continue
            buckets[rec.label].append(rec)
        return buckets

    # ---------- Export filesystem ----------
    def export_to_folders(self, buckets: Dict[int, List[ImageRecord]], out_root: str = "./mnist_by_class"):
        os.makedirs(out_root, exist_ok=True)
        for label, records in buckets.items():
            folder = os.path.join(out_root, str(label))
            os.makedirs(folder, exist_ok=True)
            for i, rec in enumerate(records):
                rec.to_pil().save(os.path.join(folder, f"{label}_{i}.png"))

    # ---------- Database helpers ----------
    def _conn(self):
        conn_str = (
            "DRIVER={driver};"
            "SERVER={server};"
            "DATABASE={database};"
            "UID={uid};"
            "PWD={pwd};"
        ).format(
            driver=settings.driver,
            server=settings.server,
            database=settings.database,
            uid=settings.username,
            pwd=settings.password,
        )
        return pyodbc.connect(conn_str, autocommit=True)

    def ensure_table(self, table_name: str = "MNISTImages"):
        conn = self._conn()
        try:
            cur = conn.cursor()
            create_sql = f"""
            IF OBJECT_ID(N'dbo.{table_name}', N'U') IS NULL
            BEGIN
                CREATE TABLE dbo.{table_name} (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    label TINYINT NOT NULL,
                    image VARBINARY(MAX) NOT NULL,
                    gzipped BIT NOT NULL DEFAULT 0,
                    created_at DATETIME2 DEFAULT SYSUTCDATETIME()
                );
                CREATE INDEX IX_{table_name}_Label ON dbo.{table_name}(label);
            END
            """
            cur.execute(create_sql)
            cur.close()
        finally:
            conn.close()

    def save_label_to_db(self, label: int, records: List[ImageRecord], table_name: str = "MNISTImages", batch_size: int = 500, compress: bool = True) -> int:
        """Ghi các ảnh của một label vào DB; trả về số ảnh đã ghi."""
        if not records:
            return 0
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.fast_executemany = True
            insert_sql = f"INSERT INTO dbo.{table_name} (label, image, gzipped) VALUES (?, ?, ?)"
            batch = []
            written = 0
            for rec in records:
                bts, gz = rec.to_bytes(compress=compress)
                batch.append((rec.label, pyodbc.Binary(bts), int(gz)))
                if len(batch) >= batch_size:
                    cur.executemany(insert_sql, batch)
                    written += len(batch)
                    batch = []
            if batch:
                cur.executemany(insert_sql, batch)
                written += len(batch)
            cur.close()
            return written
        finally:
            conn.close()

    def save_all_to_db(self, buckets: Dict[int, List[ImageRecord]], table_name: str = "MNISTImages", create_if_missing: bool = True, batch_size: int = 500, compress: bool = True) -> int:
        """Ghi tất cả buckets (dict) vào DB; trả về tổng số ảnh đã ghi."""
        if create_if_missing:
            self.ensure_table(table_name)
        total = 0
        for label, records in buckets.items():
            n = self.save_label_to_db(label, records, table_name=table_name, batch_size=batch_size, compress=compress)
            total += n
        return total

    def count_by_label_db(self, table_name: str = "MNISTImages") -> Dict[int, int]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            sql = f"SELECT label, COUNT(*) FROM dbo.{table_name} GROUP BY label ORDER BY label;"
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            return {int(r[0]): int(r[1]) for r in rows}
        finally:
            conn.close()

    def get_one_from_db(self, label: Optional[int] = None, row_id: Optional[int] = None, table_name: str = "MNISTImages", save_to: Optional[str] = None) -> Optional[Image.Image]:
        conn = self._conn()
        cur = conn.cursor()
        try:
            if row_id is not None:
                sql = f"SELECT id, label, image, gzipped FROM dbo.{table_name} WHERE id = ?;"
                cur.execute(sql, (row_id,))
            elif label is not None:
                sql = f"SELECT TOP 1 id, label, image, gzipped FROM dbo.{table_name} WHERE label = ?;"
                cur.execute(sql, (label,))
            else:
                sql = f"SELECT TOP 1 id, label, image, gzipped FROM dbo.{table_name};"
                cur.execute(sql)

            row = cur.fetchone()
            if not row:
                return None
            id_, lbl, image_bytes, gzipped = row
            raw = bytes(image_bytes)
            if gzipped:
                raw = gzip.decompress(raw)
            arr = np.frombuffer(raw, dtype=np.uint8).reshape((28, 28))
            img = Image.fromarray(arr, mode="L")
            if save_to:
                img.save(save_to)
            return img
        finally:
            cur.close()
            conn.close()