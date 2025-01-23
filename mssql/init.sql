-- init.sql
-- データベースの作成
CREATE DATABASE MCPDatabase;
GO

USE MCPDatabase;
GO

-- クエリ履歴テーブル
CREATE TABLE query_history (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    query_text NVARCHAR(MAX),
    transformed_query NVARCHAR(MAX),
    execution_result NVARCHAR(MAX),
    error_message NVARCHAR(MAX),
    execution_time FLOAT,
    success BIT,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- インデックスの作成
CREATE INDEX idx_query_history_created_at ON query_history(created_at);
CREATE INDEX idx_query_history_success ON query_history(success);

-- メタデータテーブル
CREATE TABLE mcp_metadata (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    table_name NVARCHAR(128),
    column_name NVARCHAR(128),
    data_type NVARCHAR(128),
    description NVARCHAR(MAX),
    sample_values NVARCHAR(MAX),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- パフォーマンスモニタリングテーブル
CREATE TABLE performance_metrics (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    query_id BIGINT,
    cpu_time BIGINT,
    elapsed_time BIGINT,
    logical_reads BIGINT,
    physical_reads BIGINT,
    row_count BIGINT,
    execution_plan XML,
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (query_id) REFERENCES query_history(id)
);

-- パーティション関数の作成（日付ベース）
CREATE PARTITION FUNCTION PF_QueryHistory_Date (DATETIME2)
AS RANGE RIGHT FOR VALUES (
    '2024-01-01', '2024-04-01', '2024-07-01', '2024-10-01',
    '2025-01-01', '2025-04-01', '2025-07-01', '2025-10-01'
);
GO

-- パーティションスキーマの作成
CREATE PARTITION SCHEME PS_QueryHistory_Date
AS PARTITION PF_QueryHistory_Date
ALL TO ([PRIMARY]);
GO

-- ストアドプロシージャ: クエリ履歴のクリーンアップ
CREATE PROCEDURE sp_cleanup_query_history
    @days_to_keep INT = 30
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @cutoff_date DATETIME2 = DATEADD(DAY, -@days_to_keep, GETDATE());
    
    BEGIN TRANSACTION;
    
    DELETE FROM performance_metrics
    WHERE query_id IN (
        SELECT id FROM query_history
        WHERE created_at < @cutoff_date
    );
    
    DELETE FROM query_history
    WHERE created_at < @cutoff_date;
    
    COMMIT TRANSACTION;
END;
GO

-- ジョブの作成: 自動クリーンアップ
-- Note: SQLServerエージェントが必要です
EXEC msdb.dbo.sp_add_job
    @job_name = N'Cleanup Query History',
    @enabled = 1,
    @description = N'Automatically cleanup old query history records';
GO

EXEC msdb.dbo.sp_add_jobstep
    @job_name = N'Cleanup Query History',
    @step_name = N'Execute Cleanup',
    @subsystem = N'TSQL',
    @command = N'EXEC sp_cleanup_query_history @days_to_keep = 30';
GO

EXEC msdb.dbo.sp_add_jobschedule
    @job_name = N'Cleanup Query History',
    @name = N'Daily Cleanup',
    @freq_type = 4,
    @freq_interval = 1,
    @active_start_time = 010000;
GO

-- 統計情報の自動更新設定
ALTER DATABASE MCPDatabase
SET AUTO_UPDATE_STATISTICS ON;
GO

ALTER DATABASE MCPDatabase
SET AUTO_UPDATE_STATISTICS_ASYNC ON;
GO

-- メモリ設定の最適化
EXEC sys.sp_configure 'show advanced options', 1;
GO
RECONFIGURE;
GO

EXEC sys.sp_configure 'max server memory (MB)', 8192;
GO
RECONFIGURE;
GO

-- MAXDOPの設定
EXEC sys.sp_configure 'max degree of parallelism', 4;
GO
RECONFIGURE;
GO