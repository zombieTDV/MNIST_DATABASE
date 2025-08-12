from src.utils import MNISTOrganizer

if __name__ == "__main__":
    org = MNISTOrganizer()
    # # Lấy 10 ảnh mỗi label
    buckets = org.group_by_label(limit_per_label=None, show_progress=True)
    # for lbl, recs in buckets.items():
    #     print(f"label={lbl} count={len(recs)}")

    # # Xuất ra thư mục
    # org.export_to_folders(buckets, out_root="./mnist_by_class_test")
    
    # =======================

    # Ghi vào DB
    org.ensure_table("MNISTImages")
    print("Saving process started...")
    total_inserted = org.save_all_to_db(buckets, table_name="MNISTImages")
    print("Inserted into DB:", total_inserted)
