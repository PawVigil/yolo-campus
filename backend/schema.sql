-- ============================================================
-- 校园流浪动物观测关爱系统 · 数据库建表脚本
-- 数据库: SQLite 3
-- 文件: campus_animals.db
-- 执行: python db.py → init_db()
-- 参考：系统设计说明书 7.1 完整建表 SQL
-- ============================================================

-- 启用外键约束（SQLite默认关闭！）
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------
-- 表1: user（管理员用户表）
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS user (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL,        -- SHA-256 hex (64 chars)
    role            TEXT    NOT NULL DEFAULT 'admin',
    created_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 初始管理员账号（密码: admin123）
-- SHA-256("admin123") = 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
INSERT OR IGNORE INTO user (username, password_hash)
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');

-- ----------------------------------------------------------
-- 表2: location（地点表）
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS location (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,        -- 地点名称
    description     TEXT,                    -- 地点描述
    safety_tip      TEXT,                    -- 当前生效的安全提醒（冗余缓存）
    created_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 预置5个校园地点
INSERT OR IGNORE INTO location (name, description) VALUES
    ('食堂', '校园食堂及周边区域，中午人流量大'),
    ('宿舍', '学生宿舍楼周边，傍晚较为安静'),
    ('图书馆', '图书馆前后绿化带'),
    ('操场', '田径场及周边健身区域'),
    ('花园', '校园中心花园及小树林');

-- ----------------------------------------------------------
-- 表3: detection（检测记录表 —— 核心表）
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS detection (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id     INTEGER NOT NULL,
    user_id         INTEGER NOT NULL,
    image_path      TEXT    NOT NULL,        -- 上传图片路径
    detect_time     TEXT    NOT NULL,        -- ISO 8601 拍摄/检测时间
    result_json     TEXT    NOT NULL,        -- YOLO检测结果JSON
    total_animals   INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (location_id) REFERENCES location(id),
    FOREIGN KEY (user_id)     REFERENCES user(id)
);

-- 索引：加速常见查询
CREATE INDEX IF NOT EXISTS idx_detection_location
    ON detection(location_id);
CREATE INDEX IF NOT EXISTS idx_detection_time
    ON detection(detect_time);
CREATE INDEX IF NOT EXISTS idx_detection_location_time
    ON detection(location_id, detect_time);
CREATE INDEX IF NOT EXISTS idx_detection_animals
    ON detection(total_animals);    -- 加速 WHERE total_animals > 0

-- ----------------------------------------------------------
-- 表4: safety_tip（安全提醒表）
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS safety_tip (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id     INTEGER NOT NULL,
    title           TEXT    NOT NULL,
    content         TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'draft',
                    -- CHECK(status IN ('draft','published','archived'))
                    -- SQLite check constraint via application layer
    created_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    published_at    TEXT,                    -- 发布时间（draft时为NULL）
    FOREIGN KEY (location_id) REFERENCES location(id)
);

CREATE INDEX IF NOT EXISTS idx_safety_tip_status
    ON safety_tip(status);
CREATE INDEX IF NOT EXISTS idx_safety_tip_location
    ON safety_tip(location_id);

-- ----------------------------------------------------------
-- 表5: community_share（社区分享表 —— 独立于detection数据线）
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS community_share (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id     INTEGER,                -- 可选，允许不选地点
    image_path      TEXT    NOT NULL,
    description     TEXT,                    -- 用户自行填写的描述
    nickname        TEXT,                    -- 用户昵称（匿名也可）
    breed           TEXT,                    -- YOLO识别品种名（可选）
    created_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (location_id) REFERENCES location(id)
);

CREATE INDEX IF NOT EXISTS idx_community_time
    ON community_share(created_at DESC);
