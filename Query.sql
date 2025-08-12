CREATE DATABASE MNIST_DB;
GO

USE MNIST_DB;
GO

CREATE TABLE MNISTImages (
    id INT IDENTITY(1,1) PRIMARY KEY,
    label TINYINT NOT NULL,
    image VARBINARY(MAX) NOT NULL,
    gzipped BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- tạo index để truy vấn theo class nhanh
CREATE INDEX IX_MNIST_Label ON MNISTImages(label);


-- Kiểm tra xem bảng đã tồn tại chưa
SELECT * FROM MNISTImages;

-- Kiểm tra số lượng bản ghi trong bảng
SELECT COUNT(*) FROM MNISTImages


-- Xoá dữ liệu cũ nếu có
TRUNCATE TABLE MNISTImages;